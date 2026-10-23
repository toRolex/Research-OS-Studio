# Spec48 #57 merger 验收记录

日期：2026-10-24（Asia/Shanghai）

## 状态与版本

**候选就绪，integration 未推进。** 本记录只覆盖 #51+#56+#57 本地候选；没有写入 integration、主目录、tracker，也没有 push 或开启 review。

- worktree：`/Users/rolex/.t3/worktrees/Research OS Studio/t3-8d7a63c9`
- 分支：`t3/merge-spec57-validation`
- 基线：`b0d8eadc171435896bc2b7bef76bbc54722b797c`
- #51+#56 已验收候选源：`c8c8499b1fc6e4f1d1e788228088f35ae566917e`
- #57 源：`e65c87af6437bc42f053efdb35a94c8178bc4310`
- 最新读取的 `integration/spec-48`：`c8c8499b1fc6e4f1d1e788228088f35ae566917e`；该 tip 已是本分支祖先，`git merge --no-ff --no-edit c8...` 返回 Already up to date。没有新的 integration notes commit 可并入；该 ref 未被更新。

## Merge 决策

- 从基线 no-ff 合并 #51+#56 候选，生成 `0a4bf6a062ec3d95cd557c5510b2f7c4e16fd3f8`，双亲：`b0d8eadc171435896bc2b7bef76bbc54722b797c`、`c8c8499b1fc6e4f1d1e788228088f35ae566917e`。
- 随后 no-ff 合并 #57，生成 `bb2572e8808b5e0f41ea62c005149ff4bd0de7dc`，双亲：`0a4bf6a062ec3d95cd557c5510b2f7c4e16fd3f8`、`e65c87af6437bc42f053efdb35a94c8178bc4310`。
- 三个冲突按既定边界解决：
  - `scripts/check-skills.py`：`MIGRATED_CONTRACT` 保留 #56 九项 validation 登记并添加 #57 写作登记；`LEGACY_LEAF_GATES` 不恢复任何已迁移项。
  - `skills/README.md`：仅一条 #56 Validation Cycle 行和一条 #57 Writing Cycle 行，链接目录联合测试通过。
  - `migration-boundary.md`：保留 #56 九项 validation 行并追加 #57 写作行；既有 #59 research-improvement 登记不重复。
  - `tests/test_check_skills_policy_gates.py`：LEAF_GATES 移除 #56 已迁移九叶，仍保留未迁移门（包括 `academic-plotting`）；损坏副本继续针对该未迁移能力。

## checker 过渡基线与 red→green

- 真实 checker 保持退出码 1；诊断与 `/tmp/spec48-closed-baseline/logs/head-checker.log` 字节级相同（9 条，1171 bytes），没有屏蔽或修改归档断链，也没有处理归档本体。
- 过渡允许集绑定精确诊断整行：文档路径、行号及目标均与原基线一致。替换测试将 `v2-release-host-regression.tar.gz` 目标替换为 `v2-release-host-regression-replaced.tar.gz`；数量仍为 9 且格式仍匹配，但必须被精确允许集拒绝。
- Red：`logs/allowlist-red.log`，替换诊断仍被旧“9 条 + 格式”规则错误接纳，测试失败（1 failed）。Green：精确集合比较后 `logs/allowlist-green.log`，测试通过（1 passed）。
- 这是待 #60 恢复归档策略后的临时例外；届时删除精确历史允许集与替换回归测试，恢复 checker-green 基线。不得把此过渡合同永久化。

## 验收证据

- 联合票测（49/50/51/52/53/54/56/57/59 + policy + #43 + accept-remediation）：`logs/joint-ticket-tests-post-integration.log`，213 passed，81 subtests passed。
- 全套：`logs/full-suite-post-integration.log`，6 failed，270 passed，125 subtests passed。失败与原七项历史失败精确对照后，唯一消失的是旧 `test_checker_green_and_leaf_baseline`；其余六项不变：
  1. `tests/test_config_contract.py::ConfigContractTests::test_gate_baseline_and_counterexamples`
  2. `tests/test_config_contract.py::ConfigContractTests::test_shipped_templates_and_full_checker`
  3. `tests/test_config_contract.py::ConfigContractTests::test_valid_policy_and_log_fields`
  4. `tests/test_config_contract.py::ConfigContractTests::test_valid_role_table`
  5. `tests/test_final_contract_fixes.py::FinalContracts::test_full_cli_damaged_declarations_refs_and_readme`
  6. `tests/test_review_fixes.py::ReviewFixes::test_compute_limits_are_per_unit_not_summed`
- 单装资源验收：`logs/ticket57-ac6-install.log`，`test_ac6_real_single_skill_installs_include_required_resources_and_licenses` 通过。它对通用、ML、Systems 三个 Skill 做真实单独安装及源/安装文件集合与字节比较；另以 `git diff e65c87a HEAD -- skills/writing-cycle` 为空确认 merge 未改变 #57 写作包内容。
- checker：`logs/checker-post-integration.log` 与已知基线逐字节一致，仍只报告上述九条 archive 诊断。
- `git diff --check b0d8eadc171435896bc2b7bef76bbc54722b797c HEAD` 通过。

## 限制与后续

- 本地候选并不表示 integration 已推进；候选最终 tip 见配套 merger 报告。
- 未处理 #58/#60；真实科研质量与未实测宿主不作通过声明。
- #60 必须恢复历史 evidence 归档/跟踪策略，并移除本记录所述过渡 allowlist。
