#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: bash scripts/new_paper_request.sh short_batch_name" >&2
  exit 1
fi

slug="$1"
timestamp="$(date '+%Y%m%d_%H%M')"
request_dir="docs/papers/requests/${timestamp}_${slug}"

if [[ -e "${request_dir}" ]]; then
  echo "request directory already exists: ${request_dir}" >&2
  exit 1
fi

mkdir -p "${request_dir}"
cp "docs/papers/_templates/request.md" "${request_dir}/request.md"

echo "created ${request_dir}/request.md"
