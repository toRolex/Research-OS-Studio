---
name: research-reflect
description: Reflect over one to twelve user-selected pinned research Artifacts while preserving failures and uncertainty, then stop.
---

# Research Reflect

## Contract

- Invocation: user only.
- Input: one to twelve distinct pinned outer-loop or `reflection-input@1.0.0` Artifacts.
- Output: one candidate `research-reflection@1.0.0` Artifact and one workflow report.
- Fixed budget: at most twelve sources, one candidate, twelve combined observations, five optional next steps.
- Invariants: preserve failures and uncertainty; do not alter research semantics or budgets; never choose or invoke a next workflow.

## Procedure

1. Verify every selected path, type, and SHA-256. Completion: all revisions are distinct and pinned.
2. Preserve every declared failure and uncertainty with its source path. A bounded candidate may add observations only; unknown candidate fields and any attempted decision are rejected. Completion: negative records remain explicit and reflection cannot advance the workflow.
3. Bound the combined observation view to twelve entries while retaining full failure and uncertainty arrays. Completion: counters remain within fixed limits.
4. Emit `decisions=[]`; reflection does not authorize acceptance or semantic change. Completion: candidate remains advisory.
5. Write candidate and report, list optional user choices, then stop with `automatic_next_workflow=false`.

## Failure

Stop on zero inputs, excess inputs, duplicate paths, pin drift, wrong types, unsafe paths, malformed arrays, or budget violation. Do not overwrite or advance anything.
