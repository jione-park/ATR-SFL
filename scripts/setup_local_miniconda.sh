#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MINICONDA_DIR="${ROOT_DIR}/.local/miniconda3"
INSTALLER_PATH="/tmp/Miniconda3-latest-Linux-x86_64.sh"
INSTALLER_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"

mkdir -p "${ROOT_DIR}/.local"

if [[ -x "${MINICONDA_DIR}/bin/conda" ]]; then
  echo "Miniconda already installed at ${MINICONDA_DIR}"
  exit 0
fi

if [[ ! -f "${INSTALLER_PATH}" ]]; then
  echo "Downloading Miniconda installer..."
  curl -fsSL -o "${INSTALLER_PATH}" "${INSTALLER_URL}"
fi

echo "Installing Miniconda to ${MINICONDA_DIR}"
bash "${INSTALLER_PATH}" -b -p "${MINICONDA_DIR}"

echo "Installed ${MINICONDA_DIR}/bin/conda"
