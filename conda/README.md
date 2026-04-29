# Conda Guide

This directory stores local Conda environment definitions for Hermes.

Current intended use:

- local fallback when Docker execution is blocked by host permissions
- CPU sanity validation for `CIFAR-10 + IID + full-token + DeiT-Tiny`
- GPU training fallback for actual Hermes experiments when Docker GPU execution is unavailable

Recommended paths:

- Miniconda root: `/home/jiwon/research/hermes/.local/miniconda3`
- CPU env: `/home/jiwon/research/hermes/.local/conda-envs/hermes`
- GPU env: `/home/jiwon/research/hermes/.local/conda-envs/hermes-gpu-cu121`
- cache root: `/home/jiwon/research/hermes/.local/cache`
- package cache: `/home/jiwon/research/hermes/.local/conda-pkgs`

Recommended workflow:

1. `bash scripts/setup_local_miniconda.sh`
2. CPU sanity only:
   - `bash scripts/create_local_conda_env.sh cpu`
   - `bash scripts/check_local_conda_env.sh cpu`
   - `bash scripts/run_local_experiment.sh cpu configs/experiment/cifar10_iid_full_token_sfl_sanity.json`
3. GPU training path:
   - `bash scripts/create_local_conda_env.sh gpu`
   - `bash scripts/check_local_conda_env.sh gpu`
   - `bash scripts/run_local_experiment.sh gpu configs/experiment/cifar10_iid_full_token_sfl_sanity_gpu.json`

Use `conda run -p <env_path>` instead of shell activation when possible.

The helper scripts force Conda caches into the workspace so that the environment does not depend on writable access to `~/.cache`.

The current bootstrap strategy is:

- create a minimal Conda env with `python` and `pip`
- install `torch` and `torchvision` from the CPU-only PyTorch wheel index
- install the remaining runtime stack from [requirements.runtime.txt](/home/jiwon/research/hermes/conda/requirements.runtime.txt)

CPU env strategy:

- create a minimal Conda env with `python` and `pip`
- install `torch` and `torchvision` from the CPU-only PyTorch wheel index
- install the remaining runtime stack from [requirements.runtime.txt](/home/jiwon/research/hermes/conda/requirements.runtime.txt)

GPU env strategy:

- create a separate env instead of mutating the CPU sanity env
- install `torch` and `torchvision` from the CUDA 12.1 PyTorch wheel index
- keep the rest of the runtime stack aligned with the CPU env

The CPU env is for bootstrap validation only. Real Hermes training should move to the GPU env once the code path is stable enough to justify longer runs.
