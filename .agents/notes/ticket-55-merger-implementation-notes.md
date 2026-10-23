# #55 Final merger acceptance

## Status

- Source review and candidate: done. Exact 55C delivery `9d4855d7a0cffafbd63e5899af2c659e5ff93bd3` was no-ff merged on actual integration base `0bd38385b9a7b3aa51872af415aee78ef2778bcf` as `0c98b2e18d607d80c223961b8153742499b09a56`; two obsolete #49/#52 assertions were minimally updated in `0268069f002271db6bdfb004cb23680d63c39537`.
- Candidate acceptance: done with bounded historical failures recorded below; full suite was not rerun after the two test-only adaptations.
- Integration promotion: done by fast-forward from clean `integration/spec-48` tip `0bd38385b9a7b3aa51872af415aee78ef2778bcf` to candidate `0268069f002271db6bdfb004cb23680d63c39537`.
- Exact tracked-tree and integration-checkout short tests: done. Detailed return codes/log paths: `/tmp/spec48-ticket55-merger/REPORT.md` and sibling `logs/`.

## Decisions and evidence

- Direct serial work was required: user specified one writer and prohibited further delegation. No main checkout, push, tracker, #60 shrink, or archive repair was touched.
- Review retained the non-sequential proof recipe, method/obligation/failure records, counterexample and numeric-candidate distinctions, independent writer/reviewer/repair/formula roles, inherited delegation, and proof-orchestrator resources/license. #55 AC evidence is in its 17-test contract suite and C report `/tmp/spec48-ticket55-sliceC/REPORT.md`.
- Ticket 55 install source was compared to the actual C CLI install: 14 slugs, 120 files, manifest SHA256 `7ce43069a5fa9191f15b134812b4ec45963de28d580968fe8f7f091520da07b3`, exact byte/path match. Reused C's real Skills CLI 1.7.4 install, LICENSE/permissions/links and pstack evidence; no math proof or runtime behavior is claimed.
- Initial full grouped suite exposed two legacy contract conflicts: #49 expected a legacy proof-repair Gate; #52 expected a cross-Skill source-tree link. The red evidence is preserved in `logs/full-test_spec48_ticket49.py.log` and `...ticket52.py.log`. Minimal spec-based test updates verify migrated delegation and the installable `interrogate` slug/no cross-bundle link. Post-change #49 22/22 and #52 21/21 passed. The policy suite still rejects damaged delegation contracts and reintroduced legacy gates.
- Pre-adaptation all-file grouped suite: 19 files, 268 test nodes, 8 failed. The initial summary parser undercounted by two because it missed singular `Ran 1 test`; raw per-file logs are authoritative. The two contract conflicts above were then repaired and targeted green; remaining six failure IDs match the known historical baseline in `/tmp/spec48-58-checker-merger/REPORT.md`. Full suite was deliberately not repeated. Ticket #49–59 files were each run; after fixes, exact-tree joint checks cover #49/#52/#54/#55 plus policy, tracked-scan and copier.
- Checker returned 1 for the existing 9 archive-evidence links; exact raw output equals `/tmp/spec48-closed-baseline/logs/head-checker.log` byte-for-byte. This remains a known baseline, not a new failure or a full-green claim.
- Pre-note candidate archive was reinitialized and `git add -f` tree verified equal to HEAD tree `e065334ee8cb80b3ecd4916886a7f2f0a1bb0fda`; exact-tree key tests: 89 top-level nodes passed, plus one tracked-scan and one copy-isolation test. Integration checkout itself ran only short tracked-scan and #55 tests to avoid ignored-tree contamination.

## Deviations

- Slice C's local `8f4b85b` base was not used as the promotion base; git verified actual requested integration base `0bd3838` is the source ancestor.
- No complete post-adaptation full-suite rerun: only the two changed test groups were rerun; the other groups' results are unchanged, with six known historical failures preserved and explicitly reported.
