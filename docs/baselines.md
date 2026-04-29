# Baselines

## Purpose

This file defines the minimum baseline families that a Hermes contribution should respect.

## Minimum baseline families

1. No token reduction
2. Simple static token reduction
3. Importance-based token reduction
4. Budget-matched variant without the proposed key idea

## Baseline hygiene rules

- Match training budget and evaluation settings.
- Match communication budgets where appropriate.
- If the proposed method is adaptive, compare against strong fixed-budget baselines.
- If the proposed method uses extra modules, include ablations that isolate their effect.

## Expected baseline examples

The exact contents will evolve, but likely candidates include:

- full-token split learning baseline
- random token dropping
- fixed top-k token keep policy
- attention-score-based token keep policy
- method variant without channel awareness
- method variant without reconstruction or memory

## Mandatory ablations for new ideas

Any serious new method should usually include:

- full system
- system without the key novelty
- system matched to the same token budget using a simple heuristic
- communication-performance frontier comparison
