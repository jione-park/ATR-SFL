# Harness Engineering For Hermes

## Purpose

This document explains how Hermes applies harness engineering to research work.

In Hermes, harness engineering means designing the environment in which a human researcher and an agent can do credible research together. The goal is not only to generate code quickly. The goal is to preserve reasoning, comparisons, failures, and evidence well enough that a contribution can survive later scrutiny.

## Why Hermes Needs A Harness

Hermes targets wireless federated split learning with ViT-family models and token reduction. This setting is easy to distort by accident because small implementation changes can affect:

- communication cost
- convergence speed
- split learning behavior
- client heterogeneity
- wireless assumptions
- model accuracy

Without a harness, the project would likely drift into disconnected experiments, untracked assumptions, and weak claims.

## Core Principle

The repository is the research operating system.

If a paper insight, method idea, evaluation rule, or interpretation matters after today, it should live in the repository as a durable artifact. Chat is useful for momentum, but it is not the system of record.

## Human And Agent Roles

The human researcher owns:

- choosing the research question
- judging novelty
- approving protocol changes
- deciding whether evidence is strong enough for a claim

The agent owns:

- organizing literature reviews
- drafting plans and implementation scaffolds
- implementing baselines and experiment plumbing
- running repeatable checks
- summarizing logs, tables, and ablations

The agent should produce evidence packages, not inflated claims.

## Document System

Hermes separates durable research work into specific markdown categories.

- `docs/papers/`: paper intake requests, structured reviews, and comparison indexes
- `docs/ideas/`: candidate contributions, failure modes, and mandatory ablations
- `docs/decisions/`: durable choices that change how the project is run or interpreted
- `plans/`: date-grouped task directories for non-trivial work, each containing `plan.md`
- `docs/experiment_protocol.md`: the fairness contract for comparisons
- `docs/baselines.md`: the minimum standard for credible comparisons

This separation is intentional. A paper review is not a method proposal. A method proposal is not a final claim. A final interpretation should not be hidden inside a scratch note.

## Standard Research Loop

Hermes should usually move through this loop:

1. Read a paper and save a structured review.
2. Extract a gap or mechanism relevant to Hermes.
3. Write an idea note before implementation.
4. Create a plan before any new attempt, idea session, experiment design, experiment run, or other non-trivial research work.
5. Implement the method or baseline.
6. Run experiments under the protocol.
7. Save run-level raw artifacts under `experiments/runs/`.
8. Save cross-run summaries under `experiments/summaries/`.
9. Save curated tables or figures under `experiments/tables/` and `experiments/figures/`.
9. Record the interpretation or protocol impact in markdown.

The loop matters because many false contributions come from skipping the middle steps and jumping from a vague intuition directly to a polished claim.

## Plan-First Rule

Hermes uses a plan-first workflow for substantial research actions.

That means the team should create or update a plan before:

- trying a new method direction
- holding a structured idea discussion that may change project direction
- designing an experiment family
- launching an experiment series
- changing baseline scope or evaluation logic

The point is not bureaucracy. The point is to preserve intent, validation criteria, and follow-up obligations before the work starts to branch.

## Claim Discipline

Hermes should use careful claim levels:

- `Hypothesis`: the idea sounds plausible but evidence is weak
- `Preliminary`: one or a few promising runs
- `Supported`: repeated evidence against direct baselines
- `Claim-ready`: strong enough for internal draft writing

Every serious result should answer which improvement it actually provides:

- better accuracy at the same communication budget
- lower communication cost at the same accuracy level
- faster convergence under a fixed budget
- a better Pareto frontier

## Experiment Harness

The experiment harness exists to keep comparisons fair and results reusable.

Every retained run should preserve:

- config
- code version
- seed
- dataset and partition rule
- client count
- split point
- communication metrics
- model performance metrics

Hermes standardizes experiment storage under `experiments/`:

- `experiments/runs/`: raw run folders
- `experiments/summaries/`: `master_runs.csv` and phase summary markdown
- `experiments/figures/`: exported figures
- `experiments/tables/`: exported tables

If a figure or table cannot be traced back to one or more run directories, it should not be trusted.

## Paper Review Harness

Paper reviews are not generic summaries. They are instruments for identifying contribution gaps.

Each strong review should make it easy to answer:

- what assumptions the paper makes
- whether it matches the Hermes setting
- what part can be reused
- where the paper is vulnerable
- what direct comparison would be required

Hermes separates paper work into three layers:

- requests: what the user asked the agent to investigate
- reviews: the canonical review of each paper
- indexes: queue, review index, and comparison matrix

For traceability, a completed review folder should also contain the source paper PDF as `paper.pdf` when the source allows local download. This keeps the review, the cited source, and any later reproduction notes in one stable location.

The comparison matrix exists to compress this information across papers so that the team does not repeatedly rediscover the same gaps. It should also summarize each paper's main claim in one or two lines so the team can scan the landscape quickly before reading full reviews.

## Docker And Reproducibility

Docker is part of the harness, not a convenience feature.

Hermes uses Docker to reduce environment drift and make experiments easier to reproduce across sessions and collaborators. Important results should always be traceable to:

- a git commit
- a config
- a container image or dependency lock state

If an experiment only works in an untracked local environment, it is not ready to support a paper claim.

## Markdown Management Rules

Markdown is part of the harness only if it remains legible.

- keep one file focused on one purpose
- update canonical documents instead of scattering near-duplicate notes
- mark superseded documents clearly
- prefer explicit sections over stream-of-consciousness notes
- write for the next collaborator, not only for the current moment

The validator script exists to stop the document system from decaying into an unstructured notes folder.

## What Good Looks Like

Hermes is using harness engineering well when:

- a new collaborator can understand the project by reading the repository
- an agent can continue work after interruption without guessing hidden assumptions
- paper reviews lead to concrete experiment ideas
- experiment outputs are traceable and comparable
- claims are upgraded only when evidence justifies them

## Near-Term Operating Rule

Until the first baseline stack is implemented, every substantial step should strengthen one of these areas:

- literature clarity
- baseline clarity
- experiment reproducibility
- contribution gap identification

Anything else is likely premature.
