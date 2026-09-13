"""Buy or Wait? — command-line entry point.

Full run (writes output.csv in the repository root):
    python3 code/main.py

Sample run (writes analysis/reports/predictions/<tag>.csv, never output.csv):
    python3 code/main.py --samples --tag core_v1

Options:
    --limit N / --dry-run   write to output.subset.csv (never output.csv)
    --overwrite-output      required to replace an existing output.csv (the confirmed submission is never
                            overwritten by accident; a fresh checkout has no output.csv and needs no flag)
    --evidence PATH         JSON of hand-encoded amendments by user_id (ablation / manual evidence)
    --model-evidence        resolve images and messages through the model layer (Phase 4; cached)
    --set KEY=VALUE         override a Config tunable (repeatable), e.g. --set VARIABLE_AMOUNT_STAT=p75
    --explain REQUEST_ID    print the rationale and streams for one request

Secrets: ANTHROPIC_API_KEY from the environment only (see .env.example). Deterministic given the cache.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

try:
    import buyorwait  # noqa: F401  (installed with `pip install -e .`)
except ImportError:  # running from an unpacked code.zip without installing: use the bundled src/ package
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from buyorwait.config import DEFAULT_CONFIG, Config
from buyorwait.contract import OUTPUT_COLUMNS
from buyorwait.io_dataset import load_dataset
from buyorwait.ledger import UnresolvedAmountError
from buyorwait.models import Amendment, Dataset
from buyorwait.pipeline import decide

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset"


def load_dotenv(path: Path) -> None:
    """Load KEY=VALUE lines from .env into the environment if not already set. Values are never printed or logged."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_manual_evidence(path: Path) -> dict[str, list[Amendment]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, list[Amendment]] = {}
    for user_id, items in raw.items():
        if user_id.startswith("_"):
            continue
        out[user_id] = [
            Amendment(
                kind=i["kind"],
                target=i["target"],
                source_id=i["source_id"],
                amount=Decimal(i["amount"]) if "amount" in i else None,
                currency=i.get("currency"),
                effective_from=date.fromisoformat(i["effective_from"]) if "effective_from" in i else None,
                factor=Decimal(i["factor"]) if "factor" in i else None,
                partial=bool(i.get("partial", False)),
                note=i.get("note", ""),
            )
            for i in items
        ]
    return out


def run(
    dataset: Dataset,
    use_samples: bool,
    evidence: dict[str, list[Amendment]],
    cfg: Config,
    limit: int | None,
    explain: str | None,
    skip_unresolved: bool = False,
) -> list[dict[str, str]]:
    requests = dataset.samples if use_samples else dataset.requests
    if limit is not None:
        requests = requests[:limit]
    rows: list[dict[str, str]] = []
    for r in requests:
        try:
            d = decide(r, dataset, evidence.get(r.user_id, []), cfg)
        except UnresolvedAmountError as exc:
            if not skip_unresolved:
                raise
            print(f"skipped {r.request_id}: {exc}", file=sys.stderr)
            continue
        rows.append(d.row)
        if explain == r.request_id:
            print(json.dumps(d.row, indent=2))
            print("streams:")
            for s in d.stream_summary:
                print("  ", s)
            print("notes:")
            for n in d.rationale.notes:
                print("  ", n)
    return rows


def write_rows(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(OUTPUT_COLUMNS), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--samples", action="store_true", help="run on dataset/sample_requests.csv instead of requests.csv")
    ap.add_argument("--tag", default="run", help="name for sample-run predictions under analysis/reports/predictions/")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--evidence", type=Path, help="manual evidence JSON (by user_id)")
    ap.add_argument(
        "--model-evidence",
        action="store_true",
        help="resolve evidence through the model layer (cached under data/cache/model)",
    )
    ap.add_argument("--model", default="claude-opus-5", help="model id for the evidence layer")
    ap.add_argument(
        "--offline",
        action="store_true",
        help="replay the committed cache only; raise on any cache miss (keyless reproduction)",
    )
    ap.add_argument(
        "--perception-only",
        action="store_true",
        help="run the evidence layer, write analysis/reports/perception_review.md, and stop (Phase 4 checkpoint)",
    )
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--explain", metavar="REQUEST_ID")
    ap.add_argument(
        "--skip-unresolved",
        action="store_true",
        help="ablation only: skip requests whose blank amounts have no evidence",
    )
    ap.add_argument("--out", type=Path, help="explicit output path (default: output.csv for full runs)")
    ap.add_argument("--overwrite-output", action="store_true", help="allow replacing an existing output.csv")
    args = ap.parse_args(argv)

    load_dotenv(ROOT / ".env")
    overrides = dict(kv.split("=", 1) for kv in args.set)
    cfg = DEFAULT_CONFIG.with_overrides(overrides)
    dataset = load_dataset(DATASET)
    evidence: dict[str, list[Amendment]] = {}
    if args.evidence:
        evidence = load_manual_evidence(args.evidence)
    if args.model_evidence or args.perception_only:
        from buyorwait.evidence.resolver import resolve_all

        targets = dataset.samples if args.samples else dataset.requests
        if args.limit is not None:
            targets = targets[: args.limit]
        review = ROOT / "analysis" / "reports" / ("perception_review_samples.md" if args.samples else "perception_review.md")
        usage_report = ROOT / "evaluation" / ("usage_report_samples.md" if args.samples else "usage_report.md")
        offline = args.offline or os.environ.get("BUYORWAIT_OFFLINE") == "1"
        evidence = resolve_all(
            dataset, targets, cfg, ROOT, model=args.model, offline=offline, review_path=review, usage_path=usage_report
        )
        print(f"evidence resolved for {len(targets)} requests; review: {review}; usage: {usage_report}")
        if args.perception_only:
            return 0
    rows = run(dataset, args.samples, evidence, cfg, args.limit, args.explain, args.skip_unresolved)

    if args.out is not None:
        out = args.out
    elif args.samples:
        out = ROOT / "analysis" / "reports" / "predictions" / f"{args.tag}.csv"
    elif args.limit is not None or args.dry_run:
        out = ROOT / "output.subset.csv"
    else:
        out = ROOT / "output.csv"
    if out == ROOT / "output.csv" and out.exists() and not args.overwrite_output:
        print(
            f"refusing to overwrite existing {out} (pass --overwrite-output, or --out PATH to write elsewhere)",
            file=sys.stderr,
        )
        return 3
    write_rows(rows, out)
    print(f"wrote {out} ({len(rows)} rows) config_overrides={overrides or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
