#!/usr/bin/env python3
"""Validate the Hermes markdown harness structure."""

from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parent.parent


REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "docs/README.md",
    "docs/harness_engineering.md",
    "docs/problem_formulation.md",
    "docs/experiment_protocol.md",
    "docs/baselines.md",
    "docs/papers/README.md",
    "docs/papers/reading_queue.md",
    "docs/papers/review_index.md",
    "docs/papers/comparison_matrix.md",
    "docs/papers/_templates/request.md",
    "docs/papers/_templates/review.md",
    "docs/papers/requests/README.md",
    "docs/papers/reviews/README.md",
    "docs/ideas/README.md",
    "docs/ideas/_template.md",
    "docs/decisions/README.md",
    "docs/decisions/_template.md",
    "plans/README.md",
    "plans/_template/plan.md",
    "experiments/README.md",
    "experiments/runs/README.md",
    "experiments/summaries/README.md",
    "experiments/summaries/master_runs.csv",
    "experiments/summaries/_templates/phase_summary.md",
    "experiments/figures/README.md",
    "experiments/tables/README.md",
]


PAPER_HEADINGS = [
    "## Metadata",
    "## Citation",
    "## Links",
    "## Main Claims",
    "## Why It Matters For Hermes",
    "## Problem Setting",
    "## Method Summary",
    "## Experimental Setup",
    "## Strengths",
    "## Weaknesses",
    "## Reproduction Notes",
    "## Gaps Relative To Hermes",
    "## Reusable Ideas",
    "## Required Direct Comparisons",
    "## Verdict",
]

PAPER_REQUEST_HEADINGS = [
    "## Request Context",
    "## Requested Papers",
    "## Desired Output",
    "## Status",
]

IDEA_HEADINGS_EN = [
    "## One-line Thesis",
    "## Motivation",
    "## Method Sketch",
    "## Expected Gains",
    "## Failure Modes",
    "## Required Ablations",
    "## Fair Baselines",
    "## Minimum Evidence Needed",
    "## Next Step",
]

IDEA_HEADINGS_KO = [
    "## 한줄 요약",
    "## 동기",
    "## 방법 개요",
    "## 기대 효과",
    "## 실패 가능성",
    "## 필요한 소거실험",
    "## 공정 비교 기준",
    "## 최소 필요 근거",
    "## 다음 단계",
]

DECISION_HEADINGS = [
    "## Context",
    "## Decision",
    "## Alternatives Considered",
    "## Expected Impact",
    "## Revisit Triggers",
    "## Follow-up",
]

PLAN_HEADINGS_EN = [
    "## Goal",
    "## Scope",
    "## Inputs",
    "## Deliverables",
    "## Steps",
    "## Validation",
    "## Notes",
]

PLAN_HEADINGS_KO = [
    "## 목표",
    "## 범위",
    "## 입력 자료",
    "## 산출물",
    "## 단계",
    "## 검증",
    "## 메모",
]

PLAN_DATE_DIR_PATTERN = re.compile(r"^\d{8}$")
PLAN_RUN_DIR_PATTERN = re.compile(r"^\d{4}_.+")
PAPER_REQUEST_DIR_PATTERN = re.compile(r"^\d{8}_\d{4}_.+")
PAPER_REVIEW_YEAR_PATTERN = re.compile(r"^\d{4}$")
PAPER_REVIEW_DIR_PATTERN = re.compile(r"^\d{4}_.+")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_required_files(errors: list[str]) -> None:
    for rel_path in REQUIRED_FILES:
        path = ROOT / rel_path
        if not path.exists():
            errors.append(f"missing required file: {rel_path}")


def check_single_h1(path: Path, errors: list[str]) -> None:
    text = read_text(path)
    h1_count = sum(1 for line in text.splitlines() if line.startswith("# "))
    if h1_count != 1:
        errors.append(f"{path.relative_to(ROOT)} should contain exactly one H1 heading")


def check_required_headings(path: Path, headings: list[str], errors: list[str]) -> None:
    text = read_text(path)
    for heading in headings:
        if heading not in text:
            errors.append(f"{path.relative_to(ROOT)} missing heading: {heading}")


def check_required_heading_sets(
    path: Path, heading_sets: list[list[str]], errors: list[str]
) -> None:
    text = read_text(path)
    for headings in heading_sets:
        if all(heading in text for heading in headings):
            return
    flat = " or ".join("/".join(headings[:2]) for headings in heading_sets)
    errors.append(
        f"{path.relative_to(ROOT)} missing a valid heading set: {flat}"
    )


def iter_markdown_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.glob("*.md") if path.is_file())


def iter_plan_files(directory: Path) -> list[Path]:
    plan_files: list[Path] = []
    for date_dir in sorted(directory.iterdir()):
        if not date_dir.is_dir():
            continue
        if date_dir.name in {"_template", "notes"}:
            continue
        for plan_dir in sorted(date_dir.iterdir()):
            if not plan_dir.is_dir():
                continue
            plan_files.append(plan_dir / "plan.md")
    return plan_files


def iter_paper_request_files(directory: Path) -> list[Path]:
    request_files: list[Path] = []
    requests_dir = directory / "requests"
    for child in sorted(requests_dir.iterdir()):
        if not child.is_dir():
            continue
        request_files.append(child / "request.md")
    return request_files


def iter_paper_review_files(directory: Path) -> list[Path]:
    review_files: list[Path] = []
    reviews_dir = directory / "reviews"
    for year_dir in sorted(reviews_dir.iterdir()):
        if not year_dir.is_dir():
            continue
        for paper_dir in sorted(year_dir.iterdir()):
            if not paper_dir.is_dir():
                continue
            review_files.append(paper_dir / "review.md")
    return review_files


def main() -> int:
    errors: list[str] = []

    check_required_files(errors)

    for path in [
        ROOT / rel_path
        for rel_path in REQUIRED_FILES
        if (ROOT / rel_path).exists() and (ROOT / rel_path).suffix == ".md"
    ]:
        check_single_h1(path, errors)

    papers_dir = ROOT / "docs/papers"
    requests_dir = papers_dir / "requests"
    for child in sorted(requests_dir.iterdir()):
        if not child.is_dir():
            continue
        if not PAPER_REQUEST_DIR_PATTERN.match(child.name):
            errors.append(
                f"{child.relative_to(ROOT)} should match docs/papers/requests/YYYYMMDD_HHMM_short_batch"
            )
        request_path = child / "request.md"
        if not request_path.exists():
            errors.append(f"missing paper request file: {request_path.relative_to(ROOT)}")

    for path in iter_paper_request_files(papers_dir):
        if not path.exists():
            continue
        check_single_h1(path, errors)
        check_required_headings(path, PAPER_REQUEST_HEADINGS, errors)

    reviews_dir = papers_dir / "reviews"
    for year_dir in sorted(reviews_dir.iterdir()):
        if not year_dir.is_dir():
            continue
        if not PAPER_REVIEW_YEAR_PATTERN.match(year_dir.name):
            errors.append(
                f"{year_dir.relative_to(ROOT)} should match docs/papers/reviews/YYYY"
            )
        for paper_dir in sorted(year_dir.iterdir()):
            if not paper_dir.is_dir():
                continue
            if not PAPER_REVIEW_DIR_PATTERN.match(paper_dir.name):
                errors.append(
                    f"{paper_dir.relative_to(ROOT)} should match docs/papers/reviews/YYYY/YYYY_author_shorttitle"
                )
            review_path = paper_dir / "review.md"
            if not review_path.exists():
                errors.append(f"missing paper review file: {review_path.relative_to(ROOT)}")

    for path in iter_paper_review_files(papers_dir):
        if not path.exists():
            continue
        check_single_h1(path, errors)
        check_required_headings(path, PAPER_HEADINGS, errors)

    for path in iter_markdown_files(ROOT / "docs/ideas"):
        if path.name in {"README.md", "_template.md"}:
            continue
        check_single_h1(path, errors)
        check_required_heading_sets(path, [IDEA_HEADINGS_EN, IDEA_HEADINGS_KO], errors)

    for path in iter_markdown_files(ROOT / "docs/decisions"):
        if path.name in {"README.md", "_template.md"}:
            continue
        check_single_h1(path, errors)
        check_required_headings(path, DECISION_HEADINGS, errors)

    plans_dir = ROOT / "plans"
    for date_dir in sorted(plans_dir.iterdir()):
        if not date_dir.is_dir():
            continue
        if date_dir.name in {"_template", "notes"}:
            continue
        if not PLAN_DATE_DIR_PATTERN.match(date_dir.name):
            errors.append(
                f"{date_dir.relative_to(ROOT)} should match plans/YYYYMMDD"
            )
        for plan_dir in sorted(date_dir.iterdir()):
            if not plan_dir.is_dir():
                continue
            if not PLAN_RUN_DIR_PATTERN.match(plan_dir.name):
                errors.append(
                    f"{plan_dir.relative_to(ROOT)} should match plans/YYYYMMDD/HHMM_short_task_name"
                )
            plan_path = plan_dir / "plan.md"
            if not plan_path.exists():
                errors.append(f"missing plan file: {plan_path.relative_to(ROOT)}")

    for path in iter_plan_files(plans_dir):
        if not path.exists():
            continue
        check_single_h1(path, errors)
        check_required_heading_sets(path, [PLAN_HEADINGS_EN, PLAN_HEADINGS_KO], errors)

    master_runs_path = ROOT / "experiments/summaries/master_runs.csv"
    if master_runs_path.exists():
        header = master_runs_path.read_text(encoding="utf-8").splitlines()[:1]
        expected = (
            "date,run_name,dataset,model,split_layer,baseline,seed,alpha,"
            "best_test_acc,final_test_acc,time_to_target,avg_bits,avg_token_count,"
            "avg_distortion,avg_round_latency,status,notes"
        )
        if header != [expected]:
            errors.append(
                "experiments/summaries/master_runs.csv has an unexpected header"
            )

    if errors:
        print("Hermes docs validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Hermes docs validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
