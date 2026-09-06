---
name: environment-check
description: Verify that a pinned computational environment is complete, immutable, compatible, and replayable without installing or mutating anything.
---

# Environment Check

Model-invoked discipline only. Inspect the calling workflow's pinned environment manifest and referenced local evidence. Remain read-only: do not install packages, pull images, probe remote services, rewrite lockfiles, or execute the experiment.

## Check procedure

1. Inventory the operating system, architecture, interpreter, toolchain, package lock, executable or image digests, hardware requirements, locale, time zone, environment variables by name, and external service prerequisites declared by the protocol.
2. Require immutable identities for every item that can drift. A tag, branch, unversioned executable name, editable dependency, mutable data location, or secret value copied into evidence is a finding.
3. Compare protocol requirements with recorded capabilities and distinguish `supported`, `unsupported`, and `unverified`. Availability alone does not prove compatibility or isolation.
4. Check dataset and input identities, filesystem layout, working directory, output paths, network assumptions, resource limits, and deterministic settings needed for replay.
5. Report missing provenance, incompatible constraints, undeclared dependencies, secret exposure, and host-specific assumptions with exact pinned scope and remediation.

Return `pass`, `fail`, or `blocked` plus structured findings. A pass attests only to the inspected manifest and evidence; it cannot change research semantics or budget, prove empirical reproducibility, perform a run, confer human acceptance, authorize advancement, or invoke another workflow.
