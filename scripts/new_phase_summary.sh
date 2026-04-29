#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: bash scripts/new_phase_summary.sh short_name" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATE_STR="$(date '+%Y-%m-%d')"
SHORT_NAME="$1"
TARGET_PATH="${ROOT_DIR}/experiments/summaries/${DATE_STR}_${SHORT_NAME}.md"
TEMPLATE_PATH="${ROOT_DIR}/experiments/summaries/_templates/phase_summary.md"

if [[ -e "${TARGET_PATH}" ]]; then
  echo "Phase summary already exists: ${TARGET_PATH}" >&2
  exit 1
fi

cp "${TEMPLATE_PATH}" "${TARGET_PATH}"
echo "Created ${TARGET_PATH}"
