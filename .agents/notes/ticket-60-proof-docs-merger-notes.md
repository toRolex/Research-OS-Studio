# #60 proof/docs merger — implementation notes

## Historical work-unit status (retrospective)

Added on 2026-10-24 from this note's original candidate-closeout record, not from new execution. Historical counts, failures and non-promotion boundaries below remain unchanged.

| Work unit / deliverable | Status at that stage | Existing evidence | Next step / boundary at that stage |
| --- | --- | --- | --- |
| Merge proof/docs and reconcile semantics/count | done | Sources `ff53d46` then `a11775f`; reconciliation decisions below, including the stage-specific 45 badge | Discovery/W not included; their later merger must recheck the count |
| Bounded candidate validation | done (within recorded scope) | M 4, ticket55 17, policy 4, ticket46 docs 9; checker retained nine historical archive diagnostics | No archive repair or overall #60/host/research acceptance implied |
| Candidate evidence handoff | done | `/tmp/spec48-ticket60-proof-docs-merger/REPORT.md` | Candidate not promoted/pushed at this stage; parent owns later integration |

## Scope and entry decision

Direct execution: the user supplied two completed source SHAs, a fixed merge order, and a bounded acceptance set, and explicitly prohibited further delegation. This candidate worktree started clean at `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e`; no integration/main worktree, tracker, or remote was touched.

## Merge and reconciliation decisions

- Merged proof slice `ff53d4689684099c34b8a6e026fe56b3be10ed93` first, with `--no-ff`; then merged live-docs slice `a11775f58190d09aa6a2371272e61c5e05402386`, also with `--no-ff`.
- Git reported no textual conflicts. Reviewed the resulting README, English README, Skills README, acceptance guide, glossary, proof recipe, validation map, product map, migration boundary, upstream/license references, and diagrams for semantic conflicts.
- Kept the live-docs research-mandate contract: bounded work can begin without setup or an explicit budget where authorization permits; capability dispatch is based on the current host, not a brand gate; target changes and external/destructive actions retain their hard gates.
- Kept the proof retirement contract: `/research-os` remains the proof controller, specialized resources are carried by `proof-review`, and no live operation/install/call revives `proof-orchestrator`. Historical source/acceptance records and archive policy/allowlist remain untouched.
- Reconciled one stale live-doc count: `docs/README-en.md` badge was 46 on the docs-only source, but the merged candidate tree contains 45 `SKILL.md` files after the controller retirement. Updated only the badge to 45. A later Discovery/W slice may change the count and must recheck it.

## Validation evidence

- M package manifests from the already completed real Skills CLI install were checked against the candidate source trees; all 23 `proof-review` files and all 30 `research-os` files matched. The merged candidate's M contract test then reran the offline CLI install for both packages and passed its file/hash/link checks.
- Targeted tests passed: M contract 4, ticket 55 17, policy gates 4 (via unittest discovery to make `spec48_workcopy` importable), and ticket 46 docs 9. All commands used tree-external `TMPDIR` and a 180-second wrapper.
- `check-skills.py` remains nonzero only for its exact nine pre-existing missing historical archive tarball targets; it reported no new link/reference error. No archive allowlist or historical acceptance file was changed.
- No Discovery or W/bridge source was included. Candidate is not promoted to integration and is not pushed.

Detailed command return codes, checker diagnostics, merge SHAs/parents, and final tree state are in `/tmp/spec48-ticket60-proof-docs-merger/REPORT.md`.
