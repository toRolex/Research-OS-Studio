---
name: trusted-statement-comparison
description: Conservatively compare a candidate mathematical statement with a pinned trusted statement and identify semantic drift before proof or formalization.
---

# Trusted Statement Comparison

Model-invoked discipline only. Compare two exact, digest-pinned statement records supplied by the current workflow: a candidate and a separately identified trusted statement. Do not assume equivalence from names, prose similarity, examples, or a successful proof of either statement.

## Comparison procedure

1. Normalize only presentation that is explicitly semantics-preserving. Record both original digests and never replace the source records.
2. Compare binders, quantifier order, domains, hypotheses, definitions, conventions, equality or approximation notions, exceptional cases, and conclusions.
3. Map corresponding terms and clauses. For each difference classify the candidate as stronger, weaker, incomparable, presentation-only, or not verified, and give a witness or obligation when possible.
4. Check that cited trusted material actually binds the compared statement bytes and revision. A title, theorem number, repository path, or successful compilation without byte binding is insufficient.
5. Return `equivalent` only when every semantic component is accounted for by a justified transformation; otherwise return `different` or `not-verified` with exact differences.

This discipline does not authenticate the trusted principal, prove either statement, change research semantics or budget, revise the candidate, confer human acceptance, authorize advancement or proof attempts, or invoke another workflow. Ambiguity is a reason to stop for user clarification, not to choose an interpretation.
