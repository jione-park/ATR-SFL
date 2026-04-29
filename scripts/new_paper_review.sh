#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: bash scripts/new_paper_review.sh paper_year author_shorttitle_slug" >&2
  exit 1
fi

paper_year="$1"
slug="$2"
review_dir="docs/papers/reviews/${paper_year}/${paper_year}_${slug}"

if [[ -e "${review_dir}" ]]; then
  echo "review directory already exists: ${review_dir}" >&2
  exit 1
fi

mkdir -p "${review_dir}"
cp "docs/papers/_templates/review.md" "${review_dir}/review.md"

echo "created ${review_dir}/review.md"
