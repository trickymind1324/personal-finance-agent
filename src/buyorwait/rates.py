"""Dated exchange-rate lookup (CONTRACT I-11): exact (date, from, to) or raise. Never interpolate."""

from __future__ import annotations

from datetime import date
from decimal import Decimal


class MissingRateError(LookupError):
    """No rate row for the requested (date, from_currency, to_currency)."""


def convert(amount: Decimal, ccy: str, home: str, on: date, table: dict[tuple[date, str, str], Decimal]) -> Decimal:
    if ccy == home:
        return amount
    key = (on, ccy, home)
    if key not in table:
        raise MissingRateError(f"no exchange rate for {ccy}->{home} on {on.isoformat()}")
    return amount * table[key]
