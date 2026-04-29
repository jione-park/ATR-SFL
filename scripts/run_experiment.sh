#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f src/train.py ]]; then
  echo "src/train.py is missing. Implement the training entry point before using this script." >&2
  exit 1
fi

python -m src.train "$@"
