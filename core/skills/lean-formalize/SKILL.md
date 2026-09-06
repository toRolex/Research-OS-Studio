---
name: lean-formalize
description: Explicitly formalize one confirmed and independently reviewed mathematical statement in a locked Lean project, then audit and replay it without changing the statement.
---

# Lean Formalize

This is an optional, late, user-invoked workflow. Never start because Lean is detected and never run automatically after `math-proof`.

## Hard prerequisites

Refuse before tool execution unless all are fixed and digest-bound:

- a confirmed statement revision;
- an ordinary candidate proof;
- an executed independent proof review;
- exact authorization `AUTHORIZE LEAN r<revision> <statement-digest>` from a named user principal;
- a positive hard attempt bound;
- `lean-toolchain`, exact Lake version, exact non-floating dependency revisions, source hashes, allowed imports, permitted axioms, comparator declaration, and independent replay principal.

## Allowed iteration

Within the hard attempt budget, process only caller-supplied candidate revisions of definitions, lemmas, proof terms, and build-error fixes. Do not invent an unbounded retry loop. Never weaken, replace, or rename away the trusted statement. Any semantic statement change returns `statement-mismatch` and requires a new ordinary statement revision and user confirmation outside this workflow.

## Deterministic verification chain

For every candidate:

1. validate metadata and all locked file hashes;
2. reject executable source tokens `sorry`, `admit`, placeholders, or `unsafe` outside comments;
3. reject undeclared imports and source-declared axioms not in the explicit permit list;
4. compare the normalized trusted and solution declaration statements against the locked comparator digest;
5. probe exact Lean/Lake runtime versions;
6. run `lake build`;
7. run the kernel axiom audit and require all reported axioms to be permitted;
8. run an independent `lake build` replay under a different recorded principal and produce a digest-bound receipt.

Results are only `verified`, `not-verified`, or `statement-mismatch`. Stop reasons are separately `workflow-complete`, `proof-gap`, `tooling-blocked`, `budget-exhausted`, `execution-failed`, or `user-stopped`. Missing Lean/Lake or a runtime-version mismatch is structured BLOCKED with exit code 3. Audit, comparator, build, and replay failures are exit code 1. Never report BLOCKED as PASS.

A Lean pass covers only the fixed Lean statement in the recorded trusted base. It does not establish natural-language alignment, paper correctness, research significance, or human acceptance.
