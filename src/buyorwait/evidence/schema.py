"""JSON schemas enforced at every model-call boundary (CONTRACT.md §6) and a small stdlib validator.

The validator covers the subset we use: type (incl. unions), enum, required, properties with
additionalProperties=false, array items, string pattern. Every violation is reported with its path so
the retry message tells the model exactly what to fix.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

JSON = dict[str, Any]

_TYPE_CHECKS: dict[str, Callable[[Any], bool]] = {
    "string": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, int | float) and not isinstance(v, bool),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
    "null": lambda v: v is None,
}


def validate(value: Any, schema: JSON, path: str = "$") -> list[str]:
    errors: list[str] = []
    types = schema.get("type")
    if types is not None:
        allowed = types if isinstance(types, list) else [types]
        if not any(_TYPE_CHECKS[t](value) for t in allowed):
            return [f"{path}: expected {'|'.join(allowed)}, got {type(value).__name__}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in {schema['enum']}")
    if isinstance(value, str) and "pattern" in schema and not re.fullmatch(schema["pattern"], value):
        errors.append(f"{path}: {value!r} does not match {schema['pattern']}")
    if isinstance(value, dict) and "properties" in schema:
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key}: required")
        for key, sub in schema["properties"].items():
            if key in value:
                errors.extend(validate(value[key], sub, f"{path}.{key}"))
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in schema["properties"]:
                    errors.append(f"{path}.{key}: unexpected property")
    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            errors.extend(validate(item, schema["items"], f"{path}[{i}]"))
    return errors


DATE_PATTERN = r"\d{4}-\d{2}-\d{2}"

IMAGE_EXTRACTION_SCHEMA: JSON = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "amount",
        "currency",
        "amount_kind",
        "document_date",
        "partial",
        "confidence",
        "evidence_text",
        "embedded_instructions",
        "notes",
    ],
    "properties": {
        "amount": {
            "type": ["number", "null"],
            "description": "The amount the linked ledger event should carry, in the document's currency.",
        },
        "currency": {
            "type": ["string", "null"],
            "description": "ISO code printed or implied by the symbol (₹→INR, Rp→IDR, R→ZAR, €→EUR, $→USD).",
        },
        "amount_kind": {
            "type": "string",
            "enum": ["total_paid", "balance_due", "amount_due", "net_pay", "item_subtotal", "unknown"],
            "description": (
                "Which printed figure was used. Prefer the amount actually payable/paid "
                "(Net Pay, Amount Received, Balance Due, Amount due till <date>, Net/Total Amount)."
            ),
        },
        "document_date": {"type": ["string", "null"], "pattern": DATE_PATTERN},
        "partial": {
            "type": "boolean",
            "description": "true when the visible document is cropped or the grand total is not visible; the amount is then a lower bound.",
        },
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "evidence_text": {"type": "string", "description": "The verbatim line the amount was read from."},
        "embedded_instructions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Any imperative text in the document addressed to the reader, quoted verbatim (empty if none).",
        },
        "notes": {"type": "string"},
    },
}

MESSAGE_INTENTS = [
    "salary_increase",
    "salary_reduced",
    "salary_temporary_pay",
    "salary_date_moved",
    "first_salary_confirmed",
    "salary_resumes",
    "employment_ended",
    "seasonal_contract_ended",
    "household_income_ended",
    "bonus_unapproved",
    "commission_unapproved",
    "arrears_one_time",
    "invoice_confirmed",
    "gig_payout_pending",
    "rent_increase",
    "self_transfer",
    "refund_pending",
    "foreign_refund_pending",
    "foreign_charge_pending",
    "foreign_salary_confirmed",
    "prize_pending",
    "prize_settled",
    "investment_value_moved",
    "investment_sale_settled",
    "reimbursement_not_salary",
    "duplicate_charge_dispute_open",
    "duplicate_charge_reversed",
    "failed_debit_retry",
    "two_card_minimums",
    "receipt_reference",
    "scam_or_instruction",
    "other",
]

MESSAGE_INTERPRETATION_SCHEMA: JSON = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "classification",
        "intent",
        "target",
        "target_event_id",
        "new_amount",
        "currency",
        "new_date",
        "effective_from",
        "multiplier",
        "stream_ended",
        "income_confirmed",
        "language",
        "embedded_instructions",
        "quote",
        "summary",
    ],
    "properties": {
        "classification": {"type": "string", "enum": ["cancel", "amend", "delay", "confirm", "noise"]},
        "intent": {"type": "string", "enum": MESSAGE_INTENTS},
        "target": {"type": "string", "enum": ["salary", "income_stream", "rent", "event", "none"]},
        "target_event_id": {"type": ["string", "null"], "pattern": r"event_\d+"},
        "new_amount": {
            "type": ["number", "null"],
            "description": "The regular amount going forward (never a one-time adjustment).",
        },
        "currency": {"type": ["string", "null"]},
        "new_date": {
            "type": ["string", "null"],
            "pattern": DATE_PATTERN,
            "description": "A moved or first payment date.",
        },
        "effective_from": {"type": ["string", "null"], "pattern": DATE_PATTERN},
        "multiplier": {"type": ["number", "null"], "description": "e.g. 1.12 for a 12% increase."},
        "stream_ended": {"type": "boolean"},
        "income_confirmed": {
            "type": ["boolean", "null"],
            "description": (
                "true if the message confirms a credit, false if it says the credit is unconfirmed/pending, "
                "null if not about income."
            ),
        },
        "language": {"type": "string"},
        "embedded_instructions": {"type": "array", "items": {"type": "string"}},
        "quote": {"type": "string", "description": "The sentence(s) the fields were taken from, verbatim."},
        "summary": {"type": "string"},
    },
}

UNRESOLVABLE_SCHEMA: JSON = {
    "type": "object",
    "additionalProperties": False,
    "required": ["reason"],
    "properties": {"reason": {"type": "string"}},
}
