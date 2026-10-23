# #60 Discovery serial merger implementation notes

## Status

- Input/rule audit — done; reports read from `/tmp/spec48-ticket60-writing-merger/REPORT.md` and `/tmp/spec48-ticket60-discovery/REPORT.md`; base verified as `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e`.
- First no-ff merge (`a2f48ba0bf1bc59e4c3efa45a4935c62b66d34b2`) — done; no content conflicts.
- Discovery no-ff merge (`efa36768860d6255852e2012a390f17b6ba1db3d`) — done as `c8a7835bc5a704df7ae106ea63594de40cc15041`; only `docs/README-en.md` and `docs/user-acceptance-guide.md` conflicted; resolution preserves the unified entry, live authorization semantics, and dynamic inventory.
- Migration/route/checker/test audit and real Skills CLI install — done; Research OS alone (34 files) and Discovery group (65 files) installed from the candidate using cached CLI 1.7.4, full SHA manifests and package-local-link audit passed. Proof-review (23-file manifest) and paper-writing (21-file CLI evidence) payloads were byte-compared to their validated source trees.
- Bounded serial verification and exact checker comparison — done; test logs and checker evidence under `/tmp/spec48-ticket60-discovery-merger/logs/`. Tests passed: Discovery 1, M 4, W 3, #55 17, #57 13, #58 23, policy 4, #38 21, #43 8, #46 9, accept-remediation 4, tracked-scan 1. Checker rc=1 is the exact prior 9-archive diagnostic output.
- Final candidate report and notes-only commit — done; report at `/tmp/spec48-ticket60-discovery-merger/REPORT.md`, with final candidate SHA recorded after this notes-only commit. No integration/main promotion, push, tracker operation, archive work, bridge continuation, or full #60 vote.

## Entry and scope

Direct execution was selected because this is an explicitly assigned implementation subtask with supplied source commits, reports, baseline, and acceptance boundaries; the user explicitly prohibited further dispatch. Merge in the given order on the already-bound independent worktree. Do not consume uncommitted work from the bridge or other workers.

## Decisions / deviations

- Keep Discovery as `research-os`'s `discovery` recipe; do not restore the removed standalone controller or add another orchestrator.
- Resolve public docs to describe the actual 42-Skill tree (English badge corrected from 43), with no fixed product-size requirement. Keep the writing candidate's `research-os`/experiment-bridge compatibility boundary rather than adopting Discovery source's stale claims that experiment-plan/bridge are delivered.
- In the acceptance guide, preserve both rules: no extra approval at ordinary stage transitions within the active mandate, and no automatic pilot/Validation when the requested target stops at a candidate Proposal. Update only current route/install references; do not edit archived acceptance evidence or historical provenance claims.
- Existing proof-review and paper-writing CLI evidence was inherited only after exact tree comparison: final `proof-review` equals validated source `b9e237e…` and every path in its 23-file SHA manifest verifies; final `paper-writing` equals validated source `3bf2fa3…`, whose 21-file install test compared every installed byte.

## Deviations / verification notes

- Running `test_spec48_ticket57.py` and `test_check_skills_tracked_scan.py` directly returned 0 but did not execute tests (no module entry point). Re-ran both with `python -m unittest discover`; 13 and 1 tests passed respectively. The corrected logs replace the no-op logs.
- Discovery's checker log includes a wrapper-only trailing `RETURN_CODE=1`; direct `cmp` against that file differs only by the footer. Candidate stdout exactly matches both the clean writing-merger checker log and `/tmp/spec48-closed-baseline/logs/head-checker.log`; removing that wrapper footer makes the Discovery log byte-identical too.
