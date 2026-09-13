"""Per-column scorer for Buy or Wait? predictions against dataset/sample_requests.csv.

Mirrors the six scored dimensions of the challenge:
  1 amount_safe_to_pay accuracy   2 affordability_status   3 method + plan
  4 earliest_date_for_full_payment   5 spending_changes validity   6 explanation consistency

Every run prints the metric table, writes analysis/reports/eval_<tag>.md and .json, copies the scored
predictions to analysis/reports/predictions/<tag>.csv, and diffs against the pinned run and the naive
baseline. Any regression on any column versus the pinned run exits with status 2 (stops the
line) unless --allow-regression is passed. Sample ids listed in fewshot_exclusions.txt are
never scored (they may be used as few-shot prompt examples).

Usage (repo root):
  python3 code/evaluation/score.py --predictions analysis/reports/predictions/baseline.csv --tag baseline
  python3 code/evaluation/score.py --predictions <csv> --tag <tag> [--set-pin] [--allow-regression]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

try:
    import buyorwait  # noqa: F401  (installed with `pip install -e .`)
except ImportError:  # running from an unpacked code.zip without installing: use the bundled src/ package
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from buyorwait.contract import EXPLANATION_PATTERNS, OUTPUT_COLUMNS, RowContext, template_key, to_decimal, validate_row
from buyorwait.io_dataset import build_row_contexts, load_csv

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "dataset"
REPORTS = ROOT / "analysis" / "reports"
EXCLUSIONS = Path(__file__).with_name("fewshot_exclusions.txt")
PIN = REPORTS / "eval_pinned.json"
BASELINE = REPORTS / "eval_baseline.json"

# metric name -> higher_is_better
METRICS: dict[str, bool] = {
    "safe_exact": True,
    "safe_within_5pct": True,
    "safe_mean_err_pct": False,
    "status_acc": True,
    "method_acc": True,
    "plan_exact": True,
    "method_plan_both": True,
    "earliest_exact": True,
    "changes_exact": True,
    "changes_valid": True,
    "explanation_template": True,
    "explanation_consistent": True,
    "row_valid": True,
    "composite": True,
}


@dataclass
class Scored:
    metrics: dict[str, float]
    n: int
    per_row: list[dict[str, object]]


def score(
    predictions: list[dict[str, str]],
    truth: list[dict[str, str]],
    ctxs: dict[str, RowContext],
    excluded: frozenset[str],
    allow_missing: bool = False,
) -> Scored:
    pred_by_id = {r["request_id"]: r for r in predictions}
    rows = [t for t in truth if t["request_id"] not in excluded]
    missing = [t["request_id"] for t in rows if t["request_id"] not in pred_by_id]
    if missing and not allow_missing:
        raise SystemExit(f"predictions missing for {missing}")
    rows = [t for t in rows if t["request_id"] in pred_by_id]
    acc: dict[str, list[float]] = {k: [] for k in METRICS if k != "composite"}
    per_row: list[dict[str, object]] = []
    for t in rows:
        p = pred_by_id[t["request_id"]]
        ctx = ctxs[t["request_id"]]
        requested = ctx.requested
        gt_safe, pr_safe = to_decimal(t["amount_safe_to_pay"]), to_decimal(p["amount_safe_to_pay"])
        err_pct = float(abs(pr_safe - gt_safe) / requested * 100) if requested else 0.0
        acc["safe_exact"].append(float(abs(pr_safe - gt_safe) <= Decimal("0.005")))
        acc["safe_within_5pct"].append(float(err_pct <= 5.0))
        acc["safe_mean_err_pct"].append(err_pct)
        status_ok = p["affordability_status"] == t["affordability_status"]
        method_ok = p["recommended_payment_method"] == t["recommended_payment_method"]
        plan_ok = p["payment_plan"] == t["payment_plan"]
        acc["status_acc"].append(float(status_ok))
        acc["method_acc"].append(float(method_ok))
        acc["plan_exact"].append(float(plan_ok))
        acc["method_plan_both"].append(float(method_ok and plan_ok))
        acc["earliest_exact"].append(float(p["earliest_date_for_full_payment"] == t["earliest_date_for_full_payment"]))
        acc["changes_exact"].append(float(p["spending_changes_needed"] == t["spending_changes_needed"]))
        violations = validate_row(p, ctx)
        change_violations = [x for x in violations if x.startswith(("I-8", "C-4", "C-6"))]
        acc["changes_valid"].append(float(not change_violations))
        key = template_key(p["recommended_payment_method"], p["spending_changes_needed"] != "none")
        tmpl_ok = key in EXPLANATION_PATTERNS and EXPLANATION_PATTERNS[key].match(p["decision_explanation"]) is not None
        acc["explanation_template"].append(float(tmpl_ok))
        expl_violations = [x for x in violations if x.startswith("explanation")]
        acc["explanation_consistent"].append(float(tmpl_ok and not expl_violations))
        acc["row_valid"].append(float(not violations))
        per_row.append(
            {
                "request_id": t["request_id"],
                "err_pct": round(err_pct, 2),
                "status_ok": status_ok,
                "method_ok": method_ok,
                "plan_ok": plan_ok,
                "earliest_ok": p["earliest_date_for_full_payment"] == t["earliest_date_for_full_payment"],
                "changes_ok": p["spending_changes_needed"] == t["spending_changes_needed"],
                "violations": violations,
            }
        )
    metrics = {k: (sum(v) / len(v) if v else 0.0) for k, v in acc.items()}
    metrics["composite"] = (
        sum(
            metrics[k]
            for k in (
                "safe_exact",
                "status_acc",
                "method_plan_both",
                "earliest_exact",
                "changes_exact",
                "explanation_consistent",
            )
        )
        / 6
    )
    return Scored(metrics, len(rows), per_row)


def fmt(k: str, v: float) -> str:
    return f"{v:.1f}" if k == "safe_mean_err_pct" else f"{v * 100:.1f}%"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--predictions", required=True, type=Path)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--pin", type=Path, default=PIN, help="pinned run json to diff against")
    ap.add_argument("--baseline", type=Path, default=BASELINE)
    ap.add_argument("--exclude", type=Path, default=EXCLUSIONS)
    ap.add_argument("--set-pin", action="store_true", help="write this run as the new pinned run")
    ap.add_argument("--allow-regression", action="store_true")
    ap.add_argument(
        "--allow-missing",
        action="store_true",
        help="ablation only: score the rows present (skipped rows are not counted)",
    )
    args = ap.parse_args(argv)

    excluded = (
        frozenset(x.strip() for x in args.exclude.read_text().splitlines() if x.strip())
        if args.exclude.exists()
        else frozenset()
    )
    preds = load_csv(args.predictions)
    if preds and tuple(preds[0].keys()) != OUTPUT_COLUMNS:
        raise SystemExit(f"predictions columns {tuple(preds[0].keys())} != {OUTPUT_COLUMNS}")
    truth = load_csv(DATA / "sample_requests.csv")
    result = score(preds, truth, build_row_contexts(DATA, "sample_requests.csv"), excluded, args.allow_missing)

    pinned = json.loads(args.pin.read_text())["metrics"] if args.pin.exists() else None
    base = json.loads(args.baseline.read_text())["metrics"] if args.baseline.exists() else None
    header = ["metric", "current"] + (["pinned", "Δ pin"] if pinned else []) + (["baseline", "Δ base"] if base else [])
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    regressions: list[str] = []
    for k, higher in METRICS.items():
        cur = result.metrics[k]
        cells = [k, fmt(k, cur)]
        if pinned:
            pv = pinned[k]
            delta = cur - pv
            cells += [fmt(k, pv), f"{delta * (1 if k == 'safe_mean_err_pct' else 100):+.1f}"]
            if (higher and cur < pv - 1e-9) or (not higher and cur > pv + 1e-9):
                regressions.append(k)
        if base:
            bv = base[k]
            cells += [fmt(k, bv), f"{(cur - bv) * (1 if k == 'safe_mean_err_pct' else 100):+.1f}"]
        lines.append("| " + " | ".join(cells) + " |")
    table = "\n".join(lines)
    print(f"tag={args.tag} scored_rows={result.n} excluded={sorted(excluded) or 'none'}")
    print(table)

    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "predictions").mkdir(exist_ok=True)
    dest = REPORTS / "predictions" / f"{args.tag}.csv"
    if args.predictions.resolve() != dest.resolve():
        shutil.copyfile(args.predictions, dest)
    payload = {
        "tag": args.tag,
        "n": result.n,
        "excluded": sorted(excluded),
        "metrics": result.metrics,
        "per_row": result.per_row,
    }
    (REPORTS / f"eval_{args.tag}.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    md = [
        f"# Eval report — `{args.tag}`",
        "",
        f"Scored rows: {result.n} (excluded few-shot ids: {sorted(excluded) or 'none'}).",
        f"Predictions: `analysis/reports/predictions/{args.tag}.csv`. Pinned: `{args.pin.name if pinned else 'none'}`. "
        f"Baseline: `{args.baseline.name if base else 'none'}`.",
        "",
        table,
        "",
        "## Per-row",
        "",
        "| request | safe err % | status | method | plan | earliest | changes | violations |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in result.per_row:
        ok = lambda b: "✓" if b else "✗"  # noqa: E731
        md.append(
            f"| {r['request_id']} | {r['err_pct']} | {ok(r['status_ok'])} | {ok(r['method_ok'])} | {ok(r['plan_ok'])} | "
            f"{ok(r['earliest_ok'])} | {ok(r['changes_ok'])} | {'; '.join(r['violations']) or '-'} |"
        )  # type: ignore[arg-type]
    if regressions:
        md += ["", f"**REGRESSION vs pinned on: {', '.join(regressions)}**"]
    (REPORTS / f"eval_{args.tag}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    if args.set_pin:
        args.pin.write_text(json.dumps({"tag": args.tag, "metrics": result.metrics}, indent=2), encoding="utf-8")
        print(f"pinned {args.pin}")
    if regressions and not args.allow_regression:
        print(f"REGRESSION vs pinned on: {', '.join(regressions)} — line stopped (use --allow-regression to override)")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
