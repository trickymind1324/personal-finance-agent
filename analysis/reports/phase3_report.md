# Phase 3 report — deterministic core

Checkpoint: `tests/test_phase3_core.py` (30 tests) + Phase 2 (30 tests): 60 green. `ruff check`, `ruff format --check`, `mypy --strict` clean.

## Modules (src/buyorwait)

| module | role | CONTRACT § |
|---|---|---|
| `config.py` | every tunable with read-site / on-hit / why; `--set KEY=VALUE` overrides | §9 |
| `models.py` | typed dataset + pipeline records (Profile, Request, Event, PaymentOption, Amendment, Ledger, Stream, Plan, Rationale) | §8 |
| `rates.py` | exact dated conversion, `MissingRateError` | I-11 |
| `ledger.py` | status admission table, blank-amount resolution from evidence, duplicate-charge reserve | §5.1 |
| `recurrence.py` | streams: variable categories by observed gap, fixed by description, income by day-of-month cluster, moved payday, scheduled-salary seed, amendments | §5.2 |
| `simulate.py` | daily curve (end-of-day + intraday low), `is_safe` | §5.3 |
| `solver.py` | `safe_amount_today`, `earliest_full_date` (deadline-bounded for deferred payments; T0 full window) | §5.3 |
| `plans.py` | gates, candidates, 6-rule `rank_key`, spending-change search (fewest actions, numeric ids) | §3, §4.1, §5.4 |
| `reconcile.py` | Rationale → 8 columns; explanation from templates | §7, §8 |
| `pipeline.py` | per-request flow with I-10 re-check and per-row `validate_row` (raises) | §8 |

Entry point `code/main.py` (`--samples`, `--evidence`, `--set`, `--explain`, `--limit/--dry-run` → `output.subset.csv`, never `output.csv`).

## Convention fit (sample set only) — `analysis/reports/eval_sweep_conventions.md`

| tunable | chosen | alternatives tried | evidence |
|---|---|---|---|
| VARIABLE_CADENCE | median_gap | band | templates are every 7/10/14 (groceries), 5/7/14/21 (transport), 7/14/21 (dining); band drops 10/21 |
| VARIABLE_AMOUNT_STAT | median | mean, round_mean, last, max, p75, min | lowest mean error (3.1% of requested); `min` scores higher on status but is unprincipled and wrong on 11/13/18 |
| INTRADAY_ORDER | net | debits_first | net: 3.1% vs 4.2% error, same structure |
| PROJECT_ON_T0 | include | exclude | user_19 rent on T0; exclude loses earliest_exact |
| SAFETY_SCAN_END | deadline | window | earliest_exact 72% → 92%, status 80% → 88%; 5/6 wait samples have earliest == deadline |
| DISCRETIONARY_PROJECTION | project | skip | GT reduces dining (sample 11) so dining is projected |

## Before / after on the 25 samples (with manual evidence `data/evidence/manual_samples.json`)

| metric | baseline | core_v1 | core_v5 (pinned) |
|---|---|---|---|
| safe_within_5pct | 28% | 36% | 84% |
| safe_mean_err_pct | 24.8 | 12.6 | 3.1 |
| status_acc | 32% | 76% | 88% |
| method_plan_both | 44% | 64% | 88% |
| earliest_exact | 36% | 40% | 88% |
| changes_exact | 88% | 88% | 88% |
| row_valid | 84% | 100% | 100% |
| composite | 52.7% | 63.3% | 77.3% |

Model-off ablation (`core_v4_raw`, no evidence, 23/25 rows — two need image amounts and are skipped rather than guessed): composite 73.9%, mean error 8.7%. The evidence layer is worth +3.4 composite points and cuts the amount error by 64% on the rows it touches.

## Remaining sample misses (honest list)

- 06, 11, 21: spending-change rescues missed because my trough is a few units off the knife edge (GT safe 603.30 vs 550.01; 12,510,645 vs 12,268,246; 1,543.35 vs 1,574.40 — the last is *above* GT, so no rescue is attempted). Root cause: ground truth forecasts round base amounts; history medians approximate them within ~3%.
- 04 (16.9%), 12 (9.8%), 13 (8.4%): same amount-estimation error, no structural miss.
- 10: GT leaves 12,700 headroom after removing unconfirmed gig income; mine leaves 0. Unknown convention (unconfirmed income partially counted?), left as-is.
- 25: GT 1,425,000 vs 451,492 — foreign-currency user; projection of IDR variable spend too high. Left as-is deliberately (1.6% of requested).
