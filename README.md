# Hermes

Hermes is a research repository for studying communication-efficient federated split learning with ViT-family models in wireless environments.

The immediate goal is not to collect disconnected experiments. The goal is to build a research harness that lets a human researcher and an agent collaborate on:

- reading papers and preserving structured review notes
- turning hypotheses into controlled experiment plans
- running reproducible experiments
- upgrading claims only when evidence is strong enough

## Repository map

- `AGENTS.md`: operating rules for coding agents and human-agent collaboration
- `docs/`: problem definition, protocols, baselines, paper reviews, ideas, and decisions
- `plans/`: timestamped plan directories for large tasks or experiments
- `configs/`: experiment configuration files
- `src/`: implementation code
- `scripts/`: small set of canonical validation, scaffold, and execution scripts
- `experiments/`: canonical run records, summaries, figures, and tables
- `docker/`: reproducible container environment
- `conda/`: local fallback environment definitions
- `artifacts/`: legacy pre-standardization bootstrap outputs
- `data/`: dataset location instructions only; do not commit raw datasets

## First reading order

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/harness_engineering.md`
4. `docs/problem_formulation.md`
5. `docs/experiment_protocol.md`
6. `docs/baselines.md`

## For External AI Tools

If an external AI tool indexes this repository, use the following reading order first:

1. `AGENTS.md`
2. `docs/problem_formulation.md`
3. `docs/experiment_protocol.md`
4. `docs/baselines.md`
5. latest active `plans/YYYYMMDD/*/plan.md`

Treat `AGENTS.md` and the documents under `docs/` as the source of truth. Do not infer the protocol from stale experiment outputs alone.

## Current status

This repository now contains:

- research harness and documentation scaffold
- FeSViBS reference snapshot under `third_party/`
- bootstrap `CIFAR-10 + IID + full-token + DeiT-Tiny` training-time SFL code path
- Docker and local Conda execution paths for early sanity validation
