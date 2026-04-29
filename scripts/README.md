# Scripts Guide

Hermes keeps only a small set of execution helpers in this directory.

## Execution

- `run_experiment.sh`
  - direct Python entrypoint
- `run_local_experiment.sh`
  - direct config-based launcher using the current Python environment
  - usage: `bash scripts/run_local_experiment.sh configs/experiment/cifar10_iid_full_token_sfl_sanity_gpu.json`
