# Plans Guide

Plans are for work that is big enough to benefit from an explicit execution contract.

앞으로 `plans/*/*/plan.md`의 정식 본문은 기본적으로 한국어로 작성한다. 다만 모델명, 수식, 알고리즘 이름, 논문 제목처럼 영어가 더 자연스러운 항목은 그대로 둬도 된다.

Each plan lives under a date directory:

- `plans/YYYYMMDD/HHMM_short_task_name/plan.md`

Use date plus hour and minute only. Do not include seconds.

## Scratch notes

The directory `plans/notes/` is reserved for informal user notes and raw thinking.

- files under `plans/notes/` are not treated as canonical execution plans
- the docs validator ignores `plans/notes/`
- once a note becomes actionable research work, promote it into a date-grouped plan directory

Use a plan when:

- starting a new research attempt
- exploring a new idea seriously enough to affect direction
- holding an idea review that should leave a durable record
- designing a new experiment family
- launching a new experiment run family
- adding a baseline implementation
- running a new experiment family
- integrating a new paper idea
- changing the experiment protocol

Each plan should identify what will be changed, how success will be checked, and which markdown documents must be updated when the work finishes.

## Plan-first expectation

In Hermes, plans are not reserved for late-stage implementation. A substantial attempt should start with a plan, even if the plan is brief.

## Template

Copy from:

- `plans/_template/plan.md`

## Suggested workflow

Create a new plan scaffold with:

    bash scripts/new_plan.sh "short_task_name"
