# #60 Discovery + experiment bridge merger notes

## Status

- Merge candidate: **done**; final candidate SHA is recorded in `/tmp/spec48-ticket60-all-contract-merger/REPORT.md`; both required no-ff merges are present and the worktree is clean. Parent acceptance remains separate.
- Bounded verification: **done**; 187 selected tests passed, both affected single-skill CLI installs and the Discovery group copy were audited, and the checker output exactly matches the existing baseline. Evidence is in `/tmp/spec48-ticket60-all-contract-merger/logs/`.
- Merger report: **done**; `/tmp/spec48-ticket60-all-contract-merger/REPORT.md` records merge parents, conflicts, resource migration, CLI results, tested and untested scope.
- Final all-leaf contract / pstack acceptance: **not started**; explicitly left to the parent-directed follow-up work unit; this candidate is not a #60 completion claim.

## Entry judgment and boundary

- Direct execution was chosen because the task explicitly forbids further delegation and limits this work unit to the two supplied candidate commits, shared-resource conflict resolution, and bounded verification.
- This is a candidate branch only. Do not promote it to `integration/spec-48`/main, push it, update the tracker, or treat it as full #60 acceptance. Parent follow-up still owns the terminal install/leaf-contract/pstack acceptance.
- Exact base: `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e`; first no-ff merge candidate `781fccba9d4013961c2c7862e2287ea4471e9017`, then no-ff merge bridge source `ff88e1dea24c6fb43afd5a26171d6a63c19cd3cf` (source includes W1).

## Shared-resource decisions

- Resolved conflicts in `README.md`, `docs/README-en.md`, `docs/user-acceptance-guide.md`, `skills/README.md`, and `skills/general/research-os/references/PRODUCT-MAP.md` by retaining the research mandate: no repeated approval for ordinary in-scope capability/stage transitions; scope/quota, external send, destructive action, goal replacement, and capability-specific hard gates remain enforced.
- `discovery` and `experiment-bridge` are Research OS recipe names, not standalone Skills or slash-install slugs. Discovery is gap-driven and optional through Proposal; bridge routes execution only to `run-experiment`, with monitor/health/analysis/audit/claim duties still composable and independent.
- The five retired controllers are absent from the live tree: `idea-discovery`, `proof-orchestrator`, `ml-paper-writing`, `systems-paper-writing`, `experiment-bridge`. Their user needs and specialist methods remain in `research-os` routes, `proof-review`, `paper-writing`, or `run-experiment`; no second controller was restored.
- Old controller-specific `agents/openai.yaml` files are retired with their controllers; the surviving install metadata belongs to the unified entry/package (`research-os`, `proof-review`, `paper-writing`, or `run-experiment`), not a compatibility shim.
- The final tree has 41 installable Skills (general 4, idea-cycle 6, organization 1, validation-cycle 16, writing-cycle 14). Root README, `skills/README.md`, and English inventory each resolve to the exact live tree; English badge is 41, derived from the tree rather than a target.
- Historical acceptance/atomic-switch material and the checker allowlist were not edited. The checker continues to scan tracked Markdown, including tracked archives; copy-isolation checks still use tracked files.

## Resource and payload audit

- Discovery's old 6-file controller maps its recipe to `research-os/playbooks/discovery.md`, composition rules to `references/discovery-composition.md`, templates to the Research OS package, and original MIT license to `licenses/idea-cycle/LICENSE` (unchanged SHA-256 `e30cf5dd5f49b4f9b656590e23d782b4756c924a9f0ff0162b3e7b5d87006bf5`). Per-resource source hashes are in `/tmp/spec48-ticket60-discovery-merger/logs/payload-inheritance-and-migration-hashes.txt`.
- Proof's old controller/references are retired in favor of the `/research-os` proof recipe plus `proof-review`'s independent review resources. Original license bytes are preserved (same SHA-256 `e30cf5dd5f49b4f9b656590e23d782b4756c924a9f0ff0162b3e7b5d87006bf5`); NOTICE attribution is retained as `NOTICE-ETA.md`. The 23-file installed manifest SHA-256 is `a1d7de63d0d1dcaaf03ff55ae4db8fa1290b3f0f4db246af366d7908f39d6e5b`. Final `proof-review` is byte-identical to the discovery candidate; bridge source does not contain that independent package.
- ML and Systems writing controllers route into one `paper-writing` package and its general/ML/Systems Research OS playbooks. Domain references/templates retain their specialized contents at the mapped `ml-*`/`systems-*` paths. ML/Orchestra license SHA-256 is `80b5899a9ab121a2d4aae63724f0c11defba7f23da487086932bb9abfb0f2a00`; ARIS is `e30cf5dd5f49b4f9b656590e23d782b4756c924a9f0ff0162b3e7b5d87006bf5`. `paper-writing` remains byte-identical to both merge source tips; its validated 21-file manifest SHA-256 is `0c1171d271c825311694aa184edef161776d7f4ee691bcb443f8715c99fe5eb9`.
- Bridge's six old files are absorbed by `run-experiment`: license and mandate are byte-identical (SHA-256 `e30cf5...06bf5` and `88aa76...04e1`), composition duties are consolidated in `references/composition-map.md`, and its report fields are merged into `templates/run-report.md`. The standalone bridge controller/agent metadata are deleted. New 9-file package manifest SHA-256: `a7bf613a69a3a603cf7186f518570325bb0d22da109058e9850c8e8d9373528d`.

## Verification / handoff

- Serial affected-file tests passed under `uv run --offline --no-project`, external `TMPDIR=/tmp/spec48-ticket60-all-contract-merger/tmp`, each subprocess capped at 180 seconds: #60 M 4, W 3, Discovery 1, bridge 4; #55 17, #56 27, #57 13, #58 23, #49 22, #59 20; policy gates 4; checker #38/#42/#43/#46 = 21/4/8/9; acceptance 4, tracked scan 1, copy isolation 1, idea source relocation 1. Total: 187 passing tests, zero failures. Per-group raw logs are in `/tmp/spec48-ticket60-all-contract-merger/logs/`.
- Real offline Skills CLI 1.7.4 installs used isolated HOME/CWD outside the tree. Single `research-os`: 34/34 files byte-identical, manifest `77eaa3e9aacd5345877b0072cc66000a9a7871923071c631066811d9c1070961`, 66 local links / 0 missing / 0 cross-package. The 6-Skill Discovery group (`research-os` + five Required; creative optional and omitted) installed 65 files, exact per-Skill file/hash sets, 0 missing/cross-package links. Single `run-experiment`: 9/9 files byte-identical, manifest `a7bf613a69a3a603cf7186f518570325bb0d22da109058e9850c8e8d9373528d`, 7 links / 0 missing / 0 cross-package. Raw CLI logs and resource audit are under the same merger evidence directory.
- Final `scripts/check-skills.py` is expected rc=1 only for the existing 9 missing/untracked `docs/acceptance/**/evidence/*.tar.gz` files. Output SHA-256 `acbd51e6f5e308fc570dced0eb6f46d3c9df9eb5de0323fc74271c38a0ff1cbf`; byte-for-byte `cmp` with `/tmp/spec48-closed-baseline/logs/head-checker.log` returned 0. Do not repair the archives or change the allowlist here.
- The full repository test suite was not run. Full leaf-contract and pstack acceptance remains explicitly pending the parent-directed final acceptance work unit.

## Deviations

- Kept verification to the explicitly affected contract/checker/copy/CLI groups instead of running the full repository suite. This avoids claiming terminal acceptance from a merger worker; the parent owns that separate final gate, as required by the task boundary.
