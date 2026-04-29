#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MINICONDA_DIR="${ROOT_DIR}/.local/miniconda3"
CONDA_BIN="${MINICONDA_DIR}/bin/conda"
CACHE_ROOT="${ROOT_DIR}/.local/cache"
PKGS_DIR="${ROOT_DIR}/.local/conda-pkgs"
ENVS_DIR="${ROOT_DIR}/.local/conda-envs"
PIP_CACHE_DIR="${ROOT_DIR}/.local/pip-cache"
REQUIREMENTS_FILE="${ROOT_DIR}/conda/requirements.runtime.txt"
TMPDIR_PATH="${ROOT_DIR}/.local/tmp"

ENV_KIND="${1:-cpu}"
case "${ENV_KIND}" in
  cpu)
    ENV_PATH="${ROOT_DIR}/.local/conda-envs/hermes"
    TORCH_INDEX_URL="https://download.pytorch.org/whl/cpu"
    ;;
  gpu)
    ENV_PATH="${ROOT_DIR}/.local/conda-envs/hermes-gpu-cu121"
    TORCH_INDEX_URL="https://download.pytorch.org/whl/cu121"
    ;;
  *)
    echo "Usage: bash scripts/create_local_conda_env.sh <cpu|gpu>" >&2
    exit 1
    ;;
esac

if [[ ! -x "${CONDA_BIN}" ]]; then
  echo "Missing conda binary at ${CONDA_BIN}. Run scripts/setup_local_miniconda.sh first." >&2
  exit 1
fi

mkdir -p "${ENVS_DIR}" "${CACHE_ROOT}" "${PKGS_DIR}" "${PIP_CACHE_DIR}" "${TMPDIR_PATH}"

export XDG_CACHE_HOME="${CACHE_ROOT}"
export CONDA_PKGS_DIRS="${PKGS_DIR}"
export CONDA_ENVS_PATH="${ENVS_DIR}"
export CONDA_NO_PLUGINS=true
export CONDA_SOLVER=classic
export PIP_CACHE_DIR="${PIP_CACHE_DIR}"
export PIP_NO_CACHE_DIR=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
export TMPDIR="${TMPDIR_PATH}"

if [[ -x "${ENV_PATH}/bin/python" ]]; then
  echo "Reusing existing ${ENV_KIND} env at ${ENV_PATH}"
else
  echo "Creating ${ENV_KIND} conda env at ${ENV_PATH}"
  "${CONDA_BIN}" create -y -p "${ENV_PATH}" python=3.11 pip --solver classic
fi

echo "Installing PyTorch from ${TORCH_INDEX_URL}"
echo "Installing Python packages from ${REQUIREMENTS_FILE}"
"${CONDA_BIN}" run -p "${ENV_PATH}" python -m pip install --upgrade pip
"${CONDA_BIN}" run -p "${ENV_PATH}" python -m pip install --no-cache-dir --index-url "${TORCH_INDEX_URL}" torch==2.5.1 torchvision==0.20.1
"${CONDA_BIN}" run -p "${ENV_PATH}" python -m pip install -r "${REQUIREMENTS_FILE}"

echo "${ENV_KIND} conda env ready at ${ENV_PATH}"
