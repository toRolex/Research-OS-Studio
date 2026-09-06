---
name: research-novelty
description: Compare one pinned Research Idea against one pinned Literature Review, emit an inconclusive candidate novelty report, then stop.
---

# Research Novelty

## Contract

- Invocation: user only.
- Inputs in order: one pinned `research-idea@1.0.0`, then one pinned `literature-review@1.0.0`.
- Output: one candidate `novelty-review@1.0.0` Artifact and one workflow report.
- Fixed budget: two sources, one candidate, at most eight prior-work comparisons.
- Invariants: use only pinned prior-work records; distinguish observed differences from judgment; do not accept or reject the idea.

## Procedure

1. Verify both selected byte revisions and their distinct paths. Completion: idea and literature are independently pinned.
2. Resolve the explicitly selected idea; only a sole candidate may be used without a separate selection. Multiple or zero candidates without selection fail. Completion: the idea wording is preserved.
3. Compare against at most eight pinned `prior_work` records, falling back to pinned citations. Completion: each row records only the supplied work and supplied observed difference.
4. Emit `novelty_verdict=inconclusive` and disclose missing coverage. Completion: absence of comparison material never becomes a novelty claim.
5. Write candidate and report, list optional later actions, then stop without dispatching them.

## Failure

Stop on either pin drift, wrong input order/type, duplicate input, malformed prior work, unsafe paths, or budget violation. Existing files remain untouched.
