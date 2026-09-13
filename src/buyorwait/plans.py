"""Candidate plans, eligibility gates, the 6-rule ranking and the spending-change search (CONTRACT §3, §4.1, §5.4)."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from itertools import combinations

from buyorwait.config import Config
from buyorwait.contract import fmt_padded, fmt_shortest
from buyorwait.models import Change, Ledger, Payment, PaymentOption, Plan, Profile, Request, Stream
from buyorwait.simulate import Curve, build_curve, is_safe
from buyorwait.solver import earliest_full_date, safe_amount_today


def rank_key(plan: Plan, request: Request) -> tuple[int, int, Decimal, date, int, int]:
    return (
        0 if plan.completes_by(request.desired_completion_date) else 1,  # rule 1
        len(plan.changes),  # rule 2
        plan.total_paid,  # rule 3
        plan.first_date,  # rule 4
        len(plan.payments),  # rule 5
        int(plan.payment_option_id.split("_")[-1]) if plan.payment_option_id else 0,  # rule 6
    )


def option_payments(option: PaymentOption) -> tuple[Payment, ...]:
    step = option.payment_frequency_days or 0
    return tuple(
        Payment(option.first_payment_date + timedelta(days=step * k), option.payment_amount, option.payment_amount_text)
        for k in range(option.number_of_payments)
    )


def enumerate_candidates(
    request: Request,
    profile: Profile,
    options: list[PaymentOption],
    curve: Curve,
    safe: Decimal,
    earliest: date | None,
    scan_until: date | None = None,
) -> list[Plan]:
    """Change-free candidates that pass the safety check. Gates are conjunction-only (CONTRACT §3)."""
    a = request.requested_amount
    t0 = request.request_date
    m = profile.minimum_balance_to_keep
    cands: list[Plan] = []
    eligible_full = "full_payment" in profile.methods
    eligible_partial = "partial_payment" in profile.methods and request.allows_partial_payment
    eligible_install = "installments" in profile.methods
    if eligible_full and safe >= a:  # full window (I-2); earliest == t0 iff this holds
        cands.append(Plan("full_payment", (Payment(t0, a, fmt_padded(a)),), total_paid=a))
    if eligible_full and earliest is not None and earliest > t0:
        cands.append(Plan("wait", (Payment(earliest, a, fmt_padded(a)),), total_paid=a))
    if (
        eligible_partial
        and earliest is not None
        and t0 < earliest <= request.desired_completion_date
        and Decimal(0) < safe < a
    ):
        partial: tuple[Payment, ...] = (
            Payment(t0, safe, fmt_shortest(safe)),
            Payment(earliest, a - safe, fmt_shortest(a - safe)),
        )
        if is_safe(curve, partial, m, scan_until):
            cands.append(Plan("partial_payment", partial, total_paid=a))
    if eligible_install:
        for o in sorted(options, key=lambda o: o.number):
            if o.payment_method != "installments":
                continue
            if profile.max_installment_months is not None and o.number_of_payments > profile.max_installment_months:
                continue
            pays = option_payments(o)
            if is_safe(curve, pays, m, scan_until):
                cands.append(
                    Plan("installments", pays, payment_option_id=o.payment_option_id, total_paid=o.total_payable_amount)
                )
    return cands


def change_candidates(streams: list[Stream], profile: Profile) -> list[Change]:
    """Flexible recurring expense streams in permitted categories, as single actions (CONTRACT I-8)."""
    out: list[Change] = []
    for s in streams:
        if s.kind != "expense" or not s.dates or s.category in profile.protect_categories:
            continue
        can_stop = s.flexibility in ("stoppable", "reducible_or_stoppable") and s.category in profile.stop_categories
        can_reduce = (
            s.flexibility in ("reducible", "reducible_or_stoppable")
            and s.category in profile.reduce_categories
            and s.minimum_allowed_amount is not None
            and s.minimum_allowed_amount < s.amount
        )
        if can_stop:
            out.append(Change("stop", s.key, s.latest_event_id, s.description))
        if can_reduce:
            out.append(Change("reduce_to", s.key, s.latest_event_id, s.description, s.minimum_allowed_amount))
    return out


def search_changes(
    request: Request, profile: Profile, ledger: Ledger, streams: list[Stream], cfg: Config
) -> tuple[Plan, Curve] | None:
    """Smallest set of ≤ MAX_CHANGES actions (numeric event-id order, C-4) making full payment today safe."""
    if "full_payment" not in profile.methods:
        return None
    a, t0, m = request.requested_amount, request.request_date, profile.minimum_balance_to_keep
    singles = sorted(change_candidates(streams, profile), key=lambda c: (int(c.event_id.split("_")[1]), c.action))
    for size in range(1, cfg.MAX_CHANGES + 1):
        for combo in combinations(singles, size):
            if len({c.stream_key for c in combo}) < size:
                continue  # stop and reduce never target the same stream
            curve = build_curve(ledger, streams, cfg.HORIZON_DAYS, combo, cfg.INTRADAY_ORDER)
            pays = (Payment(t0, a, fmt_padded(a)),)
            if is_safe(curve, pays, m):
                ordered = tuple(sorted(combo, key=lambda c: int(c.event_id.split("_")[1])))
                return Plan("full_payment", pays, changes=ordered, total_paid=a), curve
    return None


def choose(
    request: Request,
    profile: Profile,
    options: list[PaymentOption],
    ledger: Ledger,
    streams: list[Stream],
    cfg: Config,
) -> tuple[Plan | None, Decimal, date | None, Curve]:
    """Returns (chosen plan or None, safe amount today, earliest full date, no-change curve)."""
    curve = build_curve(ledger, streams, cfg.HORIZON_DAYS, (), cfg.INTRADAY_ORDER)
    safe = safe_amount_today(curve, profile.minimum_balance_to_keep, request.requested_amount)
    scan_until = request.desired_completion_date if cfg.SAFETY_SCAN_END == "deadline" else None
    earliest = earliest_full_date(curve, profile.minimum_balance_to_keep, request.requested_amount, scan_until)
    cands = enumerate_candidates(request, profile, options, curve, safe, earliest, scan_until)
    if not any(c.completes_by(request.desired_completion_date) for c in cands):
        rescued = search_changes(request, profile, ledger, streams, cfg)
        if rescued is not None:
            cands.append(rescued[0])
    if not cands:
        return None, safe, earliest, curve
    best = min(cands, key=lambda p: rank_key(p, request))
    return best, safe, earliest, curve
