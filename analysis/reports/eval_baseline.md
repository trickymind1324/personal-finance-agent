# Eval report — `baseline`

Scored rows: 25 (excluded few-shot ids: none).
Predictions: `analysis/reports/predictions/baseline.csv`. Pinned: `eval_pinned.json`. Baseline: `eval_baseline.json`.

| metric | current | pinned | Δ pin | baseline | Δ base |
|---|---|---|---|---|---|
| safe_exact | 16.0% | 16.0% | +0.0 | 16.0% | +0.0 |
| safe_within_5pct | 28.0% | 28.0% | +0.0 | 28.0% | +0.0 |
| safe_mean_err_pct | 24.8 | 24.8 | +0.0 | 24.8 | +0.0 |
| status_acc | 32.0% | 32.0% | +0.0 | 32.0% | +0.0 |
| method_acc | 44.0% | 44.0% | +0.0 | 44.0% | +0.0 |
| plan_exact | 44.0% | 44.0% | +0.0 | 44.0% | +0.0 |
| method_plan_both | 44.0% | 44.0% | +0.0 | 44.0% | +0.0 |
| earliest_exact | 36.0% | 36.0% | +0.0 | 36.0% | +0.0 |
| changes_exact | 88.0% | 88.0% | +0.0 | 88.0% | +0.0 |
| changes_valid | 100.0% | 100.0% | +0.0 | 100.0% | +0.0 |
| explanation_template | 100.0% | 100.0% | +0.0 | 100.0% | +0.0 |
| explanation_consistent | 100.0% | 100.0% | +0.0 | 100.0% | +0.0 |
| row_valid | 84.0% | 84.0% | +0.0 | 84.0% | +0.0 |
| composite | 52.7% | 52.7% | +0.0 | 52.7% | +0.0 |

## Per-row

| request | safe err % | status | method | plan | earliest | changes | violations |
|---|---|---|---|---|---|---|---|
| request_01 | 0.0 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_02 | 30.41 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_03 | 41.31 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_04 | 33.81 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_05 | 95.24 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_06 | 2.76 | ✗ | ✓ | ✓ | ✗ | ✗ | - |
| request_07 | 19.64 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_08 | 45.35 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_09 | 0.0 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_10 | 95.24 | ✗ | ✗ | ✗ | ✗ | ✓ | gate: full_payment not accepted by user |
| request_11 | 4.57 | ✗ | ✓ | ✓ | ✗ | ✗ | - |
| request_12 | 0.0 | ✗ | ✗ | ✗ | ✓ | ✓ | gate: full_payment not accepted by user |
| request_13 | 53.97 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_14 | 20.94 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_15 | 13.22 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_16 | 0.0 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_17 | 11.2 | ✗ | ✗ | ✗ | ✗ | ✓ | gate: full_payment not accepted by user |
| request_18 | 19.22 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_19 | 27.33 | ✗ | ✗ | ✗ | ✗ | ✓ | gate: full_payment not accepted by user |
| request_20 | 10.77 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_21 | 1.97 | ✗ | ✓ | ✓ | ✗ | ✗ | - |
| request_22 | 21.46 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_23 | 41.58 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_24 | 18.82 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_25 | 12.0 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
