# Decision: Paper review harness structure

## Context

The initial `docs/papers/` layout was flat and too lightweight for the intended workflow. Hermes needs to support a repeatable pattern where the user can hand the agent a batch of papers, the agent reviews them, and the resulting notes remain easy to browse later.

## Decision

Hermes will structure paper work into:

- `docs/papers/requests/` for intake batches
- `docs/papers/reviews/` for canonical review folders
- `docs/papers/reading_queue.md` for current progress tracking
- `docs/papers/review_index.md` for browsing completed reviews
- `docs/papers/comparison_matrix.md` for cross-paper comparison and main claim digest

## Alternatives Considered

- keeping all reviews as flat files in one directory
- using only a queue file without per-paper folders
- storing paper notes in plans or generic docs files

## Expected Impact

The literature review flow should be easier to operate and easier to revisit. User requests, full reviews, and cross-paper summaries will each have a stable place.

## Revisit Triggers

- the number of papers grows enough to require topic-specific subindexes
- reviews start accumulating extra artifacts that need a different structure
- the intake workflow proves too heavy for normal usage

## Follow-up

- add paper request and review generator scripts
- update the docs validator for nested paper review paths
