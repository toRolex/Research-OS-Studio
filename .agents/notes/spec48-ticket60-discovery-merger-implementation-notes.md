# #60 Discovery serial merger implementation notes

## Status

- Input/rule audit — done; reports read from `/tmp/spec48-ticket60-writing-merger/REPORT.md` and `/tmp/spec48-ticket60-discovery/REPORT.md`; base verified as `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e`.
- First no-ff merge (`a2f48ba0bf1bc59e4c3efa45a4935c62b66d34b2`) — done; no content conflicts.
- Discovery no-ff merge (`efa36768860d6255852e2012a390f17b6ba1db3d`) — in progress; only `docs/README-en.md` and `docs/user-acceptance-guide.md` conflicted; resolution preserves the unified entry, live authorization semantics, and dynamic inventory.
- Migration/route/checker/test audit and real Skills CLI install — not started; acceptance evidence to be added after execution.
- Bounded serial verification and exact checker comparison — not started; logs under `/tmp/spec48-ticket60-discovery-merger/`.
- Final candidate report and notes-only commit — not started; no integration/main promotion, push, tracker operation, archive work, bridge continuation, or full #60 vote.

## Entry and scope

Direct execution was selected because this is an explicitly assigned implementation subtask with supplied source commits, reports, baseline, and acceptance boundaries; the user explicitly prohibited further dispatch. Merge in the given order on the already-bound independent worktree. Do not consume uncommitted work from the bridge or other workers.

## Decisions / deviations

- Keep Discovery as `research-os`'s `discovery` recipe; do not restore the removed standalone controller or add another orchestrator.
- Resolve public docs to describe the actual 42-Skill tree, with no fixed product-size requirement. Keep the writing candidate's `research-os`/experiment-bridge compatibility boundary rather than adopting Discovery source's stale claims that experiment-plan/bridge are delivered.
- In the acceptance guide, preserve both rules: no extra approval at ordinary stage transitions within the active mandate, and no automatic pilot/Validation when the requested target stops at a candidate Proposal. Update only current route/install references; do not edit archived acceptance evidence or historical provenance claims.
- No planned scope deviations yet.
