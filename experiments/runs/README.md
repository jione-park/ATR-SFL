# Run Records

This directory contains run records grouped by date.

Directory layout:

- `experiments/runs/YYYY-MM-DD/HHMMSS_dataset_model_setting_keyparams_seedX/`

Each run folder name should make the rough setting visible without opening the folder.

Minimum required files per run:

- `config.yaml`
- `metrics.csv`
- `summary.json`
- `stdout.log`
- `notes.md`
- `checkpoints/`
- `plots/`

If a run fails after the run directory is created, keep the folder and store the failure in `summary.json` instead of deleting the record.
