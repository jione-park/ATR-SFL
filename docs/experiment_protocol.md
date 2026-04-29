# Experiment Protocol

## Purpose

This document defines the comparison contract for Hermes. If two methods are compared, they should be comparable under this protocol unless a decision note explicitly states otherwise.

## Required report fields per run

Every retained experiment run should record:

- git commit
- config path or dumped resolved config
- random seed
- dataset and split definition
- number of clients
- non-IID partition rule
- split learning cut point
- model backbone and token reduction setting
- communication metrics
- compute metrics if available
- train, validation, and test metrics

## Minimum metrics

Every serious comparison should report at least:

- top-1 accuracy or task-equivalent performance metric
- total transmitted bits
- activation bits and model update bits, if both exist
- rounds to target accuracy, if target accuracy is defined
- token keep ratio or equivalent reduction ratio
- mean and standard deviation across seeds

## Comparison rules

- Keep optimizer, training budget, and augmentation policy fixed unless the comparison requires otherwise.
- Do not give the proposed method extra tuning while leaving baselines under-tuned.
- If a method changes the compute budget substantially, report that explicitly.
- If the communication accounting changes, update this file first.

## Suggested evaluation axes

- IID vs non-IID
- small vs large client count
- favorable vs degraded wireless condition
- fixed token budget vs adaptive token budget
- fixed split point vs adaptive split point

## Evidence thresholds

Use these labels in discussion:

- `Hypothesis`: design not yet validated
- `Preliminary`: one or a few runs, not claim-ready
- `Supported`: multiple runs with direct baseline comparison
- `Claim-ready`: enough evidence for internal paper-draft use

## Result storage

- Run-level raw records: `experiments/runs/`
- Cross-run summary rows: `experiments/summaries/master_runs.csv`
- Phase interpretation notes: `experiments/summaries/*_summary.md`
- Curated tables: `experiments/tables/`
- Curated plots: `experiments/figures/`
- Interpretation and durable decisions: `docs/`
