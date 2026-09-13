"""The two evidence tasks: image amount extraction and message interpretation (CONTRACT.md §6.1, §6.2).

Prompts live under prompts/ (externalized); this module renders them, runs the bounded loop and returns typed
results. No decision logic here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from buyorwait.config import Config
from buyorwait.evidence.client import JSON, Budget, ModelClient, ModelRequest, UsageLedger
from buyorwait.evidence.loop import (
    LoopResult,
    ToolContext,
    fence,
    find_embedded_instructions,
    run_loop,
    tool_definitions,
)
from buyorwait.evidence.schema import IMAGE_EXTRACTION_SCHEMA, MESSAGE_INTERPRETATION_SCHEMA
from buyorwait.models import Event, ImageLink, Message, Profile

PROMPTS = Path(__file__).resolve().parents[3] / "prompts"


def load_prompt(name: str) -> str:
    return (PROMPTS / name).read_text(encoding="utf-8").strip()


def event_fields(e: Event) -> dict[str, str]:
    return {
        "event_id": e.event_id,
        "event_type": e.event_type,
        "description": e.description,
        "category": e.category,
        "direction": e.direction,
        "amount": str(e.amount) if e.amount is not None else "(blank)",
        "currency": e.currency,
        "event_date": e.event_date.isoformat(),
        "settlement_date": e.settlement_date.isoformat() if e.settlement_date else "",
        "status": e.status,
        "flexibility": e.flexibility,
    }


@dataclass(frozen=True)
class ImageExtraction:
    image_id: str
    event_id: str
    amount: Decimal | None
    currency: str | None
    amount_kind: str
    document_date: date | None
    partial: bool
    confidence: str
    evidence_text: str
    embedded_instructions: tuple[str, ...]
    notes: str
    outcome: str
    iterations: int
    retries: tuple[str, ...] = ()


@dataclass(frozen=True)
class MessageInterpretation:
    message_id: str
    classification: str
    intent: str
    target: str
    target_event_id: str | None
    new_amount: Decimal | None
    currency: str | None
    new_date: date | None
    effective_from: date | None
    multiplier: Decimal | None
    stream_ended: bool
    income_confirmed: bool | None
    language: str
    embedded_instructions: tuple[str, ...]
    quote: str
    summary: str
    outcome: str
    iterations: int
    retries: tuple[str, ...] = ()


def _dec(v: object) -> Decimal | None:
    return None if v is None else Decimal(str(v))


def _date(v: object) -> date | None:
    return None if v is None else date.fromisoformat(str(v))


def extract_image(
    client: ModelClient,
    cfg: Config,
    model: str,
    link: ImageLink,
    event: Event,
    profile: Profile,
    image_path: Path,
    user_events: list[Event],
    user_messages: list[Message],
    budget: Budget,
    usage: UsageLedger,
) -> ImageExtraction:
    system = load_prompt("evidence_system.md")
    task = load_prompt("image_task.md").format(
        image_id=link.image_id,
        home_currency=profile.home_currency,
        event="\n".join(f"{k}: {v}" for k, v in event_fields(event).items()),
    )
    ctx = ToolContext(
        user_id=profile.user_id,
        image_path=image_path,
        image_id=link.image_id,
        events={e.event_id: event_fields(e) for e in user_events},
        messages=[
            {
                "message_id": m.message_id,
                "sent_at": m.sent_at,
                "source_type": m.source_type,
                "message_text": m.message_text,
            }
            for m in user_messages
        ],
    )
    tools = tool_definitions("record_image_extraction", IMAGE_EXTRACTION_SCHEMA, load_prompt("image_record_tool.md"))

    def factory(history: list[JSON]) -> ModelRequest:
        return ModelRequest(
            model=model, system=system, messages=[{"role": "user", "content": task}, *history], tools=tools
        )

    res: LoopResult = run_loop(
        client,
        factory,
        ctx,
        "record_image_extraction",
        IMAGE_EXTRACTION_SCHEMA,
        cfg.MAX_TOOL_ITERATIONS,
        budget,
        usage,
        "image",
        link.image_id,
    )
    p = res.payload or {}
    return ImageExtraction(
        image_id=link.image_id,
        event_id=link.related_event_id,
        amount=_dec(p.get("amount")),
        currency=p.get("currency"),
        amount_kind=str(p.get("amount_kind", "unknown")),
        document_date=_date(p.get("document_date")),
        partial=bool(p.get("partial", True)),
        confidence=str(p.get("confidence", "low")),
        evidence_text=str(p.get("evidence_text", "")),
        embedded_instructions=tuple(res.embedded_instructions),
        notes=str(p.get("notes", "")) + (f" [{res.outcome}: {res.reason}]" if res.outcome != "recorded" else ""),
        outcome=res.outcome,
        iterations=res.iterations,
        retries=tuple(res.retries),
    )


def interpret_message(
    client: ModelClient,
    cfg: Config,
    model: str,
    message: Message,
    profile: Profile,
    related_event: Event | None,
    user_events: list[Event],
    user_messages: list[Message],
    budget: Budget,
    usage: UsageLedger,
) -> MessageInterpretation:
    system = load_prompt("evidence_system.md")
    task = load_prompt("message_task.md").format(
        message_id=message.message_id,
        sent_at=message.sent_at,
        source_type=message.source_type,
        home_currency=profile.home_currency,
        related_event="\n".join(f"{k}: {v}" for k, v in event_fields(related_event).items())
        if related_event
        else "(none — the message is attached at user level)",
        fenced=fence(message.message_text, message.message_id),
    )
    ctx = ToolContext(
        user_id=profile.user_id,
        image_path=None,
        image_id=None,
        events={e.event_id: event_fields(e) for e in user_events},
        messages=[
            {
                "message_id": m.message_id,
                "sent_at": m.sent_at,
                "source_type": m.source_type,
                "message_text": m.message_text,
            }
            for m in user_messages
        ],
    )
    tools = tool_definitions(
        "record_message_interpretation", MESSAGE_INTERPRETATION_SCHEMA, load_prompt("message_record_tool.md")
    )

    def factory(history: list[JSON]) -> ModelRequest:
        return ModelRequest(
            model=model, system=system, messages=[{"role": "user", "content": task}, *history], tools=tools
        )

    res = run_loop(
        client,
        factory,
        ctx,
        "record_message_interpretation",
        MESSAGE_INTERPRETATION_SCHEMA,
        cfg.MAX_TOOL_ITERATIONS,
        budget,
        usage,
        "message",
        message.message_id,
    )
    p = res.payload or {}
    # defense in depth: code-side scan is unioned with the model's report
    embedded = sorted(set(res.embedded_instructions) | set(find_embedded_instructions(message.message_text)))
    return MessageInterpretation(
        message_id=message.message_id,
        classification=str(p.get("classification", "noise")),
        intent=str(p.get("intent", "other")),
        target=str(p.get("target", "none")),
        target_event_id=p.get("target_event_id"),
        new_amount=_dec(p.get("new_amount")),
        currency=p.get("currency"),
        new_date=_date(p.get("new_date")),
        effective_from=_date(p.get("effective_from")),
        multiplier=_dec(p.get("multiplier")),
        stream_ended=bool(p.get("stream_ended", False)),
        income_confirmed=p.get("income_confirmed"),
        language=str(p.get("language", "")),
        embedded_instructions=tuple(embedded),
        quote=str(p.get("quote", "")),
        summary=str(p.get("summary", "")) + (f" [{res.outcome}: {res.reason}]" if res.outcome != "recorded" else ""),
        outcome=res.outcome,
        iterations=res.iterations,
        retries=tuple(res.retries),
    )
