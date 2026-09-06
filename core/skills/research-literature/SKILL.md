---
name: research-literature
description: Organize only literature records already pinned in one user-selected Research Charter Artifact, produce a candidate report, then stop.
---

# Research Literature

## Contract

- Invocation: user only.
- Input: exactly one pinned `research-charter@1.0.0` Artifact.
- Output: one candidate `literature-review@1.0.0` Artifact and one workflow report.
- Fixed budget: one source, one candidate, zero new queries, at most 50 pinned citations.
- Invariants: preserve the charter question and boundaries; include only already pinned citation records; never silently search or fetch.

## Procedure

1. Verify the selected Charter bytes and type. Completion: one fixed input revision is loaded.
2. Accept a bounded candidate synthesis payload, then copy only its citations that already occur in the pinned input; preserve the fixed question and boundaries. Completion: no unpinned source appears.
3. Record `queries=[]`; truncate beyond the citation budget with an explicit limitation. Completion: actual counters remain within every fixed limit.
4. Write the candidate and report without overwrite. Completion: report records candidate completion and explicit stop.
5. List optional review or a later user invocation of `research-gap`, then stop. Do not invoke it.

## Failure

Stop on pin drift, missing boundaries, invalid fields, unsafe paths, or budget violation. Existing files and the selected input remain unchanged.
