import copy
from typing import Dict, Tuple

import timm
import torch
from torch import nn


def _copy_blocks(blocks) -> nn.ModuleList:
    return nn.ModuleList([copy.deepcopy(block) for block in blocks])


class ClientFront(nn.Module):
    def __init__(
        self,
        patch_embed: nn.Module,
        cls_token: torch.Tensor,
        pos_embed: torch.Tensor,
        pos_drop: nn.Module,
        patch_drop: nn.Module,
        norm_pre: nn.Module,
        blocks,
    ) -> None:
        super().__init__()
        self.patch_embed = copy.deepcopy(patch_embed)
        self.cls_token = nn.Parameter(cls_token.detach().clone())
        self.pos_embed = nn.Parameter(pos_embed.detach().clone())
        self.pos_drop = copy.deepcopy(pos_drop)
        self.patch_drop = copy.deepcopy(patch_drop)
        self.norm_pre = copy.deepcopy(norm_pre)
        self.blocks = _copy_blocks(blocks)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.patch_embed(x)
        cls_token = self.cls_token.expand(x.shape[0], -1, -1)
        x = torch.cat((cls_token, x), dim=1)
        x = x + self.pos_embed[:, : x.shape[1], :]
        x = self.pos_drop(x)
        x = self.patch_drop(x)
        x = self.norm_pre(x)
        for block in self.blocks:
            x = block(x)
        return x


class ServerBack(nn.Module):
    def __init__(
        self,
        blocks,
        norm: nn.Module,
        fc_norm: nn.Module,
        pre_logits: nn.Module,
        head_drop: nn.Module,
        head: nn.Module,
    ) -> None:
        super().__init__()
        self.blocks = _copy_blocks(blocks)
        self.norm = copy.deepcopy(norm)
        self.fc_norm = copy.deepcopy(fc_norm)
        self.pre_logits = copy.deepcopy(pre_logits)
        self.head_drop = copy.deepcopy(head_drop)
        self.head = copy.deepcopy(head)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for block in self.blocks:
            x = block(x)
        x = self.norm(x)
        cls_token = x[:, 0]
        cls_token = self.fc_norm(cls_token)
        cls_token = self.pre_logits(cls_token)
        cls_token = self.head_drop(cls_token)
        return self.head(cls_token)


def build_deit_tiny_split(
    model_name: str,
    num_classes: int,
    image_size: int,
    split_block: int,
    pretrained: bool,
) -> Tuple[ClientFront, ServerBack, Dict[str, int]]:
    vit = timm.create_model(
        model_name=model_name,
        pretrained=pretrained,
        num_classes=num_classes,
        img_size=image_size,
    )
    blocks = list(vit.blocks)
    num_blocks = len(blocks)
    if split_block <= 0 or split_block >= num_blocks:
        raise ValueError(f"split_block must be in [1, {num_blocks - 1}]")

    client_front = ClientFront(
        patch_embed=vit.patch_embed,
        cls_token=vit.cls_token,
        pos_embed=vit.pos_embed,
        pos_drop=vit.pos_drop,
        patch_drop=getattr(vit, "patch_drop", nn.Identity()),
        norm_pre=getattr(vit, "norm_pre", nn.Identity()),
        blocks=blocks[:split_block],
    )
    server_back = ServerBack(
        blocks=blocks[split_block:],
        norm=vit.norm,
        fc_norm=getattr(vit, "fc_norm", nn.Identity()),
        pre_logits=getattr(vit, "pre_logits", nn.Identity()),
        head_drop=getattr(vit, "head_drop", nn.Identity()),
        head=vit.head,
    )
    model_info = {
        "num_blocks": num_blocks,
        "split_block": split_block,
        "num_tokens": int(vit.patch_embed.num_patches + 1),
        "embed_dim": int(vit.embed_dim),
    }
    return client_front, server_back, model_info
