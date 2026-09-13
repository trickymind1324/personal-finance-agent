# Anchor-insight experiment (Phase 0)

Hypothesis: the decision is fully computable from a truthful ledger; the hard part is ledger truth (image amounts, message amendments, recurrence inference). One naive simulator, identical logic, run twice: **A** raw ledger, **B** raw ledger + hand-encoded image/message evidence for the 25 sample users. Error is |sim − ground truth| as % of requested_amount (so it is comparable across currencies).

| req | user | requested | GT safe | A safe | A err% | B safe | B err% | GT earliest | A earliest | B earliest | msg | img | evidence applied in B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 | user_01 | 25256 | 25256 | 5976.42 | 76.3 | 5976.42 | 76.3 | 2024-03-03 | (empty) | (empty) | - | - |  |
| 02 | user_02 | 4.6018e+07 | 1.72291e+07 | 1.82312e+07 | 2.2 | 1.82312e+07 | 2.2 | 2025-09-15 | 2025-10-15 | 2025-09-15 | y | - | credit:Payroll credit: amount override 33345000.00->42750000.00 from 2025-08-15 (message_01: gaji bulanan naik menjadi IDR 42750000 mulai 2025-08-15) |
| 03 | user_03 | 5.491e+06 | 873000 | 993780 | 2.2 | 993780 | 2.2 | 2019-11-15 | 2019-11-15 | 2019-11-15 | y | y | event_253 amount from image_01 payslip Aug-2019 net pay IDR 4,365,000 |
| 04 | user_04 | 1.2693e+07 | 8.4018e+06 | 1.06086e+07 | 17.4 | 1.06086e+07 | 17.4 | 2024-06-15 | 2024-06-15 | 2024-06-15 | y | - |  |
| 05 | user_05 | 15488 | 737 | 0 | 4.8 | 0 | 4.8 | (empty) | (empty) | (empty) | - | - | income stopped: ledger: last salary described 'Final employer payroll' (no message) |
| 06 | user_06 | 620.4 | 603.3 | 527.68 | 12.2 | 527.68 | 12.2 | 2026-01-15 | 2026-01-15 | 2026-01-15 | y | - |  |
| 07 | user_07 | 197400 | 87170.6 | 86817.1 | 0.2 | 86817.1 | 0.2 | 2024-10-23 | 2024-10-23 | 2024-10-23 | y | - |  |
| 08 | user_08 | 996.6 | 284.57 | 0 | 28.6 | 285.2 | 0.1 | 2025-04-15 | (empty) | (empty) | y | - | credit:Payroll credit: amount override 782.57->1422.85 from 2025-02-15 (message_06: next salary is reduced to EUR 1422.85 (last settled was 782.57)) |
| 09 | user_09 | 166.61 | 166.61 | 166.61 | 0.0 | 166.61 | 0.0 | 2026-07-04 | 2026-07-04 | 2026-07-04 | - | - |  |
| 10 | user_10 | 266700 | 12700 | 266700 | 95.2 | 0 | 4.8 | (empty) | 2024-12-06 | (empty) | y | - | income stopped: message_07: QuickCrew payout still pending; balance not withdrawable until completed -> weekly gig income unconfirmed |
| 11 | user_11 | 1.311e+07 | 1.25106e+07 | 1.2361e+07 | 1.1 | 1.2361e+07 | 1.1 | 2025-07-15 | 2025-06-15 | 2025-05-15 | y | - | credit:Base salary: amount override 23256000.00->38760000.00 from 2025-05-15 (message_08: gaji pokok yang dikonfirmasi IDR 38760000; komisi belum disetujui) |
| 12 | user_12 | 65164 | 65164 | 60080.8 | 7.8 | 60080.8 | 7.8 | 2026-04-05 | (empty) | (empty) | y | - | income stopped: message_09: seasonal contract has ended; no off-season income confirmed |
| 13 | user_13 | 941.6 | 433.4 | 941.6 | 54.0 | 941.6 | 54.0 | 2024-05-15 | 2024-03-07 | 2024-03-07 | - | - |  |
| 14 | user_14 | 5414.2 | 597.74 | 0 | 11.0 | 0 | 11.0 | (empty) | (empty) | (empty) | y | - |  |
| 15 | user_15 | 3685 | 83.05 | 7.07 | 2.1 | 7.07 | 2.1 | (empty) | (empty) | (empty) | y | - |  |
| 16 | user_16 | 122500 | 122500 | 122500 | 0.0 | 122500 | 0.0 | 2023-08-12 | 2023-08-12 | 2023-08-12 | y | y | event_1442 amount from image_02 rent receipt: Balance Due 1,00,000.00 |
| 17 | user_17 | 274600 | 243850 | 244075 | 0.1 | 241692 | 0.8 | 2026-03-15 | 2026-03-15 | 2026-04-15 | - | y | event_1545 amount from image_03 nuts & spices bill: Net Amount 41272.00 |
| 18 | user_18 | 3246.1 | 462 | 557.34 | 2.9 | 557.34 | 2.9 | 2026-09-15 | 2026-09-15 | 2026-09-15 | y | - |  |
| 19 | user_19 | 39660 | 28820 | 25165.8 | 9.2 | 30012.4 | 3.0 | 2024-09-15 | 2024-09-15 | 2024-09-15 | - | y | event_1700 amount from image_04 grocery delivery: Item Bill 2854.00, image CROPPED below (fees unknown) -> partial |
| 20 | user_20 | 303700 | 5400 | 9356.25 | 1.3 | 8652.2 | 1.1 | (empty) | (empty) | (empty) | y | y | event_1786 amount from image_05 Airtel bill: Amount due till 06-Feb-2026 = 704.05 |
| 21 | user_21 | 1574.4 | 1543.35 | 1574.4 | 2.0 | 1574.4 | 2.0 | 2026-04-15 | 2026-04-03 | 2026-04-03 | - | - |  |
| 22 | user_22 | 731.5 | 475.46 | 467.83 | 1.0 | 467.83 | 1.0 | 2025-01-15 | 2025-01-15 | 2025-01-15 | y | - |  |
| 23 | user_23 | 38016 | 9152 | 8418.07 | 1.9 | 8418.07 | 1.9 | 2025-07-15 | 2025-07-15 | 2025-07-15 | y | - |  |
| 24 | user_24 | 109600 | 13420 | 13352.7 | 0.1 | 13352.7 | 0.1 | (empty) | (empty) | (empty) | y | - |  |
| 25 | user_25 | 6.0496e+07 | 1.425e+06 | 497834 | 1.5 | 497834 | 1.5 | (empty) | (empty) | (empty) | - | - |  |

## Summary

| metric | A (raw ledger) | B (raw + evidence) |
|---|---|---|
| median error (% of requested) | 2.2 | 2.1 |
| mean error (% of requested) | 13.4 | 8.4 |
| samples within 5% of GT amount_safe_to_pay | 16/25 | 19/25 |
| samples within 1% of GT amount_safe_to_pay | 5/25 | 6/25 |
| earliest_date exact match | 17/25 | 18/25 |

Users where B actually applied evidence: 11. Their mean error A → B: 13.9% → 2.5%. Users with no evidence to apply: mean error 13.0% (unchanged by construction) — this residual is the recurrence-model error the deterministic core must close in Phase 3.

## Findings

1. **Evidence is the lever.** With the simulator held constant, the 11 samples that carry image or message evidence move from 13.9% to 2.5% mean error. user_10 (gig payouts flagged 'pending, not withdrawable' by message_07) goes from 95% to 5%; user_08 (salary amended by message_06) from 29% to 0.1%. No decision logic changed.
2. **The residual is convention, not judgment.** The remaining large misses have deterministic explanations visible in the ledger: user_01 (76%) has one prorated salary plus a scheduled 'Next confirmed salary' — ground truth projects that scheduled amount monthly, the naive model did not; user_13 (54%) has a second household income that missed its expected February occurrence — ground truth treats the stream as ended; user_04 (17%) is a variable-spending amount rule (mean vs a conservative statistic). Each is a rule to fit on the 25 samples in code.
3. **Anchor insight (the README narrative):** *Buy-or-Wait is a pure function of a truthful ledger. The only place a model is needed is to make the ledger true — read the amount off the receipt, apply the payroll letter, drop the unconfirmed payout — and every one of those facts arrives through an untrusted channel. So the architecture is: model at the evidence boundary with a schema and a fence, deterministic simulation and ranking everywhere after it.*
4. **Consequence for Phase 3:** recurrence inference gets three explicit rules from this experiment (scheduled salary defines the forward stream; a missed expected occurrence ends a stream; variable-spending amount statistic is a fitted tunable), each unit-tested on a synthetic ledger and validated on the samples with before/after eval reports.

## Per-sample notes (variant B)

- **request_01** (user_01): no notes
- **request_02** (user_02): credit:Payroll credit: amount override 33345000.00->42750000.00 from 2025-08-15 (message_01: gaji bulanan naik menjadi IDR 42750000 mulai 2025-08-15)
- **request_03** (user_03): event_253 amount from image_01 payslip Aug-2019 net pay IDR 4,365,000
- **request_04** (user_04): no notes
- **request_05** (user_05): income stopped: ledger: last salary described 'Final employer payroll' (no message)
- **request_06** (user_06): no notes
- **request_07** (user_07): no notes
- **request_08** (user_08): credit:Payroll credit: amount override 782.57->1422.85 from 2025-02-15 (message_06: next salary is reduced to EUR 1422.85 (last settled was 782.57))
- **request_09** (user_09): no notes
- **request_10** (user_10): income stopped: message_07: QuickCrew payout still pending; balance not withdrawable until completed -> weekly gig income unconfirmed
- **request_11** (user_11): credit:Base salary: amount override 23256000.00->38760000.00 from 2025-05-15 (message_08: gaji pokok yang dikonfirmasi IDR 38760000; komisi belum disetujui)
- **request_12** (user_12): income stopped: message_09: seasonal contract has ended; no off-season income confirmed
- **request_13** (user_13): no notes
- **request_14** (user_14): credit:Payroll before leave: stream considered ended (last 2025-04-15, cadence 31d)
- **request_15** (user_15): no notes
- **request_16** (user_16): event_1442 amount from image_02 rent receipt: Balance Due 1,00,000.00
- **request_17** (user_17): event_1545 amount from image_03 nuts & spices bill: Net Amount 41272.00
- **request_18** (user_18): no notes
- **request_19** (user_19): event_1700 amount from image_04 grocery delivery: Item Bill 2854.00, image CROPPED below (fees unknown) -> partial
- **request_20** (user_20): event_1785 pending credit ignored; event_1786 amount from image_05 Airtel bill: Amount due till 06-Feb-2026 = 704.05
- **request_21** (user_21): no notes
- **request_22** (user_22): no notes
- **request_23** (user_23): no notes
- **request_24** (user_24): no notes
- **request_25** (user_25): no notes
