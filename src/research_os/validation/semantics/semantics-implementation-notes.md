# Semantics leaf implementation notes

## Scope

Only `core/contracts/semantics/**`, `src/research_os/validation/semantics/**`, `tests/contracts/semantics/**`, and `gates/leaf-semantics.md`.

## Decisions

- 2026-09-06: Keep L02 self-contained while L01 is being implemented concurrently; expose small validator modules and no shared-facade edits.
- 2026-09-06: Semantic contracts are strict JSON Schema type-spec contracts. Python validators additionally validate the common Artifact envelope and cross-object invariants.
- 2026-09-06: Every cross-artifact dependency is a fixed reference: a fixed Git/URI target plus the referenced bytes SHA-256. Live Git targets are valid Artifact identities but invalid dependency bindings.
- 2026-09-06: JSON Pointer scopes use either `whole_subject` or a non-empty unique pointer array. Overlap is token-prefix overlap, not string-prefix overlap; RFC 6901 escaping is validated.
- 2026-09-06: Project principals have one or more explicit roles. Human acceptance requires a bound Project principal with `user`; independent review requires a different principal and a receipt fixing inputs and declaring fresh-context isolation.
- 2026-09-06: Migration rule selection is explicit and unique. Rules use structured inclusive/exclusive SemVer bounds; receipts bind input/output refs, rule, migrator, both validators, and their pass verdicts.

## Deviations

- The shared Issue/target API owned by L01 was not present when L02 began. To avoid touching or waiting on shared facades, L02 uses private equivalents behind its own public modules. L10 may adapt the facade without changing these validators.
- The orchestration notes are outside this leaf ownership. This leaf keeps its growing notes in this directory.

## Pass log

- Pass 1 — implementation: complete; final leaf suite has 26 tests.
- Pass 2 — expert reread: independent local contract/validator cross-read complete; no source was sent to any external service.
- Pass 3 — defect hunt: hostile review confirmed and fixed stale green tests, non-executable schema contracts, overly broad target normalization, self-reported fixed refs, symlink Git objects, unbound Assessment evidence, and context-free migration receipts. Fixed Git verification reads the named commit object rather than the mutable worktree.
- Pass 4 — polish: modules remain split by PLAN interface; provider/control scans and the 34-test leaf suite pass. No external environment was executed or reported as pass.
