# AGENTS.md

## Project intent

Hermes studies new contributions for wireless federated split learning with ViT-family models, with a particular focus on token reduction under communication constraints.

The repository is intended for joint work between a human researcher and coding agents. The priority is not raw coding speed. The priority is preserving research rigor while allowing fast exploration.

## Source of truth

When instructions conflict, follow this order:

1. Direct user instructions in chat
2. This `AGENTS.md`
3. `docs/problem_formulation.md`
4. `docs/experiment_protocol.md`
5. `docs/baselines.md`
6. Relevant files under `docs/papers/`, `docs/ideas/`, `docs/decisions/`, and `plans/`

Do not treat an old conversation as the source of truth if the repository documents say otherwise.

## Mandatory workflow

Before changing code or launching a new experiment:

1. Read the relevant protocol and baseline documents.
2. If the task involves a new attempt, idea discussion, experiment design, experiment execution, or any other non-trivial change, create or update a plan directory under `plans/` before doing the work.
3. If the task is motivated by a paper, create or update the relevant request batch and review under `docs/papers/`, and store the source PDF as `paper.pdf` inside the review folder when the paper can be downloaded for local research use.
4. If the task proposes a new method, create or update an idea file in `docs/ideas/`.
5. Keep the claim level honest. Use language such as `hypothesis`, `early signal`, `ablation result`, or `supported claim`.

After meaningful work:

1. Update the relevant markdown records.
2. Save run-level raw outputs under `experiments/runs/`.
3. Save summary rows and phase summaries under `experiments/summaries/`.
4. Save only cleaned tables or figures under `experiments/tables/` and `experiments/figures/`.
4. Run `python3 scripts/validate_docs.py`.

## Research claim rules

- Do not claim a contribution from a single lucky run.
- Do not compare against weakened baselines.
- Do not silently change evaluation settings when comparing methods.
- Treat communication cost, convergence behavior, and accuracy as joint targets.
- Every claimed gain should identify whether it is:
  - better accuracy at the same communication budget
  - lower communication at the same accuracy target
  - faster convergence under a fixed budget
  - a better Pareto frontier

## Markdown management rules

- Every durable research decision belongs in markdown, not only in chat.
- Use the provided templates for `docs/papers/`, `docs/ideas/`, `docs/decisions/`, and `plans/`.
- Keep one document focused on one purpose. Do not mix paper review, method proposal, and final claim in the same file.
- Prefer updating an existing canonical document over creating near-duplicate notes.
- When a document becomes obsolete, mark it as superseded and point to the newer file.
- A new research push should begin with a plan, not only with chat discussion.
- Canonical `docs/ideas/*.md` and `plans/*/*/plan.md` files should be written in Korean by default. English technical terms, theorem notation, model names, and paper titles may remain in English where that is clearer.

## Experiment record rules

- One experiment run must map to exactly one run folder under `experiments/runs/`.
- Each run folder must contain `config.yaml`, `metrics.csv`, `summary.json`, `stdout.log`, `notes.md`, `checkpoints/`, and `plots/`.
- Cross-run summary rows belong in `experiments/summaries/master_runs.csv`.
- Important run-family interpretation belongs in `experiments/summaries/YYYY-MM-DD_<phase>_summary.md`.
- Curated plots and tables belong under `experiments/figures/` and `experiments/tables/`.
- Each experiment record should preserve:
  - git commit
  - config dump
  - random seed
  - dataset split setting
  - client count and non-IID setting
  - split point
  - communication metrics
  - accuracy metrics

## Directory guidance

- `docs/papers/`: paper requests, structured literature reviews, and comparison indexes
- `docs/ideas/`: candidate contribution concepts and required ablations
- `docs/decisions/`: durable decisions about protocol, architecture, and evaluation
- `plans/`: executable task or experiment plans
- `configs/`: versioned experiment configs
- `src/`: implementation
- `scripts/`: repeatable command entry points and validators
- `experiments/`: canonical experiment storage

## Naming conventions

- Paper request batches: `docs/papers/requests/YYYYMMDD_HHMM_short_batch/request.md`
- Paper reviews: `docs/papers/reviews/YYYY/YYYY_author_shorttitle/review.md`
- Paper PDFs: `docs/papers/reviews/YYYY/YYYY_author_shorttitle/paper.pdf`
- Idea notes: `docs/ideas/YYYYMMDD_short_idea_name.md`
- Decisions: `docs/decisions/YYYYMMDD_short_decision_name.md`
- Plans: `plans/YYYYMMDD/HHMM_short_task_name/plan.md`
- Experiment runs: `experiments/runs/YYYY-MM-DD_dataset_model_sfl_splitX_baseline[_tag]_seedY/`
- Phase summaries: `experiments/summaries/YYYY-MM-DD_short_phase_summary.md`

## Guardrails for agents

- When unsure whether a result is strong enough, downgrade the wording rather than upgrading the claim.
- If a new experiment protocol would make old results incomparable, record that explicitly before running new experiments.
- If you introduce a new metric, add it to `docs/experiment_protocol.md` before relying on it in analysis.
