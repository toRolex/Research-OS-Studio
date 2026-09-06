# Mathematical leaf implementation notes

## Scope

Only `core/skills/math-proof/**`, `core/skills/lean-formalize/**`, `src/research_os/workflows/mathematical/**`, `templates/mathematical/**`, `reference-projects/mathematical/**`, `tests/mathematical/**`, and `gates/leaf-mathematical.md`.

## Decisions

- 2026-09-06: Keep this leaf self-contained and import no shared facade implementation because the shared facade files are frozen for L10 integration.
- 2026-09-06: Model every record as deterministic JSON with strict required/allowed fields, stable issue codes, and SHA-256 binding between statement, proof, review, Lean source, and replay receipts.
- 2026-09-06: Separate mathematical result (`candidate`, `proof-gap`, `reviewed`) from stop reason; ordinary proof never probes or invokes Lean.
- 2026-09-06: Treat semantic statement identity as a canonical digest over quantifiers, hypotheses, domain, and conclusion. Any changed component requires a new monotonically increasing revision and a confirmation bound to that revision/digest.
- 2026-09-06: Independent review requires a different reviewer principal, an exact fixed input manifest, no conversation/history carry-over, and an isolation receipt digest.
- 2026-09-06: Lean execution requires explicit authorization, fixed toolchain/dependencies, confirmed statement, ordinary proof, and completed independent review. It never edits source or statement; bounded attempts mean bounded replay of caller-provided candidate source revisions.
- 2026-09-06: Lean tooling absence is exit code 3 with `tooling-blocked`. Audit or kernel failures are exit code 1 and cannot be reported as verified.
- 2026-09-06: A fixed dependency-free Lean fixture is included. This workstation has no `lean`, `lake`, or `elan`; therefore the fixture test verifies honest BLOCKED locally and is structured to require real PASS when `RESEARCH_OS_REQUIRE_LEAN=1` in the release environment.

## Deviations

- The orchestration-level implementation notes file is outside this leaf's ownership. To obey the user's stricter Owns rule, this leaf keeps its growing notes at `src/research_os/workflows/mathematical/mathematical-implementation-notes.md`.
- The release requirement says the fixed environment must truly pass Lean, while the current workstation lacks the toolchain and new external code/tool installation is forbidden. The conservative behavior is an explicit unmet release gate rather than fabricating PASS or installing Lean.

## Pass log

- Pass 1 — implementation: completed. Added strict statement/proof/review records, bounded ordinary proof execution, Lean metadata/audit/build/comparator/replay execution, skills, templates, and a fixed reference project.
- Pass 2 — expert reread: completed. Tightened review verdict gating, result/stop-reason separation, exact metadata fields, source/config locks, report digests, and failure accounting.
- Pass 3 — defect hunt: completed. Added hostile coverage for transitive and unused Lean sources, multi-import syntax, symlink/path escape, custom replay-command injection, source replacement, stale authorization, comparator mismatch, build-budget classification, and isolated replay drift.
- Pass 4 — polish: completed. Ruff lint/format clean; 31 leaf tests pass; documentation and claim boundary aligned with Issue #24 and official Lean/Lake project behavior.
