"""Every tunable constant, in one place (CONTRACT.md §9).

Each field documents: what reads it, what happens when it is hit, and why the value.
Overrides come from `Config.with_overrides({"NAME": "value"})` (CLI `--set NAME=value`),
which is how the Phase 3 sweeps are run; the defaults are the fitted values.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from typing import Any


@dataclass(frozen=True)
class Config:
    # --- forecast window -------------------------------------------------------------
    HORIZON_DAYS: int = 90
    """Read by simulate/solver. Window is [T0, T0+HORIZON_DAYS] inclusive. Statement: '90-Day Safety Check'."""

    HISTORY_DAYS: int = 190
    """Read by recurrence. Settled rows older than this before T0 are ignored for inference.
    Why: every user has ~6 months of history; 190 keeps the whole window with slack."""

    # --- recurrence inference ---------------------------------------------------------
    MIN_OCCURRENCES: int = 2
    """Read by recurrence. Groups with fewer settled occurrences are one-off and never projected.
    Statement: 'detect recurrence only when history supports it'."""

    GRACE_DAYS: int = 5
    """Read by recurrence (CONTRACT C-2). If last_occurrence + cadence + GRACE_DAYS < T0 the stream has ended.
    Why: user_13's second income missed by 15 days (ended); user_05's next payday was not yet due (not ended by this rule)."""

    VARIABLE_AMOUNT_STAT: str = "median"
    """Read by recurrence (CONTRACT C-3) for VARIABLE_CATEGORIES: one of mean | median | round_mean | p75 | max | min | last.
    Fitted on samples (analysis/reports/eval_sweep_conventions.md): median gives the lowest mean error (3.1% of requested)."""

    VARIABLE_CADENCE: str = "median_gap"
    """Read by recurrence for VARIABLE_CATEGORIES: 'band' (only weekly/biweekly/monthly gaps are recurring) or
    'median_gap' (any median gap in [3, 45] days is projected at that gap). Fitted on samples."""

    DISCRETIONARY_PROJECTION: str = "project"
    """Read by recurrence: 'project' or 'skip' for DISCRETIONARY_CATEGORIES (dining, shopping, entertainment).
    Statement says 'forecast essential variable spending conservatively'; whether discretionary spend is projected is fitted."""

    INTRADAY_ORDER: str = "net"
    """Read by simulate: 'net' (one end-of-day balance) or 'debits_first' (same-day debits land before credits).
    Fitted on samples: 'net' (debits_first raises mean error from 3.1% to 4.2% with no structural gain)."""

    PROJECT_ON_T0: str = "include"
    """Read by recurrence (R8): 'include' projects a recurring occurrence dated exactly request_date (not yet in the
    opening balance), 'exclude' starts projections the day after. Fitted on samples."""

    SAFETY_SCAN_END: str = "deadline"
    """Read by solver/plans for DEFERRED payments only (earliest date, wait, partial second payment): 'window' tests the
    balance through T0+90; 'deadline' tests through desired_completion_date. amount_safe_to_pay always uses the full
    window (statement). Fitted: 'deadline' lifts earliest_exact 72% -> 92% and status 80% -> 88% on the samples (five of the
    six 'wait' samples have earliest == deadline). Recorded in README Known Limitations as a sample-fitted convention."""

    INCOME_AMOUNT_STAT: str = "last"
    """Read by recurrence for income clusters whose amounts vary: one of last | mean | min.
    Why: fixed salaries are identical month to month; for variable income the safer reading is fitted."""

    WEEKLY_INCOME_MIN_OCCURRENCES: int = 6
    """Read by recurrence. A weekly gig-income stream needs at least this many payouts in history.
    Why: 6 months of weekly payouts gives ~26; 6 rejects a handful of one-off client payments."""

    CLUSTER_DAY_TOLERANCE: int = 3
    """Read by recurrence. Income occurrences within ±this many days-of-month form one monthly cluster.
    Why: payroll can slip a day or two around weekends; 3 keeps the 15th and 20th separate."""

    # --- plans ------------------------------------------------------------------------
    MAX_CHANGES: int = 3
    """Read by plans.search_changes. Combinations larger than this are never enumerated. Statement."""

    # --- model layer (Phase 4) --------------------------------------------------------
    MAX_TOOL_ITERATIONS: int = 4
    """Read by the evidence loop. When hit, the item falls back to the safer reading. Brief §6."""

    MAX_CALLS_PER_REQUEST: int = 8
    MAX_CALLS_TOTAL: int = 600
    MAX_TOKENS_TOTAL: int = 3_000_000
    """Read by budget. When hit: BudgetExceededError, cache is the checkpoint, clean stop. Why: 16 images + 215 messages ≈ 231 calls."""

    MAX_COST_USD: float = 8.0
    """Read by budget: hard cap on PAID spend for the whole run (cache replays cost nothing and do not count).
    When hit: BudgetExceededError before the next paid call. Why: user directive 2026-09-13 — a surprise can never drain the account."""

    def with_overrides(self, overrides: dict[str, str]) -> Config:
        kwargs: dict[str, Any] = {}
        types = {f.name: f.type for f in fields(self)}
        for k, v in overrides.items():
            if k not in types:
                raise KeyError(f"unknown config key {k!r}; known: {sorted(types)}")
            current = getattr(self, k)
            kwargs[k] = type(current)(v) if not isinstance(current, str) else v
        return replace(self, **kwargs)


VARIABLE_CATEGORIES: frozenset[str] = frozenset({"groceries", "transport", "dining", "shopping", "entertainment"})
"""Expense categories whose occurrences vary in description and amount; grouped by category, amount by VARIABLE_AMOUNT_STAT."""

DISCRETIONARY_CATEGORIES: frozenset[str] = frozenset({"dining", "shopping", "entertainment"})
"""Non-essential variable spend; projected or skipped per Config.DISCRETIONARY_PROJECTION."""

NON_RECURRING_INCOME_WORDS: tuple[str, ...] = (
    "bonus",
    "commission",
    "arrears",
    "prorated",
    "final",
    "windfall",
    "prize",
    "reimburse",
    "one-time",
    "one time",
)
"""Income descriptions containing any of these are never projected forward (statement: no bonuses/commissions until settled)."""

DEFAULT_CONFIG = Config()
