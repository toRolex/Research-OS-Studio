# Ticket #59 implementation notes

## Status

| Unit | Deliverable | Status | Evidence / next |
| --- | --- | --- | --- |
| Continuation contract | Entry route + safe continuation/pause/resume playbook | done | `skills/general/research-os/SKILL.md`, `playbooks/continuation.md`; `12 passed` targeted; installed dependency/route resources present |
| Pickup and improvement migration | Restore original artifacts/jobs/obligations; remove duplicate per-loop gate; process improvement + log | done | `playbooks/pickup.md`, `playbooks/improvement.md`, `research-improvement/{SKILL.md,references/*,templates/*}`; installed package has 22 Markdown links resolved, 0 broken |
| Checker and migration records | Missing-file diagnostics, quota/host/license/dependency checks; migration boundary and upstream provenance | done | `scripts/check-skills.py`, `references/migration-boundary.md`, `docs/upstream-sources-and-licenses.md`; checker reports only 9 known archive-link failures |
| Install and tests | Real CLI copy install, resource and dependency resolution, targeted/full tests | done | `skills` CLI 1.7.4 copied 2 skills (41 discovered); required resources 10/10 and 22 links checked/0 broken; targeted 12 passed, full suite baseline 7 failures/127 passed/44 subtests |
| Commit, integrate, post-merge verification | Commit all ticket changes, merge latest integration tip, rerun tests/checker/install | done | ticket commit on `t3/a14e0648`; latest local integration `e84f779` already up to date; post-commit tests, checker, installation and clean status recorded below |

## Scope and boundary

- Implements #59 of Spec #48 in this worktree only; no dispatches, no changes to proof family (#55), experiment leaf (#56), or writing leaf (#57).
- Retains parent-provided initial staged/unstaged work and the already-added test file; do not reset/clean or overwrite.
- Upstream method archive: `cursor/plugins` pstack subtree @ `88d47514b82e7c44f00f2b2a72ff6dd12158038c`; source/notice and MIT text are co-located in the independent `research-improvement` package.
- Before implementation, read the requested Multi-Agent, model availability, pstack model, and coding standards files; DS/GLM/Grok/Kimi are prohibited. TDD/pre-implement/writing-for-agents loaded; no TDD skill exists under the requested name in this environment. Current execution is direct, limited work—no further delegation.

## Decisions and fixes

1. Kept continuation and improvement in existing Research OS structures. `continuation.md` defines verifiable exit conditions, minimum evidence-based steps, cumulative wall-clock and resource accounting, safe pause state, pickup, stalled-route change, honest dead-end handoff, and host capability limits without claiming a background service.
2. Updated `pickup.md` to re-check approvals, authorization, raw artifacts, outstanding obligations and active jobs; old summaries remain leads, not proof. It does not renew `valid_until` or rerun verified unchanged work.
3. Migrated `research-improvement` to inherit `research-os` mandate rather than require per-loop re-approval. Batch experiments remain governed by batch authorization. Improvement workflow retains independent fresh review, evidence and failed attempts, and records process/tool proposals; public suite changes and external tracker creation remain explicit decisions.
4. Independent installation exposed broken cross-skill relative links in flattened layout. Added `references/dependencies.md` mapping the shared `<skills-root>` resources and branch-specific skill dependencies, plus missing/unsupported dependency behavior (`blocked`). Removed sibling-relative Markdown links that would fail under flat installation; skill names now resolve through this manifest.
5. Extended `continuation_contract_problems` to diagnose a missing continuation playbook instead of raising `FileNotFoundError`, and to verify tracked source/license/dependency assets. Did not weaken its existing quota, host-neutrality, or contract markers.
6. Preserved the known historical checker failure class: nine missing, intentionally untracked acceptance evidence archives. No new failure was suppressed or reclassified as a pass.

## Recovery-stage red/green and verification evidence

All commands below explicitly ran in this worktree. Python commands use `uv`; the cached pytest package was required because `uv run --offline ... pytest` could not spawn `pytest` directly. Working invocation:

```sh
cd '/Users/rolex/.t3/worktrees/Research OS Studio/t3-a14e0648'
PYTHONPATH='/Users/rolex/.cache/uv/archive-v0/ZHSqs5vxcDKWb5QD/lib/python3.14/site-packages' \
  uv run --offline python -m pytest ...
```

- **Recovery-stage targeted red before checker correction**: `... pytest -q tests/test_spec48_ticket59.py` → `2 failed, 8 passed`, exit 1. One failure confirmed the checker raised `FileNotFoundError` for absent `continuation.md`; another showed the missing quota/host-neutrality damaged fixture did not report host binding. This is a recovery-stage targeted regression, not a claim of original first-red evidence.
- **Targeted green after checker and contract fixes**: `... pytest -q tests/test_spec48_ticket59.py` → `12 passed`, exit 0 (rerun after final test edits still 12 passed).
- **Whole applicable suite**: `... pytest -q tests scripts/test_check_skills_ticket*.py` → `7 failed, 127 passed, 44 subtests passed`, exit 1. Failing tests are the known baseline set: `test_checker_green_and_leaf_baseline`, `test_gate_baseline_and_counterexamples`, `test_shipped_templates_and_full_checker`, `test_valid_policy_and_log_fields`, `test_valid_role_table`, `test_full_cli_damaged_declarations_refs_and_readme`, and `test_compute_limits_are_per_unit_not_summed`; each is triggered by the same nine missing acceptance evidence tarball links. No new test failed.
- **Full checker**: `uv run --offline python scripts/check-skills.py` → `FAIL: 9`, exit 1; all nine are the historical evidence archive links, with no continuation, license, dependency, route, quota or migration diagnostic.
- **Diff formatting**: `git diff --cached --check` → exit 0 before commit; `git diff HEAD^ HEAD --check` → exit 0 after commit.
- **License integrity**: pinned upstream `pstack/LICENSE` and shipped `UPSTREAM-LICENSE.md` both SHA256 `bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e`.
- **Real install**: `skills` CLI 1.7.4, run from `/tmp/spec48-59-install` after final dependency-link edits; a separate package-only install was also run in `/tmp/spec48-59-improvement-only`:

```sh
node /Users/rolex/.npm/_npx/5606f1555d02ef53/node_modules/skills/bin/cli.mjs \
 add '/Users/rolex/.t3/worktrees/Research OS Studio/t3-a14e0648' \
 -s research-improvement -s research-os -a claude-code -y --copy
```

  Paired install exit 0, discovered 41 skills, copied both actual skill packages. Required installed resources were present (10/10), including `research-os/references/{mandate.md,batch-authorization.md}` and all improvement references/templates/notices/licenses. Installed flattened layout link check: 22 Markdown links checked, 0 broken. Package-only install exit 0 copied `research-improvement`; its seven package assets were present, its manifest declares both Research OS shared dependencies and `blocked` behavior, and its 22 intra-package Markdown links had 0 broken.
- **Commit/integration**: ticket commit `feat(research-os): support continuation and improvement (#59)` on branch `t3/a14e0648` (full hash from final `git log -1`). `git fetch origin integration/spec-48` exited 128 (`couldn't find remote ref`); local integration tip `e84f779d78755937a59d46364e14cc6496aa2b03` was merged with `git merge --no-edit integration/spec-48` (already up to date, exit 0). Post-commit target tests 12 passed; full suite remains the baseline 7 failures; checker remains 9 historical missing archives; installed layout 0 broken links; worktree clean. `HEAD` is the ticket commit atop latest local integration tip.

## Deviations and limits

- No original red run is claimed; only the recovery-stage red above is evidenced.
- No real research execution, model behavior, long-running host service, production server job, or mathematical result was verified. Static text contracts and installation prove package structure/resource reachability only.
- The full suite/checker still return non-zero because of the same nine historical untracked archive links; no workaround or test skip was added.

## Remaining limits

- Remote `origin` branch `integration/spec-48` does not exist, so only the current local integration tip `e84f779` could be merged. No push was authorized or attempted.
- No real research execution, model behavior, long-running host service, production server job, or mathematical result was verified. Static text contracts and installation prove package structure/resource reachability only.
- The full suite and checker still return non-zero because of the exact nine historical untracked acceptance archive links; no workaround or test skip was added.
- No PR, issue write, cleanup or worktree removal was done.
