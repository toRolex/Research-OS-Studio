# #60 proof/discovery 收缩切片 M — implementation notes

## 状态

- proof 资源迁移与旧控制器删除：done；15 份 references、MIT 许可与 NOTICE 已归入 `proof-review`，旧控制器与活调用均已移除。验收：`tests/test_spec48_ticket60_contract_M.py` 4 项通过、#55 17 项通过、真实 CLI 双包独立安装与 hash/链接核对通过。
- discovery 配方迁移与旧控制器删除：本 unit 不开始；按用户预算提醒留给 parent/后续切片，保持 `creative-thinking-for-research` 现状。
- 产品地图/README/安装/校验合同同步：done；入口、配方、PRODUCT-MAP、migration-boundary、来源说明、README 目录与 checker 均无旧可调用 slug。
- integration 同步与最终复验、报告：done；明确合并 tip `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e` 已是祖先（`git merge` 返回 Already up to date）；最终定向复验通过。`a11775f` 未合并。

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
- TDD red→green：迁移前合同测试 25 failures、returncode 1；首次合并后验证时，调用者正则误把 NOTICE 中历史 upstream 路径当活调用，修正后最终 4 tests、returncode 0。最终日志 `/tmp/spec48-ticket60-contract-M/logs/final-contract-M-green.log`，SHA256 `6c49b46ef3271134ecd4774a8e93a73c2a783156fcca5421d3ab9437c6de0626`。
- 最终 `tests/test_spec48_ticket55.py`：17 tests、returncode 0，日志 SHA256 `ec9e32f129f9c20f4755bed7f779053551c4a9c4ee4b3a20ce2f2ce90ca3af52`。首次最终复验发现旧断言仍要求源码相对 Lean 路径，按 slug 索引改写测试后通过。
- 最终 checker policy 文件：4 tests、returncode 0，日志 SHA256 `1a54f5d556bf55ad437aec3ddfb89052c66ddb42675e6bea78d0473fb72f9d07`。Skills checker 自身 returncode 1，只有既有 9 条 docs/acceptance tarball 缺失诊断；日志 SHA256 `acbd51e6f5e308fc570dced0eb6f46d3c9df9eb5de0323fc74271c38a0ff1cbf`。
- Skills CLI 1.7.4 通过缓存离线安装 `research-os`、`proof-review` 两个单独 slug；cwd、HOME 均位于各自 `/tmp` 隔离目录。安装包文件清单分别 30/23 个，包内相对链接闭合、安装文件集合与源码逐文件 SHA256 一致。原始安装日志与逐文件 manifest 位于 `/tmp/spec48-ticket60-contract-M/logs/`，最终哈希见 REPORT。
- 六项既有测试失败不在本 unit 复跑；未改写历史 notes/acceptance，不处理九条 archive 诊断。
