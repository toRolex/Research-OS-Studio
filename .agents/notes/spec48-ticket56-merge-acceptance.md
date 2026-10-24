# Spec48 #51 + #56 隔离候选验收

日期：2026-10-24（Asia/Shanghai）

## 历史工作单元状态（补记）

2026-10-24依据本记录当时的#51+#56候选收束阶段补记；未重跑历史命令，不把后续#57或当前产品状态倒灌入本记录。

| 单元 / 交付目标 | 当时状态 | 原有产物与证据 | 当时下一步 / 阻塞 |
| --- | --- | --- | --- |
| 合并#51再合并#56、核对登记 | done | `e93470e`、`0b5b843`及下文Merge身份/自动合并记录 | 无（#51+#56合并范围）；不代表#57已入 |
| 联合/全套/checker候选验收 | done（完成限定验收工作） | 联合182 passed；全套7 failed/250 passed；checker九条历史诊断字节相同，见下文 | 七项历史失败保留；候选不等于整包通过 |
| #57后续合并 | 未完成（已abort） | 下文#57交接提示、冲突/测试问题与退回#56候选记录 | 需在候选分支重做冲突协调及验收；当时integration未推进 |

## 范围与边界

- 候选分支：`t3/merge-issues-56-57`；仅在当前宿主管理的 T3 Git worktree 操作。
- 基线及 `integration/spec-48` 当前 tip：`b0d8eadc171435896bc2b7bef76bbc54722b797c`；未更新 integration ref、未触碰主目录、未 push、未操作 tracker。
- 当前已验收范围：先合入 #51 候选，再合入 #56；#57 未完成，不把当前切片冒称为 #51+#56+#57 最终候选。

## Merge 身份

- #51 候选源：`522c295d55e456a513a05e67bba8a176d7c5a587`，其父为基线 `b0d8eadc171435896bc2b7bef76bbc54722b797c` 与 #51 源 `bc151b0248ea0fdc9eb46325c85b661c8d9ca9c0`。
- #51 no-ff merge：`e93470e155bcfc9edeeccf93cc6c7efb13818b21`；双亲为基线与 #51 候选源。实际差异 12 文件，543 insertions / 6 deletions；来源、六阶段 arena、安装与独立性等 AC 及证据见 `/tmp/spec48-51-merger/REPORT.md`。
- #56 源：`0b43817bc52a8dca88d5138c253e7a30105da873`。no-ff merge：`0b5b84384744a806041284cd598490fefecc171c`；双亲为 `e93470e155bcfc9edeeccf93cc6c7efb13818b21` 与 #56 源。#56 相对基线 34 文件，1580 insertions / 223 deletions；自动合并无冲突。README、sources/license、checker、skills README 与 migration-boundary 中 #51 与 #56 的登记/检查/合同均保留。

## 验收

- #56 的 F1–F6 逐项实施证据、真实单装与合同测试见 `/tmp/spec48-56-resume/REPORT.md` 原报告。
- 联合命令：`uv run --offline --no-project --with pytest --with pytest-subtests python -m pytest -q tests/test_spec48_ticket49.py tests/test_spec48_ticket50.py tests/test_spec48_ticket51.py tests/test_spec48_ticket52.py tests/test_spec48_ticket53.py tests/test_spec48_ticket54.py tests/test_spec48_ticket56.py tests/test_spec48_ticket59.py`；退出码 0，182 passed，78 subtests passed。
- 全套命令：`uv run --offline --no-project --with pytest --with pytest-subtests python -m pytest -q -p no:cacheprovider`；退出码 1，7 failed，250 passed，122 subtests passed。7 个失败 ID 与原 integration 基线名单完全相同：
  - `tests/test_check_skills_policy_gates.py::PolicyAndGates::test_checker_green_and_leaf_baseline`
  - `tests/test_config_contract.py::ConfigContractTests::test_gate_baseline_and_counterexamples`
  - `tests/test_config_contract.py::ConfigContractTests::test_shipped_templates_and_full_checker`
  - `tests/test_config_contract.py::ConfigContractTests::test_valid_policy_and_log_fields`
  - `tests/test_config_contract.py::ConfigContractTests::test_valid_role_table`
  - `tests/test_final_contract_fixes.py::FinalContracts::test_full_cli_damaged_declarations_refs_and_readme`
  - `tests/test_review_fixes.py::ReviewFixes::test_compute_limits_are_per_unit_not_summed`
- Checker：`uv run --offline --no-project python scripts/check-skills.py` 退出码 1，仍为已知 9 条 archive `.tar.gz` 缺失/未追踪链接诊断。与 `/tmp/spec48-closed-baseline/logs/head-checker.log` 比较，stdout 都是 1171 bytes 且逐字节相同；未屏蔽/放宽 checker。
- `git diff --check b0d8eadc171435896bc2b7bef76bbc54722b797c HEAD` 退出码 0。#56 合入后 worktree clean。

## #57 交接提示

#57 源审计已读其 42 文件 diff 与 `/tmp/spec48-57-resume/REPORT.md`。实际测试 hunk 把原失败节点 `test_checker_green_and_leaf_baseline` 换成 `test_checker_has_only_recorded_tarball_gaps_and_leaf_baseline`：仍实际运行 checker，要求 9 条诊断均匹配 `docs/acceptance/... evidence/*.tar.gz`、返回码为 1，并逐叶检查 `LEAF_GATES`、写作迁移登记及损坏副本反例。因此全套由 7 变 6 的预期原因是该旧“checker 必须 green”节点被新的 9 条历史 archive 合同节点取代并转绿，不是删除 archive 链接校验；#57 报告记录的全套结果是 6 failed、223 passed、108 subtests passed。该结果尚未在 #51+#56+#57 候选上复验。

测试覆盖的一个限度：policy test 锁定“恰好 9 条且全部符合 tarball 诊断格式”，没有逐条锁定 9 个路径/目标；不过本 #51+#56 候选实际 checker 输出与原 baseline 完全相同。后续合入 #57 时应继续对照这 9 条原始 ID，不得抑制它们。

预算收束时曾开始 #57 no-ff merge，随后 abort 回到已验收的 #56 SHA。冲突文件为 `scripts/check-skills.py`、`skills/README.md`、`skills/general/research-os/references/migration-boundary.md`；标记清理后联合测试提示 README 双重分类行，以及 policy test 将 #56 已迁移的 validation skills 仍列为旧 Gate。#57 当前未合入；后续仅在候选分支重做并精确解决这些跨票冲突，再按要求完成 #57 联合/全套/checker 验收。

当前候选 HEAD（本验收记录提交之前）：`0b5b84384744a806041284cd598490fefecc171c`。integration 未推进。
