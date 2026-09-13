"""Ledger normalisation (CONTRACT.md §5.1).

Turns a user's raw events plus resolved evidence into (a) known future cash flows inside the
forecast window and (b) settled history in home currency for recurrence inference. Status
handling is a table, not a chain of ifs, so every row's fate is auditable.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from buyorwait.config import Config
from buyorwait.models import Amendment, Event, Flow, HistRow, Ledger, Profile
from buyorwait.rates import convert


class UnresolvedAmountError(ValueError):
    """A forecast-affecting event has a blank amount and no evidence resolved it (never treated as zero)."""


def resolve_amount(event: Event, amendments: list[Amendment]) -> tuple[Decimal | None, str]:
    """Blank amounts come only from an `amount` amendment (image extraction)."""
    if event.amount is not None:
        return event.amount, ""
    for a in amendments:
        if a.kind == "amount" and a.target == event.event_id and a.amount is not None:
            return (
                a.amount,
                f"{event.event_id} amount {a.amount} from {a.source_id}{' (partial, lower bound)' if a.partial else ''}",
            )
    return None, f"{event.event_id} blank amount unresolved"


def normalize_ledger(
    profile: Profile,
    events: list[Event],
    amendments: list[Amendment],
    rates: dict[tuple[date, str, str], Decimal],
    t0: date,
    cfg: Config,
) -> Ledger:
    home = profile.home_currency
    end = t0 + timedelta(days=cfg.HORIZON_DAYS)
    notes: list[str] = []
    known: list[Flow] = []
    scheduled_income: list[Flow] = []
    history: list[HistRow] = []
    reversed_duplicates = {a.target for a in amendments if a.kind == "duplicate_reversed"}

    for e in events:
        if e.status in ("failed", "cancelled", "unrealized") or e.direction == "non_cash":
            continue  # dropped; a linked successor (retry / settled purchase) is counted on its own row
        on = e.settlement_date or e.event_date
        if e.status == "settled":
            if on > t0:
                raise ValueError(f"{e.event_id}: settled after request date {t0} (dataset invariant broken)")
            if on < t0 - timedelta(days=cfg.HISTORY_DAYS):
                continue
            amt, note = resolve_amount(e, amendments)
            if amt is None:
                notes.append(note + " (settled history: skipped for inference)")
                continue
            if note:
                notes.append(note)
            history.append(HistRow(e, convert(amt, e.currency, home, on, rates), on))
            continue
        # pending / scheduled
        if e.direction == "credit" and e.status == "pending":
            notes.append(f"{e.event_id} pending credit ignored ({e.description})")
            continue
        if e.event_id in reversed_duplicates:
            notes.append(f"{e.event_id} pending duplicate charge: reversal posted per evidence, not reserved")
            continue
        apply_on = max(on, t0)
        if apply_on > end:
            continue
        amt, note = resolve_amount(e, amendments)
        if amt is None:
            if e.direction == "debit":
                raise UnresolvedAmountError(
                    f"{e.event_id} ({e.description}) is a forecast-affecting debit with a blank amount"
                )
            notes.append(note + " (credit: ignored)")
            continue
        if note:
            notes.append(note)
        signed = convert(amt, e.currency, home, on, rates)
        flow = Flow(apply_on, -signed if e.direction == "debit" else signed, f"{e.status}:{e.description}", e.event_id)
        known.append(flow)
        if e.direction == "credit":
            scheduled_income.append(flow)
    for a in amendments:
        if (
            a.kind == "confirmed_credit"
            and a.amount is not None
            and a.effective_from is not None
            and t0 <= a.effective_from <= end
        ):
            flow = Flow(a.effective_from, a.amount, f"confirmed:{a.source_id}", None)
            known.append(flow)
            scheduled_income.append(flow)
            notes.append(f"confirmed credit {a.amount} on {a.effective_from} per {a.source_id}")
    history.sort(key=lambda h: (h.on, h.event.number))
    known.sort(key=lambda f: (f.on, f.event_id or ""))
    return Ledger(
        user_id=profile.user_id,
        home_currency=home,
        t0=t0,
        start_balance=profile.current_available_balance,
        minimum_balance=profile.minimum_balance_to_keep,
        known_flows=known,
        history=history,
        scheduled_income=scheduled_income,
        amendments=list(amendments),
        notes=notes,
    )
