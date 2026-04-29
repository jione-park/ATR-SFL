#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: bash scripts/run_local_experiment.sh <cpu|gpu> <config_path> [extra args...]" >&2
  exit 1
fi

ENV_KIND="$1"
CONFIG_PATH="$2"
shift 2

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONDA_BIN="${ROOT_DIR}/.local/miniconda3/bin/conda"
CACHE_ROOT="${ROOT_DIR}/.local/cache"
PKGS_DIR="${ROOT_DIR}/.local/conda-pkgs"
ENVS_DIR="${ROOT_DIR}/.local/conda-envs"

case "${ENV_KIND}" in
  cpu)
    ENV_PATH="${ROOT_DIR}/.local/conda-envs/hermes"
    ;;
  gpu)
    ENV_PATH="${ROOT_DIR}/.local/conda-envs/hermes-gpu-cu121"
    ;;
  *)
    echo "Usage: bash scripts/run_local_experiment.sh <cpu|gpu> <config_path> [extra args...]" >&2
    exit 1
    ;;
esac

if [[ ! -x "${CONDA_BIN}" ]]; then
  echo "Missing conda binary at ${CONDA_BIN}. Run scripts/setup_local_miniconda.sh first." >&2
  exit 1
fi

mkdir -p "${CACHE_ROOT}" "${PKGS_DIR}" "${ENVS_DIR}"

export XDG_CACHE_HOME="${CACHE_ROOT}"
export CONDA_PKGS_DIRS="${PKGS_DIR}"
export CONDA_ENVS_PATH="${ENVS_DIR}"
export CONDA_NO_PLUGINS=true

"${CONDA_BIN}" run -p "${ENV_PATH}" python -m src.train --config "${CONFIG_PATH}" "$@"
