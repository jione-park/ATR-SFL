# Comparison Matrix

Use this file to compare the papers that materially shape Hermes.

## Matrix

| Paper | Main Claim | Task | ViT / Token Method | FL / Split Setting | Wireless Assumption | Communication Metric | Strong Point | Limitation Relevant To Hermes | Review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DynamicViT (NeurIPS 2021) | Learn per-input token importance and hierarchically prune tokens to reduce compute with small accuracy loss. | ImageNet classification | Learned dynamic token pruning with prediction modules and attention masking | Centralized training/inference | None | FLOPs and throughput | Strong learned pruning baseline | Needs retraining and optimizes compute, not SFL communication | [Review](reviews/2021/2021_rao_dynamicvit/review.md) |
| EViT (ICLR 2022) | Preserve attentive tokens and fuse inattentive ones so ViTs run faster, or use the saved budget for higher input resolution. | ImageNet classification | Token reorganization using class-token attention and fused residual token | Centralized training/inference | None | MACs and throughput | No extra parameters and fusion may retain more information than hard pruning | Depends on stable class-token attention and ignores the split bottleneck | [Review](reviews/2022/2022_liang_evit/review.md) |
| Token Fusion / ToFu (WACV 2024, arXiv 2023) | Choose pruning or merging based on functional linearity and use MLERP to reduce merge-induced distribution shift. | ImageNet classification and image generation | Layer-wise prune-merge hybrid with norm-preserving merge | Centralized inference, can work with or without additional training | None | Compute efficiency and model accuracy | Best conceptual bridge between pruning and merging | Hermes needs a cut-aware communication policy, not only a whole-network acceleration policy | [Review](reviews/2023/2023_kim_token_fusion/review.md) |

## Main Claim Digest

- DynamicViT: learn a lightweight token selector and prune progressively across depth. This is the cleanest learned pruning baseline, but its native target is single-device acceleration.
- EViT: use class-token attention to keep important patches and fuse the rest into one residual token. This is the most immediately relevant baseline if Hermes wants communication-aware compression instead of pure dropping.
- Token Fusion / ToFu: switch between pruning and merging depending on downstream layer behavior and preserve token norms during merge. This is the strongest conceptual starting point for a cut-aware hybrid policy in SFL.
