# Eval report — `core_v1_manual`

Scored rows: 25 (excluded few-shot ids: none).
Predictions: `analysis/reports/predictions/core_v1_manual.csv`. Pinned: `eval_pinned.json`. Baseline: `eval_baseline.json`.

| metric | current | pinned | Δ pin | baseline | Δ base |
|---|---|---|---|---|---|
| safe_exact | 12.0% | 16.0% | -4.0 | 16.0% | -4.0 |
| safe_within_5pct | 36.0% | 28.0% | +8.0 | 28.0% | +8.0 |
| safe_mean_err_pct | 12.6 | 24.8 | -12.2 | 24.8 | -12.2 |
| status_acc | 76.0% | 32.0% | +44.0 | 32.0% | +44.0 |
| method_acc | 84.0% | 44.0% | +40.0 | 44.0% | +40.0 |
| plan_exact | 64.0% | 44.0% | +20.0 | 44.0% | +20.0 |
| method_plan_both | 64.0% | 44.0% | +20.0 | 44.0% | +20.0 |
| earliest_exact | 40.0% | 36.0% | +4.0 | 36.0% | +4.0 |
| changes_exact | 88.0% | 88.0% | +0.0 | 88.0% | +0.0 |
| changes_valid | 100.0% | 100.0% | +0.0 | 100.0% | +0.0 |
| explanation_template | 100.0% | 100.0% | +0.0 | 100.0% | +0.0 |
| explanation_consistent | 100.0% | 100.0% | +0.0 | 100.0% | +0.0 |
| row_valid | 100.0% | 84.0% | +16.0 | 84.0% | +16.0 |
| composite | 63.3% | 52.7% | +10.7 | 52.7% | +10.7 |

## Per-row

| request | safe err % | status | method | plan | earliest | changes | violations |
|---|---|---|---|---|---|---|---|
| request_01 | 0.0 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_02 | 21.56 | ✓ | ✓ | ✓ | ✗ | ✓ | - |
| request_03 | 39.58 | ✓ | ✓ | ✗ | ✗ | ✓ | - |
| request_04 | 7.26 | ✓ | ✓ | ✗ | ✗ | ✓ | - |
| request_05 | 4.76 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_06 | 2.76 | ✗ | ✓ | ✓ | ✗ | ✗ | - |
| request_07 | 44.16 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_08 | 6.09 | ✓ | ✓ | ✗ | ✗ | ✓ | - |
| request_09 | 0.0 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_10 | 2.64 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_11 | 4.57 | ✗ | ✓ | ✓ | ✗ | ✗ | - |
| request_12 | 0.0 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_13 | 53.97 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_14 | 11.04 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_15 | 1.89 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_16 | 8.81 | ✗ | ✗ | ✗ | ✗ | ✓ | - |
| request_17 | 11.2 | ✓ | ✓ | ✓ | ✗ | ✓ | - |
| request_18 | 15.23 | ✓ | ✓ | ✗ | ✗ | ✓ | - |
| request_19 | 27.33 | ✓ | ✗ | ✗ | ✗ | ✓ | - |
| request_20 | 7.31 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_21 | 1.97 | ✗ | ✓ | ✓ | ✗ | ✗ | - |
| request_22 | 5.82 | ✓ | ✓ | ✓ | ✗ | ✓ | - |
| request_23 | 21.48 | ✓ | ✓ | ✗ | ✗ | ✓ | - |
| request_24 | 8.35 | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| request_25 | 7.6 | ✓ | ✓ | ✓ | ✓ | ✓ | - |

**REGRESSION vs pinned on: safe_exact**
