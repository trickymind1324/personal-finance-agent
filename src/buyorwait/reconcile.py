"""Reconciliation: one Rationale object → all eight output columns (CONTRACT §8, Phase 5 lesson)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from buyorwait.contract import (
    OUTPUT_COLUMNS,
    ExplanationFacts,
    fmt_padded,
    fmt_prose_amount,
    fmt_shortest,
    render_changes,
    render_explanation,
    render_plan,
)
from buyorwait.contract import (
    Change as OutChange,
)
from buyorwait.contract import (
    Payment as OutPayment,
)
from buyorwait.models import Change, Plan, Profile, Rationale, Request
from buyorwait.simulate import Curve


def build_rationale(
    request: Request,
    profile: Profile,
    plan: Plan | None,
    safe: Decimal,
    earliest: date | None,
    curve: Curve,
    evidence_used: tuple[str, ...],
    notes: tuple[str, ...],
) -> Rationale:
    if plan is None:
        status, method = "not_affordable", "not_recommended"
    elif plan.method == "full_payment" and not plan.changes:
        status, method = "affordable_now", "full_payment"
    elif plan.method == "wait":
        status, method = "affordable_later", "wait"
    else:
        status, method = "affordable_with_plan", plan.method
    return Rationale(
        request=request,
        profile=profile,
        safe_amount=safe,
        earliest_full_date=earliest,
        plan=plan,
        status=status,
        method=method,
        changes=plan.changes if plan else (),
        curve_min=curve.minimum,
        evidence_used=evidence_used,
        notes=notes,
    )


def change_clause(c: Change) -> str:
    desc = c.description[0].lower() + c.description[1:]
    if c.action == "stop" or c.new_amount is None:
        return f"Stop the {desc}"
    return f"Reduce the {desc} to {{ccy}} {fmt_prose_amount(c.new_amount)}"


def to_output_row(r: Rationale) -> dict[str, str]:
    req, prof = r.request, r.profile
    if r.status == "not_affordable":
        earliest_text = ""
    elif r.status == "affordable_now":
        earliest_text = req.request_date.isoformat()
    else:
        earliest_text = r.earliest_full_date.isoformat() if r.earliest_full_date else ""
    plan_text = render_plan([OutPayment(p.on, p.amount_text) for p in r.plan.payments]) if r.plan else "none"
    changes_text = render_changes(
        [
            OutChange(c.action, c.event_id, fmt_padded(c.new_amount) if c.new_amount is not None else None)
            for c in r.changes
        ]
    )
    facts = ExplanationFacts(
        ccy=prof.home_currency,
        requested=req.requested_amount,
        minimum_balance=prof.minimum_balance_to_keep,
        method=r.method,
        safe=r.safe_amount,
        earliest=r.earliest_full_date,
        deadline=req.desired_completion_date,
        plan=[OutPayment(p.on, p.amount_text) for p in r.plan.payments] if r.plan else [],
        change_clauses=[change_clause(c).replace("{ccy}", prof.home_currency) for c in r.changes],
    )
    row = {
        "request_id": req.request_id,
        "amount_safe_to_pay": fmt_shortest(r.safe_amount),
        "affordability_status": r.status,
        "recommended_payment_method": r.method,
        "payment_plan": plan_text,
        "earliest_date_for_full_payment": earliest_text,
        "spending_changes_needed": changes_text,
        "decision_explanation": render_explanation(facts),
    }
    assert tuple(row) == OUTPUT_COLUMNS
    return row
