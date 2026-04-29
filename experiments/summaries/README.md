# Summaries

This directory contains:

- `master_runs.csv`: one row per run
- phase summary markdown files
- summary templates

## Master summary

Canonical file:

- `master_runs.csv`

Recommended columns:

- `date`
- `run_name`
- `dataset`
- `model`
- `split_layer`
- `baseline`
- `seed`
- `alpha`
- `best_test_acc`
- `final_test_acc`
- `time_to_target`
- `avg_bits`
- `avg_token_count`
- `avg_distortion`
- `avg_round_latency`
- `status`
- `notes`

## Phase summaries

Use names such as:

- `2026-05-02_cifar10_phase_summary.md`
- `2026-05-10_cifar100_main_summary.md`

Keep phase summaries brief. At minimum include:

- `Objective`
- `Runs included`
- `Key observations`
- `Decision`
