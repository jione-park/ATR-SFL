# Decision: Store paper PDFs with reviews

## Context

Hermes uses structured paper reviews as part of its research harness. Until now, the review system tracked markdown analysis well, but it did not explicitly require the source PDF to live alongside the review. That makes later re-reading, citation checking, and agent handoff less convenient.

## Decision

For future paper reviews, Hermes will store the downloaded paper PDF as `paper.pdf` inside the canonical review folder when the paper source permits local download for research use.

## Alternatives Considered

- keeping only external links in the review markdown
- storing PDFs in a separate shared folder disconnected from the review
- downloading papers ad hoc each time they are needed

## Expected Impact

Each review folder will become a self-contained paper workspace containing the source paper and the Hermes interpretation of it. This should improve traceability and reduce repeated paper lookup work.

## Revisit Triggers

- the repository becomes public and redistribution rights for stored PDFs become a concern
- the amount of stored paper data becomes too large for the preferred workflow
- a better document storage system replaces local PDF storage

## Follow-up

- update paper-review documentation and templates
- when reviewing new papers, save the PDF as `paper.pdf` in the review folder
