# Eval report — `core_v4_raw`

Scored rows: 23 (excluded few-shot ids: none).
Predictions: `analysis/reports/predictions/core_v4_raw.csv`. Pinned: `eval_pinned.json`. Baseline: `eval_baseline.json`.

| metric | current | pinned | Δ pin | baseline | Δ base |
|---|---|---|---|---|---|
| safe_exact | 8.7% | 12.0% | -3.3 | 16.0% | -7.3 |
| safe_within_5pct | 69.6% | 84.0% | -14.4 | 28.0% | +41.6 |
| safe_mean_err_pct | 8.7 | 3.1 | +5.6 | 24.8 | -16.1 |
| status_acc | 82.6% | 88.0% | -5.4 | 32.0% | +50.6 |
| method_acc | 87.0% | 92.0% | -5.0 | 44.0% | +43.0 |
| plan_exact | 82.6% | 88.0% | -5.4 | 44.0% | +38.6 |
| method_plan_both | 82.6% | 88.0% | -5.4 | 44.0% | +38.6 |
| earliest_exact | 82.6% | 88.0% | -5.4 | 36.0% | +46.6 |
| changes_exact | 87.0% | 88.0% | -1.0 | 88.0% | -1.0 |
| changes_valid | 100.0% | 100.0% | +0.0 | 100.0% | +0.0 |
| explanation_template | 100.0% | 100.0% | +0.0 | 100.0% | +0.0 |
| explanation_consistent | 100.0% | 100.0% | +0.0 | 100.0% | +0.0 |
| row_valid | 100.0% | 100.0% | +0.0 | 84.0% | +16.0 |
| composite | 73.9% | 77.3% | -3.4 | 52.7% | +21.2 |

## Per-row

| request | safe err % | status | method | plan | earliest | changes | violations |
|---|---|---|---|---|---|---|---|
| request_01 | 0.0 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_02 | 1.98 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_03 | 2.33 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_04 | 16.86 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_05 | 4.76 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_06 | 8.59 | ✗ | ✗ | ✗ | ✓ | ✗ | - |
| request_07 | 0.42 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_08 | 28.55 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_09 | 0.0 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_10 | 95.24 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_11 | 1.85 | ✓ | ✓ | ✓ | ✗ | ✗ | - |
| request_12 | 9.81 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_13 | 8.4 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_14 | 0.51 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_15 | 2.04 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_17 | 0.35 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_18 | 2.88 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_19 | 8.85 | ✓ | ✓ | ✗ | ✓ | ✓ | - |
| request_21 | 1.97 | ✗ | ✓ | ✓ | ✗ | ✗ | - |
| request_22 | 0.82 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_23 | 1.71 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_24 | 1.23 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_25 | 1.61 | ✓ | ✓ | ✓ | ✓ | ✓ | - |

**REGRESSION vs pinned on: safe_exact, safe_within_5pct, safe_mean_err_pct, status_acc, method_acc, plan_exact, method_plan_both, earliest_exact, changes_exact, composite**
