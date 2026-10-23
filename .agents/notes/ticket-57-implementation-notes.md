# Ticket #57 implementation notes

## 状态

| Work unit / 交付目标 | 状态 | 产物与验收证据 | 下一步 / 阻塞 |
|---|---|---|---|
| U1：统一 Writing Cycle 入口、保留专业表达与专项用途、修复 checker/合同并验证独立安装 | 待验收 | 本分支 `t3/repair-writing-cycle-skills`；快照 `/tmp/spec48-57-resume-snapshot/`；定向 `52 passed / 3 subtests`，安装一致性 `1 passed`；全套历史基线差集见下 | 全量复验已完成；尚需最新 integration tip 同步、冲突检查、定向复验与提交 |

## 入口判定与范围

- 依全局分流规则记录：直接执行本票的单 work unit。用户明确指定本会话为实现 sub-agent，并禁止继续派发；票据、spec、基线和旧 notes 已就绪，且只交付 #57 范围。
- 前置：#49 已 CLOSED；新隔离 worktree `t3/repair-writing-cycle-skills` 起于 `b0d8eadc171435896bc2b7bef76bbc54722b797c`。T3 binding 指向当前新 worktree；integration 分支不可在本任务内改写。
- TDD seam 使用已确认的 #48 Testing Decisions：安装后 Skill 套件、结构/明确合同、helper 正反例。对已从旧脏工作区恢复的改动，不追认其历史 red；后续新修复逐切片记录真实 red→green。
- 只处理 #57：Writing Cycle 入口与授权语义、专业参考可达和独立安装、checker/合同测试、必要导航。#58 绘图/共享检索资产不纳入本票。

## 已发生的决策

- 旧源分支 `t3/writing-cycle-skills@e84f779d78755937a59d46364e14cc6496aa2b03` 是 integration `b0d8ead` 的祖先（`integration...source` 计数 `35 0`）；在当前分支执行 merge 得到 Already up to date，历史已保留，不创建冗余 merge commit。
- 旧目录只读快照：41 条 tracked 路径（含 index/staged），`git diff HEAD --binary --full-index`；0 条 untracked。快照 patch SHA-256 `a308d08c20d689c3629c70780d31dba3c2fe7129c9468a17c5e7520f6170232f`。只在当前新 worktree 三方重放；README、checker、skills README、migration-boundary 与较新 integration 合同冲突，选择保留 #58/#59/#51 资产并叠加本票写作合同。
- checker 合并：MIGRATED_CONTRACT 同时保留已有迁移记录与本票写作条目；写作叶旧门从 LEGACY_LEAF_GATES 移除，但 research-improvement 等未迁移门保留。
- 交叉合同审计发现 #59 已在 integration 将 `research-improvement` 登记到 `MIGRATED_CONTRACT` 与迁移边界；旧源快照仍将它放在 `LEGACY_LEAF_GATES`，造成集合重叠。先更新过期待其不再是旧门，再运行两项回归确认 red（2 failed）；随后从 checker 移除该过期门，回归 green（2 passed）。保留该 Skill、资源、合同和已有委托语义。
- #43 checker helper 原本只检查 playbook 提到 `standards.md`，不验证专业标准文件是否被链接、目标是否存在。先新增缺链接和缺目标反例，得到 red（2 failed）；补 `paper_writing_domain_standard_problems` 检查 ML 与 Systems 专业链接/目标，8 个 #43 测试通过（3 subtests）。
- 文案合同 red→green：新增测试要求 paper-writing / drafting / talk 在未解决冲突前先按当前有效授权补查/补分析，并仅暂停受影响部分；新增 resubmit frontmatter 测试排除“所有冲突和是否投稿都交用户决定”。初始 2 failed，改写 4 个技能文档后 2 passed。
- 独立安装测试加入源目录与安装副本的完整文件集合和逐字节比较，并校验统一 `standards.md` 的资源链接仍留在安装包内；skills CLI `1.7.4` 三种目标真实 copy 安装测试通过。

## 当前验证事实（2026-10-24）

- 定向合同：`uv run --offline --no-project --with pytest pytest -q tests/test_spec48_ticket57.py scripts/test_check_skills_ticket43.py tests/test_check_skills_policy_gates.py tests/test_spec48_ticket49.py tests/test_accept_remediation_contract.py`，退出码 `0`，**52 passed，3 subtests passed**。
- 安装比较：定向 `test_ac6_real_single_skill_installs_include_required_resources_and_licenses` 退出码 `0`，**1 passed**。CLI 断言 `skills@1.7.4` 版本正确；paper-writing、ml-paper-writing、systems-paper-writing 各自在临时项目单独 `--copy` 安装，命令退出 `0`；安装目录只含所选 Skill；源/安装的相对文件集合、每个文件字节逐项相同；paper-writing 内 ML/Systems 专业参考文件存在且 `standards.md` 所有本地链接目标位于安装包内。该验收不声称外部宿主语义或科研质量。
- 全套：`uv run --offline --no-project --with pytest python -m pytest tests scripts/test_check_skills_ticket*.py -q`，退出码 `1`，**6 failed，223 passed，108 subtests passed**。6 个失败 node ID 均属于 `/tmp/spec48-closed-baseline/REPORT.md` 已记录的历史缺失 tarball 影响集合（4 个 config、1 个 final-contract、1 个 compute-limit）；原 baseline 中的 policy-gates 全绿旧节点已由本轮“精确 9 条历史诊断”合同取代。本轮未把原旧分支 14 failures 全部归为历史：定向旧断言与新安装问题均已处理。
- Checker：`uv run --offline --no-project python scripts/check-skills.py`，退出码 `1`，精确输出 9 个已记录的 acceptance evidence `.tar.gz` 未追踪/缺失链接，未出现新增问题；未屏蔽或改动这些历史失败。

## Deviations / 风险

- 无计划偏离。旧目录状态与源笔记均只读；所有冲突解决仅发生在新 worktree。
- 历史 red/green 不可由恢复后的文件推断；按用户要求，报告只列本次实际命令与退出码。
