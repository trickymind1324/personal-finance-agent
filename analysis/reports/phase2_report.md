# Phase 2 report — eval harness and naive baseline (before any solution code)

Checkpoint: `tests/test_phase2_checkpoint.py` (30 tests, green). Lint: `ruff check` and `ruff format --check` clean on `src/ code/ tests/` and the audit tooling; `mypy --strict` clean on `src/`.

## What exists now

| piece | path | role |
|---|---|---|
| Output contract | `src/buyorwait/contract.py` | enums, per-column formatting (`fmt_shortest`, `fmt_padded`, `fmt_prose_amount`, `prose_date`), plan/changes parse+render (numeric event-id order, ruling C-4), six explanation templates as regexes + `render_explanation`, `validate_row` (CONTRACT §2 structural invariants I-1..I-8, C-4, C-6, explanation consistency) |
| Dataset loading | `src/buyorwait/io_dataset.py` | `build_row_contexts` — per-request validation context from `dataset/` only |
| Scorer | `code/evaluation/score.py` | per-column metrics on `sample_requests.csv`; prints the table every run; writes `analysis/reports/eval_<tag>.{md,json}` and `analysis/reports/predictions/<tag>.csv`; diffs against the pinned run and the baseline; exits 2 on any per-column regression vs pinned |
| Naive baseline | `code/evaluation/baseline.py` | balance − minimum ≥ amount ⇒ `affordable_now`/`full_payment`, else `not_affordable` |
| Few-shot exclusion | `code/evaluation/fewshot_exclusions.txt` | ids listed here are never scored (empty for now) |

## Metrics (six scored dimensions + diagnostics)

`safe_exact` (|Δ| ≤ 0.005), `safe_within_5pct`, `safe_mean_err_pct` (lower is better), `status_acc`, `method_acc`, `plan_exact`, `method_plan_both`, `earliest_exact`, `changes_exact`, `changes_valid` (structural), `explanation_template`, `explanation_consistent` (template + every number/date agrees with the row's own columns), `row_valid`, `composite` (mean of the six dimension accuracies).

## Baseline result (committed as `analysis/reports/eval_baseline.json`, also the initial pin)

| metric | baseline |
|---|---|
| safe_exact | 16.0% |
| safe_within_5pct | 28.0% |
| safe_mean_err_pct | 24.8 |
| status_acc | 32.0% |
| method_plan_both | 44.0% |
| earliest_exact | 36.0% |
| changes_exact | 88.0% |
| changes_valid | 100.0% |
| explanation_consistent | 100.0% |
| row_valid | 84.0% |
| composite | 52.7% |

`row_valid` is 84% and not 100% because the baseline ignores the method gate: it recommends `full_payment` to users who do not accept it (4 rows). That is deliberate — the baseline is a floor, and the gate violation is exactly what the validator must catch.

## How to use from here

```
python3 code/evaluation/score.py --predictions <csv> --tag <tag>           # diff vs pin + baseline; exit 2 on regression
python3 code/evaluation/score.py --predictions <csv> --tag <tag> --set-pin # accept as the new pinned run
```
