# #55 Slice A implementation notes

## Status

- Slice A — central math-research recipe and focused contract test: **done**; changed `skills/general/research-os/SKILL.md`, `skills/general/research-os/playbooks/proof.md`, added `tests/test_spec48_ticket55.py`; red→green and post-merge focused regressions passed; code commit `a3dd38d` and integration merge `2a53fc5`.
- Slice B — leaf authorization migration: **not started; explicitly outside this slice**. Writer, repair, and formula-derivation leaf gates remain authoritative until separately migrated.
- Slice C — full installed-suite integration and role comparison: **not started; explicitly outside this slice**. Do not infer full #55 completion from Slice A; the #51 arena integration is present at the starting tip, but final combined installation/contract comparison remains outstanding.

## Entry decision and boundary

Directly execute one bounded work unit because the user assigned this implementation slice, prohibited further dispatch, and supplied the research/spec/ticket inputs and acceptance seam. Work only in the current T3 worktree; do not touch the integration checkout, tracker, push, old checkout, or test-isolation helpers.

Started at `c8c8499b1fc6e4f1d1e788228088f35ae566917e` on `t3/ticket55-math-recipe`, equal to the then-current `integration/spec-48` tip. During work the integration ref advanced to `9080258c323917e33af79c0a93a42c68c8473be2` (writing-cycle integration and test-copy isolation); merged that explicit ref on the task branch as `2a53fc5`, preserving both its writing-router edits and this slice's broader proof route.

## Decisions

- Extend the existing `proof` route/playbook rather than adding a parallel router or workflow. Keep the research objective and mandate stable while choosing or alternating local methods from evidence.
- Point at the installed arena, swarm, interrogate, formal-verification, and proof-family capabilities; preserve their distinct responsibilities and do not copy their internal prompts into the recipe.
- Reuse `mandate.md`, continuation, pickup, and improvement for authorization, quota, resumption, and improvement control. Do not introduce a second round/authorization state machine.
- Keep strict counterexamples scoped to the original claim; numerical anomalies stay candidates. A proposed main-goal replacement waits for user confirmation only on that branch; other original-goal work can continue.
- Preserve unproved equal-strength lemmas, failed methods, and the new evidence/mechanism required to reopen a route. Treat cases as method inspiration only; do not claim to have read the uncached Crouzeix prompt or certify any candidate proof.
- This slice does not migrate writer/repair/formula leaf gates, alter their product files or checker registration, or claim the full ticket is complete. Where a leaf gate still applies, it remains in force.
- No separate mathematical-method reference was added: the recipe composes the existing proof, derivation, review, repair, formal-verification, and organization Skills by their installed paths and leaves their method details/templates at their current sources of truth.
- TDD evidence: the new seven-test suite first failed against the unmodified route/recipe (expected red), then passed after the route/playbook change. Regressions passed: ticket 50 (21 tests), ticket 52 (21), ticket 59 (20), plus ticket 54's two targeted proof/formal-boundary tests.
- After merging `integration/spec-48`, the new seven-test suite, ticket 50, ticket 52, ticket 59, and the three selected ticket 54 proof/formal/flat-install tests were rerun successfully. Each command used `TMPDIR=/tmp` and a 180-second timeout.
- The full static checker currently exits 1 for nine pre-existing `docs/acceptance/**` links to ignored `evidence/*.tar.gz`; ticket 50's regression confirms there are no new checker failures. Preserve this evidence limitation; do not touch unrelated acceptance files.

## Deviations

- None so far.
