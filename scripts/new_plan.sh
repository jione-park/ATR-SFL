#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: bash scripts/new_plan.sh short_task_name" >&2
  exit 1
fi

slug="$1"
timestamp="$(date '+%Y%m%d_%H%M')"
date_part="${timestamp%%_*}"
time_part="${timestamp##*_}"
date_dir="plans/${date_part}"
plan_dir="${date_dir}/${time_part}_${slug}"

if [[ -e "${plan_dir}" ]]; then
  echo "plan directory already exists: ${plan_dir}" >&2
  exit 1
fi

mkdir -p "${plan_dir}"
cp "plans/_template/plan.md" "${plan_dir}/plan.md"

echo "created ${plan_dir}/plan.md"
