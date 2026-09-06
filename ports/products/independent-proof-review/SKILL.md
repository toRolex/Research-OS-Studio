---
name: independent-proof-review
description: Review a fixed mathematical statement and proof from fresh enumerated inputs, seeking counterexamples and proof gaps without repairing the proof.
---

# Independent Proof Review

Model-invoked discipline only. The calling workflow must provide the exact statement revision, proof revision, raw-byte digests, actor identities, and an enumerated input manifest. Start from fresh context without conversation history, hidden state, or the proof actor's interpretation. If these conditions are not established, return `blocked` rather than claiming independence.

## Review procedure

1. Reconstruct the statement literally: quantifiers, hypotheses, domains, definitions, equality notions, and conclusion. Do not strengthen assumptions or weaken the conclusion.
2. Search for boundary examples and counterexamples before following the proposed argument. Preserve any counterexample as a finding against the fixed statement.
3. Verify every lemma, dependency, case split, algebraic or analytic transition, appeal to a theorem, and discharge of side conditions. Identify circularity, hidden regularity assumptions, undefined terms, and quantifier changes.
4. Separate local gaps from a false statement. Do not fill a gap silently; state the missing proposition and why later steps depend on it.
5. Return one closed verdict: `false-statement` when a valid counterexample refutes the fixed statement; `proof-gap` when the statement is not refuted but at least one required proof obligation is unresolved or invalid; `not-verified` when fixed inputs or independence evidence are insufficient; `no-major-finding` only when the review establishes neither a counterexample nor an unresolved required obligation. Include exact scope, findings, unresolved obligations, and fixed statement/proof/input-manifest digests.

The review cannot change research semantics or budget, revise the statement, write a replacement proof, confer human acceptance, claim formal verification, authorize advancement, invoke formalization, or invoke another workflow. Any changed statement or proof invalidates the verdict and requires a fresh review.
