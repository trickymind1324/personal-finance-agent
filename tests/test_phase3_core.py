"""Phase 3 checkpoint: the deterministic core (ledger → recurrence → simulate → solver → plans → reconcile).

Every test docstring names the design decision it guards; each rule has a trip case and the nearest legitimate
negative. Synthetic ledgers are built with `mk_*` helpers so no test depends on dataset rows except the last
end-to-end block, which pins the sample-set metrics.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from buyorwait.config import DEFAULT_CONFIG, Config
from buyorwait.contract import OUTPUT_COLUMNS
from buyorwait.ledger import UnresolvedAmountError, normalize_ledger
from buyorwait.models import Amendment, Event, Flow, Ledger, Payment, PaymentOption, Plan, Profile, Request, Stream
from buyorwait.plans import change_candidates, choose, enumerate_candidates, rank_key, search_changes
from buyorwait.rates import MissingRateError, convert
from buyorwait.recurrence import add_months, infer_streams
from buyorwait.simulate import build_curve, is_safe
from buyorwait.solver import earliest_full_date, safe_amount_today

ROOT = Path(__file__).resolve().parents[1]
T0 = date(2026, 3, 5)
D = Decimal


# ----------------------------------------------------------------------------- builders
def mk_profile(**kw) -> Profile:
    base = dict(
        user_id="user_t",
        home_currency="EUR",
        current_available_balance=D("3000"),
        minimum_balance_to_keep=D("1000"),
        financial_priorities=frozenset(),
        protect_categories=frozenset({"rent"}),
        reduce_categories=frozenset({"dining"}),
        stop_categories=frozenset({"streaming"}),
        methods=frozenset({"full_payment", "partial_payment", "installments"}),
        max_installment_months=6,
    )
    base.update(kw)
    return Profile(**base)


def mk_request(**kw) -> Request:
    base = dict(
        request_id="request_t",
        user_id="user_t",
        request_date=T0,
        request_type="purchase",
        requested_amount=D("500"),
        requested_amount_text="500",
        desired_completion_date=T0 + timedelta(days=40),
        allows_partial_payment=True,
        request_text="",
    )
    base.update(kw)
    return Request(**base)


_counter = [0]


def mk_event(
    on: date,
    amount: str | None,
    category: str,
    description: str,
    direction: str = "debit",
    status: str = "settled",
    event_type: str | None = None,
    flexibility: str = "fixed",
    min_allowed: str | None = None,
    currency: str = "EUR",
    linked: str | None = None,
) -> Event:
    _counter[0] += 1
    return Event(
        event_id=f"event_{_counter[0]}",
        user_id="user_t",
        event_type=event_type or ("income" if direction == "credit" else "expense"),
        description=description,
        category=category,
        direction=direction,
        amount=D(amount) if amount is not None else None,
        currency=currency,
        event_date=on,
        settlement_date=on,
        status=status,
        linked_event_id=linked,
        flexibility=flexibility,
        minimum_allowed_amount=D(min_allowed) if min_allowed else None,
    )


def monthly(
    day: int, amount: str, category: str, description: str, months: int = 5, end: date = T0, **kw
) -> list[Event]:
    out = []
    for k in range(months, 0, -1):
        on = add_months(end, -k, day)
        if on < end:
            out.append(mk_event(on, amount, category, description, **kw))
    return out


def every(days: int, amount: str, category: str, description: str, n: int = 12, end: date = T0, **kw) -> list[Event]:
    """n occurrences every `days`, the LAST one on `end` (settled on T0 is allowed; the next is T0 + days)."""
    return [mk_event(end - timedelta(days=days * k), amount, category, description, **kw) for k in range(n - 1, -1, -1)]


def ledger_for(
    events: list[Event],
    amendments: list[Amendment] | None = None,
    profile: Profile | None = None,
    cfg: Config = DEFAULT_CONFIG,
) -> Ledger:
    return normalize_ledger(profile or mk_profile(), events, amendments or [], {}, T0, cfg)


def streams_by_key(events: list[Event], **kw) -> dict[str, Stream]:
    return {s.key: s for s in infer_streams(ledger_for(events, **kw), kw.get("cfg", DEFAULT_CONFIG))}


# ----------------------------------------------------------------------------- rates
def test_convert_uses_exact_dated_rate_and_direction() -> None:
    """Design decision I-11: exact (date, from, to) row; the inverse pair is a different row, never 1/rate."""
    table = {(date(2026, 3, 15), "USD", "EUR"): D("0.92"), (date(2026, 3, 15), "EUR", "USD"): D("1.09")}
    assert convert(D("100"), "USD", "EUR", date(2026, 3, 15), table) == D("92.00")
    assert convert(D("100"), "EUR", "USD", date(2026, 3, 15), table) == D("109.00")
    assert convert(D("100"), "EUR", "EUR", date(2026, 3, 16), table) == D("100")


def test_convert_missing_rate_raises_never_interpolates() -> None:
    """Design decision I-11: a missing (date, pair) raises MissingRateError."""
    with pytest.raises(MissingRateError):
        convert(D("1"), "USD", "EUR", date(2026, 3, 16), {(date(2026, 3, 15), "USD", "EUR"): D("0.92")})


# ----------------------------------------------------------------------------- ledger admission
def test_ledger_status_table() -> None:
    """Design decision §5.1: pending/scheduled debits reserved; pending credits ignored; failed/cancelled/unrealized dropped."""
    evs = [
        mk_event(T0 + timedelta(days=2), "50", "shopping", "Pending merchant debit", status="pending"),
        mk_event(
            T0 + timedelta(days=3),
            "70",
            "shopping",
            "Pending merchant refund",
            direction="credit",
            status="pending",
            event_type="refund",
        ),
        mk_event(T0 + timedelta(days=4), "60", "utilities", "Scheduled utility debit", status="scheduled"),
        mk_event(T0 + timedelta(days=5), "999", "utilities", "Failed utility debit", status="failed"),
        mk_event(T0 + timedelta(days=6), "999", "shopping", "Cancelled card authorization", status="cancelled"),
        mk_event(
            T0 + timedelta(days=10), "1200", "salary", "Next confirmed salary", direction="credit", status="scheduled"
        ),
    ]
    led = ledger_for(evs)
    amounts = sorted((f.on, f.amount) for f in led.known_flows)
    assert amounts == [
        (T0 + timedelta(days=2), D("-50")),
        (T0 + timedelta(days=4), D("-60")),
        (T0 + timedelta(days=10), D("1200")),
    ]
    assert [f.amount for f in led.scheduled_income] == [D("1200")]
    assert any("pending credit ignored" in n for n in led.notes)


def test_pending_debit_dated_before_request_is_reserved_on_request_date() -> None:
    """Design decision §10 (open item resolved): a pending debit with settlement before T0 is reserved on T0 (safer)."""
    led = ledger_for(
        [mk_event(T0 - timedelta(days=2), "40", "transport", "Pending fuel authorization", status="pending")]
    )
    assert [(f.on, f.amount) for f in led.known_flows] == [(T0, D("-40"))]


def test_blank_amount_debit_without_evidence_raises_and_with_evidence_is_used() -> None:
    """Design decision I-12: a forecast-affecting blank amount is never zero — raise without evidence, use the image amount with it."""
    ev = mk_event(T0 + timedelta(days=4), None, "rent", "Outstanding rent balance", status="scheduled")
    with pytest.raises(UnresolvedAmountError):
        ledger_for([ev])
    led = ledger_for([ev], [Amendment("amount", ev.event_id, "image_02", amount=D("100000"))])
    assert led.known_flows[0].amount == D("-100000")


def test_duplicate_charge_reserved_unless_reversal_posted() -> None:
    """Design decision §5.1: a pending 'possible duplicate' is reserved (safer) unless evidence says the reversal posted."""
    dup = mk_event(
        T0 + timedelta(days=3),
        "134.75",
        "shopping",
        "Possible duplicate card charge",
        status="pending",
        linked="event_x",
    )
    assert ledger_for([dup]).known_flows[0].amount == D("-134.75")
    assert ledger_for([dup], [Amendment("duplicate_reversed", dup.event_id, "message_x")]).known_flows == []


# ----------------------------------------------------------------------------- recurrence
def test_monthly_fixed_stream_keeps_day_of_month_and_last_amount() -> None:
    """Design decision R1/R2: fixed monthly item by description; projected on its day-of-month with the latest amount."""
    s = streams_by_key(monthly(2, "600", "rent", "Monthly rent"))["expense:rent:Monthly rent"]
    assert s.cadence == "monthly" and s.amount == D("600")
    assert s.dates[0] == date(2026, 4, 2) and len(s.dates) == 3


def test_add_months_clamps_to_month_length() -> None:
    """Design decision (F-006/F-011): the 31st projects to the 30th/28th, never to a fixed 28th for every month."""
    assert add_months(date(2026, 1, 31), 1, 31) == date(2026, 2, 28)
    assert add_months(date(2026, 1, 15), 1, 15) == date(2026, 2, 15)
    assert add_months(date(2024, 12, 4), 1, 4) == date(2025, 1, 4)


def test_variable_category_projects_on_observed_gap_not_only_bands() -> None:
    """Design decision (fitted, F-012): groceries every 10 days is a real template; band-only silently dropped it."""
    keys = streams_by_key(every(10, "45", "groceries", "Grocer", n=8))
    s = keys["expense:groceries:*"]
    assert s.cadence == "every:10" and len(s.dates) == 9
    band_cfg = DEFAULT_CONFIG.with_overrides({"VARIABLE_CADENCE": "band"})
    assert "expense:groceries:*" not in streams_by_key(every(10, "45", "groceries", "Grocer", n=8), cfg=band_cfg)


def test_variable_amount_statistic_is_median_by_default() -> None:
    """Design decision C-3 (fitted): variable spend uses the median of the history window."""
    evs = [
        mk_event(T0 - timedelta(days=7 * k), a, "groceries", "Grocer")
        for k, a in zip(range(5, 0, -1), ["40", "60", "50", "90", "55"], strict=True)
    ]
    assert streams_by_key(evs)["expense:groceries:*"].amount == D("55")
    assert streams_by_key(evs, cfg=DEFAULT_CONFIG.with_overrides({"VARIABLE_AMOUNT_STAT": "max"}))[
        "expense:groceries:*"
    ].amount == D("90")


def test_occurrence_on_request_date_is_projected() -> None:
    """Design decision R8 (F-007): an item due ON T0 is not yet in the opening balance and must be projected."""
    evs = monthly(5, "600", "rent", "Monthly rent")  # last on Feb 5 -> next Mar 5 == T0
    assert streams_by_key(evs)["expense:rent:Monthly rent"].dates[0] == T0
    excl = DEFAULT_CONFIG.with_overrides({"PROJECT_ON_T0": "exclude"})
    assert streams_by_key(evs, cfg=excl)["expense:rent:Monthly rent"].dates[0] == date(2026, 4, 5)


def test_missed_occurrence_ends_stream_but_not_yet_due_does_not() -> None:
    """Design decision C-2: last + cadence + GRACE_DAYS < T0 ends a stream; a stream whose next date is still ahead is alive."""
    ended = every(30, "20", "gym", "Gym plan", n=4, end=T0 - timedelta(days=36))  # next was due 6 days ago, grace is 5
    alive = every(
        30, "20", "gym", "Gym plan", n=4, end=T0 - timedelta(days=34)
    )  # next was due 4 days ago, inside grace
    assert (
        streams_by_key(ended)["expense:gym:Gym plan"].ended and not streams_by_key(ended)["expense:gym:Gym plan"].dates
    )
    assert not streams_by_key(alive)["expense:gym:Gym plan"].ended


def test_income_clusters_by_day_of_month_across_description_changes() -> None:
    """Design decision (fitted, user_14): payroll before/after leave is one stream on the 15th; skipped months do not end it."""
    evs = [
        mk_event(date(2025, 11, 15), "2717", "salary", "Payroll before leave", direction="credit"),
        mk_event(date(2025, 12, 15), "2717", "salary", "Payroll before leave", direction="credit"),
        mk_event(date(2026, 2, 15), "2717", "salary", "Payroll after returning from leave", direction="credit"),
    ]
    s = [x for x in infer_streams(ledger_for(evs), DEFAULT_CONFIG) if x.kind == "income"]
    assert (
        len(s) == 1
        and s[0].dates == (date(2026, 3, 15), date(2026, 4, 15), date(2026, 5, 15))
        and s[0].amount == D("2717")
    )


def test_moved_payday_follows_matching_description() -> None:
    """Design decision (user_07): a more recent singleton with the cluster's description continues the stream from the new day."""
    evs = [
        mk_event(
            date(2025, 11 + 0, 15) if m == 0 else date(2025, 12, 15),
            "1490",
            "salary",
            "Payroll credit",
            direction="credit",
        )
        for m in range(2)
    ]
    evs += [
        mk_event(date(2026, 1, 15), "1490", "salary", "Payroll credit", direction="credit"),
        mk_event(date(2026, 2, 23), "1490", "salary", "Payroll credit", direction="credit"),
    ]
    s = [x for x in infer_streams(ledger_for(evs), DEFAULT_CONFIG) if x.kind == "income"]
    assert len(s) == 1 and s[0].dates[0] == date(2026, 3, 23)


def test_two_household_incomes_stay_separate_and_one_can_end() -> None:
    """Design decision: the 15th and the 20th are different streams; the 20th that missed February has ended (user_13)."""
    evs = monthly(15, "1343.54", "salary", "Primary household salary", direction="credit")
    evs += monthly(20, "900", "salary", "Second household income", months=5, end=date(2026, 1, 25), direction="credit")
    inc = {s.key: s for s in infer_streams(ledger_for(evs), DEFAULT_CONFIG) if s.kind == "income"}
    assert inc["income:day15"].dates and inc["income:day20"].ended


def test_scheduled_salary_seeds_forward_stream_and_suppresses_history_twin() -> None:
    """Design decision C-1 (user_01): 'Next confirmed salary' defines the monthly stream after it; no double count on that day."""
    evs = [
        mk_event(date(2026, 2, 15), "1200", "salary", "Prorated first salary", direction="credit"),
        mk_event(date(2026, 3, 15), "2300", "salary", "Next confirmed salary", direction="credit", status="scheduled"),
    ]
    led = ledger_for(evs)
    inc = [s for s in infer_streams(led, DEFAULT_CONFIG) if s.kind == "income"]
    assert len(inc) == 1 and inc[0].dates == (date(2026, 4, 15), date(2026, 5, 15)) and inc[0].amount == D("2300")
    curve = build_curve(led, inc, 90)
    assert curve.at(date(2026, 3, 15)) - curve.at(date(2026, 3, 14)) == D("2300")  # scheduled row itself, once


def test_non_recurring_income_words_and_final_payroll() -> None:
    """Design decision R6: bonuses/commissions/arrears are never projected; 'Final employer payroll' ends the stream."""
    evs = monthly(15, "1500", "salary", "Payroll credit", months=4, end=date(2026, 2, 1), direction="credit")
    evs += [
        mk_event(date(2026, 2, 15), "1500", "salary", "Final employer payroll", direction="credit"),
        mk_event(date(2026, 2, 22), "800", "salary", "Quarterly performance bonus", direction="credit"),
    ]
    inc = [s for s in infer_streams(ledger_for(evs), DEFAULT_CONFIG) if s.kind == "income"]
    assert all(not s.dates for s in inc)


def test_weekly_gig_income_detected_and_unconfirmed_amendment_removes_it() -> None:
    """Design decision R5a + R7 (user_10): weekly payouts form a stream; 'income_unconfirmed' evidence removes all income."""
    evs = [
        mk_event(T0 - timedelta(days=7 * k), str(500 + 10 * k), "salary", f"Platform payout {k}", direction="credit")
        for k in range(10, 0, -1)
    ]
    inc = [s for s in infer_streams(ledger_for(evs), DEFAULT_CONFIG) if s.kind == "income"]
    assert (
        len(inc) == 1 and inc[0].cadence == "weekly" and len(inc[0].dates) == 13
    )  # last payout T0-7: next is on T0 (R8)
    inc2 = [
        s
        for s in infer_streams(
            ledger_for(evs, [Amendment("income_unconfirmed", "all_income", "message_x")]), DEFAULT_CONFIG
        )
        if s.kind == "income"
    ]
    assert inc2 == []


def test_salary_amount_amendment_and_new_income_and_rent_multiplier() -> None:
    """Design decision R7: message facts amend the projected amounts (salary cut, first salary, rent +12%)."""
    evs = monthly(15, "1422.85", "salary", "Payroll credit", direction="credit") + monthly(
        2, "500", "rent", "Monthly rent"
    )
    am = [
        Amendment("salary_amount", "salary", "message_06", amount=D("900"), effective_from=date(2026, 3, 15)),
        Amendment("expense_multiplier", "category:rent", "message_12", factor=D("1.12")),
    ]
    st = {s.key: s for s in infer_streams(ledger_for(evs, am), DEFAULT_CONFIG)}
    assert st["income:day15"].amount == D("900") and st["expense:rent:Monthly rent"].amount == D("560.00")
    new = [Amendment("new_income", "salary", "message_11", amount=D("1661"), effective_from=date(2026, 3, 15))]
    st2 = {s.key: s for s in infer_streams(ledger_for(monthly(2, "500", "rent", "Monthly rent"), new), DEFAULT_CONFIG)}
    assert st2["income:new"].dates[0] == date(2026, 3, 15) and st2["income:new"].amount == D("1661")


# ----------------------------------------------------------------------------- simulate & solver
def _flat_ledger(balance: str, flows: list[Flow]) -> Ledger:
    return Ledger("user_t", "EUR", T0, D(balance), D("1000"), flows, [], [], [], [])


def test_safe_amount_is_trough_minus_minimum_capped_and_nonnegative() -> None:
    """Design decision §5.3 / I-1: safe = clamp(min balance − M, 0, A)."""
    led = _flat_ledger("3000", [Flow(T0 + timedelta(days=10), D("-1500"), "bill")])
    curve = build_curve(led, [], 90)
    assert safe_amount_today(curve, D("1000"), D("5000")) == D("500")
    assert safe_amount_today(curve, D("1000"), D("300")) == D("300")
    assert safe_amount_today(
        build_curve(_flat_ledger("1200", [Flow(T0 + timedelta(days=1), D("-500"), "x")]), [], 90), D("1000"), D("100")
    ) == D("0")


def test_payment_on_payday_is_after_credit_and_later_days_use_intraday_low() -> None:
    """Design decision (fitted timing): paying on payday is allowed; under debits_first a later bill lands before that day's credit."""
    payday = T0 + timedelta(days=10)
    flows = [
        Flow(payday, D("2000"), "salary"),
        Flow(payday + timedelta(days=5), D("-1900"), "rent"),
        Flow(payday + timedelta(days=5), D("1000"), "refund"),
    ]
    led = _flat_ledger("1500", flows)
    assert earliest_full_date(build_curve(led, [], 90, (), "net"), D("1000"), D("1200")) == payday
    assert earliest_full_date(build_curve(led, [], 90, (), "debits_first"), D("1000"), D("1200")) == payday + timedelta(
        days=5
    )


def test_earliest_scan_bounded_by_deadline_when_configured() -> None:
    """Design decision (fitted): with SAFETY_SCAN_END=deadline a bill after the deadline does not block a deferred payment."""
    payday = T0 + timedelta(days=10)
    led = _flat_ledger(
        "1500", [Flow(payday, D("2000"), "salary"), Flow(T0 + timedelta(days=40), D("-2000"), "big bill")]
    )
    curve = build_curve(led, [], 90)
    assert earliest_full_date(curve, D("1000"), D("1200"), None) is None
    assert earliest_full_date(curve, D("1000"), D("1200"), T0 + timedelta(days=30)) == payday


def test_is_safe_checks_every_day_after_each_payment() -> None:
    """Design decision I-10: the plan's cumulative payments are tested against every later day, not just payment days."""
    led = _flat_ledger("2000", [Flow(T0 + timedelta(days=20), D("-600"), "bill")])
    curve = build_curve(led, [], 90)
    assert is_safe(curve, (Payment(T0, D("400"), "400"),), D("1000"))
    assert not is_safe(curve, (Payment(T0, D("401"), "401"),), D("1000"))


# ----------------------------------------------------------------------------- plans
def _plan(
    method: str, dates: list[date], amount: str, changes: int = 0, option: str | None = None, total: str | None = None
) -> Plan:
    pays = tuple(Payment(d, D(amount), amount) for d in dates)
    ch = tuple(
        __import__("buyorwait.models", fromlist=["Change"]).Change("stop", f"k{i}", f"event_{i + 1}", "x")
        for i in range(changes)
    )
    return Plan(method, pays, ch, option, D(total) if total else D(amount) * len(dates))


def test_rank_rules_each_direction() -> None:
    """Design decision §4.1: rules 1..6 in order; each pair below differs on exactly one rule."""
    r = mk_request(desired_completion_date=T0 + timedelta(days=30))
    late = _plan("wait", [T0 + timedelta(days=45)], "500")
    on_time_with_change = _plan("full_payment", [T0], "500", changes=1)
    assert rank_key(on_time_with_change, r) < rank_key(late, r)  # rule 1 beats rule 2
    no_change = _plan("wait", [T0 + timedelta(days=10)], "500")
    assert rank_key(no_change, r) < rank_key(on_time_with_change, r)  # rule 2
    cheaper = _plan("wait", [T0 + timedelta(days=20)], "500")
    dearer = _plan(
        "installments", [T0 + timedelta(days=3), T0 + timedelta(days=33)], "260", option="payment_option_9", total="520"
    )
    assert rank_key(cheaper, r) < rank_key(dearer, r)  # rule 3 beats rule 4 (earlier start)
    early = _plan("partial_payment", [T0, T0 + timedelta(days=10)], "250")
    assert rank_key(early, r) < rank_key(cheaper, r)  # rule 4
    fewer = _plan("wait", [T0], "500")
    assert rank_key(fewer, r) < rank_key(early, r)  # rule 5
    o1 = _plan("installments", [T0, T0 + timedelta(days=30)], "260", option="payment_option_2", total="520")
    o2 = _plan("installments", [T0, T0 + timedelta(days=30)], "260", option="payment_option_10", total="520")
    assert rank_key(o1, r) < rank_key(o2, r)  # rule 6 numeric (2 < 10; lexicographic would say "10" < "2")


def _options() -> list[PaymentOption]:
    return [
        PaymentOption("payment_option_1", "request_t", "full_payment", D("500"), "500", 1, T0, None, D("0"), D("500")),
        PaymentOption(
            "payment_option_2",
            "request_t",
            "installments",
            D("175"),
            "175",
            3,
            T0 + timedelta(days=3),
            30,
            D("25"),
            D("525"),
        ),
        PaymentOption(
            "payment_option_3",
            "request_t",
            "installments",
            D("30"),
            "30",
            18,
            T0 + timedelta(days=7),
            30,
            D("40"),
            D("540"),
        ),
    ]


def test_gates_remove_candidates_and_never_re_add() -> None:
    """Design decision §3: methods gate every candidate; cap removes the 18-payment option; partial needs request + user."""
    led = _flat_ledger("3000", [])
    curve = build_curve(led, [], 90)
    r = mk_request()
    all_methods = enumerate_candidates(r, mk_profile(), _options(), curve, D("500"), T0)
    assert {p.method for p in all_methods} == {"full_payment", "installments"} and all(
        p.payment_option_id != "payment_option_3" for p in all_methods
    )
    only_install = enumerate_candidates(
        r, mk_profile(methods=frozenset({"installments"})), _options(), curve, D("500"), T0
    )
    assert {p.method for p in only_install} == {"installments"}
    no_partial_request = enumerate_candidates(
        mk_request(allows_partial_payment=False),
        mk_profile(methods=frozenset({"partial_payment"})),
        _options(),
        curve,
        D("200"),
        T0 + timedelta(days=5),
    )
    assert no_partial_request == []


def test_partial_plan_is_two_payments_summing_exactly() -> None:
    """Design decision I-5: partial = safe today + remainder on earliest, only when earliest ≤ deadline."""
    led = _flat_ledger("1300", [Flow(T0 + timedelta(days=10), D("1000"), "salary")])
    curve = build_curve(led, [], 90)
    r = mk_request(requested_amount=D("500"), desired_completion_date=T0 + timedelta(days=20))
    cands = enumerate_candidates(
        r, mk_profile(methods=frozenset({"partial_payment"})), [], curve, D("300"), T0 + timedelta(days=10)
    )
    assert len(cands) == 1 and [p.amount for p in cands[0].payments] == [D("300"), D("200")]
    too_late = enumerate_candidates(
        mk_request(requested_amount=D("500"), desired_completion_date=T0 + timedelta(days=5)),
        mk_profile(methods=frozenset({"partial_payment"})),
        [],
        curve,
        D("300"),
        T0 + timedelta(days=10),
    )
    assert too_late == []


def test_change_search_smallest_set_numeric_order_and_permitted_only() -> None:
    """Design decision §5.4 / C-4 / I-8: fewest actions first, numeric event id order, only permitted flexible streams."""
    # Before payday (15th): streaming 300 on the 8th and dining 400 on the 12th. Headroom 1500, request 1450:
    # without changes the trough is 1500 - 1450 - 700 = -650 short; stopping streaming alone saves 300 (not enough),
    # reducing dining alone saves 350 (not enough); both together save 650 (exactly enough). Deadline is before payday
    # so 'wait' cannot complete in time and the search must run.
    evs = monthly(2, "1500", "rent", "Monthly rent") + monthly(
        8, "300", "streaming", "Family streaming plan", flexibility="stoppable"
    )
    evs += monthly(12, "400", "dining", "Weekend food delivery", flexibility="reducible", min_allowed="50")
    evs += monthly(15, "1800", "salary", "Payroll credit", direction="credit")
    prof = mk_profile(current_available_balance=D("2500"), methods=frozenset({"full_payment"}))
    led = ledger_for(evs, profile=prof)
    streams = infer_streams(led, DEFAULT_CONFIG)
    singles = change_candidates(streams, prof)
    assert {(c.action, c.description) for c in singles} == {
        ("stop", "Family streaming plan"),
        ("reduce_to", "Weekend food delivery"),
    }
    r = mk_request(requested_amount=D("1450"), desired_completion_date=T0 + timedelta(days=8))
    found = search_changes(r, prof, led, streams, DEFAULT_CONFIG)
    assert found is not None
    plan, _ = found
    assert [(c.action, c.description) for c in plan.changes] == [
        ("stop", "Family streaming plan"),
        ("reduce_to", "Weekend food delivery"),
    ]
    ids = [int(c.event_id.split("_")[1]) for c in plan.changes]
    assert ids == sorted(ids)  # numeric event-id order (C-4)
    chosen, *_ = choose(r, prof, [], led, streams, DEFAULT_CONFIG)
    assert chosen is not None and chosen.changes == plan.changes  # rule 1 (deadline) beats rule 2 (no changes)
    assert not any(s.category == "rent" for s in streams if any(c.stream_key == s.key for c in plan.changes))


def test_choose_prefers_full_today_then_partial_then_wait_then_installments() -> None:
    """Design decision §4.1 on a real gate mix: cheaper and earlier plans win when eligible; ineligible ones never appear."""
    evs = monthly(15, "1800", "salary", "Payroll credit", direction="credit") + monthly(
        2, "1500", "rent", "Monthly rent"
    )
    prof = mk_profile(current_available_balance=D("2600"))
    led = ledger_for(evs, profile=prof)
    streams = infer_streams(led, DEFAULT_CONFIG)
    r = mk_request(requested_amount=D("500"), desired_completion_date=T0 + timedelta(days=30))
    plan, safe, earliest, _ = choose(r, prof, _options(), led, streams, DEFAULT_CONFIG)
    assert plan is not None and plan.method in ("full_payment", "partial_payment", "wait") and safe >= D("0")
    plan2, *_ = choose(
        r,
        mk_profile(current_available_balance=D("2600"), methods=frozenset({"installments"})),
        _options(),
        led,
        streams,
        DEFAULT_CONFIG,
    )
    assert plan2 is None or plan2.method == "installments"


# ----------------------------------------------------------------------------- end to end on the samples
def test_sample_run_matches_pinned_metrics_and_every_row_validates() -> None:
    """Design decision: the core with model-resolved evidence (offline replay of the committed cache) reproduces the pinned metrics."""
    out = ROOT / "analysis" / "reports" / "predictions" / "_test_core.csv"
    res = subprocess.run(
        [
            sys.executable,
            str(ROOT / "code" / "main.py"),
            "--samples",
            "--tag",
            "_test_core",
            "--model-evidence",
            "--offline",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stderr
    rows = list(csv.DictReader(open(out, encoding="utf-8")))
    assert len(rows) == 25 and tuple(rows[0]) == OUTPUT_COLUMNS
    pinned = json.loads((ROOT / "analysis" / "reports" / "eval_pinned.json").read_text())["metrics"]
    sc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "code" / "evaluation" / "score.py"),
            "--predictions",
            str(out),
            "--tag",
            "_test_core",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert sc.returncode == 0, sc.stdout  # exit 2 would mean a regression against the pin
    got = json.loads((ROOT / "analysis" / "reports" / "eval__test_core.json").read_text())["metrics"]
    assert got["row_valid"] == 1.0 and got["composite"] >= pinned["composite"] - 1e-9
    for f in ("eval__test_core.json", "eval__test_core.md", "predictions/_test_core.csv"):
        (ROOT / "analysis" / "reports" / f).unlink()


def test_full_run_is_deterministic(tmp_path: Path) -> None:
    """Design decision I-13: two runs over the first 10 evaluation requests are byte-identical (no evidence, skip unresolved)."""
    outs = []
    for k in range(2):
        out = tmp_path / f"o{k}.csv"
        res = subprocess.run(
            [sys.executable, str(ROOT / "code" / "main.py"), "--limit", "10", "--skip-unresolved", "--out", str(out)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, res.stderr
        outs.append(out.read_bytes())
    assert outs[0] == outs[1]
