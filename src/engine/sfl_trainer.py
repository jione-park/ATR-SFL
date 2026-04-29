from __future__ import annotations

import copy
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

import torch
from torch import nn
from torch.utils.data import DataLoader

from src.data.cifar import build_cifar10_datasets, build_cifar100_datasets
from src.data.partition import build_client_dataloaders, build_iid_partitions
from src.engine.metrics import RunningAverage, top1_correct
from src.models.deit_split import build_deit_tiny_split
from src.models.interface_operator import build_interface_operator
from src.utils.experiment import (
    RunContext,
    build_master_summary_row,
    build_success_summary,
    upsert_master_summary_row,
    write_metrics_csv,
)
from src.utils.fedavg import average_state_dicts_weighted, state_dict_to_cpu
from src.utils.io import dump_json, get_git_commit
from src.utils.random import set_global_seed


SEQUENTIAL_SERVER_BOOTSTRAP = "sequential_server_bootstrap"
PARALLEL_ROUND_SERVER_TAIL = "parallel_round_server_tail"


@dataclass
class ClientTrainResult:
    front_state: Optional[Dict]
    back_state: Optional[Dict]
    metrics: Dict


class SFLTrainer:
    def __init__(self, config: Dict, run_context: RunContext) -> None:
        protocol = str(config["system"].get("training_protocol", SEQUENTIAL_SERVER_BOOTSTRAP))
        if protocol == SEQUENTIAL_SERVER_BOOTSTRAP:
            self.impl = SequentialBootstrapTrainer(config, run_context)
        elif protocol == PARALLEL_ROUND_SERVER_TAIL:
            self.impl = ParallelRoundTrainer(config, run_context)
        else:
            raise ValueError(f"Unsupported training protocol: {protocol}")

    def train(self) -> Dict:
        return self.impl.train()


class BaseTrainer:
    def __init__(self, config: Dict, run_context: RunContext) -> None:
        self.config = config
        self.run_context = run_context
        self.exp_config = config["exp"]
        self.data_config = config["data"]
        self.model_config = config["model"]
        self.training_config = config["training"]
        self.method_config = config["method"]
        self.system_config = config["system"]
        self.training_protocol = str(self.system_config.get("training_protocol", SEQUENTIAL_SERVER_BOOTSTRAP))

        self.device = self._resolve_device(self.training_config.get("device", "auto"))
        dump_json(self._build_metadata(), self.run_context.metadata_json_path)

        set_global_seed(int(self.exp_config["seed"]))

        self.train_dataset, self.test_dataset = self._build_datasets()
        partition = self.data_config["partition"].lower()
        if partition != "iid":
            raise ValueError(f"Unsupported partition for current bootstrap stage: {partition}")
        self.partitions = build_iid_partitions(
            dataset_size=len(self.train_dataset),
            num_clients=int(self.data_config["num_clients"]),
            seed=int(self.exp_config["seed"]),
        )
        self.client_loaders = build_client_dataloaders(
            dataset=self.train_dataset,
            partitions=self.partitions,
            batch_size=int(self.training_config["batch_size"]),
            num_workers=int(self.training_config["num_workers"]),
        )
        self.test_loader = DataLoader(
            self.test_dataset,
            batch_size=int(self.training_config["eval_batch_size"]),
            shuffle=False,
            num_workers=int(self.training_config["num_workers"]),
            pin_memory=False,
        )

        self.global_front, self.global_back, self.model_info = build_deit_tiny_split(
            model_name=self.model_config["backbone"],
            num_classes=int(self.model_config["num_classes"]),
            image_size=int(self.data_config["image_size"]),
            split_block=int(self.model_config["split_layer"]),
            pretrained=bool(self.model_config["pretrained"]),
        )
        self.global_front = self.global_front.to(self.device)
        self.global_back = self.global_back.to(self.device)
        self.interface_operator = build_interface_operator(config, self.model_info)

        self.criterion = nn.CrossEntropyLoss()
        self.history: List[Dict] = []
        self.metric_rows: List[Dict] = []

    def train(self) -> Dict:
        raise NotImplementedError

    def evaluate(self) -> Dict:
        self.global_front.eval()
        self.global_back.eval()

        loss_meter = RunningAverage()
        total_examples = 0
        total_correct = 0
        total_interface_bytes = 0
        total_interface_tokens = 0

        max_eval_batches = self.training_config.get("max_eval_batches")
        with torch.no_grad():
            for batch_idx, (images, labels) in enumerate(self.test_loader):
                if max_eval_batches is not None and batch_idx >= int(max_eval_batches):
                    break
                images = images.to(self.device)
                labels = labels.to(self.device)

                smashed = self.global_front(images)
                reduced_tokens, operator_stats = self._apply_interface_operator(
                    smashed,
                    batch_size=int(labels.shape[0]),
                    client_id=-1,
                    round_idx=0,
                    training=False,
                )
                logits = self.global_back(reduced_tokens)
                loss = self.criterion(logits, labels)

                batch_size = labels.shape[0]
                loss_meter.update(loss.item(), batch_size)
                total_examples += batch_size
                total_correct += top1_correct(logits, labels)
                total_interface_bytes += int(operator_stats["uplink_bytes"])
                total_interface_tokens += int(operator_stats["token_count"]) * batch_size

        return {
            "loss": loss_meter.average,
            "accuracy": total_correct / max(total_examples, 1),
            "examples": total_examples,
            "avg_interface_bytes": total_interface_bytes / max(total_examples, 1),
            "avg_interface_tokens": total_interface_tokens / max(total_examples, 1),
        }

    def _build_datasets(self):
        dataset_name = self.data_config["dataset"].lower()
        if dataset_name == "cifar10":
            return build_cifar10_datasets(
                root=self.data_config["root"],
                image_size=int(self.data_config["image_size"]),
                download=bool(self.data_config["download"]),
            )
        if dataset_name == "cifar100":
            return build_cifar100_datasets(
                root=self.data_config["root"],
                image_size=int(self.data_config["image_size"]),
                download=bool(self.data_config["download"]),
            )
        raise ValueError(f"Unsupported dataset for bootstrap stage: {dataset_name}")

    def _build_metadata(self) -> Dict:
        return {
            "repo_commit": get_git_commit("."),
            "created_at_epoch_sec": time.time(),
            "training_protocol": self.training_protocol,
        }

    def _build_optimizer(self, parameters):
        optimizer_name = self.training_config["optimizer"].lower()
        lr = float(self.training_config["lr"])
        weight_decay = float(self.training_config.get("weight_decay", 0.0))

        if optimizer_name != "adam":
            raise ValueError(f"Unsupported optimizer: {self.training_config['optimizer']}")

        return torch.optim.Adam(parameters, lr=lr, weight_decay=weight_decay)

    def _resolve_device(self, requested_device: str) -> torch.device:
        if requested_device == "auto":
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")
        return torch.device(requested_device)

    def _sample_clients(self, round_idx: int) -> List[int]:
        num_clients = int(self.data_config["num_clients"])
        participation_rate = float(self.data_config["participation_ratio"])
        sample_size = max(1, int(round(num_clients * participation_rate)))

        generator = torch.Generator()
        generator.manual_seed(int(self.exp_config["seed"]) + round_idx)
        perm = torch.randperm(num_clients, generator=generator).tolist()
        return sorted(perm[:sample_size])

    def _apply_interface_operator(
        self,
        split_tokens: torch.Tensor,
        batch_size: int,
        client_id: int,
        round_idx: int,
        training: bool,
    ):
        metadata = {
            "batch_size": int(batch_size),
            "client_id": int(client_id),
            "round_idx": int(round_idx),
            "training": bool(training),
            "full_token_count": int(self.model_info["num_tokens"]),
        }
        return self.interface_operator(split_tokens, metadata)

    def _aggregate_client_metrics(self, client_metrics: Sequence[Dict]) -> Dict:
        total_examples = sum(metric["examples"] for metric in client_metrics)
        total_correct = sum(metric["correct"] for metric in client_metrics)
        weighted_loss = sum(metric["loss"] * metric["examples"] for metric in client_metrics)
        total_uplink_bytes = sum(metric["uplink_bytes"] for metric in client_metrics)
        total_downlink_bytes = sum(metric["downlink_bytes"] for metric in client_metrics)
        total_roundtrip_bytes = sum(metric["roundtrip_bytes"] for metric in client_metrics)
        total_tokens = sum(metric["avg_interface_tokens"] * metric["examples"] for metric in client_metrics)
        total_distortion = sum(metric["avg_distortion"] * metric["examples"] for metric in client_metrics)
        client_latencies = [metric["client_latency_sec"] for metric in client_metrics]
        server_latencies = [metric["server_latency_sec"] for metric in client_metrics]
        num_clients = max(len(client_metrics), 1)

        return {
            "loss": weighted_loss / max(total_examples, 1),
            "accuracy": total_correct / max(total_examples, 1),
            "examples": total_examples,
            "avg_interface_tokens": total_tokens / max(total_examples, 1),
            "avg_distortion": total_distortion / max(total_examples, 1),
            "uplink_bytes": total_uplink_bytes,
            "downlink_bytes": total_downlink_bytes,
            "roundtrip_bytes": total_roundtrip_bytes,
            "avg_bits": (total_roundtrip_bytes * 8) / num_clients,
            "avg_uplink_bits": (total_uplink_bytes * 8) / num_clients,
            "avg_downlink_bits": (total_downlink_bytes * 8) / num_clients,
            "total_bits": total_roundtrip_bytes * 8,
            "avg_client_latency": sum(client_latencies) / num_clients if client_latencies else None,
            "avg_server_latency": sum(server_latencies) / num_clients if server_latencies else None,
            "max_client_latency": max(client_latencies) if client_latencies else None,
        }

    def _build_metric_row(
        self,
        round_idx: int,
        selected_clients: Sequence[int],
        train_metrics: Dict,
        eval_metrics: Dict,
        round_latency: float,
        cumulative_latency: float,
    ) -> Dict:
        avg_token_count = train_metrics["avg_interface_tokens"]
        return {
            "round": round_idx,
            "train_loss": train_metrics["loss"],
            "test_acc": eval_metrics["accuracy"],
            "val_acc": None,
            "avg_bits": train_metrics["avg_bits"],
            "avg_token_count": avg_token_count,
            "avg_token_ratio": avg_token_count / max(self.model_info["num_tokens"], 1),
            "avg_distortion": train_metrics["avg_distortion"],
            "avg_client_latency": train_metrics["avg_client_latency"],
            "avg_server_latency": train_metrics["avg_server_latency"],
            "round_latency": round_latency,
            "cumulative_latency": cumulative_latency,
            "avg_snr": None,
            "max_client_latency": train_metrics["max_client_latency"],
            "participating_clients": "|".join(str(client_id) for client_id in selected_clients),
            "train_acc": train_metrics["accuracy"],
            "grad_norm_proxy": None,
            "total_bits": train_metrics["total_bits"],
            "avg_uplink_bits": train_metrics["avg_uplink_bits"],
            "avg_downlink_bits": train_metrics["avg_downlink_bits"],
            "status": "completed",
        }

    def _record_round(
        self,
        round_idx: int,
        selected_clients: Sequence[int],
        train_metrics: Dict,
        eval_metrics: Dict,
        round_latency: float,
        cumulative_latency: float,
    ) -> None:
        round_summary = {
            "round": round_idx,
            "selected_clients": list(selected_clients),
            "train": train_metrics,
            "eval": eval_metrics,
            "round_latency": round_latency,
            "cumulative_latency": cumulative_latency,
        }
        self.history.append(round_summary)
        self.metric_rows.append(
            self._build_metric_row(
                round_idx=round_idx,
                selected_clients=selected_clients,
                train_metrics=train_metrics,
                eval_metrics=eval_metrics,
                round_latency=round_latency,
                cumulative_latency=cumulative_latency,
            )
        )
        dump_json(self.history, self.run_context.metrics_history_path)
        write_metrics_csv(self.run_context.metrics_csv_path, self.metric_rows)
        print(f"[round {round_idx}] {self.metric_rows[-1]}")

    def _finalize_run(self) -> Dict:
        summary = build_success_summary(
            config=self.config,
            context=self.run_context,
            metric_rows=self.metric_rows,
        )
        dump_json(summary, self.run_context.summary_json_path)
        upsert_master_summary_row(
            self.run_context.master_summary_path,
            build_master_summary_row(summary),
        )
        return summary

    def _estimate_latency_contributions(
        self,
        client_forward_sec: float,
        server_forward_sec: float,
        backward_sec: float,
    ) -> Dict[str, float]:
        shared_backward = 0.5 * float(backward_sec)
        client_latency_sec = float(client_forward_sec) + shared_backward
        server_latency_sec = float(server_forward_sec) + shared_backward
        return {
            "client_latency_sec": client_latency_sec,
            "server_latency_sec": server_latency_sec,
        }

    def _print_header(self) -> None:
        print(f"run_name={self.run_context.run_name}")
        print(f"run_dir={self.run_context.run_dir}")
        print(f"device={self.device}")
        print(f"training_protocol={self.training_protocol}")
        print(f"model_info={self.model_info}")


class SequentialBootstrapTrainer(BaseTrainer):
    def __init__(self, config: Dict, run_context: RunContext) -> None:
        super().__init__(config, run_context)
        self.server_optimizer = self._build_optimizer(self.global_back.parameters())

    def train(self) -> Dict:
        num_rounds = int(self.training_config["global_rounds"])
        cumulative_latency = 0.0
        self._print_header()

        for round_idx in range(1, num_rounds + 1):
            round_start = time.time()
            selected_clients = self._sample_clients(round_idx)
            print(f"starting round={round_idx} selected_clients={selected_clients}")
            client_results: List[ClientTrainResult] = []

            for client_id in selected_clients:
                client_results.append(self._train_selected_client(client_id, round_idx))

            front_states = [result.front_state for result in client_results if result.front_state is not None]
            weights = [result.metrics["examples"] for result in client_results]
            averaged_front = average_state_dicts_weighted(front_states, weights)
            self.global_front.load_state_dict(averaged_front, strict=True)

            train_metrics = self._aggregate_client_metrics([result.metrics for result in client_results])
            eval_metrics = self.evaluate()

            round_latency = time.time() - round_start
            cumulative_latency += round_latency
            self._record_round(
                round_idx=round_idx,
                selected_clients=selected_clients,
                train_metrics=train_metrics,
                eval_metrics=eval_metrics,
                round_latency=round_latency,
                cumulative_latency=cumulative_latency,
            )

        return self._finalize_run()

    def _train_selected_client(self, client_id: int, round_idx: int) -> ClientTrainResult:
        local_front = copy.deepcopy(self.global_front).to(self.device)
        local_front.train()
        self.global_back.train()

        local_optimizer = self._build_optimizer(local_front.parameters())

        loss_meter = RunningAverage()
        total_examples = 0
        total_correct = 0
        total_tokens = 0
        total_uplink_bytes = 0
        total_downlink_bytes = 0
        total_distortion = 0.0
        total_client_latency = 0.0
        total_server_latency = 0.0

        local_epochs = int(self.training_config["local_epochs"])
        max_train_batches = self.training_config.get("max_train_batches_per_client")
        for _ in range(local_epochs):
            for batch_idx, (images, labels) in enumerate(self.client_loaders[client_id]):
                if max_train_batches is not None and batch_idx >= int(max_train_batches):
                    break
                images = images.to(self.device)
                labels = labels.to(self.device)

                local_optimizer.zero_grad()
                self.server_optimizer.zero_grad()

                client_forward_start = time.time()
                smashed = local_front(images)
                client_forward_sec = time.time() - client_forward_start

                reduced_tokens, operator_stats = self._apply_interface_operator(
                    smashed,
                    batch_size=int(labels.shape[0]),
                    client_id=client_id,
                    round_idx=round_idx,
                    training=True,
                )

                server_forward_start = time.time()
                logits = self.global_back(reduced_tokens)
                loss = self.criterion(logits, labels)
                server_forward_sec = time.time() - server_forward_start

                backward_start = time.time()
                loss.backward()
                backward_sec = time.time() - backward_start

                local_optimizer.step()
                self.server_optimizer.step()

                latency_stats = self._estimate_latency_contributions(
                    client_forward_sec=client_forward_sec,
                    server_forward_sec=server_forward_sec,
                    backward_sec=backward_sec,
                )

                batch_size = int(labels.shape[0])
                loss_meter.update(loss.item(), batch_size)
                total_examples += batch_size
                total_correct += top1_correct(logits, labels)
                total_tokens += int(operator_stats["token_count"]) * batch_size
                total_uplink_bytes += int(operator_stats["uplink_bytes"])
                total_downlink_bytes += int(operator_stats["downlink_bytes"])
                total_distortion += float(operator_stats["distortion"]) * batch_size
                total_client_latency += latency_stats["client_latency_sec"]
                total_server_latency += latency_stats["server_latency_sec"]

        metrics = {
            "client_id": client_id,
            "loss": loss_meter.average,
            "accuracy": total_correct / max(total_examples, 1),
            "correct": total_correct,
            "examples": total_examples,
            "avg_interface_tokens": total_tokens / max(total_examples, 1),
            "avg_distortion": total_distortion / max(total_examples, 1),
            "uplink_bytes": total_uplink_bytes,
            "downlink_bytes": total_downlink_bytes,
            "roundtrip_bytes": total_uplink_bytes + total_downlink_bytes,
            "client_latency_sec": total_client_latency,
            "server_latency_sec": total_server_latency,
        }
        return ClientTrainResult(
            front_state=state_dict_to_cpu(local_front.state_dict()),
            back_state=None,
            metrics=metrics,
        )


class ParallelRoundTrainer(BaseTrainer):
    def train(self) -> Dict:
        num_rounds = int(self.training_config["global_rounds"])
        cumulative_latency = 0.0
        self._print_header()

        for round_idx in range(1, num_rounds + 1):
            selected_clients = self._sample_clients(round_idx)
            print(f"starting round={round_idx} selected_clients={selected_clients}")
            client_results: List[ClientTrainResult] = []

            for client_id in selected_clients:
                client_results.append(self._train_one_client_round(client_id, round_idx))

            weights = [result.metrics["examples"] for result in client_results]
            front_states = [result.front_state for result in client_results if result.front_state is not None]
            back_states = [result.back_state for result in client_results if result.back_state is not None]

            aggregation_start = time.time()
            averaged_front = average_state_dicts_weighted(front_states, weights)
            averaged_back = average_state_dicts_weighted(back_states, weights)
            self.global_front.load_state_dict(averaged_front, strict=True)
            self.global_back.load_state_dict(averaged_back, strict=True)
            aggregation_overhead = time.time() - aggregation_start
            aggregation_overhead += float(self.system_config.get("aggregation_overhead_sec", 0.0))

            train_metrics = self._aggregate_client_metrics([result.metrics for result in client_results])
            eval_metrics = self.evaluate()

            round_latency = float(train_metrics["max_client_latency"] or 0.0) + aggregation_overhead
            cumulative_latency += round_latency
            self._record_round(
                round_idx=round_idx,
                selected_clients=selected_clients,
                train_metrics=train_metrics,
                eval_metrics=eval_metrics,
                round_latency=round_latency,
                cumulative_latency=cumulative_latency,
            )

        return self._finalize_run()

    def _train_one_client_round(self, client_id: int, round_idx: int) -> ClientTrainResult:
        local_front = copy.deepcopy(self.global_front).to(self.device)
        local_back = copy.deepcopy(self.global_back).to(self.device)
        local_front.train()
        local_back.train()

        front_optimizer = self._build_optimizer(local_front.parameters())
        back_optimizer = self._build_optimizer(local_back.parameters())

        loss_meter = RunningAverage()
        total_examples = 0
        total_correct = 0
        total_tokens = 0
        total_uplink_bytes = 0
        total_downlink_bytes = 0
        total_distortion = 0.0
        total_client_latency = 0.0
        total_server_latency = 0.0

        local_epochs = int(self.training_config["local_epochs"])
        max_train_batches = self.training_config.get("max_train_batches_per_client")
        for _ in range(local_epochs):
            for batch_idx, (images, labels) in enumerate(self.client_loaders[client_id]):
                if max_train_batches is not None and batch_idx >= int(max_train_batches):
                    break
                images = images.to(self.device)
                labels = labels.to(self.device)

                front_optimizer.zero_grad()
                back_optimizer.zero_grad()

                client_forward_start = time.time()
                smashed = local_front(images)
                client_forward_sec = time.time() - client_forward_start

                reduced_tokens, operator_stats = self._apply_interface_operator(
                    smashed,
                    batch_size=int(labels.shape[0]),
                    client_id=client_id,
                    round_idx=round_idx,
                    training=True,
                )

                server_forward_start = time.time()
                logits = local_back(reduced_tokens)
                loss = self.criterion(logits, labels)
                server_forward_sec = time.time() - server_forward_start

                backward_start = time.time()
                loss.backward()
                backward_sec = time.time() - backward_start

                front_optimizer.step()
                back_optimizer.step()

                latency_stats = self._estimate_latency_contributions(
                    client_forward_sec=client_forward_sec,
                    server_forward_sec=server_forward_sec,
                    backward_sec=backward_sec,
                )

                batch_size = int(labels.shape[0])
                loss_meter.update(loss.item(), batch_size)
                total_examples += batch_size
                total_correct += top1_correct(logits, labels)
                total_tokens += int(operator_stats["token_count"]) * batch_size
                total_uplink_bytes += int(operator_stats["uplink_bytes"])
                total_downlink_bytes += int(operator_stats["downlink_bytes"])
                total_distortion += float(operator_stats["distortion"]) * batch_size
                total_client_latency += latency_stats["client_latency_sec"]
                total_server_latency += latency_stats["server_latency_sec"]

        metrics = {
            "client_id": client_id,
            "loss": loss_meter.average,
            "accuracy": total_correct / max(total_examples, 1),
            "correct": total_correct,
            "examples": total_examples,
            "avg_interface_tokens": total_tokens / max(total_examples, 1),
            "avg_distortion": total_distortion / max(total_examples, 1),
            "uplink_bytes": total_uplink_bytes,
            "downlink_bytes": total_downlink_bytes,
            "roundtrip_bytes": total_uplink_bytes + total_downlink_bytes,
            "client_latency_sec": total_client_latency,
            "server_latency_sec": total_server_latency,
        }
        return ClientTrainResult(
            front_state=state_dict_to_cpu(local_front.state_dict()),
            back_state=state_dict_to_cpu(local_back.state_dict()),
            metrics=metrics,
        )
