# Docker Guide

The Docker setup is the default reproducible environment for Hermes.

## Principles

- build one standard environment for experiments
- mount `data/`, `artifacts/`, and `results/` from the host
- preserve the image tag and git commit used for any important result
- treat the container as the official execution environment, not an optional convenience

## Compose files

- `docker/compose.cpu.yml`
  - default for bootstrap sanity runs
- `docker/compose.gpu.yml`
  - for later GPU-backed experiments

## Basic commands

Build CPU image:

    docker compose -f docker/compose.cpu.yml build

Open a CPU shell:

    docker compose -f docker/compose.cpu.yml run --rm research bash

Run the CIFAR-10 sanity experiment:

    docker compose -f docker/compose.cpu.yml run --rm research bash scripts/run_experiment.sh --config configs/experiment/cifar10_iid_full_token_sfl_sanity.json

## Notes

- The default `Dockerfile` starts from a CPU-safe Python base image.
- For GPU training, override `BASE_IMAGE` to a CUDA-capable image that matches your host setup and re-pin the deep learning stack if needed.
- The first execution target is `CIFAR-10 + IID + full-token + DeiT-Tiny` sanity validation, not a full paper-scale run.
- The host user must have access to the Docker daemon. If `docker compose build` fails with a socket permission error, fix host-side Docker permissions first.
