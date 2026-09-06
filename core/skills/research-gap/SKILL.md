---
name: research-gap
description: Derive bounded research-gap candidates from one user-selected pinned Literature Review Artifact, report support limits, then stop.
---

# Research Gap

## Contract

- Invocation: user only.
- Input: exactly one pinned `literature-review@1.0.0` Artifact.
- Output: one candidate `research-gap@1.0.0` Artifact and one workflow report.
- Fixed budget: one source, one candidate, at most three gaps.
- Invariants: derive only from the selected literature revision; preserve evidence links; leave selection to the user.

## Procedure

1. Verify the selected literature bytes, contract, and type. Completion: the source revision is fixed.
2. Copy at most three declared gap candidates. For each, require every evidence entry to exactly match a citation record in the pinned Literature Review; empty evidence is explicitly `unsupported`. Completion: no source or support is invented.
3. When no evidence-backed gap is declared, emit one explicitly `unsupported` candidate rather than a fabricated gap. Completion: uncertainty is visible.
4. Write the candidate with `selection=null` and a report whose actual counters fit the fixed budget. Completion: both outputs are non-overwriting.
5. List review or a later explicit `research-idea` invocation, then stop. Do not select a gap or continue.

## Failure

Stop on pin drift, wrong type, malformed evidence, unsafe paths, or budget violation. Preserve all prior files.
