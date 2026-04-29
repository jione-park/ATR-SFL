#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: bash scripts/run_local_experiment.sh <config_path> [extra args...]" >&2
  exit 1
fi

CONFIG_PATH="$1"
shift
PYTHON_BIN="${PYTHON_BIN:-python}"

"${PYTHON_BIN}" -m src.train --config "${CONFIG_PATH}" "$@"
