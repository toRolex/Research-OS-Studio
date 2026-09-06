---
name: research-charter
description: Build one candidate Research Charter from one user-selected pinned research-question Artifact, then stop for user review.
---

# Research Charter

## Contract

- Invocation: user only.
- Input: exactly one `research-question@1.0.0` Artifact, supplied with its lowercase SHA-256.
- Output: one candidate `research-charter@1.0.0` Artifact and one workflow report.
- Fixed budget: one source, one candidate.
- Invariants: preserve the supplied question; copy explicit boundaries, success criteria, budget, and invariants; never infer acceptance.

## Procedure

1. Verify the selected input bytes against the supplied SHA-256. Completion: the fixed bytes parse as the required typed Artifact.
2. Require a non-empty question and at least one explicit, non-empty boundary in the pinned input. Treat question, boundaries, success criteria, budget, and invariants as user-owned: a candidate may copy them but cannot change them. Completion: research meaning and constraints are preserved exactly.
3. Build the candidate from those supplied fields. Completion: its status is `candidate`, and no Assessment or acceptance is created.
4. Write the report with fixed budget limits and actual use. Completion: `status=stopped`, `stop_reason=candidate_complete`, and `automatic_next_workflow=false`.
5. List optional review or later invocation choices, then stop. Suggestions are not authorization.

## Failure

Stop without overwriting files when the pin, type, schema, boundary, safe path, invariant, or budget check fails. Preserve the selected input unchanged.
