# Ticket #59 implementation notes

## Review retry: independent REJECT (2026-10-21)

当前交付状态以本节为准：独立报告 `/tmp/research-os-spec48-ticket59-review/REPORT.md` 初始结论 REJECT；R1–R4 已定向修复、提交并完成合入后复验。实现提交 `a2cc3b451d8d45c8eb34b13521642a0a6565e36a`，合入本地最新 `integration/spec-48`（`bc35b36a9b7aee57f003967c67b5bca6485ab891`）的 merge commit 为 `08749d4a2bfd983f5569ee0d2b8513d8ebc1ea94`；其后提交了本票 verification notes。最终完整 branch tip 在交付回报中提供。合并时只在本 worktree 解决 migration-boundary 冲突，保留 #59、#53 两组登记；提交身份 `rolex <torolex@163.com>`。未触碰 integration/主目录，不继续派发，不 reset/clean/push/PR/写 issue/删除 worktree。

### 逐 finding 处理决定

| Finding | 响应与修复边界 | 红绿证据 |
| --- | --- | --- |
| R1 委托继承/再确认矛盾 | 区分用户独立显式调用与已授权入口级联；轮次仅核对原授权轮数、范围及剩余额度。Pickup 依原委托来源/暂停记录恢复，不另要旧式本轮批准清单；保留目标替换、越权、超额及未授权副作用门。composition map 遵循已迁移/legacy 边界。 | 初始新反例为红（见 targeted red）；最终 `test_direct_invocation_and_delegated_inheritance_are_distinct` 通过，合入后 18-ticket59 测试通过。 |
| R2 setup 硬阻塞及安装依赖断链 | 普通非付费、非作业的恢复允许按委托/暂停记录有界继续；仅作业、费用/资源批次要求 compute policy 与研究账本。setup 模板作为该分支显式成组依赖，核对真实扁平安装路径；保留无 setup 正例。 | 初始 `test_unconfigured_nonpaid_resume_is_allowed_but_job_branches_need_setup` 为红；合入后 targeted 全绿。paired CLI 正例无 setup 安装继续合同，代表 CLI 安装解析两模板。 |
| R3 reviewer 不可用时合同冲突 | 本轮统一 `blocked`；可给只读自查建议，但不能记作 fresh 独立审查，也不能计作完成 review/repair/re-review。 | 初始叶/方法/依赖一致性测试为红；合入后 `test_unavailable_reviewer_blocks_the_review_repair_round` 通过。 |
| R4 五类损坏仍虚绿 | Checker/test 针对配额重置、信旧总结、自动公共外发、截断 MIT、错误分支映射逐一检查；依赖检查解析仓库路径及扁平安装目标；许可证核完整固定文本，不声称理解任意自然语言。 | 五个报告 mutant 均拒绝：`test_ticket59_contract_checker_catches_reported_semantic_mutants` → 1 passed、5 subtests、exit 0。R1/R2/R3/级联边界四类旧句重新注入先红（4 subtests、exit 1），加入旧合同拒绝后 `test_ticket59_contract_checker_rejects_reintroduced_conflicts` → 1 passed、4 subtests、exit 0。 |

### 执行约束与入口记录

- 按用户指定由当前 luna6 xhigh 直接实现，不派发；禁止 DS/GLM/Grok/Kimi。预算按本 work unit 20% 控制，若无法完整完成先保留笔记与差异并报告未完成，不仓促合并。
- 已读取原始 brief、Spec #48、Ticket #59、独立报告及其 `probe_review.py` 精确损坏文本；当前 worktree 初始 HEAD 为 `754bc5228b335bb720d3fe5402f72b0472e4c559`，初始 clean。
- 配置技能目录中没有请求的 `tdd`、`pre-implement`、`writing-for-agents` 或 `SKILL-MECHANICS.md` 文件；因此按红→绿执行并在此维护实现决策，不把未找到的技能说成已加载。

### Review retry verification

- **TDD 红**：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/rolex/.cache/uv/archive-v0/ZHSqs5vxcDKWb5QD/lib/python3.14/site-packages UV_CACHE_DIR=/tmp/research-os-spec48-ticket59-review/uv-cache uv run --offline python -m pytest -q -p no:cacheprovider tests/test_spec48_ticket59.py`，首次新增反例后 `8 failed, 12 passed`，exit 1；失败命中 R1–R3 语义差异、R2 普通恢复硬门及 R4 checker 缺失，不是旧红记录追认。
- **定向冲突红→绿**：`... pytest -q -p no:cacheprovider tests/test_spec48_ticket59.py::CheckerRegistration::test_ticket59_contract_checker_rejects_reintroduced_conflicts` 首次 `4 failed`，exit 1；加入精确旧合同诊断后 `1 passed, 4 subtests passed`，exit 0。
- **Targeted 绿**：同 `tests/test_spec48_ticket59.py` 命令最终 `18 passed, 12 subtests passed`，exit 0。五个报告 mutant 与四类 R1/R2/R3 过期冲突句均有隔离 fixture；完整合同 fixture 为零诊断。
- **合入后 targeted suite**：`uv run --offline python -m pytest -q -p no:cacheprovider tests/test_spec48_ticket59.py tests/test_spec48_ticket50.py tests/test_spec48_ticket52.py tests/test_spec48_ticket53.py` → `87 passed, 61 subtests passed`，exit 0。包含 #50 有界一次重派/二次缺口合同，既有登记与测试保留。
- **合入后 applicable full suite**：`uv run --offline python -m pytest -q -p no:cacheprovider tests scripts/test_check_skills_ticket*.py` → `7 failed, 202 passed, 105 subtests passed`，exit 1。失败 ID 仍与已知 baseline 七项完全一致：`tests/test_check_skills_policy_gates.py::PolicyAndGates::test_checker_green_and_leaf_baseline`、`tests/test_config_contract.py::ConfigContractTests::test_gate_baseline_and_counterexamples`、`test_shipped_templates_and_full_checker`、`test_valid_policy_and_log_fields`、`test_valid_role_table`、`tests/test_final_contract_fixes.py::FinalContracts::test_full_cli_damaged_declarations_refs_and_readme`、`tests/test_review_fixes.py::ReviewFixes::test_compute_limits_are_per_unit_not_summed`；全由同九条既有 acceptance archive 断链触发，无新增失败/skip/xfail。
- **合入后 checker**：`uv run --offline python scripts/check-skills.py` → `FAIL: 9`，exit 1；仍只有同九条历史 archive 链接，无 R1–R4 或 #50/#52/#53 新诊断。
- **合入后真实 Skills CLI 1.7.4**：从最终合并工作树用三个独立 HOME/临时项目复制安装，CLI 均 exit 0，发现 45 skills。standalone：1 包/9 文件、22 链接，0 断；未装 `research-os`，按合同 blocked。paired：2 包/37 文件、79 链接；0 个已选包内断链，另有 1 个明确未选分支 `../interrogate/SKILL.md`，按需分支缺失不计失败；未装 setup 的两份批次模板只影响作业/费用分支，普通无 setup 恢复正例通过。representative：8 包/78 文件逐文件 SHA256 与源一致，113 链接、0 断；包含 `interrogate` 以解析入口引用；15 条依赖映射的仓库源/扁平目标一致，4 个选中的组合分支与 pickup 5 个反引号必读资源均实际解析，2 个 setup 模板实际存在。三个安装的完整 MIT 文件哈希均为 `bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e`。
- **合并与边界**：合入 `integration/spec-48` 本地提交 `bc35b36a9b7aee57f003967c67b5bca6485ab891`（含 #50/#52/#53）；唯一冲突是迁移登记表，手工保留 #59 行及 incoming #53 两行。#50 的 once-only bounded redispatch 注册与测试通过；`origin` 没有 `integration/spec-48` 对应 remote ref（`git ls-remote` 无结果），因此合入当时可见的最新本地 tip；未 push。整个 merge、合入后测试、CLI 安装都仅在 `t3/a14e0648` 目标 worktree；integration worktree 最终只读状态 clean。main worktree 未执行写操作，最终只读状态有本任务未触碰的本地变更，未判断其来源。
- **限制**：只验证结构、明确文本合同与 Skills CLI 安装/路径；未运行真实研究、生产宿主、后台服务、实际费用或长时任务，不据此声称科研正确性或长期运行能力。

## 原始实现状态（独立 review REJECT 之前；历史记录）

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
- Before implementation, read the requested Multi-Agent, model availability, pstack model, and coding standards files; DS/GLM/Grok/Kimi are prohibited. The requested TDD/pre-implement/writing-for-agents skills and SKILL-MECHANICS.md were not present under the configured skill roots; use explicit red→green tests and maintain these implementation notes instead. Current execution is direct—no further delegation.

## 原始实现决策（独立 review REJECT 之前；R1–R4 以本节顶部 retry 记录为准）

1. Kept continuation and improvement in existing Research OS structures. `continuation.md` defines verifiable exit conditions, minimum evidence-based steps, cumulative wall-clock and resource accounting, safe pause state, pickup, stalled-route change, honest dead-end handoff, and host capability limits without claiming a background service.
2. Updated `pickup.md` to re-check approvals, authorization, raw artifacts, outstanding obligations and active jobs; old summaries remain leads, not proof. It does not renew `valid_until` or rerun verified unchanged work.
3. Migrated `research-improvement` to inherit `research-os` mandate rather than require per-loop re-approval. Batch experiments remain governed by batch authorization. Improvement workflow retains independent fresh review, evidence and failed attempts, and records process/tool proposals; public suite changes and external tracker creation remain explicit decisions.
4. Independent installation exposed broken cross-skill relative links in flattened layout. Added `references/dependencies.md` mapping the shared `<skills-root>` resources and branch-specific skill dependencies, plus missing/unsupported dependency behavior (`blocked`). Removed sibling-relative Markdown links that would fail under flat installation; skill names now resolve through this manifest.
5. Extended `continuation_contract_problems` to diagnose a missing continuation playbook instead of raising `FileNotFoundError`, and to verify tracked source/license/dependency assets. Did not weaken its existing quota, host-neutrality, or contract markers.
6. Preserved the known historical checker failure class: nine missing, intentionally untracked acceptance evidence archives. No new failure was suppressed or reclassified as a pass.

## 初始提交的恢复阶段验证（review 前历史记录）

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

## R5 入口单包来源与许可修复（2026-10-21；此前 REJECT 保留）

- **入口与范围**：本轮只处理独立 review 的唯一剩余 R5；起始为原 worktree `t3/a14e0648`、tip `af5e3864bf41c02c9bbf034411b4faebf1546a8f`。按用户明确禁止继续派发，在一个小型、可单独验收的包资产/检查器/反例测试切片内直接完成；不重审、不重写 R1–R4，也不编辑原拒绝报告。已读 `~/.agents/Multi-Agent.md`、`model-availability.md`、`CODING_STANDARDS.md`，遵守当前 luna6 xhigh 与禁用模型约束；加载主仓 `.pi/skills/tdd/SKILL.md` 和 `/Users/rolex/.pi/agent/skills/writing-for-agents/SKILL.md`。测试 seam 取自已批准的 #48/#59 安装、结构与文本合同范围。
- **TDD 红**：新增入口单包来源/许可缺失守护后、修 checker 前运行 `uv run --offline --with pytest pytest -q -p no:cacheprovider tests/test_spec48_ticket59.py -k checker_rejects_missing_entry_package_pstack_assets`，`1 failed`（期望诊断 `LICENSE-PSTACK: 许可证不存在`，实际 checker 输出为空），确认 R5 漏检。
- **最小修复与绿**：`skills/general/research-os/` 新增 `NOTICE-PSTACK.md` 与完整 `LICENSE-PSTACK`，保留原有 Matt Pocock `LICENSE`。Notice 标固定 revision `88d47514b82e7c44f00f2b2a72ff6dd12158038c`、上游来源路径、适配范围、MIT/Lauren Tan，并明确独立安装不要求 `research-improvement`；集中来源登记同步到实际文件位置。checker 新增入口资产存在/追踪/来源标记检查、固定许可证 SHA256 与和现有上游许可证逐字节比较。R5 测试含缺失 notice/许可证与截断字节 mutant；`uv run --offline --with pytest pytest -q -p no:cacheprovider tests/test_spec48_ticket59.py -k "entry_package or continuation_checker_reports_missing_assets"` → `3 passed, 17 deselected`。完整许可 1067 bytes，SHA256 `bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e`，与 `research-improvement/UPSTREAM-LICENSE.md` byte-identical。
- **Checker**：`uv run --offline python scripts/check-skills.py` 最终仍 `FAIL: 9`，仅为已报告的九条旧 acceptance archive 链接；本轮中间版本因上游路径未标注 upstream 多报一条级联诊断，调整来源表述后消除，本次无新 checker 诊断。
- **整合与最终安装复验待记**：当前集成 tip 为 `8b21f78385d89b5f600ccbef7843278a048be0fa`，仅新增 review-only 拒绝记录；提交后需将其合入本 worktree，并在合入后重跑相关测试与真实 Skills CLI 单装/全文件字节及资源可达核验，再补记最终证据。未 push/PR/写 issue/清理 worktree。
