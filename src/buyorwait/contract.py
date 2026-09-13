"""Output contract: enums, number/date formatting, explanation templates, structural row validation.

Everything here is derived from CONTRACT.md §1, §2, §7 and verified against the 25 solved
samples in the Phase 0 convention audit. No decision logic lives here; this module only
knows what a *well-formed* output row looks like and how to render one from already-decided
values, so the scorer (Phase 2), the writer (Phase 5) and the validator share one source.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation

OUTPUT_COLUMNS: tuple[str, ...] = (
    "request_id",
    "amount_safe_to_pay",
    "affordability_status",
    "recommended_payment_method",
    "payment_plan",
    "earliest_date_for_full_payment",
    "spending_changes_needed",
    "decision_explanation",
)
STATUSES: frozenset[str] = frozenset({"affordable_now", "affordable_with_plan", "affordable_later", "not_affordable"})
METHODS: frozenset[str] = frozenset({"full_payment", "partial_payment", "installments", "wait", "not_recommended"})
ALLOWED_PAIRS: frozenset[tuple[str, str]] = frozenset(
    {
        ("affordable_now", "full_payment"),
        ("affordable_with_plan", "full_payment"),
        ("affordable_with_plan", "partial_payment"),
        ("affordable_with_plan", "installments"),
        ("affordable_later", "wait"),
        ("not_affordable", "not_recommended"),
    }
)
MAX_CHANGES = 3  # CONTRACT.md §9
ROUND_DP = 2  # CONTRACT.md §9
_CENT = Decimal("0.01")
_EVENT_ID_RE = re.compile(r"^event_(\d+)$")


class ContractError(ValueError):
    """A value violates the output contract."""


# ----------------------------------------------------------------------------- numbers & dates
def to_decimal(text: str) -> Decimal:
    try:
        return Decimal(text.strip())
    except (InvalidOperation, AttributeError) as exc:
        raise ContractError(f"not a decimal: {text!r}") from exc


def round_dp(x: Decimal) -> Decimal:
    return x.quantize(_CENT, rounding=ROUND_HALF_EVEN)


def fmt_shortest(x: Decimal) -> str:
    """amount_safe_to_pay / partial remainder: round to 2 dp, shortest repr (603.3, 873000, 87170.56)."""
    q = round_dp(x).normalize()
    if q == q.to_integral_value():
        return str(int(q))
    return format(q, "f")


def fmt_padded(x: Decimal) -> str:
    """full/wait plan amounts and reduce_to: integer if integral, else exactly 2 dp (620.4 -> 620.40)."""
    q = round_dp(x)
    if q == q.to_integral_value():
        return str(int(q))
    return format(q, "f")


def fmt_prose_amount(x: Decimal) -> str:
    """Explanation amounts: thousands separators, 2 dp iff non-integral (ZAR 25,256 / EUR 620.40)."""
    q = round_dp(x)
    if q == q.to_integral_value():
        return f"{int(q):,}"
    return f"{q:,.2f}"


def prose_date(d: date) -> str:
    """'15 June 2024' — no leading zero."""
    return f"{d.day} {d.strftime('%B')} {d.year}"


def event_number(event_id: str) -> int:
    m = _EVENT_ID_RE.match(event_id)
    if not m:
        raise ContractError(f"malformed event id {event_id!r}")
    return int(m.group(1))


# ----------------------------------------------------------------------------- plan & changes
@dataclass(frozen=True)
class Payment:
    on: date
    amount_text: str

    @property
    def amount(self) -> Decimal:
        return to_decimal(self.amount_text)


def parse_plan(text: str) -> list[Payment]:
    if text == "none":
        return []
    out: list[Payment] = []
    for chunk in text.split("|"):
        if ":" not in chunk:
            raise ContractError(f"bad plan entry {chunk!r}")
        d, a = chunk.split(":", 1)
        out.append(Payment(date.fromisoformat(d), a))
    return out


def render_plan(payments: list[Payment]) -> str:
    return "|".join(f"{p.on.isoformat()}:{p.amount_text}" for p in payments) or "none"


@dataclass(frozen=True)
class Change:
    action: str  # "stop" | "reduce_to"
    event_id: str
    new_amount_text: str | None = None

    def render(self) -> str:
        if self.action == "stop":
            return f"stop:{self.event_id}"
        return f"reduce_to:{self.event_id}:{self.new_amount_text}"


def parse_changes(text: str) -> list[Change]:
    if text == "none":
        return []
    out: list[Change] = []
    for chunk in text.split("|"):
        parts = chunk.split(":")
        if parts[0] == "stop" and len(parts) == 2:
            out.append(Change("stop", parts[1]))
        elif parts[0] == "reduce_to" and len(parts) == 3:
            out.append(Change("reduce_to", parts[1], parts[2]))
        else:
            raise ContractError(f"bad spending change {chunk!r}")
    return out


def render_changes(changes: list[Change]) -> str:
    ordered = sorted(changes, key=lambda c: event_number(c.event_id))  # CONTRACT C-4: numeric event-id order
    return "|".join(c.render() for c in ordered) or "none"


# ----------------------------------------------------------------------------- explanation templates
_AMT = r"[\d,]+(?:\.\d+)?"
_DATE = r"\d{1,2} [A-Z][a-z]+ \d{4}"
EXPLANATION_PATTERNS: dict[str, re.Pattern[str]] = {
    "affordable_now": re.compile(
        rf"^Pay (?P<ccy>[A-Z]{{3}}) (?P<amt>{_AMT}) today\. This (?:leaves at least|keeps the) (?P=ccy) (?P<min>{_AMT}) "
        rf"(?:available|minimum available) over the next 90 days\.$"
    ),
    "full_payment_with_changes": re.compile(
        rf"^(?:Stop the .+?|Reduce the .+? to [A-Z]{{3}} {_AMT}|Stop the .+? and reduce the .+? to [A-Z]{{3}} {_AMT}), "
        rf"then pay (?P<ccy>[A-Z]{{3}}) (?P<amt>{_AMT}) today\. This leaves at least (?P=ccy) (?P<min>{_AMT}) available\.$"
    ),
    "installments": re.compile(
        rf"^Use (?P<n>\d+) installments of (?P<ccy>[A-Z]{{3}}) (?P<amt>{_AMT}), starting (?P<date>{_DATE})\. "
        rf"This leaves at least (?P=ccy) (?P<min>{_AMT}) available\.$"
    ),
    "partial_payment": re.compile(
        rf"^Pay (?P<ccy>[A-Z]{{3}}) (?P<amt>{_AMT}) today and the remaining (?P=ccy) (?P<rem>{_AMT}) on (?P<date>{_DATE})\. "
        rf"This completes the full request and keeps the (?P=ccy) (?P<min>{_AMT}) minimum protected\.$"
    ),
    "wait": re.compile(
        rf"^(?:Pay (?P<ccy>[A-Z]{{3}}) (?P<amt>{_AMT}) in full on (?P<date>{_DATE})\. Paying earlier would take the balance below "
        rf"the (?P=ccy) (?P<min>{_AMT}) minimum\.|Wait until (?P<date2>{_DATE}), then pay (?P<ccy2>[A-Z]{{3}}) (?P<amt2>{_AMT}) in full\. "
        rf"Paying sooner would put the (?P=ccy2) (?P<min2>{_AMT}) minimum at risk\.)$"
    ),
    "not_recommended": re.compile(
        rf"^(?:Do not make this payment by (?P<date>{_DATE})\. None of the available options keeps the (?P<ccy>[A-Z]{{3}}) "
        rf"(?P<min>{_AMT}) minimum protected\.|Do not proceed with the (?P<ccy2>[A-Z]{{3}}) (?P<amt>{_AMT}) request\. "
        rf"Although (?P=ccy2) (?P<safe>{_AMT}) is available today, the full amount cannot be completed safely within 90 days\.)$"
    ),
}


def template_key(method: str, has_changes: bool) -> str:
    if method == "full_payment":
        return "full_payment_with_changes" if has_changes else "affordable_now"
    return method


@dataclass(frozen=True)
class ExplanationFacts:
    """Everything the templates need; produced by the reconciler from the rationale object."""

    ccy: str
    requested: Decimal
    minimum_balance: Decimal
    method: str
    safe: Decimal
    earliest: date | None
    deadline: date
    plan: list[Payment]
    change_clauses: list[
        str
    ]  # e.g. ["Stop the family streaming plan", "reduce the streaming subscription to USD 23.50"]


def render_explanation(f: ExplanationFacts) -> str:
    ccy, m = f.ccy, fmt_prose_amount(f.minimum_balance)
    a = fmt_prose_amount(f.requested)
    if f.method == "full_payment" and not f.change_clauses:
        return f"Pay {ccy} {a} today. This leaves at least {ccy} {m} available over the next 90 days."
    if f.method == "full_payment":
        if len(f.change_clauses) == 1:
            clause = f.change_clauses[0]
        else:
            clause = f.change_clauses[0] + " and " + " and ".join(c[0].lower() + c[1:] for c in f.change_clauses[1:])
        return f"{clause}, then pay {ccy} {a} today. This leaves at least {ccy} {m} available."
    if f.method == "installments":
        first = f.plan[0]
        return (
            f"Use {len(f.plan)} installments of {ccy} {fmt_prose_amount(first.amount)}, starting {prose_date(first.on)}. "
            f"This leaves at least {ccy} {m} available."
        )
    if f.method == "partial_payment":
        if f.earliest is None:
            raise ContractError("partial_payment needs an earliest date")
        return (
            f"Pay {ccy} {fmt_prose_amount(f.safe)} today and the remaining {ccy} {fmt_prose_amount(f.requested - f.safe)} "
            f"on {prose_date(f.earliest)}. This completes the full request and keeps the {ccy} {m} minimum protected."
        )
    if f.method == "wait":
        if f.earliest is None:
            raise ContractError("wait needs an earliest date")
        return f"Pay {ccy} {a} in full on {prose_date(f.earliest)}. Paying earlier would take the balance below the {ccy} {m} minimum."
    if f.method == "not_recommended":
        return f"Do not make this payment by {prose_date(f.deadline)}. None of the available options keeps the {ccy} {m} minimum protected."
    raise ContractError(f"unknown method {f.method!r}")


# ----------------------------------------------------------------------------- structural validation
@dataclass(frozen=True)
class RowContext:
    """Dataset facts needed to validate one output row structurally (no simulation)."""

    request_date: date
    deadline: date
    requested: Decimal
    allows_partial: bool
    methods: frozenset[str]
    max_installment_months: int | None
    home_currency: str
    minimum_balance: Decimal
    installment_schedules: dict[str, str]  # payment_option_id -> rendered plan string
    events: dict[
        str, dict[str, str]
    ]  # user's events by id (flexibility, category, minimum_allowed_amount, status, description, settlement_date)
    stop_categories: frozenset[str]
    reduce_categories: frozenset[str]
    protect_categories: frozenset[str]


def validate_row(row: dict[str, str], ctx: RowContext) -> list[str]:
    """Return every CONTRACT §2 structural violation for one row (empty list == well-formed)."""
    v: list[str] = []
    status, method = row["affordability_status"], row["recommended_payment_method"]
    if status not in STATUSES:
        v.append(f"bad status {status!r}")
    if method not in METHODS:
        v.append(f"bad method {method!r}")
    if v:
        return v
    if (status, method) not in ALLOWED_PAIRS:
        v.append(f"status/method pair not allowed: {status}/{method}")
    try:
        safe = to_decimal(row["amount_safe_to_pay"])
    except ContractError as exc:
        return v + [str(exc)]
    if not (Decimal(0) <= safe <= ctx.requested):
        v.append(f"I-1: amount_safe_to_pay {safe} outside [0, {ctx.requested}]")
    if row["amount_safe_to_pay"] != fmt_shortest(safe):
        v.append(f"format: amount_safe_to_pay {row['amount_safe_to_pay']!r} != shortest {fmt_shortest(safe)!r}")
    earliest_text = row["earliest_date_for_full_payment"]
    earliest = date.fromisoformat(earliest_text) if earliest_text else None
    try:
        plan = parse_plan(row["payment_plan"])
        changes = parse_changes(row["spending_changes_needed"])
    except (ContractError, ValueError) as exc:
        return v + [str(exc)]
    if any(b.on < a.on for a, b in zip(plan, plan[1:], strict=False)):
        v.append("plan not chronological")
    if plan and plan[0].on < ctx.request_date:
        v.append("plan starts before request_date")

    if status == "affordable_now":
        if safe != ctx.requested or earliest != ctx.request_date or changes:
            v.append("I-2: affordable_now requires safe==requested, earliest==request_date, no changes")
    if status == "not_affordable":
        if plan or earliest is not None or changes:
            v.append("I-3: not_affordable requires plan none, earliest empty, no changes")
    else:
        if earliest is None:
            v.append("earliest_date must be populated unless not_affordable")
        if not plan:
            v.append("plan must not be none unless not_affordable")
    if method == "full_payment":
        if "full_payment" not in ctx.methods:
            v.append("gate: full_payment not accepted by user")
        if len(plan) != 1 or plan[0].on != ctx.request_date or plan[0].amount != ctx.requested:
            v.append("full_payment plan must be exactly request_date:requested")
        elif plan[0].amount_text != fmt_padded(ctx.requested):
            v.append(f"format: full_payment amount {plan[0].amount_text!r} != {fmt_padded(ctx.requested)!r}")
        if status == "affordable_with_plan" and (not changes or safe >= ctx.requested):
            v.append("I-7: affordable_with_plan+full_payment needs changes and safe<requested")
    if method == "wait":
        if "full_payment" not in ctx.methods:
            v.append("gate: wait requires full_payment acceptance")
        if earliest is None or not (ctx.request_date < earliest <= ctx.request_date + timedelta(days=90)):
            v.append("I-4: wait needs request_date < earliest <= T90")
        if len(plan) != 1 or earliest is None or plan[0].on != earliest or plan[0].amount != ctx.requested:
            v.append("I-4: wait plan must be exactly earliest:requested")
        elif plan[0].amount_text != fmt_padded(ctx.requested):
            v.append(f"format: wait amount {plan[0].amount_text!r} != {fmt_padded(ctx.requested)!r}")
        if not (Decimal(0) <= safe < ctx.requested):
            v.append("I-4: wait needs 0 <= safe < requested")
        if changes:
            v.append("I-4: wait has no spending changes")
    if method == "partial_payment":
        if not ctx.allows_partial:
            v.append("I-5: request does not allow partial payment")
        if "partial_payment" not in ctx.methods:
            v.append("gate: partial_payment not accepted by user")
        if not (Decimal(0) < safe < ctx.requested):
            v.append("I-5: partial needs 0 < safe < requested")
        if earliest is None or earliest > ctx.deadline or earliest <= ctx.request_date:
            v.append("I-5: partial needs request_date < earliest <= deadline")
        if len(plan) != 2 or plan[0].on != ctx.request_date or earliest is None or plan[1].on != earliest:
            v.append("I-5: partial plan must be request_date:safe|earliest:remainder")
        else:
            if plan[0].amount != safe or plan[0].amount + plan[1].amount != ctx.requested:
                v.append("I-5: partial amounts must be safe and requested-safe, summing exactly to requested")
            if plan[0].amount_text != fmt_shortest(safe) or plan[1].amount_text != fmt_shortest(ctx.requested - safe):
                v.append("format: partial amounts must use shortest repr")
        if changes:
            v.append("I-5: partial has no spending changes")
    if method == "installments":
        if "installments" not in ctx.methods:
            v.append("gate: installments not accepted by user")
        matches = [oid for oid, sched in ctx.installment_schedules.items() if sched == row["payment_plan"]]
        if len(matches) != 1:
            v.append("I-6: installment plan must equal exactly one supplied option's schedule verbatim")
        elif ctx.max_installment_months is not None and len(plan) > ctx.max_installment_months:
            v.append(f"I-6: {len(plan)} payments exceed max_installment_months {ctx.max_installment_months}")
        if changes:
            v.append("I-6: installments has no spending changes")
    # spending changes (I-8)
    if len(changes) > MAX_CHANGES:
        v.append(f"I-8: more than {MAX_CHANGES} changes")
    seen: set[str] = set()
    for c in changes:
        if c.event_id in seen:
            v.append(f"I-8: {c.event_id} targeted twice")
        seen.add(c.event_id)
        ev = ctx.events.get(c.event_id)
        if ev is None:
            v.append(f"I-8: {c.event_id} is not one of the user's events")
            continue
        flex, cat = ev["flexibility"], ev["category"]
        if cat in ctx.protect_categories:
            v.append(f"I-8: {c.event_id} is in a protected category {cat}")
        if c.action == "stop":
            if flex not in ("stoppable", "reducible_or_stoppable") or cat not in ctx.stop_categories:
                v.append(f"I-8: stop:{c.event_id} not stoppable/permitted ({flex}, {cat})")
        else:
            if flex not in ("reducible", "reducible_or_stoppable") or cat not in ctx.reduce_categories:
                v.append(f"I-8: reduce_to:{c.event_id} not reducible/permitted ({flex}, {cat})")
            if c.new_amount_text is None:
                v.append("I-8: reduce_to needs an amount")
            else:
                new_amt = to_decimal(c.new_amount_text)
                min_allowed = to_decimal(ev["minimum_allowed_amount"]) if ev.get("minimum_allowed_amount") else None
                if min_allowed is None or new_amt != min_allowed:
                    v.append(f"C-6: reduce_to amount {new_amt} != minimum_allowed_amount {min_allowed}")
                if c.new_amount_text != fmt_padded(new_amt):
                    v.append(f"format: reduce_to amount {c.new_amount_text!r} != {fmt_padded(new_amt)!r}")
    if changes and row["spending_changes_needed"] != render_changes(changes):
        v.append("C-4: spending changes must be listed in numeric event-id order")
    # explanation
    key = template_key(method, bool(changes))
    m = EXPLANATION_PATTERNS[key].match(row["decision_explanation"])
    if m is None:
        v.append(f"explanation does not match the {key!r} template")
    else:
        g = {k: val for k, val in m.groupdict().items() if val}
        ccy = g.get("ccy") or g.get("ccy2")
        if ccy != ctx.home_currency:
            v.append(f"explanation currency {ccy} != home currency {ctx.home_currency}")
        minv = g.get("min") or g.get("min2")
        if minv is not None and minv != fmt_prose_amount(ctx.minimum_balance):
            v.append(f"explanation minimum {minv} != minimum_balance_to_keep {fmt_prose_amount(ctx.minimum_balance)}")
        dt = g.get("date") or g.get("date2")
        if key == "wait" and earliest is not None and dt != prose_date(earliest):
            v.append("explanation date != earliest_date_for_full_payment")
        if key == "partial_payment" and earliest is not None and dt != prose_date(earliest):
            v.append("explanation date != earliest_date_for_full_payment")
        if key == "installments" and plan and dt != prose_date(plan[0].on):
            v.append("explanation start date != first installment date")
        if (
            key == "installments"
            and plan
            and (g.get("n") != str(len(plan)) or g.get("amt") != fmt_prose_amount(plan[0].amount))
        ):
            v.append("explanation installment count/amount != plan")
        if key in ("affordable_now", "full_payment_with_changes", "wait") and g.get(
            "amt", g.get("amt2")
        ) != fmt_prose_amount(ctx.requested):
            v.append("explanation amount != requested_amount")
        if key == "partial_payment" and (
            g.get("amt") != fmt_prose_amount(safe) or g.get("rem") != fmt_prose_amount(ctx.requested - safe)
        ):
            v.append("explanation partial amounts != safe / remainder")
    return v
