# Experiment Records

Hermes stores experiment records under `experiments/`.

## Structure

- `runs/`: date-grouped run directories
- `summaries/`: cross-run summaries and phase summary markdown
- `figures/`: exported figures used in discussion or drafts
- `tables/`: exported tables used in discussion or drafts

## Core rule

One experiment run equals:

- one run directory under `runs/YYYY-MM-DD/`
- one summary record in `summaries/master_runs.csv`

## Run directory naming

Run directory names should follow:

`YYYY-MM-DD_HHMMSS_dataset_model_setting_baseline_seedX`

Examples:

- `2026-04-28_201100_cifar10_deittiny_sfl_split6_fulltoken_seed1`
- `2026-04-28_201530_cifar10_deittiny_sfl_split6_fixedk32_seed1`
- `2026-04-28_201945_cifar10_deittiny_sfl_split6_chanadapt_seed1`
- `2026-04-28_202410_cifar100_deittiny_sfl_split6_boundaware_seed2`

Rules:

- include date first
- include dataset, model, experiment type, baseline, and seed
- no spaces
- do not use ambiguous names such as `final`, `new2`, or `tmp`
- if the same setting is rerun on the same date, add a meaningful `tag`

Run path contract

Each run path should follow:

- `experiments/runs/YYYY-MM-DD/HHMMSS_dataset_model_setting_baseline_seedX/`

Run directory contract:

Each run directory should contain:

- `config.yaml`
- `metrics.csv`
- `summary.json`
- `stdout.log`
- `notes.md`
- `checkpoints/`
- `plots/`

Extra files such as `metadata.json` or `metrics_history.json` are allowed.

## Metrics definitions

Current Hermes bootstrap uses these definitions:

- `avg_bits`: mean round-trip bits per participating client in that round
- `avg_token_count`: mean transmitted token count per example
- `avg_token_ratio`: `avg_token_count / full_token_count`
- `round_latency`: current run-time latency proxy for that round
- `cumulative_latency`: cumulative sum of `round_latency`
- `avg_distortion`: optional distortion proxy; empty until a method defines it

Until the wireless latency model is fully implemented, `round_latency` is a wall-clock proxy.

## Raw vs summary

- raw per-round outputs live inside `runs/YYYY-MM-DD/<run_dir>/`
- cross-run summary rows live in `summaries/master_runs.csv`
- higher-level interpretation lives in phase summary markdown under `summaries/`

Any figure or table should be traceable back to one or more run directories.
