#!/usr/bin/env python3
"""Rebuild experiments/summaries/master_runs.csv from per-run summary.json files."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.experiment import (  # noqa: E402
    build_master_summary_row,
    ensure_master_summary_file,
    load_summary_json,
    upsert_master_summary_row,
)


RUNS_DIR = ROOT / "experiments" / "runs"
MASTER_SUMMARY_PATH = ROOT / "experiments" / "summaries" / "master_runs.csv"


def main() -> int:
    ensure_master_summary_file(MASTER_SUMMARY_PATH)
    MASTER_SUMMARY_PATH.unlink(missing_ok=True)
    ensure_master_summary_file(MASTER_SUMMARY_PATH)

    for summary_path in sorted(RUNS_DIR.glob("**/summary.json")):
        run_dir = summary_path.parent
        if not summary_path.exists():
            continue
        summary = load_summary_json(summary_path)
        upsert_master_summary_row(
            MASTER_SUMMARY_PATH,
            build_master_summary_row(summary),
        )

    print(f"Rebuilt {MASTER_SUMMARY_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
