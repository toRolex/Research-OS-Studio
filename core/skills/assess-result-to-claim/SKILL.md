---
name: assess-result-to-claim
description: Assess pinned experiment findings against a pinned Claim, produce bounded support only when declared, then stop.
---

# Assess Result to Claim

User invocation only. Require complete `experiment-analysis` findings (not a previous result-to-claim assessment) and a semantic `claim` Artifact selected by full Git commit and SHA-256. Validate shared foundation/semantics contracts, exact versions, canonical provenance, real Git bytes, and identical fixed Project/Workstream bindings. Reject dangling, cross-repository, conflicting or digest-mismatched references.

Assess only the declared method, conditions, and shared JSON Pointer scope (`whole_subject` or a nonredundant pointer array, including the empty root pointer). Conditions may explicitly be `[]`. Verdict is exactly `supports`, `does_not_support`, or `inconclusive`.

Only `supports` creates an `evidence@1.0.0` Artifact. Its spec contains only `project`, `workstream`, `description`; its single relation is `{relation: supports, claim: {target, sha256}, scope, method, conditions}`. Fix the Claim at the selected real commit and digest. Provenance uses `{activity, inputs: [fixed ref]}` to retain the analysis and Claim. Support is limited use under the recorded boundary, not proof, global truth, or human acceptance.

For every verdict, preserve limitations in a separate `experiment-analysis@1.0.0` Artifact with `role: result-to-claim-assessment`; this is a research analysis, not an Assurance Assessment. `does_not_support` and `inconclusive` produce no Evidence file or relation. Never link sibling live outputs as fixed evidence or invent their commit. Return only actual output locations in the workflow report; commit-pinned handoff requires a later explicit user action. List optional next steps and stop.
