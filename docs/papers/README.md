# Paper Review Guide

The paper harness in Hermes is designed for this workflow:

1. The user gives one or more papers.
2. The agent records that request in a request batch.
3. The agent finds the papers, stores the source PDF in the review folder when possible, reads them, and writes canonical reviews.
4. The queue, review index, and comparison matrix are updated so the literature state is easy to scan later.

Paper reviews in Hermes are not generic summaries. They exist to answer a narrower question:

What does this paper imply for our chance of making a real contribution in wireless federated split learning with token reduction?

## Structure

- `requests/`: intake batches representing what the user asked to investigate
- `reviews/`: canonical per-paper review folders
- `reading_queue.md`: current intake and progress tracking
- `review_index.md`: curated index of completed reviews
- `comparison_matrix.md`: cross-paper comparison and main-claim digest
- `_templates/`: reusable markdown templates

## Rules

- Use `docs/papers/_templates/request.md` for request batches.
- Use `docs/papers/_templates/review.md` for actual paper reviews.
- For each reviewed paper, store the downloaded source PDF as `paper.pdf` inside the review folder when the source permits local download.
- Focus on assumptions, gaps, and transferable mechanisms.
- Record why the paper matters for Hermes, not only what the paper did.
- If the paper becomes a direct baseline or closest prior work, update `comparison_matrix.md`.
- If the repository is later made public, re-check redistribution rights for stored PDFs.

## Naming

- Request batches: `docs/papers/requests/YYYYMMDD_HHMM_short_batch/request.md`
- Reviews: `docs/papers/reviews/YYYY/YYYY_author_shorttitle/review.md`
- Review PDFs: `docs/papers/reviews/YYYY/YYYY_author_shorttitle/paper.pdf`

## Suggested workflow

Create a request batch:

    bash scripts/new_paper_request.sh "token_reduction_batch"

Create a review scaffold:

    bash scripts/new_paper_review.sh 2024 "kim_token_reduction_split_learning"
