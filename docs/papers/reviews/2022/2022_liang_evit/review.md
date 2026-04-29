# Review: Not All Patches Are What You Need: Expediting Vision Transformers via Token Reorganizations

## Metadata

- Authors: Youwei Liang, Chongjian Ge, Zhan Tong, Yibing Song, Jue Wang, Pengtao Xie
- Year: 2022
- Venue: ICLR 2022
- Review focus: keep-and-fuse token reduction as a split-aware compression candidate

## Citation

Youwei Liang, Chongjian Ge, Zhan Tong, Yibing Song, Jue Wang, and Pengtao Xie. "Not All Patches Are What You Need: Expediting Vision Transformers via Token Reorganizations." ICLR 2022.

## Links

- Paper: https://openreview.net/pdf?id=feb0c5a2e1c1fc63509c2e528ca07aa95aea2d5e
- Code: https://github.com/youweiliang/evit

## Main Claims

- EViT identifies attentive tokens using class-token attention between MHSA and FFN.
- It preserves attentive tokens and fuses inattentive ones into a single token, reducing later computation while keeping gradients flowing.
- The paper reports about 50% inference speedup for DeiT-S with only about 0.3% top-1 accuracy loss on ImageNet.
- Under the same compute budget, the saved capacity can be used for higher-resolution inputs and about 1% better accuracy on DeiT-S.
- The method adds no extra parameters.

## Why It Matters For Hermes

EViT is more communication-relevant than pure pruning because it keeps a compressed residual token instead of discarding everything below the threshold. That makes it a strong baseline candidate for split learning, where hard dropping may destroy too much information before transmission.

## Problem Setting

The paper studies centralized ViT training and inference for image classification. Efficiency is measured in MACs and runtime, not in bits transmitted across a cut layer or round-wise communication cost in federated learning.

## Method Summary

EViT computes attentiveness scores from the class token to image tokens. It keeps the most attentive tokens and fuses the rest into one residual token. This token reorganization happens progressively through depth and lowers the token count seen by later MHSA and FFN blocks. The model can therefore spend the saved budget either on faster inference or on processing more input patches.

## Experimental Setup

The main evaluation uses ImageNet classification with DeiT and LV-ViT. The paper reports both speedup-at-similar-accuracy and accuracy improvement under the same compute budget.

## Strengths

- No extra selector parameters.
- Fusing inattentive tokens preserves some information instead of pure removal.
- Gives a useful trade-off viewpoint: compression can be used for speed or for admitting a richer input.

## Weaknesses

- Relies on class-token attention as the token importance signal.
- The fused residual token may blur spatial semantics.
- Still designed around centralized computation rather than split communication.

## Reproduction Notes

The important choices are where token reorganization is inserted, how the keep rate changes across depth, and how the fused residual token is formed. For Hermes, the fused token should be treated as a formal transmitted object with known positional and aggregation semantics.

## Gaps Relative To Hermes

- No split learning cut or client/server asymmetry.
- If the split is too early, class-token attention may be too immature to guide token reduction well.
- The paper ignores the communication overhead of token indices, residual metadata, and variable-length payloads.
- No non-IID or wireless adaptation.

## Reusable Ideas

- Keep-and-fuse instead of keep-or-drop only.
- Class-token-attention-driven token ranking.
- Using saved budget to transmit more informative tokens or serve harder channel conditions.
- A natural `EViT-SFL` baseline for compressed smashed-data transmission.

## Required Direct Comparisons

- Full-token SFL baseline.
- Static top-k token dropping at the same transmitted-token budget.
- DynamicViT-style learned pruning at the same budget.
- ToFu-style hybrid prune-merge at the same budget.

## Verdict

EViT is the most immediately usable baseline idea for Hermes because it already thinks in terms of preserving a compressed residual token. Its main weakness for SFL is that the token selection signal and objective were never designed around a split communication bottleneck.
