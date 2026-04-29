# Review: Token Fusion: Bridging the Gap between Token Pruning and Token Merging

## Metadata

- Authors: Minchul Kim, Shangqian Gao, Yen-Chang Hsu, Yilin Shen, Hongxia Jin
- Year: 2023
- Venue: arXiv 2023, WACV 2024
- Review focus: cut-aware hybrid prune-merge reasoning for SFL

## Citation

Minchul Kim, Shangqian Gao, Yen-Chang Hsu, Yilin Shen, and Hongxia Jin. "Token Fusion: Bridging the Gap between Token Pruning and Token Merging." arXiv:2312.01026, 2023. WACV 2024.

## Links

- Paper: https://arxiv.org/pdf/2312.01026.pdf

## Main Claims

- Pruning is preferable when downstream layers are sensitive to interpolation, while merging is preferable when downstream behavior is close to linear.
- ToFu combines pruning and merging rather than forcing a single reduction strategy.
- MLERP merging preserves feature-norm distribution better than naive averaging and reduces merge-induced distribution shift.
- The paper reports improved efficiency-accuracy trade-offs over standalone pruning or merging on classification and image generation tasks.

## Why It Matters For Hermes

ToFu is the most useful paper conceptually. Hermes may eventually need a cut-aware policy that decides when to prune and when to fuse, instead of committing to only one reduction mechanism.

## Problem Setting

The paper studies centralized ViT acceleration for classification and image generation. The optimization target is compute efficiency with preserved accuracy or generation quality, not transmitted bits or split/federated constraints.

## Method Summary

ToFu first matches similar tokens, then reduces them with a strategy that depends on the effective linearity of downstream processing. Early layers often benefit more from pruning-oriented behavior, while later layers can tolerate or benefit from averaging-style merges. To improve merge quality, ToFu replaces simple averaging with MLERP, a norm-preserving interpolation operator inspired by SLERP.

## Experimental Setup

The paper evaluates ImageNet-1K classification and image generation settings. It compares against token pruning and token merging baselines such as ToMe, with the headline result that a hybrid policy can be both faster and more accurate.

## Strengths

- Provides a principled bridge between pruning and merging.
- The norm-preserving merge idea is directly relevant when compressed tokens are transmitted.
- Can operate without extra fine-tuning in the plug-in setting.

## Weaknesses

- The main analysis is still centralized and whole-network oriented.
- The policy is layer-wise, while Hermes may care mostly about a single cut-layer bottleneck.
- Merge quality may depend heavily on the downstream task and representation geometry.

## Reproduction Notes

The key components are token matching, the rule that chooses pruning-like versus merging-like behavior, and the MLERP implementation. For Hermes, the most important part is not the exact centralized schedule but the hybrid decision logic near the cut.

## Gaps Relative To Hermes

- No federated learning, no split learning, and no wireless constraints.
- The paper spreads reduction decisions across the full depth rather than focusing on the representation that crosses the client-server split.
- It does not account for merge metadata, provenance, or variable transmission cost.
- It ignores client heterogeneity and channel-aware adaptation.

## Reusable Ideas

- Treat pruning and merging as complementary tools.
- Make the prune-versus-merge choice depend on downstream sensitivity.
- Use norm-preserving merge operators when transmitting compressed token summaries.
- A future `ToFu-SFL` baseline could decide how to compress tokens exactly at the split point.

## Required Direct Comparisons

- Full-token SFL baseline.
- Pure pruning baseline at the same transmitted-bit budget.
- Pure fusion baseline at the same budget.
- Learned pruning baseline such as DynamicViT-SFL.

## Verdict

ToFu is the best conceptual seed for a new Hermes contribution. It does not directly solve SFL, but it strongly suggests that a split-aware hybrid policy may outperform pure pruning or pure fusion once communication is the main objective.
