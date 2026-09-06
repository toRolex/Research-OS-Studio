---
name: design-experiment
description: Create a candidate experiment design from one user-selected pinned input, then stop.
---

# Design Experiment

User invocation only. Read the user-selected typed Artifact at its full 40-character Git commit and recorded SHA-256; reject digest-only or working-tree-only claims of pinning. Require explicit `project_ref` and `workstream_ref`, each `{target: {kind: git, path, commit}, sha256}` pointing to real committed Project/Workstream Artifacts. Validate their shared contracts and Workstream→Project binding; propagate those exact references through all five workflows. Fix the hypothesis, dataset, controls, metrics, run matrix, success criteria, failure criteria, stop criteria, and all six hard budget counters: elapsed seconds, USD cost, tokens, GPU-hours, attempts, and rounds.

Produce one candidate `experiment-design` Artifact and one workflow report. All computational Artifacts use `research-os/artifact@1.1.0`, exact type `@1.0.0`, and canonical provenance `{activity, inputs: [fixed ref]}`. Pass the shared foundation/type validators and verify referenced Git bytes before writing. Output targets are live candidates, not fixed handoffs: the user must commit outputs and supply the real commit plus digest before the next invocation. Reports list output locations for discovery only and are not Artifact handoffs. Do not prepare or run the experiment. Do not alter criteria after observing results. List optional next steps and stop; suggestions never authorize another workflow.

Reject missing pins, incomplete budgets, unsafe paths, empty criteria, output collisions, and any request to add budget without fresh user authorization. Never infer human acceptance.
