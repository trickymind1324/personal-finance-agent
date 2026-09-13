"""Per-request decision pipeline: ledger → streams → curve → plan → rationale → row (CONTRACT §8 data flow)."""

from __future__ import annotations

from dataclasses import dataclass

from buyorwait.config import Config
from buyorwait.contract import validate_row
from buyorwait.io_dataset import row_context_for
from buyorwait.ledger import normalize_ledger
from buyorwait.models import Amendment, Dataset, Rationale, Request
from buyorwait.plans import choose
from buyorwait.reconcile import build_rationale, to_output_row
from buyorwait.recurrence import infer_streams
from buyorwait.simulate import build_curve, is_safe


class InvariantError(AssertionError):
    """A produced row violated CONTRACT §2; raised, never warned."""


@dataclass(frozen=True)
class Decision:
    rationale: Rationale
    row: dict[str, str]
    stream_summary: tuple[str, ...]


def decide(request: Request, dataset: Dataset, amendments: list[Amendment], cfg: Config) -> Decision:
    profile = dataset.profiles[request.user_id]
    events = dataset.events_by_user.get(request.user_id, [])
    ledger = normalize_ledger(profile, events, amendments, dataset.rates, request.request_date, cfg)
    streams = infer_streams(ledger, cfg)
    options = dataset.options_by_request.get(request.request_id, [])
    plan, safe, earliest, curve = choose(request, profile, options, ledger, streams, cfg)
    # I-10: the recommended plan is re-verified with the same simulator
    if plan is not None:
        check_curve = build_curve(ledger, streams, cfg.HORIZON_DAYS, plan.changes, cfg.INTRADAY_ORDER)
        until = (
            request.desired_completion_date
            if cfg.SAFETY_SCAN_END == "deadline" and plan.method != "full_payment"
            else None
        )
        if not is_safe(check_curve, plan.payments, profile.minimum_balance_to_keep, until):
            raise InvariantError(f"{request.request_id}: chosen plan {plan.method} failed the safety re-check")
    evidence = tuple(a.source_id for a in amendments)
    notes = tuple(ledger.notes) + tuple(
        f"{s.key}: {s.cadence} x{len(s.dates)} @ {s.amount:.2f}{' ' + s.note if s.note else ''}" for s in streams
    )
    rationale = build_rationale(request, profile, plan, safe, earliest, curve, evidence, notes)
    row = to_output_row(rationale)
    violations = validate_row(row, row_context_for(request, profile, options, events))
    if violations:
        raise InvariantError(f"{request.request_id}: {violations}")
    return Decision(rationale, row, tuple(f"{s.key} {s.cadence} {s.amount:.2f} n={len(s.dates)}" for s in streams))
