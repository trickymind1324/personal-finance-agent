"""Daily balance simulation and safety test (CONTRACT.md §5.3)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from buyorwait.models import Change, Flow, Ledger, Payment, Stream


@dataclass(frozen=True)
class Curve:
    t0: date
    balances: tuple[Decimal, ...]  # end-of-day balance, index i == day t0 + i
    suffix_min: tuple[Decimal, ...]  # min(lows[i:])
    lows: tuple[Decimal, ...] = ()  # intraday low (debits applied, credits not yet)

    def index(self, on: date) -> int:
        i = (on - self.t0).days
        if not 0 <= i < len(self.balances):
            raise ValueError(f"{on} outside the forecast window starting {self.t0}")
        return i

    def at(self, on: date) -> Decimal:
        return self.balances[self.index(on)]

    @property
    def end(self) -> date:
        return self.t0 + timedelta(days=len(self.balances) - 1)

    @property
    def minimum(self) -> Decimal:
        return self.suffix_min[0]

    def low_at(self, i: int) -> Decimal:
        return self.lows[i] if self.lows else self.balances[i]


def apply_changes(streams: list[Stream], changes: tuple[Change, ...]) -> list[Stream]:
    by_key = {c.stream_key: c for c in changes}
    out: list[Stream] = []
    for s in streams:
        c = by_key.get(s.key)
        if c is None:
            out.append(s)
        elif c.action == "stop":
            continue
        elif c.new_amount is not None:
            out.append(Stream(**{**s.__dict__, "amount": c.new_amount}))
    return out


def stream_flows(streams: list[Stream]) -> list[Flow]:
    flows: list[Flow] = []
    for s in streams:
        for d in s.dates:
            flows.append(Flow(d, s.amount if s.kind == "income" else -s.amount, s.key, s.latest_event_id or None))
    return flows


def build_curve(
    ledger: Ledger,
    streams: list[Stream],
    horizon_days: int,
    changes: tuple[Change, ...] = (),
    intraday_order: str = "debits_first",
) -> Curve:
    """Daily curve. `balances[i]` is the end-of-day balance; `lows[i]` is the intraday low used for the safety
    test: with 'debits_first' the day's debits land before its credits (a bill on payday can breach the minimum)."""
    debits: dict[int, Decimal] = defaultdict(Decimal)
    credits: dict[int, Decimal] = defaultdict(Decimal)
    for f in ledger.known_flows + stream_flows(apply_changes(streams, changes)):
        i = (f.on - ledger.t0).days
        if 0 <= i <= horizon_days:
            (debits if f.amount < 0 else credits)[i] += f.amount
    balances: list[Decimal] = []
    lows: list[Decimal] = []
    bal = ledger.start_balance
    for i in range(horizon_days + 1):
        low = bal + debits.get(i, Decimal(0))
        bal = low + credits.get(i, Decimal(0))
        lows.append(low if intraday_order == "debits_first" else bal)
        balances.append(bal)
    suffix: list[Decimal] = [Decimal(0)] * len(balances)
    running = lows[-1]
    for i in range(len(balances) - 1, -1, -1):
        running = min(running, lows[i])
        suffix[i] = running
    return Curve(ledger.t0, tuple(balances), tuple(suffix), tuple(lows))


def is_safe(curve: Curve, payments: tuple[Payment, ...], minimum: Decimal, until: date | None = None) -> bool:
    """True iff balance minus cumulative payments never drops below `minimum` inside the window (or through `until`)."""
    paid = Decimal(0)
    schedule = sorted(payments, key=lambda p: p.on)
    j = 0
    for i, bal in enumerate(curve.balances):
        day = curve.t0 + timedelta(days=i)
        if until is not None and day > until and j >= len(schedule):
            return True
        if curve.low_at(i) - paid < minimum:  # the day's debits land before its credits and before today's payment
            return False
        while j < len(schedule) and schedule[j].on <= day:
            paid += schedule[j].amount
            j += 1
        if bal - paid < minimum:  # today's payment is made after the day's credits (paying on payday is allowed)
            return False
    return True
