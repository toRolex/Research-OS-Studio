# #55 Slice B implementation notes

## Status

- Writer / repair / formula-derivation authorization migration: **done pending final merged-tip verification**; all three have `委托继承`/`Gates: none`, bounded standalone requests, new-file writes in the delegated domain, inherited stages/retries, and unchanged-target constraints. `proof-repair` remains finding-scoped; compile command/output side effects remain separately bounded.
- Fresh read-only proof-review preservation: **done pending final merged-tip verification**; each pass rereads current full source/dependencies; review remains zero-write and separate from repair.
- proof-orchestrator compatibility conversion and resource reachability: **done pending final merged-tip verification**; old entry routes to research-os, keeps no parallel round/quota/pause controller, and all owned audit/Lean/notation/handoff/prompt resources remain reachable in a tracked-file flat-install snapshot.
- migration boundary + checker registration: **done pending final merged-tip verification**; all four migrated paths are in `MIGRATED_CONTRACT`, absent from `LEGACY_LEAF_GATES`, with `Gates: none`; static policy regression passes after fixing the required declaration marker.
- Slice B integrated verification/report: **in progress**; task branch is based at `9080258`, Slice A exact delivery was merged as `9c3dae0`; next merge only the specified integration tip `86caa4fd76792b056f31d5c083fb7cd918760a4c` into this branch, rerun bounded checks, commit notes/report, and record the final SHA.
- Slice C full-suite installation and role comparison: **not part of this unit; remains outstanding**.

## Entry decision and boundary

Directly implement this assigned work unit in the current independent T3 worktree: the user explicitly named the implementation-subagent role, supplied the exact AC and source artifacts, and prohibited further dispatch. Do not edit the integration/main checkout, touch `tests/spec48_workcopy.py` or other copy helpers, update tracker, or push. Work began at integration tip `9080258c323917e33af79c0a93a42c68c8473be2`; exact Slice A delivery `3ae1717b273c438fde0c15167de58c8874413133` was merged with history preserved as `9c3dae0`.

## Decisions and evidence

- Use contract counterexamples in the existing #55 test suite before production edits. The first focused red run found the three write Skills absent from `MIGRATED_CONTRACT` and still registered with legacy gates. A follow-up flat-install snapshot also found cross-Skill developer-relative references in proof-repair and proof-orchestrator. The snapshot uses `git ls-files` and copies only the selected tracked Skill files; it does not use the shared recursive copy helper or copy ignored evidence.
- Keep each leaf's math method and local template/reference files in its own package. For references to a different Skill's rules, name the required Skill and have it read its own bundled rules; do not use a source-tree-relative link or fork a second authoritative rule set.
- The old proof-orchestrator name will route into research-os's proof recipe; research-os remains the only owner of target, rounds, quota, pause/resume and stop control. Preserve its owned reference and prompt files and make the compatibility entry link-reachable to them.
- Preserve proof-review as a fresh review each invocation and zero-write capability; repair must not replace reviewer judgment or reuse a stale pass.
- Remove Slice A's implementation-stage wording only from product-facing proof recipe text; record the migration history and unavailable/unread case material in implementation notes, while keeping genuine applicability and non-endorsement boundaries in the recipe.
- TDD / policy evidence so far: `test_spec48_ticket55.py` is green (14 tests, exit 0). The focused policy test first reported 13 diagnostics (the exact nine archive links plus four missing `Gates: none` markers, exit 1); the four markers were added without changing checker scan behavior. Re-run that policy test and the checker once after the integration merge. The direct checker baseline previously showed exactly the nine expected archive-link diagnostics (exit 1); re-confirm after merge.
- Known next-integration cross-point: #58 candidate `14a18ce6f34b9caff1181b240e3fe28ab539552f` is not integrated and is intentionally not merged here. It preserves #57 and migrates `academic-plotting`; later combination must relocate policy/#49/#57 old-gate negative examples currently using `proof-repair` to an actual remaining legacy leaf or replace them with damaged migrated-contract counterexamples. Do not count migrated `proof-repair` as legacy or delete negative coverage. This branch does not pre-pull the #58 candidate.

## Deviations

- None. The independent-install test is deliberately a minimal tracked-file snapshot, not Slice C's full package installation acceptance.
