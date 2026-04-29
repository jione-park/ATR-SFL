# AGENTS.md

## Project intent

Hermes studies wireless federated split learning with ViT-family models, with a particular focus on token reduction under communication constraints.

This public repository is intentionally code-first. It supports collaboration between a human researcher and coding agents, but it does not track the full local research workspace.

## Source of truth

When instructions conflict, follow this order:

1. Direct user instructions in chat
2. This `AGENTS.md`
3. `README.md`
4. `configs/`
5. `src/`

Do not treat an old conversation, deleted markdown, or stale local outputs as the source of truth if the repository files say otherwise.

## Public repo scope

- Keep the tracked repository focused on:
  - `src/`
  - `configs/`
  - `scripts/`
  - `README.md`
  - `AGENTS.md`
- Keep local research workspace directories such as `docs/`, `plans/`, `experiments/`, `data/`, `docker/`, `conda/`, and `third_party/` on disk when needed for local work, but do not track them in the public git repo unless the user explicitly asks for that.
- Do not commit datasets, experiment outputs, paper notes, plans, local environments, or vendor snapshots unless the user explicitly asks for that.
- Local artifacts may still be written under ignored paths such as `docs/`, `plans/`, `data/`, `experiments/`, `artifacts/`, and `results/`.

## Working rules

- When changing trainer semantics, config schema, or script entrypoints, update the matching tracked documentation in the same change.
- Keep claim level honest. Prefer `hypothesis`, `early signal`, or `baseline` over stronger language when evidence is limited.
- Do not silently change evaluation settings when comparing methods.
- Treat communication cost, convergence behavior, and accuracy as joint targets.

## Research claim rules

- Do not claim a contribution from a single lucky run.
- Do not compare against weakened baselines.
- Do not silently change evaluation settings when comparing methods.
- Treat communication cost, convergence behavior, and accuracy as joint targets.
- Every claimed gain should identify whether it is better accuracy at the same budget, lower communication at the same target, faster convergence, or a better Pareto frontier.

## Directory guidance

- `configs/`: versioned experiment configs
- `src/`: implementation
- `scripts/`: repeatable command entry points
- ignored local paths such as `docs/`, `plans/`, and `experiments/` may still exist for research records and run outputs

## Naming conventions

- config files should stay explicit about dataset, model, split layer, baseline, and protocol
- filenames should avoid ambiguous suffixes such as `final`, `tmp`, or `new2`

## Guardrails for agents

- When unsure whether a result is strong enough, downgrade the wording rather than upgrading the claim.
- If a new experiment protocol would make old results incomparable, say so explicitly in chat and in the commit message or config change.
- If a script or config becomes obsolete after a code change, update or remove it in the same patch.
