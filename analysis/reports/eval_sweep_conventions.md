# Convention sweep (Phase 3, sample set only)

Grid: {"VARIABLE_AMOUNT_STAT": ["mean", "median", "round_mean", "min", "p75"], "VARIABLE_CADENCE": ["band", "median_gap"], "INTRADAY_ORDER": ["net", "debits_first"], "PROJECT_ON_T0": ["include", "exclude"], "SAFETY_SCAN_END": ["window", "deadline"]}

Ranked by safe_within_1pct, then earliest_exact, then method_plan_both, then lower mean error. Top 25 of 75 cells (5 raised).

| rank | VARIABLE_AMOUNT_STAT | VARIABLE_CADENCE | INTRADAY_ORDER | PROJECT_ON_T0 | SAFETY_SCAN_END | safe≤1% | safe≤5% | mean err% | earliest | method+plan | status | changes | composite |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | median | band | net | include | deadline | 40% | 80% | 3.3 | 80% | 84% | 88% | 88% | 76.0% |
| 2 | round_mean | band | net | include | deadline | 40% | 80% | 3.3 | 76% | 84% | 88% | 88% | 75.3% |
| 3 | median | band | net | include | window | 40% | 80% | 3.3 | 72% | 76% | 80% | 88% | 72.0% |
| 4 | round_mean | band | net | include | window | 40% | 80% | 3.3 | 68% | 76% | 80% | 88% | 71.3% |
| 5 | median | median_gap | debits_first | include | deadline | 36% | 80% | 4.2 | 92% | 88% | 88% | 88% | 78.0% |
| 6 | round_mean | median_gap | debits_first | include | deadline | 36% | 80% | 4.1 | 88% | 88% | 88% | 88% | 77.3% |
| 7 | mean | median_gap | debits_first | include | deadline | 36% | 80% | 4.1 | 88% | 88% | 88% | 88% | 77.3% |
| 8 | mean | band | net | include | deadline | 36% | 80% | 3.3 | 76% | 84% | 88% | 88% | 75.3% |
| 9 | median | median_gap | debits_first | include | window | 36% | 80% | 4.2 | 76% | 76% | 72% | 88% | 70.7% |
| 10 | round_mean | median_gap | debits_first | include | window | 36% | 80% | 4.1 | 72% | 72% | 68% | 88% | 68.7% |
| 11 | mean | median_gap | debits_first | include | window | 36% | 80% | 4.1 | 72% | 72% | 68% | 88% | 68.7% |
| 12 | mean | band | net | include | window | 36% | 80% | 3.3 | 68% | 76% | 80% | 88% | 71.3% |
| 13 | median | median_gap | net | include | deadline | 32% | 84% | 3.1 | 92% | 88% | 88% | 88% | 78.0% |
| 14 | round_mean | median_gap | net | include | deadline | 32% | 84% | 3.0 | 88% | 88% | 88% | 88% | 77.3% |
| 15 | median | median_gap | net | exclude | deadline | 32% | 80% | 4.2 | 84% | 92% | 88% | 88% | 77.3% |
| 16 | median | band | debits_first | include | deadline | 32% | 80% | 4.3 | 84% | 84% | 88% | 88% | 76.7% |
| 17 | round_mean | median_gap | net | exclude | deadline | 32% | 80% | 4.1 | 80% | 92% | 88% | 88% | 76.7% |
| 18 | mean | median_gap | net | exclude | deadline | 32% | 80% | 4.1 | 80% | 92% | 88% | 88% | 76.7% |
| 19 | median | median_gap | net | include | window | 32% | 84% | 3.1 | 80% | 76% | 76% | 88% | 72.0% |
| 20 | round_mean | band | debits_first | include | deadline | 32% | 80% | 4.3 | 76% | 84% | 88% | 88% | 75.3% |
| 21 | mean | band | debits_first | include | deadline | 32% | 80% | 4.3 | 76% | 84% | 88% | 88% | 75.3% |
| 22 | round_mean | median_gap | net | include | window | 32% | 84% | 3.0 | 76% | 76% | 76% | 88% | 71.3% |
| 23 | median | band | net | exclude | deadline | 32% | 68% | 5.1 | 72% | 88% | 88% | 88% | 75.3% |
| 24 | median | median_gap | net | exclude | window | 32% | 80% | 4.2 | 72% | 80% | 76% | 88% | 71.3% |
| 25 | median | band | debits_first | include | window | 32% | 80% | 4.3 | 72% | 76% | 76% | 88% | 71.3% |

## Cells that raised

- {'VARIABLE_AMOUNT_STAT': 'min', 'VARIABLE_CADENCE': 'band', 'INTRADAY_ORDER': 'debits_first', 'PROJECT_ON_T0': 'include', 'SAFETY_SCAN_END': 'deadline'}: InvariantError: request_06: chosen plan full_payment failed the safety re-check
- {'VARIABLE_AMOUNT_STAT': 'p75', 'VARIABLE_CADENCE': 'band', 'INTRADAY_ORDER': 'net', 'PROJECT_ON_T0': 'include', 'SAFETY_SCAN_END': 'deadline'}: InvariantError: request_16: chosen plan full_payment failed the safety re-check
- {'VARIABLE_AMOUNT_STAT': 'p75', 'VARIABLE_CADENCE': 'band', 'INTRADAY_ORDER': 'net', 'PROJECT_ON_T0': 'exclude', 'SAFETY_SCAN_END': 'deadline'}: InvariantError: request_16: chosen plan full_payment failed the safety re-check
- {'VARIABLE_AMOUNT_STAT': 'p75', 'VARIABLE_CADENCE': 'median_gap', 'INTRADAY_ORDER': 'net', 'PROJECT_ON_T0': 'include', 'SAFETY_SCAN_END': 'deadline'}: InvariantError: request_16: chosen plan full_payment failed the safety re-check
- {'VARIABLE_AMOUNT_STAT': 'p75', 'VARIABLE_CADENCE': 'median_gap', 'INTRADAY_ORDER': 'net', 'PROJECT_ON_T0': 'exclude', 'SAFETY_SCAN_END': 'deadline'}: InvariantError: request_16: chosen plan full_payment failed the safety re-check
