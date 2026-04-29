# Review: DynamicViT: Efficient Vision Transformers with Dynamic Token Sparsification

## Metadata

- Authors: Yongming Rao, Wenliang Zhao, Benlin Liu, Jiwen Lu, Jie Zhou, Cho-Jui Hsieh
- Year: 2021
- Venue: NeurIPS 2021
- Review focus: learned dynamic pruning as a future SFL baseline

## Citation

Yongming Rao, Wenliang Zhao, Benlin Liu, Jiwen Lu, Jie Zhou, and Cho-Jui Hsieh. "DynamicViT: Efficient Vision Transformers with Dynamic Token Sparsification." NeurIPS 2021.

## Links

- Paper: https://proceedings.neurips.cc/paper/2021/file/747d3443e319a22747fbb873e8b2f9f2-Paper.pdf
- Code: https://github.com/raoyongming/DynamicViT

## Main Claims

- A lightweight prediction module can estimate token importance from intermediate features and prune tokens progressively.
- Hierarchical dynamic pruning can remove a large fraction of tokens while maintaining ImageNet accuracy.
- The paper reports pruning 66% of tokens with about 31% to 37% FLOPs reduction and over 40% throughput improvement, while keeping accuracy drop within about 0.5% on several ViT backbones.

## Why It Matters For Hermes

DynamicViT is the most direct learned token-pruning baseline among the three papers. If Hermes wants a split-aware learned selector instead of a static heuristic, this is the primary paper to adapt.

## Problem Setting

The paper studies centralized image classification with ViT-like backbones such as DeiT and LV-ViT. The core goal is to reduce computation and improve throughput on a single uninterrupted model pipeline, not to compress a client-to-server representation in split federated learning.

## Method Summary

DynamicViT inserts prediction modules between transformer blocks. Each module combines local token features with a global aggregated feature and predicts keep/drop probabilities. Token reduction is hierarchical, so the network gradually drops more tokens as depth increases. During training, Gumbel-Softmax and attention masking make the discrete pruning decision differentiable. During inference, the model simply keeps the most informative tokens under a predefined pruning ratio.

## Experimental Setup

The main evaluation is ImageNet classification on DeiT and LV-ViT variants. The reported trade-off is framed in FLOPs, throughput, and top-1 accuracy.

## Strengths

- Strong learned baseline rather than a hand-designed token heuristic.
- Input-adaptive token selection.
- Hierarchical pruning matches the intuition that token importance evolves across depth.
- The differentiable masking path is reusable for a split-aware learned selector.

## Weaknesses

- Requires extra selector modules and training support.
- Optimizes centralized compute, not transmitted bits.
- Does not address client heterogeneity, wireless constraints, or split backpropagation.

## Reproduction Notes

The critical components are prediction-module placement, local-global token scoring, differentiable masking, and the target pruning ratios. For Hermes, the token selector should be implemented in a way that it can sit exactly at or before the split point rather than somewhere arbitrary in the backbone.

## Gaps Relative To Hermes

- No federated learning, no split learning, and no wireless setting.
- The main benefit is less downstream computation, whereas Hermes needs less communication across the cut.
- The method does not account for index-mask payload, variable-length transmission, or per-client budgets.
- Joint end-to-end centralized training is assumed.

## Reusable Ideas

- Learned local-global token scoring.
- Progressive token keep-rate scheduling.
- Differentiable masking for discrete token selection.
- A future `DynamicViT-SFL` baseline where the selector is trained against a communication-aware loss.

## Required Direct Comparisons

- Full-token SFL baseline at the same split point.
- Static top-k or fixed-ratio token dropping at the same communication budget.
- EViT-style keep-and-fuse baseline.
- ToFu-style prune-merge hybrid baseline.

## Verdict

DynamicViT should be treated as the strongest learned pruning reference. It is highly relevant to Hermes, but it must become cut-aware and communication-aware before it can serve as an SFL contribution.
