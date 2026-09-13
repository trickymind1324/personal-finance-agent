"""Evidence → Amendments with code-side cross-checks and conflict precedence (CONTRACT.md §4.2, §6).

The model reports facts with a fixed intent catalogue; this module decides deterministically what each intent
does to the ledger. Every FK is re-checked, every foreign amount is converted with the dated rate (raise on a
missing rate), and every step-4 (safer-reading) resolution is written to the review report.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path

from buyorwait.config import Config
from buyorwait.evidence.client import (
    Budget,
    BudgetExceededError,
    CacheMissError,
    ModelParseError,
    UsageLedger,
    make_client,
)
from buyorwait.evidence.tasks import ImageExtraction, MessageInterpretation, extract_image, interpret_message
from buyorwait.models import Amendment, Dataset, Request
from buyorwait.rates import MissingRateError, convert

DEFAULT_MODEL = "claude-opus-5"


@dataclass
class ResolutionLog:
    images: list[ImageExtraction] = field(default_factory=list)
    messages: list[MessageInterpretation] = field(default_factory=list)
    amendments: dict[str, list[Amendment]] = field(default_factory=dict)
    safer_readings: list[str] = field(default_factory=list)
    injections: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


# ----------------------------------------------------------------------------- mapping rules
INCOME_ENDING_INTENTS = {"employment_ended", "seasonal_contract_ended"}
NOISE_INTENTS = {
    "bonus_unapproved",
    "commission_unapproved",
    "self_transfer",
    "refund_pending",
    "foreign_refund_pending",
    "foreign_charge_pending",
    "prize_pending",
    "prize_settled",
    "investment_value_moved",
    "investment_sale_settled",
    "reimbursement_not_salary",
    "duplicate_charge_dispute_open",
    "failed_debit_retry",
    "two_card_minimums",
    "receipt_reference",
    "scam_or_instruction",
    "other",
}


def _home_amount(
    amount: Decimal,
    currency: str | None,
    home: str,
    on: date | None,
    rates: dict[tuple[date, str, str], Decimal],
    log: ResolutionLog,
    who: str,
) -> Decimal | None:
    if not currency or currency == home:
        return amount
    if on is None:
        log.safer_readings.append(f"{who}: foreign amount {amount} {currency} without a date — ignored (safer)")
        return None
    try:
        return convert(amount, currency, home, on, rates)
    except MissingRateError as exc:
        log.safer_readings.append(f"{who}: {exc} — amendment dropped (safer: history-based projection kept)")
        return None


def message_to_amendments(
    m: MessageInterpretation,
    home: str,
    rates: dict[tuple[date, str, str], Decimal],
    user_event_ids: set[str],
    log: ResolutionLog,
) -> list[Amendment]:
    who = m.message_id
    if m.embedded_instructions:
        log.injections.append(f"{who}: {'; '.join(m.embedded_instructions)}")
    if m.outcome != "recorded":
        log.safer_readings.append(f"{who}: {m.outcome} — no amendment applied ({m.summary})")
        return []
    if m.intent == "scam_or_instruction" or m.classification == "noise" or m.intent in NOISE_INTENTS:
        return []
    if m.target_event_id and m.target_event_id not in user_event_ids:
        log.safer_readings.append(f"{who}: target {m.target_event_id} is not this user's event — amendment dropped")
        return []
    eff = m.effective_from or m.new_date
    out: list[Amendment] = []
    if m.intent in (
        "salary_increase",
        "salary_reduced",
        "salary_temporary_pay",
        "salary_resumes",
        "arrears_one_time",
        "foreign_salary_confirmed",
    ):
        if m.new_amount is None:
            log.safer_readings.append(f"{who}: {m.intent} without an amount — ignored")
            return []
        amt = _home_amount(m.new_amount, m.currency, home, eff, rates, log, who)
        if amt is None:
            return []
        out.append(
            Amendment("salary_amount", "salary", who, amount=amt, currency=home, effective_from=eff, note=m.intent)
        )
        if m.new_date and m.intent == "salary_resumes":
            out.append(Amendment("salary_date", "salary", who, effective_from=m.new_date, note=m.intent))
        return out
    if m.intent == "salary_date_moved":
        if m.new_date is None:
            log.safer_readings.append(f"{who}: salary_date_moved without a date — ignored")
            return []
        return [Amendment("salary_date", "salary", who, effective_from=m.new_date, note=m.intent)]
    if m.intent == "first_salary_confirmed":
        if m.new_amount is None or eff is None:
            log.safer_readings.append(f"{who}: first salary without amount/date — ignored")
            return []
        amt = _home_amount(m.new_amount, m.currency, home, eff, rates, log, who)
        if amt is None:
            return []
        return [
            Amendment("salary_amount", "salary", who, amount=amt, currency=home, effective_from=eff, note=m.intent),
            Amendment("new_income", "salary", who, amount=amt, currency=home, effective_from=eff, note=m.intent),
        ]
    if m.intent in INCOME_ENDING_INTENTS:
        return [Amendment("stream_ended", "all_income", who, note=m.intent)]
    if m.intent == "household_income_ended":
        # Safer reading (ruled 2026-09-12): keep only the primary stream; cap it at the stated remaining amount if lower.
        out = [
            Amendment(
                "stream_ended", "income:secondary", who, note="household income ended — secondary streams dropped"
            )
        ]
        if m.new_amount is not None:
            amt = _home_amount(m.new_amount, m.currency, home, eff, rates, log, who)
            if amt is not None:
                out.append(
                    Amendment("salary_cap", "salary", who, amount=amt, note="remaining confirmed monthly salary (cap)")
                )
        log.safer_readings.append(
            f"{who}: household income ended — primary stream kept, capped at the stated remaining amount (safer reading)"
        )
        return out
    if m.intent == "gig_payout_pending":
        log.safer_readings.append(
            f"{who}: platform payout pending / not withdrawable — gig income not projected (safer)"
        )
        return [Amendment("income_unconfirmed", "all_income", who, note=m.intent)]
    if m.intent == "invoice_confirmed":
        if m.new_amount is None or eff is None:
            log.safer_readings.append(f"{who}: invoice_confirmed without amount/date — ignored")
            return []
        amt = _home_amount(m.new_amount, m.currency, home, eff, rates, log, who)
        if amt is None:
            return []
        log.safer_readings.append(
            f"{who}: only the confirmed invoice is counted; other freelance income unconfirmed (safer)"
        )
        return [
            Amendment("income_unconfirmed", "all_income", who, note=m.intent),
            Amendment("confirmed_credit", "income", who, amount=amt, currency=home, effective_from=eff, note=m.intent),
        ]
    if m.intent == "rent_increase":
        factor = m.multiplier or Decimal("1.12")
        return [Amendment("expense_multiplier", "category:rent", who, factor=factor, note=m.intent)]
    if m.intent == "duplicate_charge_reversed" and m.target_event_id:
        return [Amendment("duplicate_reversed", m.target_event_id, who, note=m.intent)]
    log.safer_readings.append(f"{who}: intent {m.intent} has no ledger effect")
    return []


def image_to_amendment(x: ImageExtraction, event_currency: str, log: ResolutionLog) -> Amendment | None:
    if x.embedded_instructions:
        log.injections.append(f"{x.image_id}: {'; '.join(x.embedded_instructions)}")
    if x.outcome != "recorded" or x.amount is None:
        log.safer_readings.append(f"{x.image_id}: {x.outcome} — amount unresolved for {x.event_id} ({x.notes})")
        return None
    if x.currency and x.currency != event_currency:
        log.safer_readings.append(
            f"{x.image_id}: document currency {x.currency} != event currency {event_currency}; amount taken in event currency (flagged)"
        )
    if x.partial:
        log.safer_readings.append(f"{x.image_id}: partial document — {x.amount} used as a lower bound for {x.event_id}")
    return Amendment(
        "amount",
        x.event_id,
        x.image_id,
        amount=x.amount,
        currency=event_currency,
        partial=x.partial,
        note=f"{x.amount_kind}; {x.evidence_text}",
    )


# ----------------------------------------------------------------------------- driver
def resolve_all(
    dataset: Dataset,
    requests: list[Request],
    cfg: Config,
    root: Path,
    model: str = DEFAULT_MODEL,
    offline: bool = False,
    review_path: Path | None = None,
    usage_path: Path | None = None,
) -> dict[str, list[Amendment]]:
    client = make_client(root / "data" / "cache" / "model", offline)
    budget = Budget(cfg.MAX_CALLS_PER_REQUEST, cfg.MAX_CALLS_TOTAL, cfg.MAX_TOKENS_TOTAL, cfg.MAX_COST_USD)
    usage = UsageLedger()
    log = ResolutionLog()
    users = [r.user_id for r in requests]
    try:
        for uid in users:
            budget.start_request()
            profile = dataset.profiles[uid]
            events = dataset.events_by_user.get(uid, [])
            messages = dataset.messages_by_user.get(uid, [])
            ids = {e.event_id for e in events}
            amendments: list[Amendment] = []
            for e in events:
                link = dataset.images_by_event.get(e.event_id)
                if link is None or e.amount is not None:
                    continue
                path = root / "dataset" / "media" / "images" / f"{link.image_id}.png"
                if not path.exists():
                    log.skipped.append(f"{link.image_id}: file missing — {e.event_id} left unresolved")
                    continue
                x = extract_image(client, cfg, model, link, e, profile, path, events, messages, budget, usage)
                log.images.append(x)
                print(
                    f"[perception] {link.image_id} -> {e.event_id}: {x.outcome} amount={x.amount} {x.currency} "
                    f"partial={x.partial} calls={usage.calls}",
                    file=sys.stderr,
                )
                a = image_to_amendment(x, e.currency, log)
                if a is not None:
                    amendments.append(a)
            for m in messages:
                related = dataset.events_by_id.get(m.related_event_id) if m.related_event_id else None
                mi = interpret_message(client, cfg, model, m, profile, related, events, messages, budget, usage)
                log.messages.append(mi)
                print(
                    f"[perception] {m.message_id} ({uid}): {mi.classification}/{mi.intent} amount={mi.new_amount} calls={usage.calls}",
                    file=sys.stderr,
                )
                amendments.extend(message_to_amendments(mi, profile.home_currency, dataset.rates, ids, log))
            log.amendments[uid] = amendments
    except (BudgetExceededError, CacheMissError, ModelParseError) as exc:
        log.skipped.append(f"STOPPED: {type(exc).__name__}: {exc} (paid so far ${budget.paid_cost_usd:.2f})")
        raise
    finally:
        if review_path is not None:
            write_review(log, review_path)
        if usage_path is not None:
            usage_path.parent.mkdir(parents=True, exist_ok=True)
            usage_path.write_text(
                usage.report_markdown(len(requests), f"{model}, {'offline (cache replay)' if offline else 'live'}"),
                encoding="utf-8",
            )
    return log.amendments


def write_review(log: ResolutionLog, path: Path) -> None:
    n_users = sum(1 for v in log.amendments.values() if v)
    lines = [
        "# Perception review (Phase 4 checkpoint)",
        "",
        f"Images: {len(log.images)} · Messages: {len(log.messages)} · Users with amendments: {n_users}",
        "",
        "## Image extractions",
        "",
        "| image | event | amount | ccy | kind | partial | conf | outcome | iters | evidence text | notes |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for x in log.images:
        lines.append(
            f"| {x.image_id} | {x.event_id} | {x.amount} | {x.currency} | {x.amount_kind} | {x.partial} | {x.confidence} | "
            f"{x.outcome} | {x.iterations} | {x.evidence_text.replace('|', '/')} | {x.notes.replace('|', '/')} |"
        )
    lines += [
        "",
        "## Message interpretations",
        "",
        "| message | class | intent | target | amount | ccy | new_date | eff_from | mult | ended | income_conf | lang "
        "| outcome | iters | summary |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for m in log.messages:
        target = m.target + (":" + m.target_event_id if m.target_event_id else "")
        lines.append(
            f"| {m.message_id} | {m.classification} | {m.intent} | {target} | {m.new_amount} | {m.currency} | {m.new_date} | "
            f"{m.effective_from} | {m.multiplier} | {m.stream_ended} | {m.income_confirmed} | {m.language} | {m.outcome} | "
            f"{m.iterations} | {m.summary.replace('|', '/')} |"
        )
    lines += ["", "## Amendments applied (by user)", ""]
    for uid, ams in log.amendments.items():
        if ams:
            parts = []
            for a in ams:
                detail = a.target
                if a.amount is not None:
                    detail += f", {a.amount}"
                if a.effective_from:
                    detail += f", from {a.effective_from.isoformat()}"
                if a.factor:
                    detail += f", x{a.factor}"
                parts.append(f"{a.kind}({detail}) ← {a.source_id}")
            lines.append(f"- **{uid}**: " + "; ".join(parts))
    lines += ["", "## Embedded instructions detected (matched phrases)", ""] + (
        [f"- {i}" for i in log.injections] or ["- none"]
    )
    lines += ["", "## Safer-reading resolutions and dropped amendments", ""] + (
        [f"- {s}" for s in log.safer_readings] or ["- none"]
    )
    retried = [(x.image_id, x.retries) for x in log.images if x.retries]
    retried += [(m.message_id, m.retries) for m in log.messages if m.retries]
    lines += ["", "## Retries (items that did not pass on the first try)", ""]
    lines += [f"- {item}: " + " | ".join(r) for item, r in retried] or [
        "- none — every response passed schema validation on the first try"
    ]
    lines += ["", "## Skipped / stops", ""] + ([f"- {s}" for s in log.skipped] or ["- none"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    payload = {"images": [asdict(x) for x in log.images], "messages": [asdict(m) for m in log.messages]}
    path.with_suffix(".json").write_text(json.dumps(payload, indent=1, default=str), encoding="utf-8")
