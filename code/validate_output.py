"""Validate an output.csv against CONTRACT.md before submission (Phase 5).

Re-asserts every structural invariant on every row: header and row order versus the template, allowed enums and
status/method pairs, amount bounds and formatting, plan arithmetic and chronology, installment schedules matching a
supplied option, spending-change FK validity and permissions, explanation template consistency. Exits non-zero
with the full violation list on any failure; prints a one-line OK otherwise.

Usage (repo root):  python3 code/validate_output.py [output.csv]
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import buyorwait  # noqa: F401  (installed with `pip install -e .`)
except ImportError:  # running from an unpacked code.zip without installing: use the bundled src/ package
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from buyorwait.contract import OUTPUT_COLUMNS, validate_row
from buyorwait.io_dataset import build_row_contexts, load_csv

ROOT = Path(__file__).resolve().parents[1]


def validate(path: Path, dataset_dir: Path) -> list[str]:
    problems: list[str] = []
    rows = load_csv(path)
    template = load_csv(dataset_dir / "output.csv")
    if not rows:
        return ["output has no rows"]
    if tuple(rows[0].keys()) != OUTPUT_COLUMNS:
        problems.append(f"header {tuple(rows[0].keys())} != {OUTPUT_COLUMNS}")
    if [r["request_id"] for r in rows] != [t["request_id"] for t in template]:
        problems.append(
            f"request ids/order differ from dataset/output.csv template ({len(rows)} rows vs {len(template)})"
        )
    ctxs = build_row_contexts(dataset_dir, "requests.csv")
    for r in rows:
        ctx = ctxs.get(r["request_id"])
        if ctx is None:
            problems.append(f"{r['request_id']}: unknown request id")
            continue
        for v in validate_row(r, ctx):
            problems.append(f"{r['request_id']}: {v}")
        if any(not r[c] for c in OUTPUT_COLUMNS if c != "earliest_date_for_full_payment"):
            problems.append(f"{r['request_id']}: empty cell in a required column")
    return problems


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else ROOT / "output.csv"
    problems = validate(path, ROOT / "dataset")
    if problems:
        print(f"INVALID: {len(problems)} problem(s) in {path}")
        for p in problems:
            print("  " + p)
        return 1
    print(f"OK: {path} passes every CONTRACT invariant ({len(load_csv(path))} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
