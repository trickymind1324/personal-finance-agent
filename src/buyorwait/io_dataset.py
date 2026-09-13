"""Dataset loading helpers shared by the runtime, the scorer and the validator.

Only reads files under dataset/ (CONTRACT.md §8, `io_dataset.py`). Organizer-only files
never exist here. Amount strings are kept as text until a caller converts them with
`buyorwait.contract.to_decimal`, so nothing is rounded on the way in.
"""
from __future__ import annotations

import csv
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from buyorwait.contract import RowContext, to_decimal
from buyorwait.models import Dataset, Event, ImageLink, Message, PaymentOption, Profile, Request


def load_csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def installment_schedule(option: dict[str, str]) -> str:
    """Render a supplied installment option exactly as a payment_plan string (CONTRACT I-6)."""
    n = int(option["number_of_payments"])
    first = date.fromisoformat(option["first_payment_date"])
    step = int(option["payment_frequency_days"])
    return "|".join(f"{(first + timedelta(days=step * k)).isoformat()}:{option['payment_amount']}" for k in range(n))


def _split(text: str) -> frozenset[str]:
    return frozenset(x for x in text.split("|") if x)


def build_row_contexts(dataset_dir: Path, requests_file: str) -> dict[str, RowContext]:
    """One RowContext per request in `requests_file` (e.g. 'sample_requests.csv' or 'requests.csv')."""
    requests = load_csv(dataset_dir / requests_file)
    prof = {p["user_id"]: p for p in load_csv(dataset_dir / "financial_profiles.csv")}
    events_by_user: dict[str, dict[str, dict[str, str]]] = {}
    for e in load_csv(dataset_dir / "financial_events.csv"):
        events_by_user.setdefault(e["user_id"], {})[e["event_id"]] = e
    options_by_request: dict[str, dict[str, str]] = {}
    for o in load_csv(dataset_dir / "request_payment_options.csv"):
        if o["payment_method"] == "installments":
            options_by_request.setdefault(o["request_id"], {})[o["payment_option_id"]] = installment_schedule(o)
    ctxs: dict[str, RowContext] = {}
    for r in requests:
        p = prof[r["user_id"]]
        ctxs[r["request_id"]] = RowContext(
            request_date=date.fromisoformat(r["request_date"]),
            deadline=date.fromisoformat(r["desired_completion_date"]),
            requested=to_decimal(r["requested_amount"]),
            allows_partial=r["allows_partial_payment"] == "true",
            methods=_split(p["payment_methods_user_will_consider"]),
            max_installment_months=int(p["max_installment_months"]) if p["max_installment_months"] else None,
            home_currency=p["home_currency"],
            minimum_balance=to_decimal(p["minimum_balance_to_keep"]),
            installment_schedules=options_by_request.get(r["request_id"], {}),
            events=events_by_user.get(r["user_id"], {}),
            stop_categories=_split(p["expense_categories_user_is_willing_to_stop"]),
            reduce_categories=_split(p["expense_categories_user_is_willing_to_reduce"]),
            protect_categories=_split(p["expense_categories_to_protect"]),
        )
    return ctxs


# ----------------------------------------------------------------------------- typed dataset
def _dec(text: str) -> Decimal | None:
    return to_decimal(text) if text.strip() else None


def _date(text: str) -> date | None:
    return date.fromisoformat(text) if text.strip() else None


def _request(r: dict[str, str]) -> Request:
    return Request(
        request_id=r["request_id"],
        user_id=r["user_id"],
        request_date=date.fromisoformat(r["request_date"]),
        request_type=r["request_type"],
        requested_amount=to_decimal(r["requested_amount"]),
        requested_amount_text=r["requested_amount"],
        desired_completion_date=date.fromisoformat(r["desired_completion_date"]),
        allows_partial_payment=r["allows_partial_payment"] == "true",
        request_text=r["request_text"],
    )


def load_dataset(dataset_dir: Path) -> Dataset:
    profiles: dict[str, Profile] = {}
    for p in load_csv(dataset_dir / "financial_profiles.csv"):
        profiles[p["user_id"]] = Profile(
            user_id=p["user_id"],
            home_currency=p["home_currency"],
            current_available_balance=to_decimal(p["current_available_balance"]),
            minimum_balance_to_keep=to_decimal(p["minimum_balance_to_keep"]),
            financial_priorities=_split(p["financial_priorities"]),
            protect_categories=_split(p["expense_categories_to_protect"]),
            reduce_categories=_split(p["expense_categories_user_is_willing_to_reduce"]),
            stop_categories=_split(p["expense_categories_user_is_willing_to_stop"]),
            methods=_split(p["payment_methods_user_will_consider"]),
            max_installment_months=int(p["max_installment_months"]) if p["max_installment_months"] else None,
        )
    events_by_user: dict[str, list[Event]] = {}
    events_by_id: dict[str, Event] = {}
    for e in load_csv(dataset_dir / "financial_events.csv"):
        ev = Event(
            event_id=e["event_id"],
            user_id=e["user_id"],
            event_type=e["event_type"],
            description=e["description"],
            category=e["category"],
            direction=e["direction"],
            amount=_dec(e["amount"]),
            currency=e["currency"],
            event_date=date.fromisoformat(e["event_date"]),
            settlement_date=_date(e["settlement_date"]),
            status=e["status"],
            linked_event_id=e["linked_event_id"] or None,
            flexibility=e["flexibility"],
            minimum_allowed_amount=_dec(e["minimum_allowed_amount"]),
        )
        events_by_user.setdefault(ev.user_id, []).append(ev)
        events_by_id[ev.event_id] = ev
    options_by_request: dict[str, list[PaymentOption]] = {}
    for o in load_csv(dataset_dir / "request_payment_options.csv"):
        options_by_request.setdefault(o["request_id"], []).append(
            PaymentOption(
                payment_option_id=o["payment_option_id"],
                request_id=o["request_id"],
                payment_method=o["payment_method"],
                payment_amount=to_decimal(o["payment_amount"]),
                payment_amount_text=o["payment_amount"],
                number_of_payments=int(o["number_of_payments"]),
                first_payment_date=date.fromisoformat(o["first_payment_date"]),
                payment_frequency_days=int(o["payment_frequency_days"]) if o["payment_frequency_days"] else None,
                financing_fee=to_decimal(o["financing_fee"]),
                total_payable_amount=to_decimal(o["total_payable_amount"]),
            )
        )
    messages_by_user: dict[str, list[Message]] = {}
    for m in load_csv(dataset_dir / "messages.csv"):
        messages_by_user.setdefault(m["user_id"], []).append(
            Message(
                m["message_id"],
                m["user_id"],
                m["request_id"] or None,
                m["related_event_id"] or None,
                m["sent_at"],
                m["source_type"],
                m["message_text"],
            )
        )
    images_by_event = {
        i["related_event_id"]: ImageLink(i["image_id"], i["user_id"], i["request_id"], i["related_event_id"])
        for i in load_csv(dataset_dir / "images.csv")
    }
    rates = {
        (date.fromisoformat(x["rate_date"]), x["from_currency"], x["to_currency"]): to_decimal(x["rate"])
        for x in load_csv(dataset_dir / "exchange_rates.csv")
    }
    return Dataset(
        profiles=profiles,
        requests=[_request(r) for r in load_csv(dataset_dir / "requests.csv")],
        samples=[_request(r) for r in load_csv(dataset_dir / "sample_requests.csv")],
        events_by_user=events_by_user,
        events_by_id=events_by_id,
        options_by_request=options_by_request,
        messages_by_user=messages_by_user,
        images_by_event=images_by_event,
        rates=rates,
    )


def row_context_for(
    request: Request, profile: Profile, options: list[PaymentOption], events: list[Event]
) -> RowContext:
    """RowContext from typed records (used by the pipeline's per-row invariant check)."""
    schedules: dict[str, str] = {}
    for o in options:
        if o.payment_method == "installments" and o.payment_frequency_days is not None:
            schedules[o.payment_option_id] = "|".join(
                f"{(o.first_payment_date + timedelta(days=o.payment_frequency_days * k)).isoformat()}:{o.payment_amount_text}"
                for k in range(o.number_of_payments)
            )
    ev = {
        e.event_id: {
            "flexibility": e.flexibility,
            "category": e.category,
            "minimum_allowed_amount": str(e.minimum_allowed_amount) if e.minimum_allowed_amount is not None else "",
            "status": e.status,
            "description": e.description,
        }
        for e in events
    }
    return RowContext(
        request_date=request.request_date,
        deadline=request.desired_completion_date,
        requested=request.requested_amount,
        allows_partial=request.allows_partial_payment,
        methods=profile.methods,
        max_installment_months=profile.max_installment_months,
        home_currency=profile.home_currency,
        minimum_balance=profile.minimum_balance_to_keep,
        installment_schedules=schedules,
        events=ev,
        stop_categories=profile.stop_categories,
        reduce_categories=profile.reduce_categories,
        protect_categories=profile.protect_categories,
    )
