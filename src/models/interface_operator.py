from __future__ import annotations

from typing import Any, Dict, Tuple

import torch

from src.engine.metrics import tensor_nbytes, tensor_token_count


class IdentitySplitOperator:
    def __init__(self, full_token_count: int) -> None:
        self.full_token_count = int(full_token_count)

    def __call__(
        self,
        split_tokens: torch.Tensor,
        metadata: Dict[str, Any],
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        del metadata
        token_count = tensor_token_count(split_tokens)
        payload_bytes = tensor_nbytes(split_tokens)
        stats = {
            "token_count": token_count,
            "uplink_bytes": payload_bytes,
            "downlink_bytes": payload_bytes,
            "distortion": 0.0,
            "full_token_count": self.full_token_count,
        }
        return split_tokens, stats


def build_interface_operator(config: Dict[str, Any], model_info: Dict[str, Any]):
    operator_name = str(config["model"].get("token_operator", "full_sequence")).lower()
    if operator_name in {"full_sequence", "fullsequence", "identity", "fulltoken"}:
        return IdentitySplitOperator(full_token_count=int(model_info["num_tokens"]))
    raise ValueError(f"Unsupported token operator for current bootstrap stage: {operator_name}")
