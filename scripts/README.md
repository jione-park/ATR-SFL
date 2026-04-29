# Scripts Guide

Hermes keeps only a small set of canonical scripts in this directory.

## Environment setup

- `setup_local_miniconda.sh`
  - install workspace-local Miniconda
- `create_local_conda_env.sh`
  - create or refresh a local conda env
  - usage: `bash scripts/create_local_conda_env.sh cpu`
  - usage: `bash scripts/create_local_conda_env.sh gpu`
- `check_local_conda_env.sh`
  - verify a local conda env
  - usage: `bash scripts/check_local_conda_env.sh cpu`
  - usage: `bash scripts/check_local_conda_env.sh gpu`

## Experiment execution

- `run_experiment.sh`
  - direct Python entrypoint without Conda wrapping
- `run_local_experiment.sh`
  - run an experiment through a local conda env
  - usage: `bash scripts/run_local_experiment.sh gpu configs/experiment/cifar10_iid_full_token_sfl_sanity_gpu.json`

## Experiment summaries

- `rebuild_master_runs.py`
  - rebuild `experiments/summaries/master_runs.csv`
- `new_phase_summary.sh`
  - create a phase summary markdown scaffold

## Research markdown scaffolds

- `new_plan.sh`
- `new_paper_request.sh`
- `new_paper_review.sh`

## Validation

- `validate_docs.py`
