# Evidence comparison: model-resolved vs hand-encoded (25 sample users)

Model amendments come from `analysis/reports/perception_review_samples.md` (claude-opus-5, cached). Hand-encoded amendments come from `data/evidence/manual_samples.json`. `same` = identical amendment set; otherwise every difference is listed with a verdict.

| user | model | manual | verdict |
|---|---|---|---|
| user_01 | — | same | same |
| user_02 | salary_amount·salary·42750000·from 2025-08-15 ← message_01 | same | same |
| user_03 | amount·event_253·4365000 ← image_01 | same | same |
| user_04 | — | same | same |
| user_05 | — | stream_ended·salary ← ledger:event_390 | see below |
| user_06 | salary_amount·salary·1037.52 ← message_04 | — | see below |
| user_07 | salary_date·salary·from 2024-09-23 ← message_05 | — | see below |
| user_08 | salary_amount·salary·1422.85 ← message_06 | salary_amount·salary·1422.85·from 2025-02-15 ← message_06 | see below |
| user_09 | — | same | same |
| user_10 | income_unconfirmed·all_income ← message_07 | same | same |
| user_11 | — | salary_amount·salary·38760000·from 2025-05-15 ← message_08 | see below |
| user_12 | stream_ended·all_income ← message_09 | same | same |
| user_13 | — | same | same |
| user_14 | salary_date·salary·from 2025-08-15 ← message_10 | — | see below |
| user_15 | salary_amount·salary·1661·from 2026-01-15 ← message_11 | — | see below |
| user_16 | amount·event_1442·100000 ← image_02; expense_multiplier·category:rent·x1.12 ← message_12 | same | same |
| user_17 | amount·event_1545·41272 ← image_03 | same | same |
| user_18 | — | same | same |
| user_19 | amount·event_1700·2854.0·partial ← image_04 | amount·event_1700·2854·partial ← image_04 | see below |
| user_20 | amount·event_1786·704.05 ← image_05 | same | same |
| user_21 | — | same | same |
| user_22 | — | same | same |
| user_23 | — | same | same |
| user_24 | — | same | same |
| user_25 | — | same | same |

Agreement: 17/25 users identical.

## Disagreements and verdicts

Eight users differ in the rendered amendment set; only one differs in ledger effect.

| user | difference | verdict |
|---|---|---|
| user_05 | manual: salary stream ended (hand-derived from the ledger's "Final employer payroll" row); model: no message exists for this user | Equivalent. The core's terminal-description rule (recurrence R6) ends the stream from the ledger alone; the manual entry was redundant. |
| user_06 | model adds `salary_amount 1037.52` (message_04, temporary pay) | Model right; effect identical because history already shows 1,037.52 for the last two paydays. |
| user_07 | model adds `salary_date 2024-09-23` (message_05) | Model right; effect identical because the last settled payday already moved to the 23rd and the moved-payday rule follows it. |
| user_08 | same amount 1,422.85; manual carried an `effective_from`, model did not | Equivalent: the amount applies to every projected payday either way. |
| user_11 | manual: `salary_amount 38,760,000` from message_08; model: intent `commission_unapproved`, no amendment | **Model right.** With the hand-encoded raise the sample decides `wait` (earliest 2025-05-15); with the model reading it reproduces the ground truth exactly: `affordable_with_plan` / `full_payment` with a dining reduction (`reduce_to:event_989:665950`). Ground truth therefore did not treat "gaji pokok yang dikonfirmasi IDR 38,760,000" as a raise over the settled 23,256,000 base. The manual entry was wrong. |
| user_14 | model adds `salary_date 2025-08-15` alongside the same `salary_amount 2717` | Equivalent: the date equals the payday the stream already projects. |
| user_15 | model adds `salary_amount 1661` alongside the same `new_income 1661 from 2026-01-15` | Equivalent: both carry 1,661 on the 15th. |
| user_19 | `2854.0` vs `2854` | Same value (Decimal rendering); both flagged partial, image_04 as required. |

Net effect on the sample evaluation (analysis/reports/eval_core_v5_model.md): no column regressed; status 88% → 92%, method+plan 88% → 92%, composite 77.3% → 78.7%. The only changed row is request_11, where the model-resolved evidence matches ground truth and the hand-encoded file did not.
