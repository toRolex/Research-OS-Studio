# #51 integration resume notes

## Status

| Work unit | Status | Artifact / evidence | Next |
|---|---|---|---|
| Integrate #51 with current Spec48, install, and regression verification | done | Product commit `3096cf0a1044ee210ab090f6db539b782574c556`; full acceptance report `/tmp/spec48-51-resume/REPORT.md`; source `t3/arena-capability` merged as `1553ca4817304129a827d0be1b386213f90ff554` | 无 |

## Entry decision and scope

- Direct execution: this is one tightly coupled ticket-resume unit, and the user explicitly prohibited further dispatch. No workers are used.
- Preconditions: the new worktree was clean at the requested base; the old source worktree was clean at `54674a367393a9f25d27303cff0d4d7401510e11`. No source snapshot was needed, and the old worktree remains read-only.
- The source branch contains eight commits beyond the requested base; its history is preserved by the merge above. The old review's 503 is not treated as approval.
- Acceptance source: `/tmp/spec48-goal-preflight/{REPORT.md,spec.json,tickets.json}` and #51's five acceptance criteria. Test seams were pre-confirmed in #48 Testing Decisions: installed skill suite; structure/explicit contracts; helper positive and negative examples.
- Existing `ticket51-evidence/` is historical evidence only. Fresh verification in this worktree will be recorded separately; known historical checker archive-link failures and seven full-suite failures remain visible and are not suppressed.
- Arena content is inherited, not to be rewritten. Preserve complete candidate reading, rubric-before-run, synthesis across cross-judging, hand-edited graft, and whole-result mathematical recheck (assumptions, notation, dependency closure); a selected candidate is not proof.

## Decisions / deviations

- Do not claim prior red evidence as newly produced. Current resume evidence is separate from the source branch's historical notes.

### Cycle 1 — installable entry discovery

- Fresh baseline on this worktree: `uv run --offline --no-project --with pytest --with pytest-subtests python -m pytest -q tests/test_spec48_ticket51.py` → 18 passed, 2 subtests passed.
- Real `skills@1.7.4` installs of `arena` and `research-os` both exited 0 and matched their source trees byte-for-byte. The installer flattens each selected skill into `.claude/skills/<slug>`; the old repository-relative `../../organization/arena/SKILL.md` link therefore did not resolve after install, although `.claude/skills/arena/SKILL.md` existed.
- TDD evidence: replacing the entry assertion with the installed-slug contract failed first (1 failed); changing only the entry pointer to open the installable `arena` skill slug made it pass (1 passed). No arena body rewrite.
- Correct install destination is `.claude/skills/` for this explicit `claude-code` target. An initial comparison against `.agents/skills/` was a path assumption error; the CLI's reported destination and second comparison against `.claude/skills/` established the actual installed tree.

### Next cycle

- The source-record cycle below closes this issue; remaining work is final regression, source/hash/install checks, integration-tip sync, commit, and the required report.

### Cycle 2 — central source record

- The target source catalog named the pstack revision but omitted `pstack/skills/arena/SKILL.md` and the packaged arena license path. A contract test failed first (1 failed); the source-record addition made it pass (1 passed).
- The record now names the exact upstream asset/blob, absent sibling resources, host-specific upstream references not adopted as runtime dependencies, retained mechanism, plugin-level MIT license, exact packaged notice hash, and installation boundary.
- Upstream source directory inspection found only `SKILL.md`; `pstack/LICENSE` and the packaged `arena/LICENSE` compare byte-for-byte (SHA256 `bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e`).

## Final verification before commit

- Latest local integration ref was explicitly resolved and merged: `b0d8eadc171435896bc2b7bef76bbc54722b797c`; already an ancestor, so no extra merge commit. The original source worktree remained clean at `54674a367393a9f25d27303cff0d4d7401510e11`.
- Fresh targeted suite: **19 passed, 2 subtests passed**. Targeted Ruff and `git diff --check` passed.
- Full suite: **223 passed, 7 failed, 107 subtests passed**. The seven failure names exactly match `/tmp/spec48-closed-baseline/REPORT.md`; all are consequences of the same nine historical `docs/acceptance` tarball links. Direct `scripts/check-skills.py` exited 1 with those nine known diagnostics; they were not suppressed from the full-suite result.
- Actual install with cached Skills CLI 1.7.4 / Node v22.23.2: separate `arena` and `research-os` Claude Code installs each exited 0; each installed tree recursively matched its source (diff exit 0), the entry resolves by installed slug with sibling `arena/SKILL.md` present, and arena's local `LICENSE` is present. Evidence tree: `/tmp/spec48-51-install.DGsSvm`.
- Upstream `SKILL.md` Git blob `b198b9e425c6b3e6ff01ca789b97ca5b4abb7ce2` matched the fixed-revision manifest; `pstack/LICENSE` exact byte comparison passed. Candidate reading, rubric-first declaration, isolation, cross-judge synthesis, full candidate reading, hand graft, mathematical recheck, and “winner is not proof” remain in the inherited skill and passing contracts.
- Scope limit: the tests and CLI install verify artifact/structure/contracts only, not real research or mathematical quality. The previous review r2 503 remains failed, never counted as approval. No new worker/reviewer, tracker, push, or PR was used.
