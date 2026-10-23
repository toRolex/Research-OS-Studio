# #60 proof/discovery 收缩切片 M — implementation notes

## 状态

- proof 资源迁移与旧控制器删除：待最终验收；实现目标为旧控制器无调用者、方法与许可在 proof-review 包完整可达；当前已通过合同测试与真实 CLI 树外安装，待在明确 integration tip 后复验。
- discovery 配方迁移与旧控制器删除：本 unit 不开始；按用户预算提醒留给 parent/后续切片，保持 `creative-thinking-for-research` 现状。
- 产品地图/README/安装/校验合同同步：待最终验收；当前本切片相关活调用清理完成，#55 与 checker policy 定向测试通过。
- integration 同步与最终复验、报告：进行中；integration tip 已核实为 `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e`，`a11775f` 不在本次合并范围。

## 入口与边界

入口判定：直接执行，不派发。任务交付物和 seam 已由用户明确给出，且本线程明确禁止继续派发；根据用户后续预算提醒，本 work unit 仅完成 proof-orchestrator 资源迁移与控制器退休，idea-discovery 留给 parent。当前 worktree `t3/shrink-proof-discovery-controllers` 从 integration 基线 `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e` 创建，HEAD 与基线一致、工作树干净。不改 ML/Systems/experiment-bridge 产品，不写 integration/main worktree，不 push、不改 tracker，不提前合并 `a11775f` 活文档分支。

已读取全局 Multi-Agent、model-availability、CODING_STANDARDS，仓库 AGENTS.md、pre-implement、writing-for-agents、SKILL-MECHANICS 与 TDD；输入依据为 `/tmp/spec48-ticket60-prep/REPORT.md`、`/tmp/spec48-ticket55-{sliceB,sliceC,merger}/REPORT.md`、`/tmp/spec48-goal-preflight/{spec.json,tickets.json}`。本任务通过 ticket/spec 指定的安装边界作为预先约定 seam：资源/许可保留、调用者消除、发现配方语义与真实 Skills CLI 独立安装。

## 决策与偏离

- 按“先归属/验证资源，再断开调用者，最后删除入口控制器”的次序迁移；不得把证明方法塞回入口正文，不把用户需求到 Proposal 固定成阶段流水线。
- 历史 notes/acceptance 不改写；旧数目/目录断言以真实资源、职责和调用图正反例替代。保持权限与证据边界。
- TDD 按一个 seam 一个测试/最小实现推进，所有 Python 与 checker 命令串行且设置树外 `TMPDIR`，单命令 180 秒上限；报告保存原始日志、实际 returncode 与 SHA256。既有 6 个失败和 9 条 archive 诊断精确保留，不借本切片隐藏或放宽。

### Deviations

按用户后续交接提醒，将最初的 proof + discovery 双控制器任务缩为一个可单独验收的 proof 资源迁移与退休切片；idea-discovery 资源、配方、调用者和 CLI 验证明确交 parent/后续 slice，不为一次完成全部范围而扩张。

## 证据记录

- TDD contract red：`/tmp/spec48-ticket60-contract-M/logs/proof-red.log`，`tests/test_spec48_ticket60_contract_M.py` 首轮 25 failures，真实 returncode 1；诊断为替代资源、许可证/NOTICE、旧控制器和调用图尚未迁移。
- TDD green：同测试 4 tests 通过，returncode 0；最终测试输出见 `/tmp/spec48-ticket60-contract-M/logs/test-contract-M-final.log`，SHA256 `a96b8a0ff4f90d78ab052a1751acd8f202860fc81dc6f36e605701014e9aa367`。
- 已运行 #55 proof 合同 17 tests（returncode 0）与 checker policy 文件 4 tests（returncode 0）。Skills checker 自身 returncode 1，只有既有 9 条 docs/acceptance tarball 缺失诊断；无新资源/迁移诊断。
- Skills CLI 1.7.4 通过缓存离线安装 `research-os`、`proof-review` 两个单独 slug；cwd、HOME 均位于 `/tmp` 独立目录。包内相对链接闭合，安装包文件集合与源码逐文件 SHA256 一致。原始输出与 manifest 位于 `/tmp/spec48-ticket60-contract-M/logs/`，最终哈希索引见 REPORT。
- 六项既有测试失败不在本 unit 复跑；未改写历史 notes/acceptance，不处理九条 archive 诊断。
