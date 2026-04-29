import argparse
import contextlib
import sys
import traceback

from src.engine.sfl_trainer import SFLTrainer
from src.utils.config import load_config
from src.utils.experiment import (
    build_failure_summary,
    build_master_summary_row,
    prepare_run_context,
    upsert_master_summary_row,
)
from src.utils.io import TeeStream, dump_json


DEFAULT_CONFIG = "configs/experiment/cifar10_iid_full_token_sfl.json"


def parse_args():
    parser = argparse.ArgumentParser(description="Hermes training entrypoint")
    parser.add_argument(
        "--config",
        type=str,
        default=DEFAULT_CONFIG,
        help="Path to the experiment config file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    run_context = prepare_run_context(config, args.config)

    with run_context.stdout_log_path.open("w", encoding="utf-8") as log_handle:
        tee = TeeStream(sys.stdout, log_handle)
        with contextlib.redirect_stdout(tee), contextlib.redirect_stderr(tee):
            try:
                trainer = SFLTrainer(config, run_context)
                summary = trainer.train()
                print(summary)
            except Exception as exc:
                traceback.print_exc()
                summary = build_failure_summary(config, run_context, str(exc))
                dump_json(summary, run_context.summary_json_path)
                upsert_master_summary_row(
                    run_context.master_summary_path,
                    build_master_summary_row(summary),
                )
                raise


if __name__ == "__main__":
    main()
