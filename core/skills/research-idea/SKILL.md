---
name: research-idea
description: Build bounded idea candidates from one user-selected pinned Research Gap Artifact without claiming novelty, then stop.
---

# Research Idea

## Contract

- Invocation: user only.
- Input: exactly one pinned `research-gap@1.0.0` Artifact containing a selected or candidate gap.
- Output: one candidate `research-idea@1.0.0` Artifact and one workflow report.
- Fixed budget: one source, one candidate, at most three ideas.
- Invariants: preserve gap wording; expose assumptions and tests; make no novelty claim or user selection.

## Procedure

1. Verify the selected gap bytes and type. Completion: the revision cannot drift during execution.
2. Resolve the explicitly selected gap; only a sole candidate may be used without a separate selection. Multiple or zero candidates without selection fail. Completion: the gap exists and its wording is unchanged.
3. Copy at most three declared ideas with assumptions and tests; if absent, create one conservative investigation proposal tied verbatim to the gap. Completion: `novelty_claim=null` and `selection=null`.
4. Write the candidate and fixed-budget report without overwrite. Completion: the report records stopped candidate completion.
5. List review or a later explicit novelty check using pinned idea and literature inputs, then stop.

## Failure

Stop on absent gap, pin drift, malformed candidate fields, unsafe paths, or budget violation. Do not modify inputs or existing outputs.
