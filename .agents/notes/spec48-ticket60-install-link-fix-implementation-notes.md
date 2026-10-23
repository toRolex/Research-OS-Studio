# #60 flat-install link fix — implementation notes

## Status

| Work unit | Status | Artifacts / evidence | Next |
|---|---|---|---|
| Fix 13 full-install edges and declare paper-writing's standalone dependency boundary | 待验收 | `tests/test_ticket60_flat_install_links.py` is green (4 tests); initial red was 1 error / 3 failures | Repeat real CLI installs from the committed source tree |
| Validate isolated Skills CLI 1.7.4 installs | in progress | Baseline: `/tmp/spec48-ticket60-final-install/REPORT.md`, `install-audit.json`; provisional CLI runs rc=0 before commit | Reinstall all 41 and representative standalone writing leaves with fresh HOME/cwd bound to committed tree |
| Submit isolated implementation | not started | This notes file | Commit only after report and verification are complete |

## Entry decision and work-unit boundary

- Direct execution: the parent assigned one bounded implementation unit and explicitly prohibited further delegation. No additional worker was started.
- Worktree `t3/fix-flat-install-skill-links` was clean at entry and fast-forwarded to requested candidate `f7b03400a4b77bc77265e9076199977815163a87` before exploration or edits.
- Scope: the 12 writing-Skill mandate edges, the `paper-writing` → `proof-review` route, necessary co-located mandate references, and `paper-writing` standalone dependency/blocked-branch wording. Do not touch integration/tracker, archive regressions, #45 tests, or research-improvement's composition map.
- No TDD-named skill is installed in the available skill roots; follow the requested red/green sequence directly. `writing-for-agents` favors one canonical authority; package-local excerpts are a distribution copy only and must point to the canonical mandate.

## Decisions

- Full mandate is not copied verbatim: it links to other research-os references and is too broad for a standalone writing leaf. Use a self-contained, license-preserving distribution excerpt sourced from `skills/general/research-os/references/mandate.md`, mirroring the existing validation-cycle package pattern. Keep the canonical full mandate authoritative; every installed leaf gets byte-identical excerpt content and its existing package license remains intact.
- Resolve each leaf's contract through `references/mandate.md`, which works in source and in Skills CLI's flattened `--copy` tree. Do not rely on a category-directory path that only parses in a full checkout.
- Invoke the conditional proof review by discoverable `proof-review` slug, not a source-category path. Declare `paper-writing`'s required/conditional sibling packages; missing a needed package blocks only that stage and must not be represented as a complete workflow.
- Baseline installer audit has 13 full-install misses: 12 mandate edges plus one proof-review category path. The paper-writing single-install's 20 sibling/resource references are dependency absences, not additional full-install broken paths; classify these explicitly rather than claiming single-package full workflow support.

## Verification so far

- Red/green: the newly added focused contract test failed before the fix (1 missing excerpt error, 3 assertions red), then passed 4/4 after the changes.
- `uv run --offline --no-project python -m unittest tests/test_ticket60_flat_install_links.py tests/test_spec48_ticket60.py tests/test_spec48_ticket60_bridge.py tests/test_spec48_ticket60_contract_M.py`: 15 tests passed. A pytest invocation was attempted but the isolated uv environment has no `pytest` module (rc=1); the stdlib unittest suite ran successfully.
- Provisional fresh-cache CLI 1.7.4 installs (full 41, paper-writing, paper-compile) each returned rc=0 and exact-copy audits passed. These were run before commit and are not the final acceptance evidence; repeat on the committed source tree.

## Deviations

- None so far.
