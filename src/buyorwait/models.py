"""Typed records for the dataset and the decision pipeline (CONTRACT.md §8 field lists)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Profile:
    user_id: str
    home_currency: str
    current_available_balance: Decimal
    minimum_balance_to_keep: Decimal
    financial_priorities: frozenset[str]
    protect_categories: frozenset[str]
    reduce_categories: frozenset[str]
    stop_categories: frozenset[str]
    methods: frozenset[str]
    max_installment_months: int | None


@dataclass(frozen=True)
class Request:
    request_id: str
    user_id: str
    request_date: date
    request_type: str
    requested_amount: Decimal
    requested_amount_text: str
    desired_completion_date: date
    allows_partial_payment: bool
    request_text: str


@dataclass(frozen=True)
class Event:
    event_id: str
    user_id: str
    event_type: str
    description: str
    category: str
    direction: str  # debit | credit | non_cash
    amount: Decimal | None  # None when blank in the CSV (must be resolved from an image)
    currency: str
    event_date: date
    settlement_date: date | None
    status: str  # settled | pending | scheduled | failed | cancelled | unrealized
    linked_event_id: str | None
    flexibility: str  # fixed | reducible | stoppable | reducible_or_stoppable
    minimum_allowed_amount: Decimal | None

    @property
    def number(self) -> int:
        return int(self.event_id.split("_")[1])


@dataclass(frozen=True)
class PaymentOption:
    payment_option_id: str
    request_id: str
    payment_method: str
    payment_amount: Decimal
    payment_amount_text: str
    number_of_payments: int
    first_payment_date: date
    payment_frequency_days: int | None
    financing_fee: Decimal
    total_payable_amount: Decimal

    @property
    def number(self) -> int:
        return int(self.payment_option_id.split("_")[-1])


@dataclass(frozen=True)
class Message:
    message_id: str
    user_id: str
    request_id: str | None
    related_event_id: str | None
    sent_at: str
    source_type: str
    message_text: str


@dataclass(frozen=True)
class ImageLink:
    image_id: str
    user_id: str
    request_id: str
    related_event_id: str


@dataclass(frozen=True)
class Dataset:
    profiles: dict[str, Profile]
    requests: list[Request]
    samples: list[Request]
    events_by_user: dict[str, list[Event]]
    events_by_id: dict[str, Event]
    options_by_request: dict[str, list[PaymentOption]]
    messages_by_user: dict[str, list[Message]]
    images_by_event: dict[str, ImageLink]
    rates: dict[tuple[date, str, str], Decimal]


# ----------------------------------------------------------------------------- evidence → ledger
@dataclass(frozen=True)
class Amendment:
    """One resolved fact from the evidence layer (image or message), already cross-checked in code.

    kind:
      amount            target=event_id, amount=resolved amount (event currency), partial flag in note
      salary_amount     target='salary', amount=new regular amount (currency=home or given), effective_from
      salary_date       target='salary', effective_from=new next payday (day-of-month continues)
      stream_ended      target='salary' | 'income:<description substring>' | 'all_income'
      income_unconfirmed target='all_income' (gig payouts pending)
      new_income        target='salary', amount, effective_from (first confirmed salary), monthly thereafter
      expense_multiplier target='category:<category>', factor
      duplicate_reversed target=event_id (pending duplicate charge reversal posted → do not reserve)
    """

    kind: str
    target: str
    source_id: str
    amount: Decimal | None = None
    currency: str | None = None
    effective_from: date | None = None
    factor: Decimal | None = None
    partial: bool = False
    note: str = ""


# ----------------------------------------------------------------------------- ledger / streams / curve
@dataclass(frozen=True)
class Flow:
    on: date
    amount: Decimal  # signed, home currency
    label: str
    event_id: str | None = None


@dataclass(frozen=True)
class HistRow:
    event: Event
    amount_home: Decimal
    on: date


@dataclass(frozen=True)
class Ledger:
    user_id: str
    home_currency: str
    t0: date
    start_balance: Decimal
    minimum_balance: Decimal
    known_flows: list[Flow]  # pending/scheduled rows applied inside the window
    history: list[HistRow]  # settled rows on/before t0, in home currency
    scheduled_income: list[Flow]  # subset of known_flows that are scheduled credits
    amendments: list[Amendment]
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Stream:
    kind: str  # income | expense
    key: str
    category: str
    description: str
    cadence: str  # monthly | weekly | biweekly
    amount: Decimal  # home currency, per occurrence (after amendments)
    dates: tuple[date, ...]  # projected occurrences inside the window
    flexibility: str
    minimum_allowed_amount: Decimal | None
    latest_event_id: str
    ended: bool = False
    note: str = ""


@dataclass(frozen=True)
class Change:
    action: str  # stop | reduce_to
    stream_key: str
    event_id: str
    description: str
    new_amount: Decimal | None = None


@dataclass(frozen=True)
class Payment:
    on: date
    amount: Decimal
    amount_text: str


@dataclass(frozen=True)
class Plan:
    method: str  # full_payment | partial_payment | installments | wait
    payments: tuple[Payment, ...]
    changes: tuple[Change, ...] = ()
    payment_option_id: str | None = None
    total_paid: Decimal = Decimal(0)

    @property
    def first_date(self) -> date:
        return self.payments[0].on

    @property
    def last_date(self) -> date:
        return self.payments[-1].on

    def completes_by(self, deadline: date) -> bool:
        return self.last_date <= deadline


@dataclass(frozen=True)
class Rationale:
    """Single source of truth for all eight output columns (CONTRACT §8 reconcile)."""

    request: Request
    profile: Profile
    safe_amount: Decimal
    earliest_full_date: date | None
    plan: Plan | None
    status: str
    method: str
    changes: tuple[Change, ...]
    curve_min: Decimal
    evidence_used: tuple[str, ...]
    notes: tuple[str, ...]
