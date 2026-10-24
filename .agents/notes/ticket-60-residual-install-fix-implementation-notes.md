# #60 Residual Install Fix — Implementation Notes

## Status

- K01 `paper-compile-repair` dependency boundary + seven-edge source/CLI install contract: done; real standalone install declares the sibling and blocked branches; required-combo install resolves all seven edges; full Skills CLI install resolves all seven edges in each of 53 actual package destinations (371 edges), with resource/license hashes matching the sole source copy. Evidence: `logs/residual-suite-final2.log` (4/4), `logs/full-install-all-destinations-final.log`, and the independent path audit below.
- K02 `paper-claim-audit` caller handoff semantics: done; real CLI standalone install confirms leaf read-only return, authorized caller routing, and the existing fee/outbound/no-edit gates. Evidence: `logs/residual-suite-final2.log` (4/4).
- F-R2-01 authoritative build-reference authorization semantics: done through installed `paper-compile-repair/references/build.md` → sibling `paper-compile/references/build.md`; standalone approval separated from valid-parent delegation, while full diff, concurrency, closure, sandbox, and budget enforcement remain required. Evidence: `logs/build-reference-green-final.log` and `logs/ticket60-C01-final.log`.
- Serial selected regression/checker/integration-tip verification complete; final branch identity and commit are captured in `/tmp/spec48-residual-contract-install/REPORT.md` after commit.

## Entry, scope, and acceptance

- Directly execute this explicitly assigned implementation unit; do not dispatch. The user supplied two exact residuals and the public installed-package TDD seam, and explicitly forbade further delegation.
- Branch `t3/fix-residual-install-contracts`, isolated worktree `/Users/rolex/.t3/worktrees/Research OS Studio/t3-2822eef2`; clean start at `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e`.
- First merged the specified final candidate `a658e9312ebdd69888eb0ab914dca6426399d0eb` by fast-forward; current starting HEAD is exactly that candidate. No integration/main writes, pushes, tracker operations, or historical archive edits.
- Inputs: `/tmp/spec48-final-fix-merger/REPORT.md`, `/tmp/spec48-ticket60-final-contracts/FINDINGS.md` (C01/C06), and `/tmp/spec48-ticket60-contract-re-review-r2/REPORT.md` (F-R2-01). Acceptance is limited to (1) accurately declared `paper-compile` sibling dependency with branch-specific block behavior and seven resource edges resolvable in source/flat combined installs, (2) read-only claim-audit return with caller-level delegation in the still-valid mandate, and (3) F-R2-01 authorization clarity in the canonical build resource reached by the repair Skill's required pointer chain. Preserve C01 safety build/TeX closure/sandbox gates and claim-audit read-only/fee/outbound gates. Parent owns later independent contract review and full-suite acceptance; this unit must not declare #60 passed.
- Loaded global `Multi-Agent.md`, `model-availability.md`, `CODING_STANDARDS.md`; writing-for-agents and pre-implement skills; TDD `SKILL.md`, `tests.md`, `mocking.md`; `GLOSSARY.md` and ADR-0005. TDD seam explicitly supplied by user: cached Skills CLI 1.7.4 in isolated `/tmp` HOME/cwd, standalone repair install and required sibling combo, then installed contract assertions. Commands are serial, use external TMPDIR, and have <=180-second limits.

## Decisions / deviations

- Start with the minimal installed-contract red test. Keep the four canonical compilation resources maintained only under `paper-compile`; do not duplicate or alter source licensing. Declaring `paper-compile` as a required sibling is preferable if all seven edges resolve in source and the CLI's flat sibling layout, while standalone absence blocks only affected operations and does not bypass C01 gates.
- The specific branch mapping will be documented next to `paper-compile-repair`'s local references, rather than copied into canonical resources. `paper-claim-audit` will return only its own read-only findings; its caller may route other audits only under the valid existing delegation; missing authorization/new scope still requires user authorization.
- New review input identifies F-R2-01 in that same C01 mandatory build-reference chain. Sync only the canonical `paper-compile/references/build.md` authorization language: standalone approval versus a still-valid parent delegation covering dirty source/repair scope, temporary write domain, and enforceable budget. Full diff display, concurrent-change recheck, input closure, sandbox guarantees, and actual budget enforcement remain mandatory.
- Two first GREEN attempts rejected semantically correct wording because the test expected a specific contiguous phrase (`不声称全部依赖随包提供`; `本叶只读返回`). Assertions were narrowed to the actual contract meaning (`并非单包自包含`; read-only completion returned to caller), not product text distorted to satisfy literal wording. One subsequent C06 assertion was similarly corrected to assert `不代做` plus the exact caller delegation sentence.
- One strengthened F-R2 assertion likewise expected a non-existent exact phrase; it was corrected to the actual wording `由有效父委托明确覆盖`, then the installed-pointer-chain test passed. A #57 test command first named the wrong module and the corrected run exposed that the new dependency document had to be staged for the checker's tracked-file scan; after staging, #57 passed. Both failed logs and return codes remain in `/tmp`.

## Verification evidence

All Python test/check commands ran serially as `timeout 180s env TMPDIR=/tmp/spec48-residual-contract-install/tmp uv run --offline --no-project ...`; direct Skills CLI invocations ran offline at pinned `skills@1.7.4` in independent `/tmp` HOME and cwd trees and each had subprocess timeout 175 seconds.

| Scope | Result | Log (SHA-256) |
| --- | --- | --- |
| K01/K02/F-R2-01 residual installed contracts, standalone + required combo + full CLI install | 4/4, rc=0 | `/tmp/spec48-residual-contract-install/logs/residual-suite-final2.log` `80f911d9c5f298c02e7c5dc30afccfa734b65c1c1e1bbc39edf1eb15aab73837` |
| Full-install destinations audit | 53 installed `paper-compile-repair` packages, 371/371 resource edges resolved with canonical hashes; rc=0 | `/tmp/spec48-residual-contract-install/logs/full-install-all-destinations-final.log` `22e829aca1176149bfcedab7d8bffeffc7f0a979086fc54135ba3fbadaf50861` |
| A1 | 3/3, rc=0 | `logs/ticket60-A1-final.log` `ae1260056ff2303e8b844bc7da407dbaa9190035236c029267f2cac4fb8e9482` |
| C01 installed | 1/1, rc=0 | `logs/ticket60-C01-final.log` `ad32eb494d73d98e2eea35115cab3498b588a8ee094fd178b2dc4666889081d2` |
| C02/C04 | 2/2, rc=0 | `logs/ticket60-C02-C04-final.log` `291736d273825ccbc9df5f95e1b7c2f702b1ef1e0f8aa5481e40a0d112bdcf59` |
| C03/C05/C06 | 7/7, rc=0 | `logs/ticket60-C03-C05-C06-final.log` `7f1ecb3b9bcb1f0fdc628fa761399c33db14e0d68e26165a4070abe0735a1ac1` |
| #57 | 13/13, rc=0 | `logs/ticket57-final.log` `441f960d110a05b825dbaac74100d559fdeeb08bf31ac034f37a862835c5386c` |
| Checker | rc=1, exactly the original 9 diagnostics; byte-identical to `/tmp/spec48-closed-baseline/logs/head-checker.log`, same SHA `acbd51e6f5e308fc570dced0eb6f46d3c9df9eb5de0323fc74271c38a0ff1cbf`; no archive changes | `logs/checker-final.log`, return code `logs/checker-final.rc` |
| Skills CLI version | 1.7.4, rc=0 | `logs/skills-cli-version.log` `1a3c4b0fe305f01ca60cad618335ee22e94eaeef15f7a51da56fb9a9ca0b17a9` |

The four canonical sibling resource hashes are: diagnostics `72382836b7a0528ca39f523a8208cdc2832b3b0eaf62f80f8d29230a997bfd4b`; build `aa791b8d4ffcc0d55d7c7ea5a09df6171eef5c2b7ab06a94777870e9c7c24573`; PDF checks `a69673e8772a2671050a92d6499ab3882ef8dda1d88ce734b8b5165aa5da69ee`; compilation template `46d88680a576718217e573900d42e0d9fad4b4b03a1ee5ef36d9ab025d0f1a44`. `paper-compile/LICENSE` remains canonical and unchanged, SHA-256 `e30cf5dd5f49b4f9b656590e23d782b4756c924a9f0ff0162b3e7b5d87006bf5`; installed hashes equal source for all seven edges. The four resource files were not copied or forked.

`git diff --cached --check` passed. Selected regressions above are not the full 328-test suite; no independent review or overall #60 acceptance was performed by this implementation worker. The pre-delivery merge of `integration/spec-48` returned `Already up to date` at tip `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e`. The external delivery report records the final local branch commit; no push/tracker/integration write occurs here.

## Verification

- Not yet run; append exact commands, return codes, log paths/hashes, seven edge/resource hashes/license and checker baseline comparison as evidence is collected.
