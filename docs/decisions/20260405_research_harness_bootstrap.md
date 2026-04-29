# Decision: Research harness bootstrap

## Context

Hermes started as an empty repository. Without an explicit harness, paper reviews, ideas, experiment settings, and final claims would likely spread across chat history and ad hoc notes, making the project hard to reproduce or scale with agent help.

## Decision

Hermes will treat markdown documents plus reproducible scripts as the primary operating system for research work. The initial canonical structure is:

- root-level `AGENTS.md` for collaboration rules
- `docs/` for problem statement, protocols, baselines, paper reviews, ideas, and decisions
- `plans/` for non-trivial execution plans stored as timestamped directories
- `docker/` for the standard experiment environment

## Alternatives Considered

- relying on chat history and notebooks as the main record
- keeping only code and reconstructing research rationale later
- using a single large lab notebook instead of typed document categories

## Expected Impact

The repository should remain legible to both humans and agents. New work should be easier to scope, review, reproduce, and continue after interruptions.

## Revisit Triggers

- the document categories become too rigid for the actual workflow
- a better experiment orchestration pattern replaces the current structure
- the project scope changes beyond wireless federated split learning with token reduction

## Follow-up

- populate `docs/papers/reading_queue.md`
- create the first literature review files
- define the first official baseline plan
