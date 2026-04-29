# Hermes

Hermes is a public code-first repository for studying communication-efficient federated split learning with ViT-family models in wireless environments.

This repo intentionally tracks only the runnable code surface:

- `src/`
- `configs/`
- `scripts/`
- `README.md`
- `AGENTS.md`

Research notes, plans, vendor snapshots, datasets, and experiment outputs are kept out of version control in this public repo.
Those directories may still exist locally for research work. In particular, `docs/`, `plans/`, `experiments/`, `data/`, `docker/`, `conda/`, and `third_party/` are part of the local workspace but are intentionally not tracked in the public git history.

## Repository map

- `AGENTS.md`: operating rules for coding agents and public-repo scope
- `configs/`: versioned experiment configurations
- `scripts/`: execution helpers
- `src/`: implementation code

## First reading order

1. `AGENTS.md`
2. `README.md`
3. `configs/README.md`
4. `src/README.md`
5. one config under `configs/experiment/`
6. `src/train.py`
7. `src/engine/sfl_trainer.py`

## For External AI Tools

If an external AI tool indexes this repository, read in this order:

1. `AGENTS.md`
2. `README.md`
3. `configs/README.md`
4. `src/README.md`
5. `configs/experiment/*.json`
6. `src/train.py`
7. `src/engine/sfl_trainer.py`

Treat `AGENTS.md`, `README.md`, `configs/`, and `src/` as the source of truth.

## Current status

This repository currently contains:

- bootstrap `CIFAR-10/CIFAR-100 + DeiT-Tiny` training-time SFL code
- two protocol names used consistently in code and configs
  - `sequential_server_bootstrap`
  - `parallel_round_server_tail`
- local research records and run outputs may still be written under ignored paths such as `docs/`, `plans/`, `data/`, and `experiments/`
