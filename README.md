# Personal Finance Agent

An AI-powered expense affordability agent. For every request — "can I afford this laptop?" — it decides whether the user should **pay in full**, **pay partially**, **use installments**, **wait**, or **not proceed**, along with the maximum amount safe to pay today, a dated payment plan, the earliest safe date for full payment, and any flexible expenses that must be stopped or reduced. Decisions are personalized per user from real transaction history, and a 90-day balance forecast against the user's own minimum-balance floor is the safety authority.

Originally built solo under a 24-hour hackathon constraint, with a fully deterministic, zero-cost reproduction path.

## Why it's interesting

- **The model never decides money.** Every output column is a pure function of a truthful ledger — the hard part is making the ledger true, because 16 event amounts live only inside receipt images and 215 messages amend salaries, move paydays, end contracts and raise rent. So the model sits at exactly one boundary, the evidence boundary, and everything downstream is deterministic, unit-tested code. The Phase-0 experiment that fixed this architecture: applying evidence to a frozen naive simulator cut mean amount error on evidence-bearing cases from 13.9% to 2.5% (`analysis/reports/anchor_experiment.md`).
- **The model corrected the human.** The 25 solved samples were first hand-encoded so the deterministic core could be fitted model-free. When the same evidence was later re-resolved by the model, it disagreed once — reading a message as "commission unapproved, no raise" where the hand encoding had applied a salary raise — and the ground truth sided with the model (`analysis/reports/evidence_comparison.md`).
- **Prompt-injection defense in depth.** Message and image content is untrusted: it is fenced with defanged delimiters before the model sees it, any imperative aimed at the reader is recorded as a verbatim matched phrase rather than a boolean, and an independent code-side scan gates behavior. The dataset's two prize-fee scam messages — one English, one Indonesian — were both caught and produced no ledger amendment.
- **Schema enforcement and a bounded tool loop.** The model may call `inspect_image` and read tools for at most 4 iterations and must finish through a strict-schema record tool or `declare_unresolvable`. Failures are classified before retry (parse errors retried ≤2 with the error list, transport errors with backoff, refusals never), and structured fields pass foreign-key and dated-currency re-checks in code after the model.
- **Deterministic plan selection with runtime-asserted invariants.** Eligibility gates are conjunction-only from the user's accepted payment methods, candidate plans are ranked by one six-rule tuple (deadline, no spending changes, total cost, start date, payment count, option id), and a final reconciliation stage derives all eight output columns from a single rationale object — a contract violation raises instead of being silently patched.
- **Reproducible by construction.** Every model response is cached, content-addressed by hash of the rendered prompt, tool schemas and model id, so any change to those is a new key rather than a silent replay. The default run reproduces `output.csv` **bit-identically with no API key and zero API calls**, and the packaging step proves it from a fresh unpack with a double-run diff.

## Quick start

```bash
python3 -m pip install -r requirements.txt   # offline path needs only the standard library

python3 code/main.py --model-evidence --offline --out /tmp/output.csv   # keyless, zero API calls via committed caches
cmp /tmp/output.csv output.csv                                          # bit-identical reproduction
python3 code/validate_output.py output.csv                              # contract check (bounds, vocab, plan arithmetic)

python3 code/main.py --samples --model-evidence --offline --tag demo    # 25 solved samples → analysis/reports/predictions/demo.csv
python3 code/evaluation/score.py --predictions analysis/reports/predictions/demo.csv --tag demo   # per-column metrics vs pinned run + baseline

python3 -m pytest -q                                                    # 76 offline tests, all model calls mocked
```

An `ANTHROPIC_API_KEY` (env or `.env`) is only needed to regenerate the model caches from scratch; spend is then capped per call, per run, per token and in USD, with a pre-flight check before every paid call. See `docs/CONTRACT.md` for the decision contract and design assumptions.

## How it works

```
context build (per request, no model)
  profile ▸ events ▸ payment options ▸ dated FX rates
        │
        ▼
evidence resolution (model, cached, bounded ≤4-iteration tool loop)
  blank-amount receipts ─► amount + evidence      messages ─► cancel / amend / delay /
  line + partial/confidence flags                 confirm / noise / scam + typed fields
        │  fenced untrusted text ▸ strict schema ▸ error taxonomy ▸ FK re-checks
        ▼
ledger normalisation (deterministic)
  status table ▸ dedupe ▸ linked-event chains ▸ dated currency conversion
        │
        ▼
recurrence inference ──► 90-day daily simulation ──► safe-amount solver
  income by day-of-month, moved paydays,   balance trough vs minimum floor,
  ended streams, never bonuses             earliest safe full-payment date
        │
        ▼
plan selection (deterministic authority)
  eligibility gates ▸ full / partial / installment / wait candidates
  ▸ six-rule ranking ▸ bounded spending-change search
        │
        ▼
reconciliation — one rationale object → all 8 columns,
invariants raise, explanation generated last ──► output.csv
```

## Repository layout

```text
code/            entry point, output validator, per-column scorer, naive baseline, packaging
src/buyorwait/   the package: ledger, recurrence, simulate, solver, plans, reconcile, evidence/
prompts/         every prompt and tool description the model sees
data/            333 content-addressed cached model responses + sample evidence
docs/            design artifacts: decision contract, failure log (22 worked entries)
analysis/        reports from the build: data and convention audits, threshold sweep, eval runs, perception reviews
tests/           76 offline tests: contract, deterministic core, model layer
dataset/         provided inputs (250 requests, 275 profiles, 25k events, receipts, messages)
output.csv       final predictions (250 rows, contract-validated)
```

## Evaluation

`code/evaluation/score.py` scores the 25 solved samples per column — safe-amount accuracy within tolerance, status, method-plus-plan, earliest date, spending changes, contract validity — and every run prints the full table diffed against a pinned run and a committed naive baseline, so improvements are always before/after evidence rather than a single best-looking result. A model-off ablation isolates what the evidence layer is worth, and the final composite improved from 52.7% (baseline) to 78.7% with no column regressing when model-resolved evidence replaced the hand-encoded file.

**A note on honesty:** the decision pass and the cache replay are deterministic byte for byte — two consecutive full runs produce an identical `output.csv`, verified by hash. A cold re-run of perception with an empty cache is not: the model could word an evidence string differently or pick a different intent for a borderline message. The structured fields that reach the ledger are constrained by schema and code-side cross-checks, so a re-run would most likely produce the same amendments, but that is a likelihood, not a guarantee, and this README does not claim otherwise.
