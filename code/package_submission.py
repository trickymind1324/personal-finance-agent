"""Build code.zip for submission and verify it reproduces output.csv offline from a fresh unpack.

Contents (relative to the repository root): the runnable solution (code/, src/, pyproject.toml), prompts/,
data/cache/model/ and data/evidence/, evaluation/ (usage reports + the submitted output as
evaluation/output.reference.csv), README.md, CONTRACT.md, FAILURES.md, tests/, analysis/reports/, and
dataset/ so the unpack is self-contained. Excluded: .env, log.txt, .git, caches, build artefacts, output.csv at
the root (the reproduction writes it).

Verification: unzip into a temporary directory, run `python3 code/main.py --model-evidence --offline` there with
no API key in the environment, and require the produced output.csv to be byte-identical to the submitted one.

Usage (repo root):  python3 code/package_submission.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZIP = ROOT / "code.zip"
INCLUDE_DIRS = ("code", "src", "prompts", "data", "evaluation", "tests", "analysis", "dataset")
INCLUDE_FILES = ("README.md", "CONTRACT.md", "FAILURES.md", "pyproject.toml", "requirements.txt", ".env.example", ".gitignore")
EXCLUDE_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".git", "build", "dist"}
EXCLUDE_SUFFIXES = (".pyc", ".egg-info")


def wanted(path: Path) -> bool:
    if any(part in EXCLUDE_PARTS or part.endswith(".egg-info") for part in path.parts):
        return False
    return not path.name.endswith(EXCLUDE_SUFFIXES)


def build() -> list[str]:
    if not (ROOT / "output.csv").exists():
        raise SystemExit("output.csv is missing at the repository root; nothing to package")
    names: list[str] = []
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in INCLUDE_FILES:
            zf.write(ROOT / f, f)
            names.append(f)
        for d in INCLUDE_DIRS:
            for p in sorted((ROOT / d).rglob("*")):
                if p.is_file() and wanted(p.relative_to(ROOT)):
                    rel = p.relative_to(ROOT).as_posix()
                    zf.write(p, rel)
                    names.append(rel)
        zf.write(ROOT / "output.csv", "evaluation/output.reference.csv")
        names.append("evaluation/output.reference.csv")
    return names


def verify() -> None:
    with tempfile.TemporaryDirectory(prefix="buyorwait_verify_") as tmp:
        with zipfile.ZipFile(ZIP) as zf:
            zf.extractall(tmp)
        env = {k: v for k, v in os.environ.items() if not k.startswith("ANTHROPIC")}
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        res = subprocess.run(
            [sys.executable, "code/main.py", "--model-evidence", "--offline"],
            cwd=tmp,
            env=env,
            capture_output=True,
            text=True,
            timeout=1800,
        )
        if res.returncode != 0:
            raise SystemExit(f"offline reproduction FAILED in the unpacked zip:\n{res.stderr[-2000:]}")
        produced = (Path(tmp) / "output.csv").read_bytes()
        reference = (ROOT / "output.csv").read_bytes()
        if produced != reference:
            raise SystemExit("offline reproduction produced a DIFFERENT output.csv than the submitted one")
        val = subprocess.run([sys.executable, "code/validate_output.py"], cwd=tmp, env=env, capture_output=True, text=True)
        if val.returncode != 0:
            raise SystemExit(f"validator failed inside the unpacked zip:\n{val.stdout[-2000:]}")
        print("verified: fresh unpack reproduces output.csv byte-identically without an API key, and validates")


def main() -> None:
    names = build()
    size_mb = ZIP.stat().st_size / 1e6
    print(f"wrote {ZIP} ({size_mb:.1f} MB, {len(names)} files)")
    verify()
    shutil.rmtree(ROOT / "build", ignore_errors=True)


if __name__ == "__main__":
    main()
