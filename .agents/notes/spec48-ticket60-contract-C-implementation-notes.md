# Spec48 #60 C03/C05/C06 合同修复 notes

## 状态

| Work unit | 状态 | 产物与验收证据 | 下一步/阻塞 |
|---|---|---|---|
| 候选整合与依据核对 | done | worker worktree `t3/resolve-final-contract-gaps` 已合入候选 `f7b03400a4b77bc77265e9076199977815163a87`，无冲突；`/tmp/spec48-ticket60-final-contracts/FINDINGS.md`、`COVERAGE-41.md` 与 `/tmp/spec48-goal-preflight/spec.json` 已读 | 无 |
| C03/C05/C06 安装合同 seam | done | 七个技能包实际安装后跑 `tests/test_spec48_ticket60_final_contract_C.py`：原候选 **RED 7 tests / 18 failures / rc=1**；修复后 **GREEN 7/7 / rc=0**；合并本地 integration tip 后复跑 **7/7 / rc=0**。代码 commit `e7fcb080db6dbc3c0e505581edd89086b6835bbc` | parent 独立审查 |
| Green/回归和安全门复核 | done | Checker **9 archive 缺件**与 historical-nine 一致；全 tests **286 项/6 个既有失败**与 historical-six 一致；scripts **49 项另1个 #45 非本包 fixture 失败**。完整日志在 `/tmp/spec48-contract-fix-C/logs/`，未修归档/失败 | parent 结合其余 work units 验收 |
| 报告及自有 notes commit | done | `/tmp/spec48-contract-fix-C/REPORT.md` 已含 findings 响应、actual diff commit、TDD/回归日志和 worker SHA/branch/worktree；本 notes 已独立提交 | parent 另行合并与判定 #60 总体验收 |

## 入口判定与范围

- 依据 `~/.agents/Multi-Agent.md`：本任务已被拆为明确的实现 worker 单元，用户指定不得继续派发；在本 worktree 内直接执行，不触碰 integration/主目录，不 push/tracker。
- 前置依赖是合入指定候选，而非合并到 integration。当前分支 `t3/resolve-final-contract-gaps`，起点 `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e`；已合入 candidate，后续只对用户指定 integration tip 做本分支复验。
- 明确的本地 integration tip 为 `integration/spec-48` → `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e`；在 worker 分支执行 `git merge --no-edit --no-ff integration/spec-48` 返回 Already up to date（tip 已是第一父链），之后已重跑安装态 7/7。
- 完整实际 diff 已提交于 `e7fcb080db6dbc3c0e505581edd89086b6835bbc`；当前代码分支 HEAD 同该 SHA。完整 worker 报告位于 `/tmp/spec48-contract-fix-C/REPORT.md`。
- 原 findings 是合同矛盾线索，不当作真实 agent 行为复现。不得把取消重复点名/阶段确认扩展为取消安全门。

## 决策记录

### 2026-10-24 — 候选与材料

- 合并前工作树干净；候选不在当前 HEAD 祖先链中，执行 `git merge --no-edit --no-ff f7b03400a4b77bc77265e9076199977815163a87`，无冲突。候选的 tree 为 `9e5f781a5108bc09ab508abfa62857ad9a5d196c`。
- 已完整阅读 findings、41-skill coverage、spec body、writing-for-agents、SKILL-MECHANICS、pre-implement、TDD 验收先例；模型可用性检查允许当前 luna6，不调用受限模型。

### 2026-10-24 — 安装 seam 与回归边界

- 新测试调用 tracked-only `tests/spec48_workcopy.py::copy_tracked_tree`，不复制 ignored archives；通过离线 `skills@1.7.4` 将六个目标叶与 `research-improvement` 共七个包复制安装后，检查安装态正文。Red 的反例同时检查整份安装正文中 finding 所指出的旧强制点名/拒绝级联条款消失，以及只读、目标替换、fresh review、有效 batch/额度/并发、外发与独立调用边界保留。
- 第一次 Green 暴露测试措辞对 `fresh` 与“禁止实验”的文本表示假定过窄；把断言改成验证现有的“未参与生成/修订 reviewer”与“不亲自实验”合同后复跑 7/7。原日志另存 `tdd-green-test-adjustment.log`；最终通过日志为 `tdd-green-final.log`。
- Checker 找到9个历史 evidence tarball 未跟踪/不存在，逐条与 `historical-nine-archives.txt` 一致；未补拷、未修改这些归档。全 tests 286 项有6个失败，名称与 `historical-six-failures.txt` 完全一致。scripts suite 49 项另有 `test_check_skills_ticket45.Ticket45Routes.test_positive_cascade_and_corrupt_copy` 失败：候选 proof recipe 已不含测试要替换的退役字符串，测试确认损坏副本与原文本相同；本包不触及 proof 路由或该测试，未扩 scope 修复。

## Deviations

- 回归中发现一个非本包既有脚本测试（#45 proof fixture）失败；依据用户“只改指定范围”不改 proof 路由/fixture，仅如实报告。历史9 archive 与6 failure 明确保留，不修复或重打包。
