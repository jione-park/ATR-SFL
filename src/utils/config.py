from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


DEFAULT_TRAINING_PROTOCOL = "sequential_server_bootstrap"


def load_config(path: str) -> Dict[str, Any]:
    config_path = Path(path)
    raw_config = _load_raw_config(config_path)
    return normalize_config(raw_config)


def _load_raw_config(path: Path) -> Dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    if suffix in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError(
                "YAML config loading requires PyYAML. Install the runtime requirements first."
            ) from exc
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        if not isinstance(data, dict):
            raise ValueError(f"Config file must contain a mapping at top level: {path}")
        return data
    raise ValueError(f"Unsupported config extension: {path.suffix}")


def normalize_config(raw_config: Dict[str, Any]) -> Dict[str, Any]:
    if "exp" in raw_config and "data" in raw_config:
        config = deepcopy(raw_config)
        return _apply_defaults(config)
    return _apply_defaults(_convert_legacy_config(raw_config))


def _convert_legacy_config(raw_config: Dict[str, Any]) -> Dict[str, Any]:
    dataset = raw_config.get("dataset", {})
    model = raw_config.get("model", {})
    federation = raw_config.get("federation", {})
    optimizer = raw_config.get("optimizer", {})
    training = raw_config.get("training", {})
    artifacts = raw_config.get("artifacts", {})

    experiment_name = str(artifacts.get("experiment_name", "experiment"))
    return {
        "exp": {
            "run_name": None,
            "date": None,
            "seed": int(training.get("seed", 1)),
            "tag": "sanity" if "sanity" in experiment_name else "",
        },
        "data": {
            "dataset": dataset.get("name", "cifar10"),
            "root": dataset.get("root", "data"),
            "image_size": int(dataset.get("image_size", 224)),
            "download": bool(dataset.get("download", True)),
            "num_clients": int(federation.get("num_clients", 10)),
            "participation_ratio": float(federation.get("participation_rate", 1.0)),
            "partition": federation.get("partition", "iid"),
            "dirichlet_alpha": federation.get("dirichlet_alpha"),
        },
        "model": {
            "backbone": model.get("name", "deit_tiny_patch16_224"),
            "num_classes": int(model.get("num_classes", 10)),
            "pretrained": bool(model.get("pretrained", False)),
            "split_layer": int(model.get("split_block", 6)),
            "token_operator": model.get("token_operator", "full_sequence"),
            "cls_guided": bool(model.get("cls_guided", False)),
        },
        "training": {
            "global_rounds": int(training.get("rounds", 1)),
            "local_epochs": int(training.get("local_epochs", 1)),
            "batch_size": int(training.get("batch_size", 32)),
            "eval_batch_size": int(training.get("eval_batch_size", 64)),
            "num_workers": int(training.get("num_workers", 0)),
            "optimizer": optimizer.get("name", "adam"),
            "lr": float(optimizer.get("lr", 1e-4)),
            "weight_decay": float(optimizer.get("weight_decay", 0.0)),
            "device": training.get("device", "auto"),
            "max_train_batches_per_client": training.get("max_train_batches_per_client"),
            "max_eval_batches": training.get("max_eval_batches"),
            "target_accuracy": training.get("target_accuracy"),
        },
        "wireless": {
            "channel_model": "none",
            "snr_states_db": [],
            "bandwidth_hz": None,
        },
        "method": {
            "baseline": _infer_legacy_baseline(experiment_name),
            "token_budget_mode": "none",
            "token_budget_candidates": [],
            "residual_fusion": False,
            "lambda_tradeoff": None,
        },
        "system": {
            "uplink_only": False,
            "latency_model": "wallclock_proxy",
            "training_protocol": DEFAULT_TRAINING_PROTOCOL,
            "server_aggregation": "fedavg",
            "client_aggregation": "fedavg",
            "aggregation_overhead_sec": 0.0,
        },
        "storage": {
            "run_root": "experiments/runs",
            "summary_root": "experiments/summaries",
            "figure_root": "experiments/figures",
            "table_root": "experiments/tables",
        },
    }


def _infer_legacy_baseline(experiment_name: str) -> str:
    lowered = experiment_name.lower()
    for candidate in ("boundaware", "chanadapt", "fixedk48", "fixedk32", "oracle", "fulltoken"):
        if candidate in lowered:
            return candidate
    if "full_token" in lowered or "fulltoken" in lowered:
        return "fulltoken"
    return "fulltoken"


def _apply_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    exp = config.setdefault("exp", {})
    if not exp.get("date"):
        exp["date"] = datetime.now().strftime("%Y-%m-%d")
    if not exp.get("time"):
        exp["time"] = datetime.now().strftime("%H%M%S")
    if exp.get("seed") is None:
        exp["seed"] = 1
    if exp.get("tag") is None:
        exp["tag"] = ""
    exp.setdefault("run_name", None)

    data = config.setdefault("data", {})
    data.setdefault("dataset", "cifar10")
    data.setdefault("root", "data")
    data.setdefault("image_size", 224)
    data.setdefault("download", True)
    data.setdefault("num_clients", 10)
    data.setdefault("participation_ratio", 1.0)
    data.setdefault("partition", "iid")
    data.setdefault("dirichlet_alpha", None)

    model = config.setdefault("model", {})
    model.setdefault("backbone", "deit_tiny_patch16_224")
    model.setdefault("num_classes", 10)
    model.setdefault("pretrained", False)
    model.setdefault("split_layer", 6)
    model.setdefault("token_operator", "full_sequence")
    model.setdefault("cls_guided", False)

    training = config.setdefault("training", {})
    training.setdefault("global_rounds", 1)
    training.setdefault("local_epochs", 1)
    training.setdefault("batch_size", 32)
    training.setdefault("eval_batch_size", 64)
    training.setdefault("num_workers", 0)
    training.setdefault("optimizer", "adam")
    training.setdefault("lr", 1e-4)
    training.setdefault("weight_decay", 0.0)
    training.setdefault("device", "auto")
    training.setdefault("max_train_batches_per_client", None)
    training.setdefault("max_eval_batches", None)
    training.setdefault("target_accuracy", None)

    wireless = config.setdefault("wireless", {})
    wireless.setdefault("channel_model", "none")
    wireless.setdefault("snr_states_db", [])
    wireless.setdefault("bandwidth_hz", None)

    method = config.setdefault("method", {})
    method.setdefault("baseline", "fulltoken")
    method.setdefault("token_budget_mode", "none")
    method.setdefault("token_budget_candidates", [])
    method.setdefault("residual_fusion", False)
    method.setdefault("lambda_tradeoff", None)

    system = config.setdefault("system", {})
    system.setdefault("uplink_only", False)
    system.setdefault("latency_model", "wallclock_proxy")
    system.setdefault("training_protocol", DEFAULT_TRAINING_PROTOCOL)
    system.setdefault("server_aggregation", "fedavg")
    system.setdefault("client_aggregation", "fedavg")
    system.setdefault("aggregation_overhead_sec", 0.0)

    storage = config.setdefault("storage", {})
    storage.setdefault("run_root", "experiments/runs")
    storage.setdefault("summary_root", "experiments/summaries")
    storage.setdefault("figure_root", "experiments/figures")
    storage.setdefault("table_root", "experiments/tables")

    return config
