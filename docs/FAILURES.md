# FAILURES.md

Numbered, append-only record of every failure hit while building the submission.
Each entry: exact incorrect behavior → root cause → targeted fix → measured effect.

## F-001 — Brief fact "7 users with pending possible-duplicate charges" was wrong (2026-09-12 22:20 IST)

- Incorrect behavior: the Phase 0 data-audit check "7 pending 'Possible duplicate card charge' rows" FAILED.
- Root cause: the survey summary (and therefore the brief, §1b) overstated the count. The ledger has 6 such rows: users 138, 156, 198, 210, 234, 252. The number was typed from memory instead of computed.
- Fix: check now asserts 6 and prints the user list; the brief fact is corrected in analysis/reports/data_audit.md and CONTRACT.md.
- Measured effect: check passes; the reserve-the-pending-duplicate rule is unchanged (it is per-row, not per-count).

## F-002 — Cancelled-authorization check too narrow (2026-09-12 22:20 IST)

- Incorrect behavior: check "every cancelled authorization is the TARGET of a settled purchase with the same amount" FAILED.
- Root cause: two encodings exist. 8 rows described "Card authorization" are cancelled AND superseded by a linked settled "Settled card purchase" of the same amount (a dedupe case). 14 rows described "Cancelled card/booking/merchant authorization" stand alone with no counterpart. The check assumed only the first shape.
- Fix: check now asserts (a) cancelled rows never carry `linked_event_id` themselves, (b) every superseded one has an exact-amount settled successor, and reports both counts. Ledger rule: cancelled rows are dropped from cash flow in both shapes; the successor settled purchase is counted once.
- Measured effect: check passes with detail "8 superseded, 14 standalone".

## F-003 — Amount-in-text regex swallowed the trailing sentence period (2026-09-12 22:20 IST)

- Incorrect behavior: 58 requests flagged as "requested_amount not found in request_text".
- Root cause: pattern `[\d.,]+` captured `1,302.40.` (sentence-final period), which then had two dots and was mis-routed to the Indonesian thousands-dot branch.
- Fix: capture must end on a digit (`[\d.,]*\d`); route by "contains comma" (English) vs "more than one dot" (Indonesian) vs plain.
- Measured effect: 0 mismatches across 250 requests (request_43's `43.339.000` normalises correctly).

## F-004 — Heuristic message buckets missed the Indonesian arrears template (2026-09-12 22:20 IST)

- Incorrect behavior: message_02 unmatched by the exploratory intent buckets.
- Root cause: Indonesian phrasing "penyesuaian satu kali" (one-time adjustment) was not in the `arrears_one_time` pattern.
- Fix: pattern extended. (These buckets are exploratory only; the runtime classifier is the model with a schema, cross-checked in code.)
- Measured effect: 215/215 messages matched.

## F-005 — Convention audit crashed parsing installment plan amount (2026-09-12 22:20 IST)

- Incorrect behavior: `ValueError: could not convert string to float: '15952906.67|2025-09-07'`.
- Root cause: split on `:` before splitting on `|`, so the second token contained the next entry's date.
- Fix: split the plan on `|` first, then `:`.
- Measured effect: script runs to completion; results recorded in analysis/reports/convention_audit.md.

## F-006 — Naive simulator projected every monthly item on the 28th (2026-09-12 22:55 IST)

- Incorrect behavior: variant A/B curves showed one lumped flow on the 28th of each month (user_01: −7,237 on 2024-03-28; user_19: +49,397 on 2024-09-28) instead of rent on the 2nd/4th, salary on the 15th, etc. amount_safe_to_pay errors of 76% (user_01) and 27% (user_19).
- Root cause: `add_months()` used `range(day, 27, -1)`, which is empty for any day ≤ 27, so the fallback `date(y, m, 28)` was always returned.
- Fix: keep the target day; only step down for months shorter than the target day.
- Measured effect: see analysis/reports/anchor_experiment.md rerun figures (recorded in the per-turn log entry).

## F-007 — Recurring items due ON request_date were skipped (2026-09-12 22:55 IST)

- Incorrect behavior: user_19's rent (settled monthly on the 4th; request_date 2024-09-04) was never projected, overstating amount_safe_to_pay.
- Root cause: projection loop skipped `nxt <= request_date`; settled history ends the day before the request, so an item due on request_date is not yet in `current_available_balance`.
- Fix: skip only `nxt < request_date`. Design rule carried into CONTRACT.md: the forecast window is [request_date, request_date+90] inclusive at both ends, and any projected or scheduled flow dated request_date is applied before the payment is tested.
- Measured effect: recorded with F-006.

## F-008 — Scorer crashed copying predictions onto themselves (2026-09-12 23:45 IST)

- Incorrect behavior: `shutil.SameFileError` when `--predictions analysis/reports/predictions/baseline.csv --tag baseline` (source and archive path coincide).
- Root cause: unconditional copy to `analysis/reports/predictions/<tag>.csv`.
- Fix: compare resolved paths and skip the copy when identical.
- Measured effect: baseline scoring completes; `analysis/reports/eval_baseline.json` written and pinned.

## F-009 — Checkpoint fixture failed to import the scorer module (2026-09-12 23:45 IST)

- Incorrect behavior: 12 test errors, `AttributeError: 'NoneType' object has no attribute '__dict__'` inside `dataclasses` when the test loaded `score.py` via `importlib.util.spec_from_file_location`.
- Root cause: the module was executed without being registered in `sys.modules`, so `@dataclass` could not resolve the module namespace for the `Scored` class annotations.
- Fix: moved `build_contexts` into the package as `buyorwait.io_dataset.build_row_contexts` (the Phase 5 validator needs it for all 250 requests anyway); the scorer and tests import it normally. No `sys.path` hacks.
- Measured effect: 30/30 tests pass.

## F-010 — Shell chain committed before lint was green (2026-09-12 23:55 IST)

- Incorrect behavior: commit `c692b8c` was created while `ruff check` still reported 5 errors and before `analysis/reports/phase2_report.md` existed.
- Root cause: the `&&` chain ended at the report heredoc; `git commit` was on a new line and ran unconditionally.
- Fix: fixed the 5 lint items (one long f-string in score.py, three unused locals and one unused loop variable in the audit tooling), re-ran ruff/mypy/pytest/audits/scorer to green, then amended the commit (unpushed) to include the report.
- Measured effect: single Phase 2 commit with all checks green.

## F-016 — Commit ran on red a second time (2026-09-13 02:10 IST)

- Incorrect behavior: commit 6f14086 was created while `ruff check` reported 6 import-order/unused-name errors (repeat of F-010).
- Root cause: the `git commit` line was outside the `&&` chain again.
- Fix: the verification chain now ends with the commit itself (`ruff … && mypy && pytest … && git commit`), so nothing commits unless every check is green; the offending commit was amended.
- Measured effect: amended commit is lint/type/test green (60 passed).

## F-017 — Two monthly incomes mis-detected as one weekly gig stream (2026-09-13 03:05 IST)

- Incorrect behavior: synthetic ledger with salaries on the 15th and 20th produced a single `income:weekly` stream (ended), so both real streams vanished.
- Root cause: weekly detection used the median of consecutive gaps; alternating 5/25-day gaps have median 5.
- Fix: `_mostly_weekly` requires at least 80% of gaps in 5–9 days. Test `test_core_applies_confirmed_credit_and_salary_cap` covers the two-income case; user_13 (15th + 20th) and user_42 (15th + 20th) are the real-data instances.
- Measured effect: 75/75 tests pass; sample metrics unchanged (pin holds).

## F-018 — `mypy | tail -1` hid mypy's exit code (2026-09-13 02:20 IST)

- Incorrect behavior: the Phase 3 commit chain reported green while mypy had 4 errors (`Decimal * None`, two untyped signatures, a tuple type).
- Root cause: piping mypy into `tail` made the pipeline's exit status that of `tail`.
- Fix: mypy runs unpiped in every chain; the 4 errors were fixed (None guard on the multiplier, explicit `Decimal`/`date` annotations in reconcile, a typed `tuple[Payment, ...]` for the partial plan) and the commit amended.
- Measured effect: `mypy --strict` clean on 19 source files.

## F-019 — Transcript timestamps ran ahead of the clock (2026-09-12T23:12:10+05:30)

- Incorrect behavior: log.txt entries stamped 2026-09-13T00:05 and 03:10 and FAILURES entries F-008..F-018 carry estimated times up to ~4 hours later than the wall clock; the shell clock at the time of this note reads 2026-09-12T23:12:10+05:30.
- Root cause: timestamps were estimated from perceived elapsed work instead of read from `date`.
- Fix: every later log/FAILURES entry takes its timestamp from `date` in the same shell command; earlier entries are left as written (append-only log) with this correction recorded in both files.
- Measured effect: ordering of entries is unaffected; only absolute times before this note are overstated.

## F-020 — API rejected strict tool schemas as too complex (2026-09-12T23:26:46+05:30)

- Incorrect behavior: first live call failed with `400 invalid_request_error: Schema is too complex.` (request_id req_011CeyyaFC5fHzB4fFPnT9uK).
- Root cause: `strict: true` on the record tools; the message schema has a 32-value intent enum, nullable unions and regex patterns, which exceeds the strict-mode schema limits.
- Fix: removed `strict` from the tool definitions. Enforcement is unchanged: every final tool payload is validated by `buyorwait.evidence.schema.validate` and retried with the error list (≤ 2).
- Measured effect: recorded after the smoke test below.

## F-021 — Piped pytest let a failing test through to a commit, third occurrence of the pattern (2026-09-12T23:51:42+05:30)

- Incorrect behavior: commit dae353c was created with `test_budget_stops_cleanly` failing (old call signature passing an int to `Budget.charge`).
- Root cause: `python3 -m pytest -q 2>&1 | tail -1 && git commit` — the pipeline's status is `tail`'s (same class as F-010, F-016, F-018).
- Fix: verification chains run `pytest -q >/dev/null` unpiped before `git commit`; the test was updated to the `ModelResponse`-based signature plus a new dollar-cap test; commit amended (9343b84).
- Measured effect: 76/76 green before the amended commit.

## F-022 — Reconciliation raised on a wait plan with zero safe amount (2026-09-13T00:18:17+05:30)

- Incorrect behavior: decision pass stopped at request_123 with `InvariantError: I-4: wait needs 0 < safe < requested`.
- Root cause: I-4 was derived from the 25 samples, where every `wait` row happens to have a positive amount_safe_to_pay. The statement requires `0 < amount_safe_to_pay` only for `partial_payment`; `affordable_later` needs only that the full amount becomes safe later. request_123 has nothing safe today and a safe full payment after its next payday.
- Fix: I-4 relaxed to `0 ≤ safe < A` in contract.py, CONTRACT.md and the convention audit; partial_payment keeps the strict `0 < safe`. No override was applied — the reconciler raises rather than fixes, and the contract was corrected instead.
- Measured effect: recorded below with the full decision pass.
