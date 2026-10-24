# #53 独立复审与唯一合并验收

日期：2026-10-21。入口判定：用户明确指定本 agent 独立 review 与唯一 merger，不再派发、不实现 feature；在授权 Git worktree 内直接完成有界验收。

## 状态

2026-10-24依据本记录2026-10-21合并验收收束阶段补记下三项下一步；第1项已有“动态证据待下项”不重复改，历史失败/时间与证据保留，本次未重跑。

- 合同与原 R1–R3 核对：done（静态）；两独立正文均内联对象/依赖/验证资产绑定、stale 与受影响覆盖重跑；上游启动/doctor/证据清理等机制仍在，动态证据待下项。
- 干净 archive / fault injection / 真 CLI 单装 / 精确基线比较：done；票测 27 passed/49 subtests，候选全套 7 failed/163 passed/93 subtests；7 个失败 nodeid、9 条 checker 完整诊断均与 dd70401 基线精确一致。两包真 CLI 单装、完整文件/许可/执行位及安装副本 helper 正反例通过。；当时下一步/阻塞：进入下项整合复验，历史失败不改绿。
- no-ff 语义整合与最终联合/全量复验：done；merge b545af55，五票联合 116 passed/49 subtests；全量 7 failed/184 passed/93 subtests，失败 ID 与 checker 9 诊断同基线精确一致；最终单装与整包安装均通过。；当时下一步/阻塞：无（该候选验收范围）；科研/宿主E2E不在本次。
- 验收记录提交：done（本文件作为独立验收提交）；仓库身份 `rolex <torolex@163.com>`，ignored 原始证据不提交，不 push/PR/issues/清 worktree。；当时下一步/阻塞：交parent后续总验收；不把本票记录当整包通过。

## 固定对象与边界

- 初始 integration：`dd70401cd46dbc6adb6eeaec2eead0b20d07a83f`，clean；含 #49/#50/#52/#54。
- 候选：`4f484a47bd8212d8a1da56041ca88304c546af8f`，分支 `t3/spec-53-verification-skills`；不在源 worktree 执行或修改。
- prior：`/tmp/research-os-spec48-ticket53-review/REPORT.md`；R1 对象/依赖/验证资产绑定与 stale，R2 fragment/外链，R3 checker crash 不能被 stdout 过滤吞掉。
- 验证代码和故障注入仅放 ignored 证据目录的 archive；不改产品来隐藏问题，不把 helper/安装通过宣称为应用 e2e 或数学质量。
- 已读 Multi-Agent、model-availability、pstack-models、CODING_STANDARDS、writing-for-agents / SKILL-MECHANICS 与 pre-implement；未调用受禁模型，无动态 workflow。

## Preflight 证据

根：`.agents/notes/ticket-53-merge-evidence/`（ignored，不强加证据包到 Git）。`verify.py`、`commands.json`、`logs/` 保存实际 argv/cwd/exit/stdout/stderr；`candidate-comparison.json` 保存完整失败 ID/诊断的精确对照，不用正则豁免新失败。

- baseline 全套：7 failed / 157 passed / 44 subtests；候选：7 failed / 163 passed / 93 subtests。候选尚不含 #52，不能用通过数差直接衡量交付。最终必须在合并树重验。
- R1：分别删改两个正文的验证资产版本/stale 合同，两个定向票测各报 2 个失败子断言；checker 也分别新增该技能缺 stale 的诊断。恢复后 diff 为空，票测回到 27/49 通过。
- R2：源 helper 与实际 CLI 安装副本均对 fragment 合法链接 exit0、缺失 fragment 文件 exit1、外链 exit0；另测 `./`、标题/空格、scheme、query、孤儿、普通死链、缺索引、无参数及所有随票 fixtures。故意注入忽略 fragment 回归，现有 R2 票测 exit1，恢复后全票通过。不是只测统计。
- R3：调用实际票测 wrapper，分别注入 RuntimeError、异常 exit2、FAIL 摘要诊断数不符、伪 OK 带 stderr，四项都被 AssertionError 拒绝（exit1）；未复制一个自制过滤器冒充被测代码。
- 候选真 CLI 1.7.4 两个空项目各安装一个技能：create 8 文件、maintain 4 文件（观察值，非固定数量合同）；所有文件字节/执行位与候选相等，LICENSE 与 pinned 上游 MIT 字节相等；create 5 个 Markdown 本地引用可达，maintain 无必需兄弟文件依赖。证据 `candidate-installation-manifest.json`、`candidate-installed-helper-probes.json`。

## 逐 AC 与原 findings 复核

| 项 | 结论 | 本轮实际依据 |
| --- | --- | --- |
| AC1 适配两能力、许可、共置资源 | ACCEPT | 亲读 pinned pstack 两正文与采用示例/许可；NOTICE 标明 revision/适配范围；独立包 MIT 与上游字节一致，无新增第三方运行依赖 |
| AC2 启动、健康、驱动、证据、清理及覆盖差异 | ACCEPT（合同） | create 保留空数据迁移/种子到可用、隔离、doctor 版本/端口/auth、真实路径与动作/结果/副作用、dry-run 实际观察、只清自己实例与清理后证据存活；自证一个映射特征。maintain 每个特征源读+真实驱动，doctor 首次/新会话/失败后重检、失稳重置与最终 teardown |
| AC3 未运行草稿、失败不可达如实、保留证据 | ACCEPT（合同） | 未执行状态写入生成 skill；替身差距保留未验证；维护 blocked、verified-unreachable 须具体前置与尝试路径；失败不削弱旅程，不把待执行覆盖当完成 |
| AC4 helper 正反例、不建科研 runtime | ACCEPT | 源与真安装副本运行随包示例及独立正反例；fragment 的原合法/漏报输入、外链误报输入已直接复验；故障注入会失败，未新增产品 runtime |
| AC5 安装、独立资源、verify 原则与数学边界 | ACCEPT（安装+合同） | 两包真实 CLI 分别安装到空项目，完整发行文件/许可/资源/执行位核查；两正文独立绑定对象/依赖/验证资产与范围假设；维护只改验证不改产品，子代理缺失 blocked、不串行冒充；行为/形式化/数学质量明确分开 |
| R1 | CLOSED | 两独立安装正文均包含每轮 actual revision/dirty diff、关键输入/数据、依赖工具链与验证资产版本、范围假设；相关变化立即 stale，旧证据仅历史，重跑受影响覆盖并重新绑定后恢复；删改合同被定向测试+checker 检出 |
| R2 | CLOSED | scheme/path/fragment 分离；带 fragment 的本地缺文件不再漏报，合法 fragment 不再孤儿，外链不再本地死链；源与安装副本均复现相反于原问题的正确退出码 |
| R3 | CLOSED | 票测 wrapper 核 exit/stderr/摘要与诊断条数；本轮四类崩溃/伪报告注入均拒绝，不再把空 stdout 当无新错误 |

### 非阻断范围限制

- helper 是轻量 inline Markdown 相对 `.md` 文件/索引检查，不是完整 CommonMark 或 anchor 存在性检查。fragment 探针检查的是目标文件是否存在，**不证明标题锚点存在**；root-relative fixture 报错来自本地文件未被相对链接索引，不冒称校验网站根路径资源。
- 上述自然语言合同通过不等于生成 skill 已在真实应用跑过。未测试浏览器/服务/远程生产环境、真实多子代理驱动或数学真值；只把本票要求的安装/结构/合同/helper seam 判定通过。
- KISS/YAGNI/DRY：移植两独立技能，helper 单文件无依赖；两包内联短证据合同是独立安装的必要自足，不引入中央 Artifact 协议。未改产品行为来隐藏发现。

## 整合决策

- 使用授权的 Git worktree，不用 jj；`git merge --no-ff --no-commit <固定源 tip>`，五个共享文件自动合并无冲突。保留 #52 interrogate 与 #53 两能力登记，未采用覆盖一方整文件的解决方式。
- merge commit：`b545af55aaa9ede9ea8f491d41f80545b47cfa4f`，父为初始 dd70401 与固定源 tip；祖先检查均 exit0。
- README badge、目录锚点、能力标题和数量说明按合并后实际发现的 45 个技能更新（不是新增数量断言）。除必要登记元数据外没有额外产品改动。

## 最终复验（合并树 b545af55）

全部 Python 经 uv，Python 3.14.4，pytest 9.1.1，Skills CLI 1.7.4。最终快照来自 `git archive HEAD`，建立临时 Git 追踪，仅导出已提交文件，TMPDIR/cache 在快照外。不是在包含 ignored 大证据树的 worktree 递归 copy 后得出结果。

| 验证 | 退出码与结果 | 证据（相对证据根） |
| --- | --- | --- |
| #49/#50/#52/#53/#54 完整票测联合 | 0；116 passed / 49 subtests | `logs/final-combined.log` |
| 全套 `uv run --no-project --with pytest python -m pytest -p no:cacheprovider -q` | 1；7 failed / 184 passed / 93 subtests | `logs/final-full.log` |
| `uv run --no-project python scripts/check-skills.py` | 1；9 条历史诊断，无新增 | `logs/final-checker.log` |
| 与初始 dd70401 精确比较 | 7 个 nodeid 相等，9 条完整诊断含路径/行号/目标相等，两个 exact_match=true | `final-comparison.json`（非模式过滤） |
| 最终两技能真实 CLI 单独安装 | 各 exit0；create 8 文件，maintain 4 文件；完整文件集/字节/许可/执行位相等，相对资源在单包内可达 | `logs/final-install-*.log`、`final-installation-manifest.json` |
| 最终安装副本 helper | 示例/合法 fragment/外链/标题/空格/query 等 exit0；孤儿/死链/缺失 fragment 文件/缺索引 exit1，无参 exit2 | `final-installed-helper-probes.json`、`logs/final-installed-*.log` |
| 真 CLI 整套安装 | 0；45 技能 / 310 文件；每个文件字节和执行位与最终源精确一致（含全部许可/来源文件） | `final-all-summary.json`、`final-all-installation-manifest.json`、`logs/final-install-all.log` |
| 他票与源 #53 保真 | #49 mandate、#50 swarm、#52 interrogate 及 49/50/52/54 票测不变；既有 swarm/aggregate/interrogate/formal checker AST 不变；#53 两目录/fixtures/票测与原源相同，checker AST 相同；MIGRATED_CONTRACT 为双方条目无损并集 | `final-preservation.json`、`final-shared-registration-audit.json`、`logs/ticket53-source-preserved.log` |
| 版本关系、格式、状态 | 两父均为 merge HEAD 祖先；diff --check exit0，工作树 clean（证据 ignored） | `logs/{merge-parents,source-tip-retained,integration-retained,final-diff-check,final-tree-status}.log` |

完整 #54 模块（含 WorkCopy/当前树检查）本轮包含在联合 116 项中并通过，未删测或按历史失败模式屏蔽。worker 源环境曾不能全绿的记录不作为本轮结论；本轮清洁快照和外置 TMPDIR 的实际结果为准。

### 未解历史问题（明确保留，不称全库全绿）

以下 7 个失败 ID 在 dd70401 / 候选 / 最终三者精确相同，原始 assertion/输出保存在各 full log；checker 9 条均是 tracked acceptance 文档引用 ignored `evidence/*.tar.gz`，完整路径、行号与目标逐项在 `final-comparison.json` 保留。

```text
tests/test_check_skills_policy_gates.py::PolicyAndGates::test_checker_green_and_leaf_baseline
tests/test_config_contract.py::ConfigContractTests::test_gate_baseline_and_counterexamples
tests/test_config_contract.py::ConfigContractTests::test_shipped_templates_and_full_checker
tests/test_config_contract.py::ConfigContractTests::test_valid_policy_and_log_fields
tests/test_config_contract.py::ConfigContractTests::test_valid_role_table
tests/test_final_contract_fixes.py::FinalContracts::test_full_cli_damaged_declarations_refs_and_readme
tests/test_review_fixes.py::ReviewFixes::test_compute_limits_are_per_unit_not_summed
```

**最终结论：AC1–5 ACCEPT，R1–R3 CLOSED；无新增阻断，已按授权 no-ff 合入。** 仍存在上述历史失败，不扩票修复；安装/helper/合同验收不代表真实应用 e2e、全宿主实际加载、长期自主运行或数学质量已验证。

未继续派发、未改主目录/源 worktree、未写 orchestrator notes、未 push/PR/issues、未清理 worktree。证据留在唯一授权写域内。
