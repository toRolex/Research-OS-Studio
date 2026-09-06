---
name: publication-claim-audit
description: Audit whether every scoped publication claim is closed by pinned evidence and assurance without overstating results or hiding conflicts.
---

# Publication Claim Audit

Model-invoked discipline only. Read the calling workflow's staged, digest-pinned manuscript, Claim, Evidence, Assessment, and external-reference records. Do not edit prose, add evidence, resolve conflicts, freeze a Publication, or accept any claim.

## Audit procedure

1. Enumerate every factual, empirical, mathematical, formal, novelty, causal, and generalization claim in the primary text, including claims implied by captions, tables, abstracts, and conclusions.
2. Map each claim to its canonical Claim identity and exact Evidence `supports` scope, method, and conditions. Flag missing, circular, stale, broader-than-evidence, or merely related material.
3. Compare wording strength with the study design, uncertainty, negative results, proof status, formal-verification status, independent review, and known limitations.
4. Check each assurance dimension separately: `structural_conformance`, `empirical_reproducibility`, `mathematical_argument_review`, `formal_verification`, `independent_review`, and `human_acceptance`. Require the versioned pinned Assessment definition and subject binding for every dimension needed by the staged profile; if it is absent, return `blocked` for that dimension. Do not average dimensions or let one favorable Assessment hide a conflicting Assessment on intersecting scope.
5. Verify that failed attempts, exclusions, deviations, counterexamples, and unresolved gaps relevant to a claim remain visible in the staged package.

Return per-claim `supported`, `unsupported`, `conflicted`, or `blocked` findings plus exact byte scopes. The result is preflight advice only; it cannot change research semantics or budget, create human acceptance, mutate the manifest, waive a gate, authorize advancement or freeze, or invoke another workflow.
