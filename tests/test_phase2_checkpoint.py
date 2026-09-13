"""Phase 2 checkpoint: the eval harness and output contract are trustworthy before any solution code.

Each test docstring names the design decision it guards. Every rule is tested in both directions:
the trip case and the nearest legitimate negative.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from buyorwait.contract import (
    EXPLANATION_PATTERNS,
    OUTPUT_COLUMNS,
    Change,
    event_number,
    fmt_padded,
    fmt_prose_amount,
    fmt_shortest,
    parse_changes,
    parse_plan,
    prose_date,
    render_changes,
    template_key,
    validate_row,
)
from buyorwait.io_dataset import build_row_contexts

ROOT = Path(__file__).resolve().parents[1]
SCORE = ROOT / "code" / "evaluation" / "score.py"
BASELINE = ROOT / "code" / "evaluation" / "baseline.py"


def load(name: str) -> list[dict[str, str]]:
    with open(ROOT / "dataset" / name, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


@pytest.fixture(scope="module")
def samples() -> list[dict[str, str]]:
    return load("sample_requests.csv")


@pytest.fixture(scope="module")
def contexts() -> dict:
    return build_row_contexts(ROOT / "dataset", "sample_requests.csv")


# ----------------------------------------------------------------------------- formatting
@pytest.mark.parametrize(
    "text,expected",
    [("603.30", "603.3"), ("17229139.20", "17229139.2"), ("873000.00", "873000"), ("87170.555", "87170.56")],
)
def test_fmt_shortest_matches_sample_convention(text: str, expected: str) -> None:
    """Design decision: amount_safe_to_pay is round-half-even to 2 dp then shortest repr, never padded (conv. audit §4)."""
    assert fmt_shortest(Decimal(text)) == expected


@pytest.mark.parametrize(
    "text,expected", [("620.4", "620.40"), ("996.6", "996.60"), ("25256", "25256"), ("23.5", "23.50")]
)
def test_fmt_padded_matches_plan_and_reduce_to_convention(text: str, expected: str) -> None:
    """Design decision: full/wait plan amounts and reduce_to amounts are integer-or-2dp padded (conv. audit §4)."""
    assert fmt_padded(Decimal(text)) == expected


def test_fmt_shortest_and_padded_differ_only_by_trailing_zero() -> None:
    """Nearest negative: the two rules agree on integers and disagree only on a trailing zero."""
    assert fmt_shortest(Decimal("620.40")) == "620.4" != fmt_padded(Decimal("620.4"))
    assert fmt_shortest(Decimal("25256")) == fmt_padded(Decimal("25256"))


def test_prose_amount_and_date() -> None:
    """Design decision: explanation numbers use thousands separators, 2 dp iff non-integral; dates 'D Month YYYY'."""
    assert fmt_prose_amount(Decimal("15952906.67")) == "15,952,906.67"
    assert fmt_prose_amount(Decimal("18000")) == "18,000"
    assert prose_date(date(2024, 6, 15)) == "15 June 2024"
    assert prose_date(date(2024, 3, 3)) == "3 March 2024"


def test_render_changes_numeric_order_not_lexicographic() -> None:
    """Design decision C-4 (ruled): changes listed by numeric event id; lexicographic would put event_1816 first."""
    changes = [Change("reduce_to", "event_1816", "23.50"), Change("stop", "event_989")]
    assert render_changes(changes) == "stop:event_989|reduce_to:event_1816:23.50"
    assert sorted(c.event_id for c in changes) == ["event_1816", "event_989"]  # the lexicographic trap
    assert event_number("event_989") < event_number("event_1816")


def test_parse_plan_and_changes_round_trip(samples: list[dict[str, str]]) -> None:
    """Design decision: plan/changes strings are parsed and re-rendered losslessly for all 25 samples."""
    for s in samples:
        plan = parse_plan(s["payment_plan"])
        assert ("|".join(f"{p.on.isoformat()}:{p.amount_text}" for p in plan) or "none") == s["payment_plan"]
        assert render_changes(parse_changes(s["spending_changes_needed"])) == s["spending_changes_needed"]


# ----------------------------------------------------------------------------- templates
def test_every_sample_explanation_matches_its_template(samples: list[dict[str, str]]) -> None:
    """Design decision: explanations are template-generated; all 25 ground-truth texts match the template set."""
    for s in samples:
        key = template_key(s["recommended_payment_method"], s["spending_changes_needed"] != "none")
        assert EXPLANATION_PATTERNS[key].match(s["decision_explanation"]), s["request_id"]


def test_template_rejects_wrong_method_text() -> None:
    """Nearest negative: a 'wait' text does not match the affordable_now template."""
    text = "Pay ZAR 38,016 in full on 15 July 2025. Paying earlier would take the balance below the ZAR 27,000 minimum."
    assert EXPLANATION_PATTERNS["wait"].match(text)
    assert not EXPLANATION_PATTERNS["affordable_now"].match(text)


# ----------------------------------------------------------------------------- structural validation
def test_ground_truth_rows_have_zero_violations(samples: list[dict[str, str]], contexts) -> None:
    """Design decision: validate_row encodes CONTRACT §2 exactly — ground truth must pass with no violations."""
    for s in samples:
        row = {k: s[k] for k in OUTPUT_COLUMNS}
        assert validate_row(row, contexts[s["request_id"]]) == [], s["request_id"]


@pytest.mark.parametrize(
    "request_id,mutation,expect",
    [
        ("request_01", {"amount_safe_to_pay": "25257"}, "I-1"),
        ("request_01", {"amount_safe_to_pay": "25256.0"}, "format"),
        ("request_03", {"earliest_date_for_full_payment": "2019-09-03"}, "I-4"),
        ("request_05", {"payment_plan": "2025-11-06:15488"}, "I-3"),
        ("request_19", {"payment_plan": "2024-09-04:28820|2024-09-15:10841"}, "I-5"),
        ("request_02", {"payment_plan": "2025-08-08:15952906.67|2025-09-07:15952906.67"}, "I-6"),
        ("request_06", {"spending_changes_needed": "stop:event_476|stop:event_476"}, "I-8"),
        ("request_21", {"spending_changes_needed": "reduce_to:event_1816:23.50|stop:event_1815"}, "C-4"),
        ("request_11", {"spending_changes_needed": "reduce_to:event_989:700000"}, "C-6"),
        (
            "request_04",
            {
                "decision_explanation": "Pay IDR 12,693,000 in full on 15 June 2024. Paying earlier would take the balance below the IDR 30,686,601 minimum."
            },
            "explanation minimum",
        ),
        (
            "request_07",
            {
                "recommended_payment_method": "full_payment",
                "payment_plan": "2024-09-05:197400",
                "spending_changes_needed": "none",
                "decision_explanation": "Pay INR 197,400 today. This leaves at least INR 93,000 available over the next 90 days.",
            },
            "gate",
        ),
    ],
)
def test_validate_row_trips_on_each_invariant(
    samples: list[dict[str, str]], contexts, request_id: str, mutation: dict[str, str], expect: str
) -> None:
    """Design decision: each invariant has a trip case — mutate one ground-truth row and the named check fires."""
    s = next(x for x in samples if x["request_id"] == request_id)
    row = {k: s[k] for k in OUTPUT_COLUMNS}
    row.update(mutation)
    violations = validate_row(row, contexts[request_id])
    assert any(expect in v for v in violations), violations


# ----------------------------------------------------------------------------- scorer end to end
def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *cmd], cwd=cwd, capture_output=True, text=True)


def test_scorer_gives_perfect_score_on_ground_truth(tmp_path: Path, samples: list[dict[str, str]]) -> None:
    """Design decision: the scorer's metrics are 100% on the ground truth itself (sanity of the harness)."""
    pred = tmp_path / "gt.csv"
    with open(pred, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(OUTPUT_COLUMNS), lineterminator="\n")
        w.writeheader()
        for s in samples:
            w.writerow({k: s[k] for k in OUTPUT_COLUMNS})
    pin = tmp_path / "pin.json"
    res = run(
        [
            str(SCORE),
            "--predictions",
            str(pred),
            "--tag",
            "test_gt",
            "--pin",
            str(pin),
            "--baseline",
            str(tmp_path / "none.json"),
        ],
        ROOT,
    )
    assert res.returncode == 0, res.stdout + res.stderr
    metrics = json.loads((ROOT / "analysis" / "reports" / "eval_test_gt.json").read_text())["metrics"]
    for k, v in metrics.items():
        assert v == (0.0 if k == "safe_mean_err_pct" else 1.0), (k, v)
    for f in ("eval_test_gt.json", "eval_test_gt.md", "predictions/test_gt.csv"):
        (ROOT / "analysis" / "reports" / f).unlink()


def test_scorer_stops_the_line_on_regression(tmp_path: Path) -> None:
    """Design decision: any per-column regression versus the pinned run exits non-zero unless explicitly allowed."""
    base_pred = ROOT / "analysis" / "reports" / "predictions" / "baseline.csv"
    assert base_pred.exists(), "run code/evaluation/baseline.py first"
    pin = tmp_path / "pin.json"
    pin.write_text(json.dumps({"tag": "fake", "metrics": {"status_acc": 1.0}}), encoding="utf-8")
    # pinned has only status_acc; fill the rest from the real baseline so only status_acc regresses
    real = json.loads((ROOT / "analysis" / "reports" / "eval_baseline.json").read_text())["metrics"]
    fake = dict(real)
    fake["status_acc"] = 1.0
    pin.write_text(json.dumps({"tag": "fake", "metrics": fake}), encoding="utf-8")
    res = run([str(SCORE), "--predictions", str(base_pred), "--tag", "test_regress", "--pin", str(pin)], ROOT)
    assert res.returncode == 2 and "REGRESSION" in res.stdout
    res2 = run(
        [str(SCORE), "--predictions", str(base_pred), "--tag", "test_regress", "--pin", str(pin), "--allow-regression"],
        ROOT,
    )
    assert res2.returncode == 0
    for f in ("eval_test_regress.json", "eval_test_regress.md", "predictions/test_regress.csv"):
        (ROOT / "analysis" / "reports" / f).unlink()


def test_fewshot_exclusion_removes_rows_from_scoring(tmp_path: Path) -> None:
    """Design decision: ids listed as few-shot examples are never scored."""
    base_pred = ROOT / "analysis" / "reports" / "predictions" / "baseline.csv"
    excl = tmp_path / "excl.txt"
    excl.write_text("request_01\nrequest_02\n", encoding="utf-8")
    res = run(
        [
            str(SCORE),
            "--predictions",
            str(base_pred),
            "--tag",
            "test_excl",
            "--exclude",
            str(excl),
            "--pin",
            str(tmp_path / "nopin.json"),
            "--baseline",
            str(tmp_path / "nobase.json"),
        ],
        ROOT,
    )
    assert res.returncode == 0, res.stdout + res.stderr
    payload = json.loads((ROOT / "analysis" / "reports" / "eval_test_excl.json").read_text())
    assert payload["n"] == 23 and payload["excluded"] == ["request_01", "request_02"]
    for f in ("eval_test_excl.json", "eval_test_excl.md", "predictions/test_excl.csv"):
        (ROOT / "analysis" / "reports" / f).unlink()


def test_baseline_is_committed_and_imperfect() -> None:
    """Design decision: the naive baseline is a committed, deliberately weak reference — never the pinned best."""
    metrics = json.loads((ROOT / "analysis" / "reports" / "eval_baseline.json").read_text())["metrics"]
    assert 0.0 < metrics["composite"] < 1.0
    assert metrics["status_acc"] < 1.0
