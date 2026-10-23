# #60 flat-install link fix — implementation notes

## Status

| Work unit | Status | Artifacts / evidence | Next |
|---|---|---|---|
| Fix 13 full-install edges and declare paper-writing's standalone dependency boundary | done | Implementation commit `3df3c63de4f6c06f096d178d2187094e2191ca25`; focused contract tests 4/4 green | None |
| Validate isolated Skills CLI 1.7.4 installs | done | `/tmp/spec48-install-link-fix/REPORT.md`; committed-source full/single install logs and SHA-bound audit | None |
| Submit isolated implementation | done | Implementation commit above; this final notes update is committed separately | Parent can merge this isolated branch; no push performed |

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
- Committed source identity: implementation SHA `3df3c63de4f6c06f096d178d2187094e2191ca25`, tree `f37bcd8120689d70b1381348c4fcfb7f01ff2d3e`, branch `t3/fix-flat-install-skill-links`, worktree `/Users/rolex/.t3/worktrees/Research OS Studio/t3-94e8135d`.
- Committed-source CLI `skills@1.7.4`: version, full 41, single `paper-writing`, and single `paper-compile` each rc=0 with separate HOME/cwd. Full install: 41 installed, 0 failed, 332 files, 57 license/notice files, no symlinks, 393/393 concrete local paths resolve. Paper-writing single retains 20 expected sibling/resource misses; paper-compile single is 7/7 resolved.
- Full manifest source/install SHA-256: `513af6a354200e1dc53d26c6185b9a0ec2f48790b3670bdef970fb0c82b351b2`. All 12 mandate excerpt copies match canonical SHA `60c40e03b390ed08241067d7e256094cb6fdf5af35343a930e0ec6a1bd0899a0`.
- `uv run --offline --no-project python -m unittest tests/test_ticket60_flat_install_links.py tests/test_spec48_ticket60.py tests/test_spec48_ticket60_bridge.py tests/test_spec48_ticket60_contract_M.py`: 15 tests passed. `pytest` could not import in the offline uv environment (`No module named pytest`, rc=1); the stdlib unittest suite ran successfully. The full 328-node suite and known #45/archive failures were not re-run or altered.
- Final report: `/tmp/spec48-install-link-fix/REPORT.md`, SHA-256 `0bfdaa6f8d86bb6f872a894a0204bb3df67c137d3c9a62fcdec73a5747e6d273`. Raw committed-source install/test logs and complete file/link audit are under `/tmp/spec48-install-link-fix/committed/`.

## Deviations

- `pytest` was unavailable in the isolated uv environment; scoped tests were run through stdlib `unittest` instead. No scope or authorization deviations.
