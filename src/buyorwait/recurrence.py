"""Recurrence inference (CONTRACT.md §5.2) — first-class core module.

Input: a normalised Ledger. Output: Streams with projected occurrences inside the window.
Rules (each unit-tested on a synthetic ledger in tests/test_phase3_core.py):
  R1 expense grouping: VARIABLE_CATEGORIES by category, everything else by description
  R2 cadence from the median gap: weekly 5–9d, biweekly 12–16d, monthly 26–35d; otherwise one-off
  R3 ended stream (C-2): last + cadence + GRACE_DAYS < T0
  R4 scheduled salary seeds the forward stream (C-1) and suppresses a history-based twin
  R5 income clusters by day-of-month (±CLUSTER_DAY_TOLERANCE); weekly gig income by gap
  R6 terminal descriptions ('Final employer payroll') and NON_RECURRING words end/skip income
  R7 amendments: salary_amount / salary_date / stream_ended / income_unconfirmed / new_income / expense_multiplier
  R8 occurrences dated exactly T0 are projected (not yet in the opening balance)
"""

from __future__ import annotations

import calendar
import statistics
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from buyorwait.config import DISCRETIONARY_CATEGORIES, NON_RECURRING_INCOME_WORDS, VARIABLE_CATEGORIES, Config
from buyorwait.models import HistRow, Ledger, Stream

CADENCES: dict[str, tuple[int, int, int]] = {"weekly": (5, 9, 7), "biweekly": (12, 16, 14), "monthly": (26, 35, 30)}


def add_months(dt: date, k: int, day: int) -> date:
    """Same day-of-month k months after dt, clamped to the target month's length (31st -> 30th/28th/29th)."""
    y, m = dt.year, dt.month + k
    while m > 12:
        m -= 12
        y += 1
    while m < 1:
        m += 12
        y -= 1
    return date(y, m, min(day, calendar.monthrange(y, m)[1]))


def detect_cadence(dates: list[date], variable: bool = False) -> str | None:
    """Named cadence for fixed items; for variable categories any median gap in [3, 45] days becomes 'every:<n>'."""
    if len(dates) < 2:
        return None
    gaps = [(b - a).days for a, b in zip(dates, dates[1:], strict=False)]
    med = statistics.median(gaps)
    for name, (lo, hi, _) in CADENCES.items():
        if lo <= med <= hi:
            return name
    if variable and 3 <= med <= 45:
        return f"every:{int(round(med))}"
    return None


def cadence_days(cadence: str) -> int:
    return CADENCES[cadence][2] if cadence in CADENCES else int(cadence.split(":")[1])


def stat(values: list[Decimal], how: str) -> Decimal:
    if how == "last":
        return values[-1]
    if how == "mean":
        return sum(values, Decimal(0)) / len(values)
    if how == "max":
        return max(values)
    if how == "median":
        return statistics.median(values)
    if how == "round_mean":  # integer base-amount hypothesis (ground-truth troughs are whole numbers)
        return Decimal(round(sum(values, Decimal(0)) / len(values)))
    if how == "min":
        return min(values)
    if how == "p75":
        s = sorted(values)
        return s[min(len(s) - 1, (3 * len(s) + 3) // 4 - 1)] if len(s) > 1 else s[0]
    raise ValueError(f"unknown statistic {how!r}")


def project_dates(last: date, cadence: str, t0: date, end: date, include_t0: bool = True) -> tuple[date, ...]:
    out: list[date] = []
    k = 1
    while True:
        nxt = (
            add_months(last, k, last.day) if cadence == "monthly" else last + timedelta(days=cadence_days(cadence) * k)
        )
        if nxt > end:
            break
        if nxt > t0 or (include_t0 and nxt == t0):  # R8
            out.append(nxt)
        k += 1
    return tuple(out)


def _mostly_weekly(dates: list[date]) -> bool:
    """Weekly gig income: at least 80% of consecutive gaps are 5–9 days (two monthly paydays alternate 5/25 and must not match)."""
    gaps = [(b - a).days for a, b in zip(dates, dates[1:], strict=False)]
    return bool(gaps) and sum(1 for g in gaps if 5 <= g <= 9) >= 0.8 * len(gaps)


def _ended(last: date, cadence: str, t0: date, cfg: Config) -> bool:
    return last + timedelta(days=cadence_days(cadence) + cfg.GRACE_DAYS) < t0  # R3


def _is_non_recurring_income(description: str) -> bool:
    d = description.lower()
    return any(w in d for w in NON_RECURRING_INCOME_WORDS)


# ----------------------------------------------------------------------------- expenses
def _expense_streams(ledger: Ledger, cfg: Config, end: date) -> list[Stream]:
    groups: dict[tuple[str, str], list[HistRow]] = defaultdict(list)
    for h in ledger.history:
        e = h.event
        if e.direction != "debit" or e.event_type in ("investment_purchase",):
            continue
        if cfg.DISCRETIONARY_PROJECTION == "skip" and e.category in DISCRETIONARY_CATEGORIES:
            continue
        key = (e.category, "*") if e.category in VARIABLE_CATEGORIES else (e.category, e.description)
        groups[key].append(h)
    # R1 fallback: singleton descriptions inside a fixed category are re-grouped by category
    leftovers: dict[str, list[HistRow]] = defaultdict(list)
    for (cat, desc), rows in list(groups.items()):
        if desc != "*" and len(rows) < cfg.MIN_OCCURRENCES:
            leftovers[cat].extend(rows)
            del groups[(cat, desc)]
    for cat, rows in leftovers.items():
        if len(rows) >= cfg.MIN_OCCURRENCES:
            groups[(cat, "*")] = sorted(rows, key=lambda h: h.on)
    multipliers = {a.target.split(":", 1)[1]: a for a in ledger.amendments if a.kind == "expense_multiplier"}
    streams: list[Stream] = []
    for (cat, desc), rows in sorted(groups.items()):
        rows.sort(key=lambda h: (h.on, h.event.number))
        if len(rows) < cfg.MIN_OCCURRENCES:
            continue
        dates = [h.on for h in rows]
        cadence = detect_cadence(dates, variable=(desc == "*" and cfg.VARIABLE_CADENCE == "median_gap"))
        if cadence is None:
            continue
        last = rows[-1]
        ended = _ended(last.on, cadence, ledger.t0, cfg)
        how = cfg.VARIABLE_AMOUNT_STAT if desc == "*" else "last"
        amount = stat([h.amount_home for h in rows], how)
        note = ""
        factor = multipliers[cat].factor if cat in multipliers else None
        if factor is not None:
            amount = amount * factor
            note = f"amount x{multipliers[cat].factor} per {multipliers[cat].source_id}"
        streams.append(
            Stream(
                kind="expense",
                key=f"expense:{cat}:{desc}",
                category=cat,
                description=last.event.description if desc == "*" else desc,
                cadence=cadence,
                amount=amount,
                dates=() if ended else project_dates(last.on, cadence, ledger.t0, end, cfg.PROJECT_ON_T0 == "include"),
                flexibility=last.event.flexibility,
                minimum_allowed_amount=last.event.minimum_allowed_amount,
                latest_event_id=last.event.event_id,
                ended=ended,
                note=note,
            )
        )
    return streams


# ----------------------------------------------------------------------------- income
def _income_streams(ledger: Ledger, cfg: Config, end: date) -> list[Stream]:
    amend = ledger.amendments
    if any(a.kind in ("income_unconfirmed", "stream_ended") and a.target == "all_income" for a in amend):
        return []
    rows = [
        h
        for h in ledger.history
        if h.event.direction == "credit"
        and h.event.event_type == "income"
        and not _is_non_recurring_income(h.event.description)
    ]
    ended_targets = [a.target for a in amend if a.kind == "stream_ended" and a.target.startswith("income:")]
    salary_ended = any(a.kind == "stream_ended" and a.target == "salary" for a in amend)
    rows = [
        h for h in rows if not any(t.split(":", 1)[1].lower() in h.event.description.lower() for t in ended_targets)
    ]
    streams: list[Stream] = []
    scheduled_days = {f.on for f in ledger.scheduled_income}

    # R5a weekly gig income: many payouts, short gaps
    rows.sort(key=lambda h: (h.on, h.event.number))
    all_dates = [h.on for h in rows]
    if len(rows) >= cfg.WEEKLY_INCOME_MIN_OCCURRENCES and _mostly_weekly(all_dates):
        last = rows[-1]
        ended = _ended(last.on, "weekly", ledger.t0, cfg) or salary_ended
        streams.append(
            Stream(
                kind="income",
                key="income:weekly",
                category="salary",
                description=last.event.description,
                cadence="weekly",
                amount=stat(
                    [h.amount_home for h in rows],
                    cfg.INCOME_AMOUNT_STAT if cfg.INCOME_AMOUNT_STAT != "last" else "mean",
                ),
                dates=() if ended else project_dates(last.on, "weekly", ledger.t0, end),
                flexibility="fixed",
                minimum_allowed_amount=None,
                latest_event_id=last.event.event_id,
                ended=ended,
            )
        )
        return streams

    # R5b monthly streams: cluster ALL income rows by day-of-month (a payroll keeps its day even when its description
    # changes across leave or an employer change). A more recent singleton whose description matches a cluster is a
    # moved payday: that cluster continues from the singleton's date (user_07: 15th -> 23rd).
    rows.sort(key=lambda h: (h.on, h.event.number))
    clusters: list[list[HistRow]] = []
    for h in rows:
        for c in clusters:
            if min(abs(c[-1].on.day - h.on.day), 31 - abs(c[-1].on.day - h.on.day)) <= cfg.CLUSTER_DAY_TOLERANCE:
                c.append(h)
                break
        else:
            clusters.append([h])
    moved: list[list[HistRow]] = []
    for single in [c for c in clusters if len(c) == 1]:
        h = single[0]
        for c in clusters:
            if len(c) >= cfg.MIN_OCCURRENCES and c[-1].event.description == h.event.description and h.on > c[-1].on:
                c.append(h)  # continue the stream from the new payday
                moved.append(single)
                break
    clusters = [c for c in clusters if c not in moved]
    salary_amount = next((a for a in amend if a.kind == "salary_amount"), None)
    salary_cap = next((a for a in amend if a.kind == "salary_cap" and a.amount is not None), None)
    secondary_ended = any(a.kind == "stream_ended" and a.target == "income:secondary" for a in amend)
    salary_date = next((a for a in amend if a.kind == "salary_date"), None)
    new_income = next((a for a in amend if a.kind == "new_income"), None)
    primary_done = False
    for c in sorted(clusters, key=lambda c: -len(c)):
        c.sort(key=lambda h: (h.on, h.event.number))
        cadence = "monthly"  # same day-of-month cluster; skipped months (unpaid leave) do not break the stream
        last = c[-1]
        if len(c) < cfg.MIN_OCCURRENCES:
            continue
        ended = _ended(last.on, cadence, ledger.t0, cfg) or last.event.description.lower().startswith("final")
        amounts = [h.amount_home for h in c]
        identical = max(amounts) - min(amounts) <= max(amounts) * Decimal("0.01")
        amount = amounts[-1] if identical else stat(amounts, cfg.INCOME_AMOUNT_STAT)
        projected = () if ended else project_dates(last.on, cadence, ledger.t0, end)
        note = ""
        is_primary = not primary_done
        if not is_primary and secondary_ended:
            ended, projected, note = True, (), "secondary income ended per evidence"
        if is_primary:
            primary_done = True
            if salary_cap is not None and salary_cap.amount is not None and amount > salary_cap.amount:
                amount = salary_cap.amount
                note = f"capped at remaining confirmed salary per {salary_cap.source_id}"
            if salary_ended:
                ended, projected, note = True, (), "salary stream ended per evidence"
            if salary_date is not None and salary_date.effective_from is not None and not ended:
                nd = salary_date.effective_from
                projected = tuple(
                    d for d in (nd, *project_dates(nd, "monthly", ledger.t0, end)) if ledger.t0 <= d <= end
                )
                note = f"payday moved to {nd} per {salary_date.source_id}"
            if salary_amount is not None and salary_amount.amount is not None and not ended:
                amount = salary_amount.amount
                note = (note + "; " if note else "") + f"amount {amount} per {salary_amount.source_id}"
        # R4 suppression: a scheduled income within ±3 days already represents this payday
        projected = tuple(d for d in projected if not any(abs((d - s).days) <= 3 for s in scheduled_days))
        streams.append(
            Stream(
                kind="income",
                key=f"income:day{last.on.day}",
                category="salary",
                description=last.event.description,
                cadence="monthly",
                amount=amount,
                dates=projected,
                flexibility="fixed",
                minimum_allowed_amount=None,
                latest_event_id=last.event.event_id,
                ended=ended,
                note=note,
            )
        )
    # R4 scheduled salary seeds the forward stream (C-1)
    for f in ledger.scheduled_income:
        if "salary" not in f.label.lower() and "payroll" not in f.label.lower():
            continue
        amount = f.amount
        if salary_amount is not None and salary_amount.amount is not None:
            amount = salary_amount.amount
        future = tuple(d for d in project_dates(f.on, "monthly", ledger.t0, end) if d > f.on)
        if salary_ended:
            future = ()
        streams.append(
            Stream(
                kind="income",
                key=f"income:scheduled:{f.event_id}",
                category="salary",
                description="Next confirmed salary (continued)",
                cadence="monthly",
                amount=amount,
                dates=future,
                flexibility="fixed",
                minimum_allowed_amount=None,
                latest_event_id=f.event_id or "",
                note="seeded by scheduled salary row (C-1)",
            )
        )
        # drop history-based monthly clusters on the same day (the scheduled row supersedes them)
        streams = [
            s
            for s in streams
            if not (s.key.startswith("income:day") and abs(int(s.key[10:]) - f.on.day) <= cfg.CLUSTER_DAY_TOLERANCE)
        ]
    # R7 new income from evidence (first confirmed salary) when history has no salary stream
    if new_income is not None and new_income.amount is not None and new_income.effective_from is not None:
        if not any(s.kind == "income" and s.dates for s in streams):
            first = new_income.effective_from
            dates = tuple(d for d in (first, *project_dates(first, "monthly", ledger.t0, end)) if ledger.t0 <= d <= end)
            streams.append(
                Stream(
                    kind="income",
                    key="income:new",
                    category="salary",
                    description="Confirmed new salary",
                    cadence="monthly",
                    amount=new_income.amount,
                    dates=dates,
                    flexibility="fixed",
                    minimum_allowed_amount=None,
                    latest_event_id="",
                    note=f"per {new_income.source_id}",
                )
            )
    return streams


def infer_streams(ledger: Ledger, cfg: Config) -> list[Stream]:
    end = ledger.t0 + timedelta(days=cfg.HORIZON_DAYS)
    return _expense_streams(ledger, cfg, end) + _income_streams(ledger, cfg, end)
