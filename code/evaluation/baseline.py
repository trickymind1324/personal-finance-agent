"""Naive baseline predictor (committed reference point for every eval report).

Rule: if current_available_balance - minimum_balance_to_keep >= requested_amount then
affordable_now / full_payment today, else not_affordable / not_recommended with
amount_safe_to_pay = clamp(balance - minimum, 0, requested). No forecasting, no
gates, no evidence. It exists so improvements are always shown as before/after.

Usage (repo root):  python3 code/evaluation/baseline.py [--out analysis/reports/predictions/baseline.csv] [--requests dataset/sample_requests.csv]
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

try:
    import buyorwait  # noqa: F401  (installed with `pip install -e .`)
except ImportError:  # running from an unpacked code.zip without installing: use the bundled src/ package
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from buyorwait.contract import (
    OUTPUT_COLUMNS,
    ExplanationFacts,
    Payment,
    fmt_padded,
    fmt_shortest,
    render_explanation,
    to_decimal,
)

ROOT = Path(__file__).resolve().parents[2]


def predict(request: dict[str, str], profile: dict[str, str]) -> dict[str, str]:
    requested = to_decimal(request["requested_amount"])
    headroom = to_decimal(profile["current_available_balance"]) - to_decimal(profile["minimum_balance_to_keep"])
    safe = max(Decimal(0), min(requested, headroom))
    t0 = date.fromisoformat(request["request_date"])
    deadline = date.fromisoformat(request["desired_completion_date"])
    common = dict(
        ccy=profile["home_currency"],
        requested=requested,
        minimum_balance=to_decimal(profile["minimum_balance_to_keep"]),
        safe=safe,
        deadline=deadline,
        change_clauses=[],
    )
    if headroom >= requested:
        plan = [Payment(t0, fmt_padded(requested))]
        facts = ExplanationFacts(method="full_payment", earliest=t0, plan=plan, **common)  # type: ignore[arg-type]
        return {
            "request_id": request["request_id"],
            "amount_safe_to_pay": fmt_shortest(safe),
            "affordability_status": "affordable_now",
            "recommended_payment_method": "full_payment",
            "payment_plan": f"{t0.isoformat()}:{fmt_padded(requested)}",
            "earliest_date_for_full_payment": t0.isoformat(),
            "spending_changes_needed": "none",
            "decision_explanation": render_explanation(facts),
        }
    facts = ExplanationFacts(method="not_recommended", earliest=None, plan=[], **common)  # type: ignore[arg-type]
    return {
        "request_id": request["request_id"],
        "amount_safe_to_pay": fmt_shortest(safe),
        "affordability_status": "not_affordable",
        "recommended_payment_method": "not_recommended",
        "payment_plan": "none",
        "earliest_date_for_full_payment": "",
        "spending_changes_needed": "none",
        "decision_explanation": render_explanation(facts),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--requests", type=Path, default=ROOT / "dataset" / "sample_requests.csv")
    ap.add_argument("--out", type=Path, default=ROOT / "analysis" / "reports" / "predictions" / "baseline.csv")
    args = ap.parse_args()
    with open(ROOT / "dataset" / "financial_profiles.csv", newline="", encoding="utf-8") as fh:
        prof = {p["user_id"]: p for p in csv.DictReader(fh)}
    with open(args.requests, newline="", encoding="utf-8") as fh:
        requests = list(csv.DictReader(fh))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(OUTPUT_COLUMNS), lineterminator="\n")
        w.writeheader()
        for r in requests:
            w.writerow(predict(r, prof[r["user_id"]]))
    print(f"wrote {args.out} ({len(requests)} rows)")


if __name__ == "__main__":
    main()
