# Documentation Map

This directory is the durable memory of the project. If an idea, protocol choice, paper insight, or experiment interpretation matters after today, it should live here.

## Reading order

Read the documents in this order before major implementation or analysis work:

1. `problem_formulation.md`
2. `harness_engineering.md`
3. `experiment_protocol.md`
4. `baselines.md`
5. relevant paper reviews in `papers/`
6. relevant idea notes in `ideas/`
7. relevant decisions in `decisions/`

## Document types

- `problem_formulation.md`: the stable statement of the research problem
- `harness_engineering.md`: the operating model for human-agent research collaboration
- `experiment_protocol.md`: the evaluation contract that keeps comparisons fair
- `baselines.md`: the minimum comparison set for any new method
- `bootstrap_cifar10_full_token_sanity_run.md`: the current known-good description of the first runnable local SFL bootstrap path
- `../experiments/README.md`: the canonical experiment result storage contract
- `papers/`: structured reviews of external papers
- `ideas/`: method proposals and research hypotheses
- `decisions/`: durable decisions and why they were made
- `plans/`: date-grouped task directories containing `plan.md`

## Markdown governance

- One document should have one job.
- Use explicit headings instead of free-form notes.
- Distinguish between:
  - `Hypothesis`: plausible but unverified idea
  - `Evidence`: concrete experimental or literature support
  - `Decision`: choice the project will currently follow
  - `Open question`: unresolved issue that blocks confidence
- Link related documents instead of copying text across files.
- Preserve the strongest current version of a statement in one canonical file.

## Update checklist

When adding a new paper review:

1. Create or update a request batch under `papers/requests/`.
2. Create the review from `papers/_templates/review.md`.
3. Update `papers/reading_queue.md`.
4. Update `papers/review_index.md`.
5. Update `papers/comparison_matrix.md` if the paper matters for direct comparison.

When adding a new method idea:

1. Create the idea note from `ideas/_template.md`.
2. Link the motivating papers.
3. State the minimum evidence needed before making any claim.
4. Create or update a plan before turning the idea into real implementation or experiment work.

When changing the experimental contract:

1. Update `experiment_protocol.md`.
2. Create a decision note in `decisions/`.
3. Call out which old results became incomparable, if any.

When changing run storage or summary conventions:

1. Update `../experiments/README.md`.
2. Update `experiment_protocol.md` if metric meanings changed.
3. Update `AGENTS.md` if the operational workflow changed.
