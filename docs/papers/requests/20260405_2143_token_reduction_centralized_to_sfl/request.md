# Paper Request Batch: Centralized token reduction to SFL adaptation

## Request Context

The user asked for an initial review of three token reduction papers that were developed for centralized ViT settings, then asked for a plan that explains how to reinterpret them for split federated learning in wireless environments.

## Requested Papers

- Title: DynamicViT: Efficient Vision Transformers with Dynamic Token Sparsification
  Link: https://proceedings.neurips.cc/paper/2021/file/747d3443e319a22747fbb873e8b2f9f2-Paper.pdf
  Why it matters: A strong learned dynamic pruning baseline for token reduction.

- Title: Not All Patches Are What You Need: Expediting Vision Transformers via Token Reorganizations
  Link: https://openreview.net/pdf?id=feb0c5a2e1c1fc63509c2e528ca07aa95aea2d5e
  Why it matters: A keep-and-fuse approach with no extra parameters, potentially relevant to communication-aware token compression.

- Title: Token Fusion: Bridging the Gap between Token Pruning and Token Merging
  Link: https://arxiv.org/pdf/2312.01026.pdf
  Why it matters: A hybrid prune-merge view that may inspire a split-aware policy near the cut layer.

## Desired Output

- one canonical review per paper
- updated queue, review index, and comparison matrix
- a plan that translates the centralized assumptions into SFL-specific modification points

## Status

Reviewed and indexed on 2026-04-05.
