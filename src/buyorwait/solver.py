"""Safe amount today and earliest full-payment date (CONTRACT.md §5.3).

Timing convention (fitted, see analysis/reports/eval_sweep_conventions.md): a payment made on day t happens after that day's
credits (paying on payday is allowed), while every later day is tested at its intraday low (debits before credits).
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from buyorwait.contract import round_dp
from buyorwait.simulate import Curve


def _floor_from(curve: Curve, i: int, until: int | None = None) -> Decimal:
    """min(balance at end of day i, intraday lows of days i+1..until) (until=None: through the window end)."""
    if until is None or until >= len(curve.lows) - 1:
        later = curve.suffix_min[i + 1] if i + 1 < len(curve.suffix_min) else curve.balances[i]
    else:
        later = min(curve.lows[i + 1 : until + 1]) if until > i else curve.balances[i]
    return min(curve.balances[i], later)


def safe_amount_today(curve: Curve, minimum: Decimal, requested: Decimal) -> Decimal:
    """clamp(floor_from(T0) - M, 0, A), rounded to 2 dp (CONTRACT I-1)."""
    raw = _floor_from(curve, 0) - minimum
    return round_dp(max(Decimal(0), min(requested, raw)))


def earliest_full_date(
    curve: Curve, minimum: Decimal, requested: Decimal, scan_until: date | None = None
) -> date | None:
    """First t with floor_from(t, until) - A >= M, else None. `scan_until` bounds the check (SAFETY_SCAN_END=deadline)."""
    until = None if scan_until is None else max(0, (scan_until - curve.t0).days)
    for i in range(len(curve.balances)):
        # day 0 always uses the full window so that earliest == T0 <=> amount_safe_to_pay == A (CONTRACT I-2)
        if _floor_from(curve, i, None if i == 0 else until) - requested >= minimum:
            return curve.t0 + timedelta(days=i)
    return None
