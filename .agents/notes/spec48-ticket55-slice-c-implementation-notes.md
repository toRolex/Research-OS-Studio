# #55 Slice C implementation notes

## Status

| Work unit | Status | Artifact / evidence | Next step |
|---|---|---|---|
| Establish Slice C branch from exact B delivery | done | Branch `t3/validate-skills-cli-math`; merge commit `889017977a9470b8c44bec32d296d640d05dfae0` has parents integration `86caa4fd76792b056f31d5c083fb7cd918760a4c` and exact B `6f9eba6764035f7b4f95481c98b4c371d184efff` | None |
| Real Skills CLI 1.7.4 combo installation and package/reference/license audit | done | `/tmp/spec48-ticket55-sliceC/post-merge-combined`; `skills list --json` discovers exactly 14 requested slugs; 14/14 file sets and bytes match, notices match, package-local links resolve after the promotion merge | Preserve logs/hashes in report |
| Independent math leaf installs (writer, repair, formula, review; compatibility entry dependencies) | done | Separate CLI projects/HOMEs under `/tmp/spec48-ticket55-sliceC/leaf-*`; four leaf file sets/bytes/notices/local links pass. CLI one-skill install does not resolve dependencies; compatibility-only text fails closed if `research-os` is missing; pair install exposes both | Record no-dependency behavior and install logs |
| #55 recipe/principle/capability/verification responsibility matrix against pinned pstack | done | Pin `88d47514b82e7c44f00f2b2a72ff6dd12158038c`; reuse `/tmp/research-os-spec48-upstream/README.md` rows #50–54 and current source/license records | No broad upstream re-survey or math certification |
| Minimal docs/dead-link correction and TDD regression | done | Replaced `research-os` sibling Markdown link and source-tree paths with installable slugs; refreshed product map, validation roles, migration map, selective-install guidance. Ticket tests: 17 passed | Keep resources/notices; no #60/history changes |
| Merge specified integration tip and rerun ticket-scoped verification | done | Merge commit `8f4b85b334f9253b7d77a4adeacf41ee264fa392`, second parent exact integration tip `0bd38385b9a7b3aa51872af415aee78ef2778bcf`. Checker, migration map, and policy-test conflicts resolved. Kept B's proof skills out of legacy gates; rewrote #58 proof-repair negative cases to damage the new delegated contract. Targeted tests: ticket55 17/17; damaged-policy negative 1/1; checker historical baseline 1/1. Post-merge CLI exact-set/bytes/link audit passes | Record handoff gate in report |
| Slice C evidence report | 进行中 | Target: `/tmp/spec48-ticket55-sliceC/REPORT.md` | Include CLI exit codes/log hashes, matrix, per-AC evidence, limitations, and final #55 merger gate |

This is one bounded implementation work unit, handled directly because the user explicitly prohibited further dispatch and supplied the required reports/spec/cache artifacts. Scope is only #55 Slice C; Slice C acceptance does not close #55 until the final combination merger revalidates. No tracker, push, integration checkout, main checkout, #58 candidate, or #60 contraction work is authorized.

## Decisions and evidence

- Base is the supplied exact Slice B delivery, not a reconstructed feature branch. The current T3 worktree is already isolated from integration/main.
- The acceptance seam is the real cached Skills CLI 1.7.4 installation in disposable project and `HOME` roots, not source-directory copying. Tests and manual comparison distinguish installation/structure evidence from mathematical validity.
- The `skills` 1.7.4 tarball was present in npm's local cache; `npm exec --offline --package=skills@1.7.4` reported version `1.7.4`. Use `--copy` so installation byte/file-set checks inspect the CLI output rather than development symlinks.
- Full CLI combo installs 14 slugs: `research-os`, `arena`, `swarm`, `interrogate`, behavior/formal create+maintain, four math leaves, `proof-orchestrator`, and `research-improvement`. CLI list discovers all 14; every installed file set exactly matches source, including licenses/notices. Four math leaves also install alone with exact bytes and reachable local references.
- CLI installs only selected skills. `proof-orchestrator` explicitly stops and requests `research-os` when that entry is missing; the proof recipe says an unavailable optional capability blocks only its dependent branch. The final combo includes both compatibility alias and entry.
- The pinned pstack responsibility crosswalk reuses its cached upstream map (`/tmp/research-os-spec48-upstream/README.md`, #50–54 and entry-context rows) plus existing source/licensing records; it distinguishes pstack organization/verification patterns from Research OS's local math proof family.
- Integration merge of the accepted four-ticket tip exposed the known #58 conflict: its policy negative test treated `proof-repair` as legacy. Kept `formula-derivation`, `proof-writer`, `proof-repair`, and `proof-orchestrator` in `MIGRATED_CONTRACT`; `LEGACY_LEAF_GATES` retains only `proof-review`'s empty baseline. Negative cases now corrupt migrated `proof-repair`'s `Gates: none`, reintroduce a legacy `Gate:`, remove the delegation section, duplicate the marker, or mutate invocation policy.
- The promoted tracked-Markdown checker caught `validation.md`'s source-tree `references/lean-methods.md` token as an invalid installed reference. Replaced it with the installable `proof-orchestrator` slug; a new #55 test was RED before the minimal fix, then GREEN.
- Final post-merge install/list/audit used isolated project and `HOME` paths under `/tmp/spec48-ticket55-sliceC/post-merge-*`; actual CLI log SHA256s and return codes are recorded in `/tmp/spec48-ticket55-sliceC/REPORT.md`.
- The user's bounded fallback is controlling: if the full matrix cannot fit this work unit, finish the core combo and two representative independent leaf installs, then report the exact remainder instead of implying full completion.

## Deviations

- Real CLI isolation exposed one cross-skill Markdown link (`research-os` → sibling `interrogate`) that resolved only when both separate packages were installed. Replaced it with the discovered Skill slug; also replaced development-tree file paths in the proof recipe with installable slugs and documented CLI's non-resolving dependency behavior. This keeps standalone entry links valid while preserving optional cross-skill composition.
- Promotion integration resolved within the C unit's bounded scope. No #58 runtime/feature code was changed; only its stale proof-repair negative fixture was retargeted from an obsolete legacy gate to a damaged migrated contract, preserving the intended checker failure coverage.
