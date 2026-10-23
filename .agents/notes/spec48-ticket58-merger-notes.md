# Spec48 #58 merger notes

## Entry and scope

Direct execution: the user explicitly prohibited further dispatch. This isolated branch started at the exact accepted base `9080258c323917e33af79c0a93a42c68c8473be2`; #58 source is `5668ed6eecd4b1194da324ba951960c364ea4ac8`. No integration ref, main checkout, remote, or issue tracker was written.

## Conflict decisions

- Keep #51 `arena` in both catalogs; use #58's gap-driven/composable `idea-discovery` description. Both README catalogs enumerate the actual 46 Skill paths exactly once.
- Keep #57's unified `paper-writing` route, on-demand ML/Systems standards, delegated compile/citation-fix authorization inheritance, read-only audits, and no auto-submission wording. #58's writing-cycle product delta is limited to `academic-plotting`; its shared discovery/retrieval assets remain separate.
- Union the checker registrations: #58's idea-cycle leaves and `academic-plotting` enter `MIGRATED_CONTRACT`; only the remaining formula/proof leaves stay in `LEGACY_LEAF_GATES`. Keep migration, continuation, ticket-59, formal/behavior verification, experiment, arena, and research-asset checks. The damaged-gate fixture now targets still-unmigrated `proof-repair`.
- Repository-copy tests use `tests/spec48_workcopy.py`; no whole-ROOT `copytree` remains in policy, #54, #56, or #58 workcopy paths. Small per-Skill fixture copies remain local to their tests.

## Pre-integration evidence

- Focused #58/policy/49/51/57/59 run: 103 passed, 66 subtests passed.
- Joint 49/50/51/52/53/54/56/57/58/59 + copy-isolation/policy + ticket checker run: 274 passed, 137 subtests passed.
- Full suite: 6 failed, 294 passed, 179 subtests; the six failing node IDs exactly match `/tmp/spec48-test-copy-isolation/logs/full-suite-post-commit.log`. No historical failure was changed to manufacture green.
- `scripts/check-skills.py`: exit 1 with exactly the original nine archive-link diagnostics; stdout byte-matches `/tmp/spec48-closed-baseline/logs/head-checker.log`.
- Skills CLI 1.7.4 installed the merged full package into `/tmp/spec48-58-merger/install/full`; all 46 Skill directories and 338 files match source path/content hashes. The prior 7 single-Skill and Discovery-group install evidence remains applicable because those payloads are unchanged.

The latest integration-tip merge and its affected-copy regression rerun are recorded in `/tmp/spec48-58-merger/REPORT.md`.
