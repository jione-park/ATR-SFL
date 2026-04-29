#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONDA_BIN="${ROOT_DIR}/.local/miniconda3/bin/conda"
CACHE_ROOT="${ROOT_DIR}/.local/cache"
PKGS_DIR="${ROOT_DIR}/.local/conda-pkgs"
ENVS_DIR="${ROOT_DIR}/.local/conda-envs"

ENV_KIND="${1:-cpu}"
case "${ENV_KIND}" in
  cpu)
    ENV_PATH="${ROOT_DIR}/.local/conda-envs/hermes"
    ;;
  gpu)
    ENV_PATH="${ROOT_DIR}/.local/conda-envs/hermes-gpu-cu121"
    ;;
  *)
    echo "Usage: bash scripts/check_local_conda_env.sh <cpu|gpu>" >&2
    exit 1
    ;;
esac

if [[ ! -x "${CONDA_BIN}" ]]; then
  echo "Missing conda binary at ${CONDA_BIN}" >&2
  exit 1
fi

mkdir -p "${CACHE_ROOT}" "${PKGS_DIR}" "${ENVS_DIR}"

export XDG_CACHE_HOME="${CACHE_ROOT}"
export CONDA_PKGS_DIRS="${PKGS_DIR}"
export CONDA_ENVS_PATH="${ENVS_DIR}"
export CONDA_NO_PLUGINS=true

"${CONDA_BIN}" run --no-capture-output -p "${ENV_PATH}" python - <<'PY'
import torch
import torchvision
import timm
print("torch", torch.__version__)
print("torchvision", torchvision.__version__)
print("timm", timm.__version__)
print("cuda_available", torch.cuda.is_available())
print("cuda_device_count", torch.cuda.device_count())
if torch.cuda.is_available():
    print("cuda_device_name", torch.cuda.get_device_name(0))
    print("torch_cuda_version", torch.version.cuda)
PY
