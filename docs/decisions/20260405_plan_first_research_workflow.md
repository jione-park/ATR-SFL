# Decision: Plan-first research workflow

## Context

Hermes is intended for joint human-agent research. Without a plan-first rule, new ideas, experiments, and direction changes can start from chat and branch quickly before the intended scope, validation, or update obligations are written down.

## Decision

Hermes will require a plan before substantial research actions, including:

- new method attempts
- structured idea discussions that may affect direction
- experiment design work
- experiment execution campaigns
- protocol or baseline changes

## Alternatives Considered

- writing plans only for implementation-heavy work
- relying on idea notes alone for early-stage exploration
- documenting intent after the experiments are already running

## Expected Impact

The project should preserve intent, scope, and validation criteria earlier in the workflow. This should make research branches easier to review, continue, compare, and clean up.

## Revisit Triggers

- the workflow becomes too heavy for short exploratory tasks
- the plan templates stop matching the real work pattern
- automation provides a clearly better way to capture pre-work intent

## Follow-up

- keep plan directories lightweight enough for fast creation
- reinforce the rule in `AGENTS.md` and `docs/harness_engineering.md`
