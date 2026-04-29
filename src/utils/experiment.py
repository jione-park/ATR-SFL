from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List

from src.utils.io import dump_text, dump_yaml


BASELINE_VOCAB = {
    "fulltoken",
    "fixedk32",
    "fixedk48",
    "chanadapt",
    "boundaware",
    "oracle",
}

MODEL_ALIASES = {
    "deit_tiny_patch16_224": "deittiny",
}

METRICS_COLUMNS = [
    "round",
    "train_loss",
    "test_acc",
    "val_acc",
    "avg_bits",
    "avg_token_count",
    "avg_token_ratio",
    "avg_distortion",
    "avg_client_latency",
    "avg_server_latency",
    "round_latency",
    "cumulative_latency",
    "avg_snr",
    "max_client_latency",
    "participating_clients",
    "train_acc",
    "grad_norm_proxy",
    "total_bits",
    "avg_uplink_bits",
    "avg_downlink_bits",
    "status",
]

MASTER_RUNS_COLUMNS = [
    "date",
    "run_name",
    "dataset",
    "model",
    "split_layer",
    "baseline",
    "seed",
    "alpha",
    "best_test_acc",
    "final_test_acc",
    "time_to_target",
    "avg_bits",
    "avg_token_count",
    "avg_distortion",
    "avg_round_latency",
    "status",
    "notes",
]


@dataclass(frozen=True)
class RunContext:
    run_name: str
    run_dir: Path
    config_path: Path
    stdout_log_path: Path
    notes_path: Path
    checkpoints_dir: Path
    plots_dir: Path
    metrics_csv_path: Path
    metrics_history_path: Path
    summary_json_path: Path
    metadata_json_path: Path
    master_summary_path: Path


def prepare_run_context(config: Dict[str, Any], config_source_path: str) -> RunContext:
    storage = config["storage"]
    run_root = Path(storage["run_root"])
    summary_root = Path(storage["summary_root"])
    figure_root = Path(storage["figure_root"])
    table_root = Path(storage["table_root"])

    for root in (run_root, summary_root, figure_root, table_root):
        root.mkdir(parents=True, exist_ok=True)

    run_name = resolve_run_name(config)
    run_dir = resolve_run_directory(run_root, config, run_name)
    if run_dir.exists():
        raise FileExistsError(
            f"Run directory already exists: {run_dir}. "
            "Change exp.run_name or exp.tag to create a distinct record."
        )

    checkpoints_dir = run_dir / "checkpoints"
    plots_dir = run_dir / "plots"
    checkpoints_dir.mkdir(parents=True, exist_ok=False)
    plots_dir.mkdir(parents=True, exist_ok=False)

    context = RunContext(
        run_name=run_name,
        run_dir=run_dir,
        config_path=run_dir / "config.yaml",
        stdout_log_path=run_dir / "stdout.log",
        notes_path=run_dir / "notes.md",
        checkpoints_dir=checkpoints_dir,
        plots_dir=plots_dir,
        metrics_csv_path=run_dir / "metrics.csv",
        metrics_history_path=run_dir / "metrics_history.json",
        summary_json_path=run_dir / "summary.json",
        metadata_json_path=run_dir / "metadata.json",
        master_summary_path=summary_root / "master_runs.csv",
    )

    dump_yaml(config, context.config_path)
    dump_text(build_run_notes_template(run_name, config, config_source_path), context.notes_path)
    write_metrics_csv(context.metrics_csv_path, [])
    ensure_master_summary_file(context.master_summary_path)
    return context


def resolve_run_directory(run_root: Path, config: Dict[str, Any], run_name: str) -> Path:
    exp = config["exp"]
    date_token = str(exp["date"])
    time_token = str(exp.get("time", "")).strip()
    if not time_token:
        return run_root / run_name
    return run_root / date_token / run_name


def resolve_run_name(config: Dict[str, Any]) -> str:
    exp = config["exp"]
    provided = exp.get("run_name")
    if provided:
        if " " in provided:
            raise ValueError("exp.run_name must not contain spaces")
        return provided

    date_token = str(exp["date"])
    time_token = slugify_token(exp.get("time", ""))
    dataset = slugify_token(config["data"]["dataset"])
    model = model_alias(config["model"]["backbone"])
    split_layer = int(config["model"]["split_layer"])
    baseline = canonical_baseline_name(config["method"]["baseline"])
    tag = slugify_token(exp.get("tag", ""))
    seed = int(exp["seed"])

    parts = [
        date_token,
        time_token if time_token else None,
        dataset,
        model,
        "sfl",
        f"split{split_layer}",
        baseline,
    ]
    if tag:
        parts.append(tag)
    parts.append(f"seed{seed}")
    return "_".join(part for part in parts if part)


def canonical_baseline_name(value: str) -> str:
    baseline = slugify_token(value)
    if baseline in BASELINE_VOCAB:
        return baseline
    return baseline


def model_alias(backbone: str) -> str:
    if backbone in MODEL_ALIASES:
        return MODEL_ALIASES[backbone]
    return slugify_token(backbone)


def slugify_token(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower()
    text = text.replace("-", "")
    text = text.replace("_", "")
    return re.sub(r"[^a-z0-9]", "", text)


def build_run_notes_template(run_name: str, config: Dict[str, Any], config_source_path: str) -> str:
    protocol = config["system"].get("training_protocol", "unknown")
    return "\n".join(
        [
            f"# Run Notes: {run_name}",
            "",
            "## Objective",
            "",
            f"- source_config: `{config_source_path}`",
            f"- dataset: `{config['data']['dataset']}`",
            f"- baseline: `{config['method']['baseline']}`",
            f"- protocol: `{protocol}`",
            f"- split_layer: `{config['model']['split_layer']}`",
            f"- seed: `{config['exp']['seed']}`",
            "",
            "## Key Observations",
            "",
            "-",
            "",
            "## Follow-up",
            "",
            "-",
        ]
    ) + "\n"
def write_metrics_csv(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=METRICS_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(_normalize_row(row, METRICS_COLUMNS))


def ensure_master_summary_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MASTER_RUNS_COLUMNS)
        writer.writeheader()


def upsert_master_summary_row(path: Path, row: Dict[str, Any]) -> None:
    ensure_master_summary_file(path)
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows.extend(reader)

    updated = False
    for index, existing in enumerate(rows):
        if existing["run_name"] == row["run_name"]:
            rows[index] = _normalize_row(row, MASTER_RUNS_COLUMNS)
            updated = True
            break
    if not updated:
        rows.append(_normalize_row(row, MASTER_RUNS_COLUMNS))

    rows.sort(key=lambda item: (item["date"], item["run_name"]))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MASTER_RUNS_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def build_success_summary(
    config: Dict[str, Any],
    context: RunContext,
    metric_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    test_acc_values = [row["test_acc"] for row in metric_rows if row.get("test_acc") is not None]
    best_test_acc = max(test_acc_values) if test_acc_values else None
    final_test_acc = metric_rows[-1]["test_acc"] if metric_rows else None
    target_accuracy = config["training"].get("target_accuracy")
    time_to_target = None
    if target_accuracy is not None:
        for row in metric_rows:
            test_acc = row.get("test_acc")
            if test_acc is not None and test_acc >= float(target_accuracy):
                time_to_target = row.get("cumulative_latency")
                break

    summary = {
        "date": config["exp"]["date"],
        "run_name": context.run_name,
        "run_dir": str(context.run_dir),
        "dataset": config["data"]["dataset"],
        "model": model_alias(config["model"]["backbone"]),
        "split_layer": int(config["model"]["split_layer"]),
        "baseline": canonical_baseline_name(config["method"]["baseline"]),
        "protocol": config["system"].get("training_protocol", "unknown"),
        "seed": int(config["exp"]["seed"]),
        "alpha": config["data"].get("dirichlet_alpha"),
        "best_test_acc": best_test_acc,
        "final_test_acc": final_test_acc,
        "time_to_target_accuracy": time_to_target,
        "avg_bits_per_round": mean_optional(row.get("total_bits") for row in metric_rows),
        "avg_token_count": mean_optional(row.get("avg_token_count") for row in metric_rows),
        "avg_distortion": mean_optional(row.get("avg_distortion") for row in metric_rows),
        "avg_round_latency": mean_optional(row.get("round_latency") for row in metric_rows),
        "final_cumulative_latency": metric_rows[-1]["cumulative_latency"] if metric_rows else None,
        "status": "completed",
        "notes": str(config["exp"].get("tag", "") or ""),
        "metrics_path": str(context.metrics_csv_path),
        "config_path": str(context.config_path),
        "stdout_log_path": str(context.stdout_log_path),
    }
    return summary


def build_failure_summary(
    config: Dict[str, Any],
    context: RunContext,
    error_message: str,
) -> Dict[str, Any]:
    return {
        "date": config["exp"]["date"],
        "run_name": context.run_name,
        "run_dir": str(context.run_dir),
        "dataset": config["data"]["dataset"],
        "model": model_alias(config["model"]["backbone"]),
        "split_layer": int(config["model"]["split_layer"]),
        "baseline": canonical_baseline_name(config["method"]["baseline"]),
        "protocol": config["system"].get("training_protocol", "unknown"),
        "seed": int(config["exp"]["seed"]),
        "alpha": config["data"].get("dirichlet_alpha"),
        "best_test_acc": None,
        "final_test_acc": None,
        "time_to_target_accuracy": None,
        "avg_bits_per_round": None,
        "avg_token_count": None,
        "avg_distortion": None,
        "avg_round_latency": None,
        "final_cumulative_latency": None,
        "status": "failed",
        "notes": error_message,
        "metrics_path": str(context.metrics_csv_path),
        "config_path": str(context.config_path),
        "stdout_log_path": str(context.stdout_log_path),
    }


def build_master_summary_row(summary: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "date": summary.get("date"),
        "run_name": summary.get("run_name"),
        "dataset": summary.get("dataset"),
        "model": summary.get("model"),
        "split_layer": summary.get("split_layer"),
        "baseline": summary.get("baseline"),
        "seed": summary.get("seed"),
        "alpha": summary.get("alpha"),
        "best_test_acc": summary.get("best_test_acc"),
        "final_test_acc": summary.get("final_test_acc"),
        "time_to_target": summary.get("time_to_target_accuracy"),
        "avg_bits": summary.get("avg_bits_per_round"),
        "avg_token_count": summary.get("avg_token_count"),
        "avg_distortion": summary.get("avg_distortion"),
        "avg_round_latency": summary.get("avg_round_latency"),
        "status": summary.get("status"),
        "notes": summary.get("notes"),
    }


def load_summary_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _normalize_row(row: Dict[str, Any], columns: List[str]) -> Dict[str, Any]:
    normalized = {}
    for column in columns:
        value = row.get(column)
        normalized[column] = "" if value is None else value
    return normalized


def mean_optional(values: Iterable[Any]) -> Any:
    filtered = [float(value) for value in values if value is not None]
    if not filtered:
        return None
    return sum(filtered) / len(filtered)
