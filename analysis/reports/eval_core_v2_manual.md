# Eval report — `core_v2_manual`

Scored rows: 25 (excluded few-shot ids: none).
Predictions: `analysis/reports/predictions/core_v2_manual.csv`. Pinned: `eval_pinned.json`. Baseline: `eval_baseline.json`.

| metric | current | pinned | Δ pin | baseline | Δ base |
|---|---|---|---|---|---|
| safe_exact | 16.0% | 16.0% | +0.0 | 16.0% | +0.0 |
| safe_within_5pct | 72.0% | 28.0% | +44.0 | 28.0% | +44.0 |
| safe_mean_err_pct | 5.3 | 24.8 | -19.5 | 24.8 | -19.5 |
| status_acc | 76.0% | 32.0% | +44.0 | 32.0% | +44.0 |
| method_acc | 84.0% | 44.0% | +40.0 | 44.0% | +40.0 |
| plan_exact | 72.0% | 44.0% | +28.0 | 44.0% | +28.0 |
| method_plan_both | 72.0% | 44.0% | +28.0 | 44.0% | +28.0 |
| earliest_exact | 64.0% | 36.0% | +28.0 | 36.0% | +28.0 |
| changes_exact | 88.0% | 88.0% | +0.0 | 88.0% | +0.0 |
| changes_valid | 100.0% | 100.0% | +0.0 | 100.0% | +0.0 |
| explanation_template | 100.0% | 100.0% | +0.0 | 100.0% | +0.0 |
| explanation_consistent | 100.0% | 100.0% | +0.0 | 100.0% | +0.0 |
| row_valid | 100.0% | 84.0% | +16.0 | 84.0% | +16.0 |
| composite | 69.3% | 52.7% | +16.7 | 52.7% | +16.7 |

## Per-row

| request | safe err % | status | method | plan | earliest | changes | violations |
|---|---|---|---|---|---|---|---|
| request_01 | 0.0 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_02 | 6.33 | ✓ | ✓ | ✓ | ✗ | ✓ | - |
| request_03 | 8.45 | ✓ | ✓ | ✗ | ✗ | ✓ | - |
| request_04 | 17.39 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_05 | 4.76 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_06 | 0.58 | ✗ | ✗ | ✗ | ✓ | ✗ | - |
| request_07 | 44.16 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_08 | 0.06 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_09 | 0.0 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_10 | 4.76 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_11 | 4.57 | ✗ | ✓ | ✓ | ✗ | ✗ | - |
| request_12 | 0.0 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_13 | 8.09 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_14 | 11.04 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_15 | 2.06 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_16 | 0.0 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_17 | 0.79 | ✓ | ✓ | ✓ | ✗ | ✓ | - |
| request_18 | 5.81 | ✓ | ✓ | ✗ | ✗ | ✓ | - |
| request_19 | 3.01 | ✓ | ✓ | ✗ | ✓ | ✓ | - |
| request_20 | 2.29 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_21 | 1.97 | ✗ | ✓ | ✓ | ✗ | ✗ | - |
| request_22 | 1.04 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_23 | 1.93 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_24 | 3.27 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_25 | 0.45 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
