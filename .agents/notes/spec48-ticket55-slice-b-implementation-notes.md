# #55 Slice B implementation notes

## Status

- Writer / repair / formula-derivation authorization migration: **done**; all three have `委托继承`/`Gates: none`, bounded standalone requests, new-file writes in the delegated domain, inherited stages/retries, and unchanged-target constraints. `proof-repair` remains finding-scoped; compile command/output side effects remain separately bounded. Verified by the post-merge 14-test #55 suite and policy baseline test.
- Fresh read-only proof-review preservation: **done**; each pass rereads current full source/dependencies; review remains zero-write and separate from repair. Verified by the #55 contract test.
- proof-orchestrator compatibility conversion and resource reachability: **done for Slice B's minimum seam**; old entry routes to research-os, keeps no parallel round/quota/pause controller, and all owned audit/Lean/notation/handoff/prompt resources remain reachable in a tracked-file flat-install snapshot. Full suite installation remains Slice C.
- migration boundary + checker registration: **done**; all four migrated paths are in `MIGRATED_CONTRACT`, absent from `LEGACY_LEAF_GATES`, with `Gates: none`; the focused policy baseline passes and the checker retains exactly the nine archive diagnostics.
- Slice B integrated verification/report: **done**; report is `/tmp/spec48-ticket55-sliceB/REPORT.md`. Branch `t3/research-delegation-migration`, worktree `/Users/rolex/.t3/worktrees/Research OS Studio/t3-e338517e`; implementation commit `9f32d2fc681ac7b6339acc19cabafbe038f0750f`; merged latest instructed integration tip `86caa4fd76792b056f31d5c083fb7cd918760a4c` as `33b1193c46683c989028e9d152459d2a680c1a3d` into this branch only. Exact Slice A was already merged as `9c3dae0`.
- Slice C full-suite installation and role comparison: **not part of this unit; remains outstanding**.

## Entry decision and boundary

Directly implement this assigned work unit in the current independent T3 worktree: the user explicitly named the implementation-subagent role, supplied the exact AC and source artifacts, and prohibited further dispatch. Do not edit the integration/main checkout, touch `tests/spec48_workcopy.py` or other copy helpers, update tracker, or push. Work began at integration tip `9080258c323917e33af79c0a93a42c68c8473be2`; exact Slice A delivery `3ae1717b273c438fde0c15167de58c8874413133` was merged with history preserved as `9c3dae0`.

## Decisions and evidence

- Use contract counterexamples in the existing #55 test suite before production edits. The first focused red run found the three write Skills absent from `MIGRATED_CONTRACT` and still registered with legacy gates. A follow-up flat-install snapshot also found cross-Skill developer-relative references in proof-repair and proof-orchestrator. The snapshot uses `git ls-files` and copies only the selected tracked Skill files; it does not use the shared recursive copy helper or copy ignored evidence.
- Keep each leaf's math method and local template/reference files in its own package. For references to a different Skill's rules, name the required Skill and have it read its own bundled rules; do not use a source-tree-relative link or fork a second authoritative rule set.
- The old proof-orchestrator name will route into research-os's proof recipe; research-os remains the only owner of target, rounds, quota, pause/resume and stop control. Preserve its owned reference and prompt files and make the compatibility entry link-reachable to them.
- Preserve proof-review as a fresh review each invocation and zero-write capability; repair must not replace reviewer judgment or reuse a stale pass.
- Remove Slice A's implementation-stage wording only from product-facing proof recipe text; record the migration history and unavailable/unread case material in implementation notes, while keeping genuine applicability and non-endorsement boundaries in the recipe.
- TDD / policy evidence: the post-merge `test_spec48_ticket55.py` is green (14 tests, exit 0). The focused policy test first reported 13 diagnostics (the exact nine archive links plus four missing `Gates: none` markers, exit 1); the four markers were added without changing checker scan behavior. After merging integration, the focused policy test passed (exit 0) and the checker again showed exactly the nine expected archive-link diagnostics (exit 1).
- Known next-integration cross-point: #58 candidate `14a18ce6f34b9caff1181b240e3fe28ab539552f` is not integrated and is intentionally not merged here. It preserves #57 and migrates `academic-plotting`; later combination must relocate policy/#49/#57 old-gate negative examples currently using `proof-repair` to an actual remaining legacy leaf or replace them with damaged migrated-contract counterexamples. Do not count migrated `proof-repair` as legacy or delete negative coverage. This branch does not pre-pull the #58 candidate.
- Final post-merge commands (serial, each `TMPDIR=/tmp`, `timeout 180s`):
  - `uv run --no-project python -m unittest discover -s tests -p 'test_spec48_ticket55.py' -v` → exit **0**, 14 tests OK.
  - `uv run --no-project python -m unittest discover -s tests -p 'test_check_skills_policy_gates.py' -k checker_has_only_recorded_tarball_gaps_and_leaf_baseline -v` → exit **0**, 1 selected test OK.
  - `uv run --no-project python scripts/check-skills.py` → exit **1**, exactly the preserved nine `docs/acceptance/**` references to absent/untracked `evidence/*.tar.gz`; no migration/resource diagnostics.
  - `git diff --check 9c3dae0..HEAD` → exit **0**.
- TDD red history: the first focused test run exited **1** and included one tracked-snapshot helper path error; after correcting only that test helper, the flat-install red command exited **1** specifically because proof-repair and proof-orchestrator referenced sibling proof-review rules via source-tree-relative links. Those dependencies were changed to Skill-name/local-bundle resolution; the final snapshot passes for all five affected Skill bundles. A policy red run exited **1** with 13 lines (nine historical archives + four missing `Gates: none` migration markers); adding the required marker to the four migrated Skills restored the exact nine-only baseline. No mock was needed for these static Skill-contract seams.
- The integration merge brought its own tracked-copy-isolation commit, including changes to `tests/spec48_workcopy.py` and nearby test fixtures; those files were not hand-edited by this Slice B implementation. No `tests/spec48_workcopy.py` helper changes were authored here, and the #55 snapshot uses `git ls-files` only.
- The cached #48 spec cites the Crouzeix prompt without a pinned revision; no local copy was available during this work, so it was not read or copied. This implementation-state fact is retained here rather than exposed as product prose; the central recipe only states that cases provide method inspiration and do not endorse candidate proofs.

## Deviations

- None. The independent-install test is deliberately a minimal tracked-file snapshot, not Slice C's full package installation acceptance.
