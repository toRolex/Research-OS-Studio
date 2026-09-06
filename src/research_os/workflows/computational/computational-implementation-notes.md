# Computational leaf implementation notes

Date: 2026-09-06
Scope: L05 only.

## Inputs read

- `PLAN.md`: L05 owns five canonical computational skills, computational runtime, templates, reference project, tests, and `gates/leaf-computational.md`.
- `CONTEXT.md`: workflows are explicit user entrypoints; typed Artifact handoff; no automatic next workflow; Evidence embeds the sole canonical `supports` relation.
- GitHub Issue #24: computational stories 25–47 and implementation/testing decisions.

## Gates

1. Five complete workflow skill contracts, each stops after candidate/report production.
2. Deterministic local CPU reference experiment executes for real.
3. Programmatic counters for seconds, cost, tokens, GPU-hours, attempts, rounds hard-stop before over-budget work.
4. Append-only attempt ledger preserves failures; ordinary mode stops on first failure; bounded mode retries only within budget.
5. Analysis consumes pinned run bytes only and cannot execute/subprocess/re-run.
6. Result-to-claim never infers claim truth from run success; Evidence embeds scoped, conditioned `supports` only when assessment supports it.
7. Leaf tests and hostile negative paths pass; gate records measured evidence.

## Decisions

- Implement a standalone provider-neutral Python package under the owned workflow directory. Integration facade remains frozen for L10.
- Use immutable JSON output files and exclusive creation. Every attempt receives a unique ledger record and separate stdout/stderr files; no failed attempt is overwritten.
- Measure deterministic budget dimensions from executor receipts, with monotonic elapsed time additionally checked at workflow boundaries. Monetary/token/GPU counters default to zero for local CPU but remain mandatory fields.
- Treat limits as inclusive maxima: a candidate operation is rejected before execution when projected consumption would exceed a limit; exact exhaustion is allowed and then stops further attempts.
- Use SHA-256 pins on every workflow input. The runtime refuses mismatched bytes before producing outputs.
- Keep Artifact envelope compatible with the thin Core while defining computational type specs locally; L01/L02 integration may later register the type validators without changing this leaf runtime.

## Deviations

- The global implementation notes file is outside L05 Owns. To obey strict ownership, this task-local growing note is stored at `src/research_os/workflows/computational/computational-implementation-notes.md`.
- Canonical P0 `target` has no content-digest field for same-repository paths. Input pins therefore use `{target, sha256}` references, while `supports.target` copies the Claim's canonical full-commit Git target and the pinned Claim bytes remain in provenance.
- Analysis needs to produce derived artifacts but may not modify run inputs or trigger experiments. A dedicated `analysis/` sandbox is excluded from the mutation guard; every other project file is digest-checked before/after the analyzer callback.

## Pass log

1. **Complete implementation:** added five skills, workflow runtime, six-counter budget, append-only attempt ledger, local CPU executor, templates, reference fixture, and 12 behavior tests.
2. **Expert reread:** tightened finite `supports`, full-commit Claim requirement, exact workflow stopping, and elapsed-time accounting.
3. **Defect hunt:** fixed bounded mode incorrectly stopping after the first attempt because zero-cost dimensions were interpreted as exhausted; fixed elapsed time double-counting; allowed isolated derived analysis output while guarding experiment state.
4. **Polish:** Ruff lint/format clean; real CPU result digest measured as `14bb74736605077a994e6c9346538af6d48d4809e54f7e130f15501dd938cfc7`.
