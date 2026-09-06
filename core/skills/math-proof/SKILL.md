---
name: math-proof
description: Explicitly run one bounded ordinary-mathematics proof workflow while preserving statement control, failed attempts, proof gaps, and independent review boundaries.
---

# Math Proof

Run only after the user explicitly invokes `math-proof`. Read only the pinned inputs named by the user. Work inside this invocation and stop after writing candidate records and a workflow report; never invoke `lean-formalize` or another user workflow.

## Required control sequence

1. Record examples and adversarial counterexamples before claiming a candidate proof. A counterexample is retained evidence and stops the current statement; do not silently add assumptions to evade it.
2. Produce a statement candidate whose semantic identity includes quantifiers, hypotheses, domain, and conclusion.
3. Require the exact user confirmation `CONFIRM STATEMENT r<revision> <semantic-digest>` before proof attempts.
4. If any quantifier, hypothesis, domain, conclusion, or other mathematical meaning changes, create the next revision with a `supersedes` digest, discard the old confirmation for the new revision, and stop for reconfirmation.
5. Build an acyclic lemma map with explicit dependencies and `open|proved|gap` status.
6. Respect the invocation's positive integer `max_attempts`. Retain every attempt with its approach, full argument, outcome, and gaps. Never continue after the bound.
7. Emit mathematical result separately from stop reason. Stop reasons are `workflow-complete`, `counterexample-found`, `statement-unconfirmed`, `proof-gap`, `budget-exhausted`, `execution-failed`, or `user-stopped`.
8. Request independent proof review only as an optional next step. Review does not confer human acceptance. Human acceptance remains a separate user-owned Assessment.

## Independent review receipt

A review is independent only when it fixes the exact statement and proof digests, uses a principal different from the proof actor, starts from a fresh context, receives only an enumerated fixed input manifest, excludes conversation history and hidden state, and records the input-manifest digest. A new statement or proof revision invalidates the old review.

Use `templates/mathematical/` records and the deterministic validators in `research_os.workflows.mathematical`. Preserve failures; never overwrite old records or convert a gap into a pass.
