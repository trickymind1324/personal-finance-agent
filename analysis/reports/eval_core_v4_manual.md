# Eval report — `core_v4_manual`

Scored rows: 25 (excluded few-shot ids: none).
Predictions: `analysis/reports/predictions/core_v4_manual.csv`. Pinned: `eval_pinned.json`. Baseline: `eval_baseline.json`.

| metric | current | pinned | Δ pin | baseline | Δ base |
|---|---|---|---|---|---|
| safe_exact | 12.0% | 16.0% | -4.0 | 16.0% | -4.0 |
| safe_within_5pct | 84.0% | 28.0% | +56.0 | 28.0% | +56.0 |
| safe_mean_err_pct | 3.1 | 24.8 | -21.7 | 24.8 | -21.7 |
| status_acc | 88.0% | 32.0% | +56.0 | 32.0% | +56.0 |
| method_acc | 92.0% | 44.0% | +48.0 | 44.0% | +48.0 |
| plan_exact | 88.0% | 44.0% | +44.0 | 44.0% | +44.0 |
| method_plan_both | 88.0% | 44.0% | +44.0 | 44.0% | +44.0 |
| earliest_exact | 92.0% | 36.0% | +56.0 | 36.0% | +56.0 |
| changes_exact | 88.0% | 88.0% | +0.0 | 88.0% | +0.0 |
| changes_valid | 100.0% | 100.0% | +0.0 | 100.0% | +0.0 |
| explanation_template | 100.0% | 100.0% | +0.0 | 100.0% | +0.0 |
| explanation_consistent | 100.0% | 100.0% | +0.0 | 100.0% | +0.0 |
| row_valid | 100.0% | 84.0% | +16.0 | 84.0% | +16.0 |
| composite | 78.0% | 52.7% | +25.3 | 52.7% | +25.3 |

## Per-row

| request | safe err % | status | method | plan | earliest | changes | violations |
|---|---|---|---|---|---|---|---|
| request_01 | 0.0 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_02 | 1.98 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_03 | 2.33 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_04 | 16.86 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_05 | 4.76 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_06 | 8.59 | ✗ | ✗ | ✗ | ✓ | ✗ | - |
| request_07 | 0.42 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_08 | 0.66 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_09 | 0.0 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_10 | 4.76 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_11 | 1.85 | ✗ | ✗ | ✗ | ✗ | ✗ | - |
| request_12 | 9.81 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_13 | 8.4 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_14 | 0.51 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_15 | 2.04 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_16 | 0.0 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_17 | 0.32 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_18 | 2.88 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_19 | 3.12 | ✓ | ✓ | ✗ | ✓ | ✓ | - |
| request_20 | 1.09 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_21 | 1.97 | ✗ | ✓ | ✓ | ✗ | ✗ | - |
| request_22 | 0.82 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_23 | 1.71 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_24 | 1.23 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_25 | 1.61 | ✓ | ✓ | ✓ | ✓ | ✓ | - |

**REGRESSION vs pinned on: safe_exact**
