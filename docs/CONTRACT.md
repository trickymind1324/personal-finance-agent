# CONTRACT.md — Buy or Wait? decision contract

Plan of record for the runtime. Every rule here is either (a) quoted from the task statement and provided rules, (b) derived from the 25 solved rows in `dataset/sample_requests.csv` by the Phase 0 convention audit (260 checks, all passing, see `analysis/reports/convention_audit.md`), or (c) an explicit convention decision, marked **[CONVENTION]** and listed in §10 as a tunable to be fitted on the samples in Phase 3 with before/after eval reports. Anything marked **[ASSERT]** is a runtime invariant that raises; nothing warns.

Vocabulary: `R` = request row, `U` = profile row, `T0` = `R.request_date`, `T90` = `T0 + 90 days`, `D` = `R.desired_completion_date`, `A` = `R.requested_amount`, `M` = `U.minimum_balance_to_keep`, `B0` = `U.current_available_balance`.

---

## 1. Output schema and per-column formatting

`output.csv`, UTF-8, header exactly:

```
request_id,amount_safe_to_pay,affordability_status,recommended_payment_method,payment_plan,earliest_date_for_full_payment,spending_changes_needed,decision_explanation
```

One row per `request_id` in `dataset/requests.csv`, same order as the template. **[ASSERT]** row count 250, ids identical and in template order.

| column | type | formatting rule (derived) | source |
|---|---|---|---|
| `request_id` | str | verbatim | template |
| `amount_safe_to_pay` | number | `round(x, 2)` printed as the **shortest** repr: `603.3`, `17229139.2`, `87170.56`, `873000`. Never padded. | conv. audit §4 |
| `affordability_status` | enum | `affordable_now` \| `affordable_with_plan` \| `affordable_later` \| `not_affordable` | statement |
| `recommended_payment_method` | enum | `full_payment` \| `partial_payment` \| `installments` \| `wait` \| `not_recommended` | statement |
| `payment_plan` | str | `YYYY-MM-DD:amount` entries joined by `\|`, chronological, or `none`. Amount formatting per method: **full_payment / wait** → `A` as integer if integral else padded to 2 dp (`620.4`→`620.40`); **installments** → the option's `payment_amount` string verbatim; **partial_payment** → first = `amount_safe_to_pay` string, second = `A − safe` shortest repr. | conv. audit §4 |
| `earliest_date_for_full_payment` | date or empty | ISO date; `= T0` for `affordable_now`; **empty** for `not_affordable`; populated for every other status. | conv. audit §3 |
| `spending_changes_needed` | str | `none`, or up to 3 of `stop:<event_id>` / `reduce_to:<event_id>:<amount>` joined by `\|`; `reduce_to` amount integer if integral else 2 dp padded (`23.50`). | conv. audit §4 |
| `decision_explanation` | str | one of the templates in §7, fully determined by the rationale object. | conv. audit §5 |

Explanation-only number format: thousands separators, 2 dp iff non-integral (`ZAR 25,256`, `EUR 620.40`, `IDR 15,952,906.67`). Prose dates `D Month YYYY`, no leading zero (`15 June 2024`). Currency code = `U.home_currency`.

## 2. Invariants (runtime-asserted in `validate_output.py` and at each producing function)

- **I-1** `0 ≤ amount_safe_to_pay ≤ A`.
- **I-2** `affordable_now` ⇔ (`amount_safe_to_pay == A` ∧ `earliest == T0` ∧ method `full_payment` ∧ `full_payment ∈ U.methods` ∧ changes `none`).
- **I-3** `not_affordable` ⇔ method `not_recommended` ⇔ plan `none` ⇔ earliest empty; changes `none`.
- **I-4** `affordable_later` ⇔ method `wait`; plan is exactly one entry `earliest:A`; `T0 < earliest ≤ T90`; `full_payment ∈ U.methods`; changes `none`; `0 ≤ safe < A` (a user with nothing safe today may still be able to pay in full after a payday — request_123 on the evaluation set; the statement puts a `safe > 0` requirement on `partial_payment` only, F-022).
- **I-5** `partial_payment` ⇒ status `affordable_with_plan`; `R.allows_partial_payment == true`; `partial_payment ∈ U.methods`; `0 < safe < A`; plan has exactly two entries `T0:safe | earliest:(A−safe)`; the two amounts sum to `A` exactly (decimal arithmetic); `earliest ≤ D`.
- **I-6** `installments` ⇒ status `affordable_with_plan`; `installments ∈ U.methods`; plan equals the schedule of exactly one supplied option for `R`: dates `first_payment_date + k·payment_frequency_days`, `k = 0..n−1`, amounts = option `payment_amount` string; `n ≤ U.max_installment_months`; changes `none`.
- **I-7** `affordable_with_plan` + `full_payment` ⇒ changes ≠ `none`; plan `T0:A`; `safe < A`.
- **I-8** spending changes: ≤ 3 actions; every event id exists, belongs to `U`, is the **latest settled occurrence** of a recurring stream; `stop` only on `flexibility ∈ {stoppable, reducible_or_stoppable}` in a category ∈ `U.expense_categories_user_is_willing_to_stop`; `reduce_to` only on `flexibility ∈ {reducible, reducible_or_stoppable}` in a category ∈ `U.expense_categories_user_is_willing_to_reduce`, new amount `== minimum_allowed_amount` **[CONVENTION C-6]** and `< current amount`; no event appears twice; no category in `U.expense_categories_to_protect`.
- **I-9** Every plan payment date is within `[T0, T90]`... except installment options may extend beyond `T90`; then **the simulation still applies every payment inside the window** and the plan's completion-by-deadline flag is computed from the true last date.
- **I-10** The recommended plan passes the safety check (§5) with the same simulator that produced `amount_safe_to_pay` — re-run, not trusted.
- **I-11** Every foreign-currency conversion used a rate row whose `(rate_date, from, to)` exists exactly; missing rate ⇒ raise (`MissingRateError`), never interpolate.
- **I-12** Every event with blank `amount` has a resolved amount from the evidence layer with `partial=false`, or is treated by the safer-reading rule (§6.4) with the decision recorded in the rationale; never silently zero.
- **I-13** Determinism: two consecutive full runs from the committed cache produce byte-identical `output.csv`.
- **I-14** The explanation cites only events/dates/amounts present in the rationale object (generated after all overrides).

## 3. Eligibility gates (conjunction-only, one-directional)

```
eligible_full      = "full_payment" in U.methods
eligible_partial   = "partial_payment" in U.methods and R.allows_partial_payment
eligible_install   = "installments" in U.methods            # cap applies per option: n ≤ U.max_installment_months
eligible_wait      = eligible_full                           # wait is deferred full payment
```

`max_installment_months` is present iff `installments` is in the methods list (verified on all 275 profiles, `analysis/reports/data_audit.md`), so it is a cap, never a gate. A gate can only remove candidates; nothing downstream re-adds one. `not_recommended` is the fallback when the candidate set is empty.

## 4. Pure-function specs

### 4.1 Plan ranking

```python
def rank_key(plan: Plan, R: Request) -> tuple:
    return (
        0 if plan.completes_by(R.desired_completion_date) else 1,   # rule 1
        len(plan.spending_changes),                                # rule 2 (0 preferred)  [CONVENTION C-7: count, not bool]
        plan.total_paid,                                           # rule 3 (Decimal)
        plan.first_payment_date,                                   # rule 4 (earlier first)
        plan.n_payments,                                           # rule 5 (fewer)
        plan.payment_option_id or "",                              # rule 6 (lowest id; '' sorts first for non-option plans)
    )
```

Chosen plan = `min(candidates, key=rank_key)`. Sample evidence: rule 1 beats rule 2 (samples 06, 11, 21 accept a spending change to meet the deadline); `earliest` is capacity-only and ignores methods (sample 12).

### 4.2 Conflict resolution over evidence

```python
def resolve(facts: list[Fact]) -> Fact:
    """facts describe the same slot (e.g. next salary amount). Returns the winner."""
    # 1. explicit cancellation / settlement / amendment beats everything
    # 2. newer record from the same source beats older (by sent_at / event_date)
    # 3. settled event beats estimate / forecast / message-implied value
    # 4. otherwise the financially safer value: lower income, higher/earlier expense, later income date
```

Each `Fact` carries `slot, value, source_kind ∈ {event_settled, event_scheduled, event_pending, message, image, inferred}, source_id, observed_at, explicit ∈ {cancel, settle, amend, confirm, none}`. Every resolution that reached step 4 is logged with the competing facts (transcript requirement).

## 5. Ledger → simulation semantics

### 5.1 Row admission (`normalize_ledger`)

| status / shape | cash-flow treatment |
|---|---|
| `settled`, `settlement_date ≤ T0` | already inside `B0`; used only for recurrence inference |
| `settled`, `settlement_date > T0` | does not occur in data (**[ASSERT]** no future settled rows) |
| `pending` debit | reserved on `max(settlement_date, T0)` |
| `pending` credit (refunds, gig payouts) | ignored |
| `scheduled` debit | applied on `settlement_date` |
| `scheduled` credit (`Next confirmed salary`) | applied on `settlement_date`; **defines the forward salary stream** (amount, day-of-month) **[CONVENTION C-1]** |
| `failed`, `cancelled` | dropped; the linked successor (`Scheduled bill payment retry`, `Settled card purchase`) is the one counted |
| `unrealized` / `non_cash` (`investment_valuation`) | dropped; never cash |
| `Possible duplicate card charge` (pending, linked to a settled original, dispute open) | reserved (safer reading) unless a message says the reversal was posted |
| refund credits (`settled`) with `settlement_date ≤ T0` | inside `B0`; excluded from income recurrence |
| `income` rows whose description matches `bonus|commission|arrears|prorated|final|windfall|prize|reimburse|one-time` | never projected forward |

Currency: `amount_home = amount × rate(settlement_date, currency → home_currency)`; projected occurrences use the rate on the projected date. **[ASSERT]** I-11.

Blank `amount`: resolved from the linked image via the evidence layer (§6).

### 5.2 Recurrence inference (`infer_streams`) — first-class module

Input: settled history within `HISTORY_DAYS` before `T0`. Output: list of `Stream(kind ∈ {income, expense}, key, cadence_days, next_dates, amount, flexibility, category, latest_event_id, minimum_allowed_amount)`.

- Grouping: expense rows in `VARIABLE_CATEGORIES = {groceries, transport, dining, shopping, entertainment}` group by category; all other rows group by `description`. Income rows group by description, except when a user has ≥ 4 distinct income descriptions (gig/freelance), which are clustered by cadence (weekly) or day-of-month cluster (semi-monthly).
- A group is recurring iff `n ≥ MIN_OCCURRENCES` and its median gap is in one of `{weekly 6–8, biweekly 13–15, monthly 26–35}` days; otherwise it is one-off and not projected.
- **Ended stream rule [CONVENTION C-2]:** if `last_occurrence + cadence + GRACE_DAYS < T0` (the expected occurrence was missed before the request), the stream is ended. Evidence: user_13's second household income (missed Feb) and user_12's seasonal contract.
- **Scheduled salary rule [C-1]:** a scheduled income row seeds/overrides the salary stream: its amount and day-of-month continue monthly after it. Evidence: user_01 (only a prorated first salary in history; GT projects 23,320 monthly).
- **Description-terminal rule:** `Final employer payroll` ends the stream (user_05). Message-driven ends/starts/amendments come from §6.
- Projected amount: fixed-flexibility groups use the latest amount; `VARIABLE_CATEGORIES` use `VARIABLE_AMOUNT_STAT ∈ {mean, p75, max}` **[CONVENTION C-3, fitted in Phase 3]**.
- Projected dates: monthly streams keep the day-of-month (clamped to month length); weekly/biweekly step from the last occurrence. Occurrences dated exactly `T0` are projected (not yet in `B0`).
- Suppression: a projected income within ±3 days of a scheduled income row is dropped (the scheduled row represents it).
- **Income clustering (fitted, Phase 3):** all income rows (after excluding non-recurring words) are clustered by day-of-month (±`CLUSTER_DAY_TOLERANCE`) regardless of description, because payroll descriptions change across leave or employer changes (user_14: "Payroll before leave" → "Payroll after returning from leave" is one stream). A same-day cluster with ≥ 2 occurrences is monthly even when months are skipped. A more recent singleton whose description equals a cluster's description is a moved payday and the cluster continues from it (user_07: 15th → 23rd). Weekly gig income is detected by gap (≥ `WEEKLY_INCOME_MIN_OCCURRENCES` payouts, median gap 5–9 days).
- **Variable cadence (fitted):** `VARIABLE_CADENCE=median_gap` — the dataset's templates are groceries every 7/10/14 days, transport every 5/7/14/21, dining every 7/14/21 (`analysis/reports/data_audit.md` §11 gap table); a band-only rule silently drops the 10- and 21-day streams.
- **Variable amount (fitted, C-3):** `median` of the history window (lowest mean error in `analysis/reports/eval_sweep_conventions.md`). Ground-truth troughs are whole numbers, so the generator forecasts round base amounts that history only approximates; exact-match on `amount_safe_to_pay` is therefore bounded (see Known Limitations).

### 5.3 Simulation (`simulate`)

Daily balance `bal[t]` for `t ∈ [T0, T90]` inclusive: `bal[T0] = B0 + flows[T0]`, `bal[t] = bal[t−1] + flows[t]`. A plan `P` (list of dated payments) is **safe** iff `min_t (bal[t] − paid_by(P, t)) ≥ M`.

- `amount_safe_to_pay = clamp(min_t bal[t] − M, 0, A)` with **no** spending changes and no plan applied (statement: "before optional spending changes").
- `earliest_date_for_full_payment = min { t ∈ [T0, T90] : min(bal[t], min_{t < s ≤ S} low[s]) − A ≥ M }`, else empty, where `S = D` under the fitted `SAFETY_SCAN_END=deadline` (a deferred payment is tested through the desired completion date; five of six `wait` samples have earliest == deadline and the fit lifts earliest_exact from 72% to 92%) and `S = T90` otherwise. A payment on day `t` is made after that day's credits (paying on payday is allowed). Computed on the no-changes ledger. `amount_safe_to_pay` always uses the full window, and so does `t = T0` in the earliest scan, so that `earliest == T0 ⇔ amount_safe_to_pay == A` (I-2) and a `full_payment` today is never chosen on a deadline-bounded check (F-015).
- Installment safety: apply each option payment on its date (payments after `T90` are outside the window and not tested; the plan still must "complete by deadline" for rule 1).

### 5.4 Spending-change search (`search_changes`)

Only entered when no change-free candidate completes by `D`. Candidates = recurring expense streams with `flexibility ≠ fixed` whose category is in the matching permit list and not in the protect list. Actions: `stop` removes all future occurrences; `reduce_to` sets future amounts to `minimum_allowed_amount`. Enumerate combinations of ≤ 3 actions (never two actions on one stream), smallest cardinality first, then **numeric ascending `event_id`** (`event_989` before `event_1816`; a generator iterates numerically) **[CONVENTION C-4, ruled 2026-09-12; logged as an assumption]**; first combination under which `full_payment` on `T0` is safe wins. Output lists the chosen changes in numeric event-id order. Result feeds the ranking as a `full_payment` plan with changes; explanation names each change.

## 6. Evidence layer (the only model-driven part)

### 6.1 Image extraction — `extract_amount(image_path, event_context) -> ImageExtraction`

Fields: `amount: Decimal | null`, `currency: str | null`, `amount_kind ∈ {total_paid, balance_due, amount_due, net_pay, item_subtotal}`, `document_date: date | null`, `partial: bool` (true when the visible document is cropped / the grand total is not visible), `confidence ∈ {high, medium, low}`, `evidence_text: str` (verbatim line the amount was read from), `embedded_instructions: list[str]` (matched phrases). Rule for "total vs rounded total": use the line labelled as the amount actually payable/paid (`Net Amount`, `Amount Received`, `Balance Due`, `Amount due till <date>`, `Net Pay`); if both a precise and a rounded figure are printed for the same line, take the **precise** one (**[CONVENTION C-5]**, justified: the ledger stores 2-dp amounts; rounding is the merchant's display). A `partial=true` extraction is handled by the safer-reading rule: for a debit, the visible subtotal is a **lower bound** — used as the amount and flagged in the rationale; for a credit, ignored. Concrete case: image_04 (event_1700, user_19): the 13 visible line items sum exactly to the visible `Item Bill 2854.00`; only the fee lines below the crop are missing, so 2854.00 is used, flagged partial. Materiality: event_1700 is **settled history** (2024-09-03, before the 2024-09-04 request), so it affects only the grocery recurrence statistic, never a forecast flow; residual error bound = the unseen delivery/handling fees, typically a few percent of one grocery order, diluted across ~26 grocery observations.

### 6.2 Message interpretation — `interpret_message(message, context) -> MessageInterpretation`

Fields: `classification ∈ {cancel, amend, delay, confirm, noise}`, `target ∈ {salary_stream, rent_stream, event:<id>, income_stream:<desc>, none}`, `new_amount`, `new_date`, `effective_from`, `multiplier`, `stream_ended: bool`, `income_confirmed: bool`, `language`, `embedded_instructions: list[str]`, `quote: str`. Untrusted text is fenced with a defanged delimiter; any imperative addressed to the reader ("pay the release charge", "bayar biaya") is reported as a matched phrase and classified `noise`. Code re-checks: FK of `target`, that `new_amount` is a number in the user's currency or a declared foreign currency, and applies §4.2 precedence against ledger rows.

### 6.3 Loop bounds

≤ 4 tool iterations per evidence item; JSON schema validated on every reply; error taxonomy classified before retry: `refusal` (no retry, safer reading), `parse_error` (retry with the validation message, ≤ 2), `timeout/transport` (retry with backoff, ≤ 2). All calls cached by `sha256(rendered_prompt + tool_schemas + model_id)` under `data/cache/`; offline mode reads only the cache and raises on a miss.

### 6.4 Safer-reading defaults (when evidence is absent or unresolvable)

Debit with unknown amount → reserve the visible lower bound if any, else the stream's latest amount if recurring, else raise `UnresolvedAmountError` (the run stops; a blank amount is never zero). Credit with unknown amount → ignore. Unconfirmed income → not projected.

## 7. Explanation templates (rationale → text; no model in the default path)

- `affordable_now`: `Pay {ccy} {A} today. This leaves at least {ccy} {M} available over the next 90 days.`
- `affordable_with_plan`/`full_payment`+changes: `{Change clause}, then pay {ccy} {A} today. This leaves at least {ccy} {M} available.` where the change clause is `Stop the {desc}` / `Reduce the {desc} to {ccy} {new}` / `Stop the {desc1} and reduce the {desc2} to {ccy} {new}` (description lower-cased).
- `installments`: `Use {n} installments of {ccy} {payment_amount}, starting {first date}. This leaves at least {ccy} {M} available.`
- `partial_payment`: `Pay {ccy} {safe} today and the remaining {ccy} {A−safe} on {earliest}. This completes the full request and keeps the {ccy} {M} minimum protected.`
- `wait`: `Pay {ccy} {A} in full on {earliest}. Paying earlier would take the balance below the {ccy} {M} minimum.`
- `not_recommended`: `Do not make this payment by {D}. None of the available options keeps the {ccy} {M} minimum protected.`

Optional model polish is off by default; if enabled it must preserve every number/date token (asserted) or the template text is used.

## 8. Module map (`src/buyorwait/`)

| module | function | signature | notes |
|---|---|---|---|
| `io_dataset.py` | `load_dataset` | `(root: Path) -> Dataset` | frozen dataclasses; all CSVs; Decimal amounts |
| `rates.py` | `convert` | `(amount: Decimal, ccy: str, home: str, on: date, table: RateTable) -> Decimal` | raises `MissingRateError` |
| `evidence/images.py` | `extract_amount` | `(image: Path, ctx: EventContext, client: ModelClient) -> ImageExtraction` | cached |
| `evidence/messages.py` | `interpret_message` | `(msg: Message, ctx: UserContext, client: ModelClient) -> MessageInterpretation` | cached |
| `evidence/resolver.py` | `resolve_evidence` | `(user: UserContext, extractions, interpretations) -> list[Amendment]` | applies §4.2; logs step-4 resolutions |
| `ledger.py` | `normalize_ledger` | `(user: Profile, events: list[Event], amendments: list[Amendment], rates: RateTable, T0: date) -> Ledger` | §5.1 |
| `recurrence.py` | `infer_streams` | `(ledger: Ledger, T0: date, cfg: RecurrenceConfig) -> list[Stream]` | §5.2 |
| `simulate.py` | `build_curve` | `(ledger: Ledger, streams: list[Stream], T0: date, changes: tuple[Change, ...] = ()) -> Curve` | daily balances |
| `simulate.py` | `is_safe` | `(curve: Curve, payments: list[Payment], M: Decimal) -> bool` | §5.3 |
| `solver.py` | `safe_amount_today` | `(curve: Curve, M: Decimal, A: Decimal) -> Decimal` | I-1 |
| `solver.py` | `earliest_full_date` | `(curve: Curve, M: Decimal, A: Decimal) -> date \| None` | §5.3 |
| `plans.py` | `enumerate_candidates` | `(R, U, options, curve, streams, safe, earliest) -> list[Plan]` | gates §3, §5.4 |
| `plans.py` | `rank_key` | `(plan: Plan, R: Request) -> tuple` | §4.1 |
| `reconcile.py` | `build_rationale` | `(R, U, chosen: Plan \| None, safe, earliest, evidence_used) -> Rationale` | single source of truth for all 8 columns |
| `explain.py` | `render_explanation` | `(rationale: Rationale) -> str` | §7 |
| `output.py` | `write_output` / `format_row` | `(rows: list[OutputRow], path: Path)` | §1 formatting |
| `validate_output.py` | `validate` | `(path: Path, dataset: Dataset) -> None` | raises on any I-* violation |
| `budget.py` | `Budget` | `max_calls_per_request, max_calls_total, max_tokens_total` | clean stop + checkpoint |
| `usage.py` | `UsageLedger` | per-call provider/model/in/out tokens → `evaluation/usage_report.md` | required deliverable |

Data flow per request: `load → evidence (model, cached) → resolve → normalize_ledger → infer_streams → build_curve → safe_amount_today / earliest_full_date → enumerate_candidates → rank → search_changes (if needed) → build_rationale → render_explanation → format_row`; then `validate` over the whole file.

## 9. Tunables (every constant: where defined, where read, what happens when hit, why)

| name | value | defined | read by | on hit | why |
|---|---|---|---|---|---|
| `HORIZON_DAYS` | 90 | `config.py` | simulate, solver | window end; earliest beyond it ⇒ empty | statement "90-Day Safety Check" |
| `HISTORY_DAYS` | 190 | `config.py` | recurrence | older settled rows ignored for inference | data: every user has exactly ~6 months |
| `MIN_OCCURRENCES` | 2 | `config.py` | recurrence | fewer ⇒ one-off, not projected | statement "detect recurrence only when history supports it"; 2 keeps new-job users (C-1 covers 1) |
| `GRACE_DAYS` | 5 | `config.py` | recurrence (C-2) | expected occurrence missed by more ⇒ stream ended | fits user_13 (missed by 15) without ending user_05 (not yet due) |
| `VARIABLE_AMOUNT_STAT` | mean (to fit) | `config.py` | recurrence (C-3) | changes projected variable spending | statement "forecast essential variable spending conservatively"; fitted on samples |
| `MAX_CHANGES` | 3 | `config.py` | search_changes | combos beyond ⇒ not enumerated | statement |
| `MAX_TOOL_ITERATIONS` | 4 | `config.py` | evidence loop | loop stops ⇒ safer reading | brief §6 |
| `MAX_CALLS_PER_REQUEST` / `MAX_CALLS_TOTAL` / `MAX_TOKENS_TOTAL` | 8 / 600 / 3,000,000 | `config.py` | budget | `BudgetExceededError` ⇒ cache is the checkpoint, run stops cleanly | cost first-class; 16 images + 215 messages ≈ 231 calls + retries |
| `MAX_COST_USD` | 8.00 | `config.py` | budget (paid calls only; pre-flight before each paid call) | `BudgetExceededError` before the call that could cross it | user directive 2026-09-13: a surprise can never drain the account |
| `ROUND_DP` | 2 | `config.py` | output | amounts rounded half-even before shortest repr | sample amounts have ≤ 2 dp |
| `VARIABLE_CADENCE` | median_gap | `config.py` | recurrence | band-only would drop 10/21-day streams | template gap table |
| `INTRADAY_ORDER` | net | `config.py` | simulate | debits_first tests a payday bill before the salary | fitted: net has lower error |
| `PROJECT_ON_T0` | include | `config.py` | recurrence R8 | exclude starts projections the day after T0 | fitted (user_19 rent on T0) |
| `SAFETY_SCAN_END` | deadline | `config.py` | solver/plans (deferred payments) | window would test through T90 | fitted (+20 pts earliest_exact) |
| `DISCRETIONARY_PROJECTION` | project | `config.py` | recurrence | skip drops dining/shopping/entertainment | GT reduces dining (sample 11) so it is projected |
| `WEEKLY_INCOME_MIN_OCCURRENCES` / `CLUSTER_DAY_TOLERANCE` | 6 / 3 | `config.py` | recurrence | gig stream not detected / paydays merged | data: 26 weekly payouts; 15th vs 20th must stay apart |

## 10. Conventions to fit in Phase 3 (each gets a before/after `analysis/reports/eval_<tag>.md`)

- **C-1** scheduled salary seeds the forward stream (user_01). 
- **C-2** missed-occurrence ends a stream, `GRACE_DAYS` (user_13, user_12).
- **C-3** variable-spending amount statistic (user_04, user_06).
- **C-4** spending-change combination order: fewest actions, then numeric event id (ruled; samples 06, 11, 21 give one data point each).
- **C-5** precise-over-rounded receipt figure.
- **C-6** `reduce_to` amount = `minimum_allowed_amount` (3/3 samples).
- **C-7** rule 2 counts actions (0 preferred); a single point (sample 21 uses two actions where presumably one was insufficient).
- **Ruled (2026-09-12):** a `wait` whose earliest date is after `D` but within `T90`, with no spending-change rescue → `wait` + `affordable_later` (the `affordable_later` definition has no deadline clause; `not_affordable` requires "cannot be completed safely within the forecast period"). Cited evidence that rule 1 dominates rule 2: samples 06, 11, 21 all have `earliest > D` and ground truth chose changes + `full_payment`. Recorded in README Known Limitations as untested by samples.
- **Open:** pending debit whose `settlement_date < T0` — reserved on `T0` (safer).

## 11. Corrections to the brief established in Phase 0

- Pending "Possible duplicate card charge" rows: **6** users (138, 156, 198, 210, 234, 252), not 7 (F-001).
- Cancelled rows have two shapes (8 superseded by a linked settled purchase, 14 standalone); both are dropped (F-002).
