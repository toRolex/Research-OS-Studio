---
name: experiment-audit
description: Audit a pinned experiment protocol and run for traceability, protocol drift, execution integrity, and unsupported conclusions inside the current workflow.
---

# Experiment Audit

Model-invoked discipline only. Work only inside the calling workflow and only from its enumerated, digest-pinned protocol, preparation, run, logs, and result bytes. Do not start, rerun, repair, cancel, or extend an experiment.

## Audit procedure

1. Bind every finding to the exact Project, Workstream, commit, path, SHA-256, run identity, attempt, and declared budget present in the inputs. Treat absent bindings as unknown, never inferred.
2. Compare the executed command, environment, inputs, metrics, criteria, seeds, resource limits, and output inventory against the preregistered protocol. Record each deviation separately, including deviations that appear beneficial.
3. Check that failures, partial outputs, exclusions, retries, timeouts, and negative results remain visible and that attempt identities cannot be collapsed or overwritten.
4. Trace every reported result to immutable output bytes. Distinguish observed output, derived statistic, interpretation, and Claim support; one cannot substitute for another.
5. Classify each finding as `blocker`, `major`, `minor`, or `note`, with exact evidence, affected scope, and a conservative remediation that requires a new user-authorized workflow when execution would change.

Return `pass` only when no blocker or major finding remains. Return `blocked` when required pinned evidence is unavailable and `fail` when supplied evidence contradicts the protocol or integrity contract. The result is advisory input to the calling workflow; it cannot change research semantics or budget, confer human acceptance, authorize advancement, or invoke another workflow.
