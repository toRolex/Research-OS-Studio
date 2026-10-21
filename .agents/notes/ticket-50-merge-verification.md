# Ticket #50 合并复验

日期：2026-10-21；角色：唯一 integration merger，不继续派发、不实现 feature。

## 状态

| 单元 | 状态 | 产物与验收标准 | 下一步 |
|---|---|---|---|
| 固定补丁与逐 AC 审查 | done | 固定 `15791e08aa3a85934c70891ccc832087102d27b8`；原审查不改写；下文逐 AC 对照 | 无 |
| F1、精确基线与实际安装 | done | `ticket-50-merge-evidence/`；21 passed，两个损坏副本各 1 failed；完整 7 失败 / 9 诊断精确相等；CLI 安装字节一致 | 无 |
| no-ff 合并及合并后验证 | done | merge `2cdc144032a07c155edc60c12569cac15117099a`；组合 68 passed，工作树票测 21 passed，精确基线和最终 CLI 文件审计通过 | 无；本记录单独提交 |

## 边界与输入

- 用户明确禁止派发，故直接处理本票复验与整合。使用已批准的 Git worktree 例外，不使用 jj。
- 唯一写域为本 integration worktree；不触碰主目录、源 worktree，不 push / PR / issue / 清 worktree。
- 已读取 Multi-Agent、model-availability、pstack-models、CODING_STANDARDS 与 pre-implement；不调用其他模型。
- 起点 `e84f779d78755937a59d46364e14cc6496aa2b03`，初始 clean；仓库身份 `rolex <torolex@163.com>`。
- 权威输入：`/tmp/research-os-spec48-context/{spec/#48.md,tickets/#50.md,retry-ticket-50.json}`。
- 原独立 review：`/tmp/research-os-spec48-ticket50-review/REPORT.md`，审查 `6da4ffe95201a7b9ab19b1097c6f4ae1fbb66d7f`，五 AC ACCEPT；本次仅复用未变部分证据，独立核验后续四文件补丁及最终安装。
- 验证结构、合同、资源与安装，不声称数学真值、模型实际遵从或全部宿主运行已通过。

## 决策与 Deviations

- 不依赖票测里宽泛 `evidence/` 豁免：独立比较同一基线的完整失败 nodeid 及 checker 诊断，任何新失败阻断。
- 新建本票合并复验记录，不改原 review、原实现记录或 orchestrator notes。
- 合并后首次直接在 worktree 跑组合测试时，已有 #49/#54 `WorkCopy` fixture 会 copytree 整个 ROOT，仅排除 `.git/.venv/__pycache__`；本次 TMPDIR 又设在 ROOT 下，造成临时副本递归包含自身及 ignored 证据。观察到部分输出 `.............F`，未形成可归因的完整测试报告，主动只终止本次 pytest（exit 143），原日志 `logs/postmerge-combined.log` 与命令记录保留，不把它算通过。纠正**验收环境**而非产品/测试：从实际 merge HEAD 导出干净 Git archive 后运行，TMPDIR 是该源树之外的同写域兄弟目录；以完整重跑及基线精确比较作为门槛。相同干净快照也用于最终 CLI，防止 ignored 损坏副本影响发现。原始临时证据保留，未清理任何 worktree。

## 逐 AC 审查

以原独立审查五 AC ACCEPT 为未变部分证据，重新对照 `6da4ffe..15791e0` 四文件差异、候选完整 swarm 正文与固定上游正文。

1. **AC1 来源 / 许可：保持。** 来源仍固定 pstack `88d47514b82e7c44f00f2b2a72ff6dd12158038c`，正文及 LICENSE 未在小修中改变归属。原报告 `upstream-integrity.json` 核过 Git blob / 长度 / MIT；本轮安装另做 LICENSE 全文比较。
2. **AC2 机制：保持。** Frame 仍在 Fan out 前定义 done predicate、分片/竞赛/混合、first pass/rank all/best-of、独立可写路径与 SHA/方法；Fan out 的自足 brief、Aggregate 逐终态审查和 Report 未被削减。
3. **AC3 宿主 / 模型：保持。** 仍要求真实 subagent，无能力则 blocked、不串行冒充；解析项目 `implementer` 角色，缺项沿用当前会话并披露，无 Cursor cloud、个人目录或固定模型绑定。
4. **AC4 缺席 / 有界重派：ACCEPT。** 缺证不 pass、缺口不计覆盖与掉线记录保留；现在 Aggregate 明示剩余额度允许时最多一次、否则直接缺口、二次缺证最终缺口。checker 从 Aggregate 到 Report 局部查三项，避免“下一次会话”在全文虚绿。真实损坏副本已各得到目标测试失败与新增 checker 诊断。属于文本合同守卫，不宣称模型运行行为证明。
5. **AC5 安装 / 入口：ACCEPT，合并后已核新鲜性。** 本补丁没有改变包集、入口、playbook 或映射。候选及实际 merge HEAD 分别导出并用真实 CLI 1.7.4 新建项目安装，单独与组合均 exit 0，完整文件集和字节一致；见下文证据。

KISS/YAGNI/DRY：小修复用现有 checker 调用链，新函数只负责本地 Aggregate 合同；没有新增 runtime 或调度 feature；测试用真实损坏正文文件。保留原全文标记断言不会代替新局部合同测试。

## 合并前独立运行结果

证据根：`.agents/notes/ticket-50-merge-evidence/`，命令 / cwd / exit 索引 `commands.json`，复跑程序 `verify.py`。所有新快照来自本 integration 仓库的固定 SHA `git archive`；未触碰源 worktree，未用 copytree 冒充安装。

- 候选票测：**21 passed**（exit 0），`logs/candidate-targeted.log`。
- 全套 `tests` + `scripts/test_check_skills_ticket*.py`：基线 **7 failed / 115 passed / 44 subtests passed**，候选 **7 failed / 136 passed / 44 subtests passed**，均 exit 1；完整失败 nodeid 集合相等。
- checker：基线与候选均 **同 9 条完整诊断**、exit 1；没有按 evidence 模式滤掉结果。精确集合见 `candidate-comparison.json`；全部原始 stdout/stderr 保存在 `logs/{baseline,candidate}-{full,checker}.log`。
- **F1 独立反例 A**：真实 `damaged-unbounded/` git 快照，Aggregate 换成“不设次数上限，直到证据完整”，全文仍有“下一次会话”等无关“一次”；局部合同测试 **1 failed / exit 1**，checker 在历史 9 条之外新增三项（额度内上限、额度不足缺口、二次缺证缺口）。
- **F1 独立反例 B**：真实 `damaged-terminal/` git 快照，仅把二次缺证条款改为“保留原结果状态”，仍有一般“缺口不算通过”；局部合同测试 **1 failed / exit 1**，checker 新增“二次缺证后的最终缺口”。
- 两损坏副本完整 diff、测试、checker 见 `logs/damaged-{unbounded,terminal}-{diff,test,checker}.log`，新增诊断集合另存 `damaged-*-comparison.json`。旧 F1 原 review 不改写；F1 响应为**已修复并独立复验**，不追认旧 19 条检查具有此能力。
- 真实 CLI 1.7.4，`node <缓存 CLI> add <candidate> -s swarm -a claude-code -y` 及 `-s research-os -s swarm` 均 exit 0。单独 swarm **3/3**、组合入口 **27/27** 与 swarm **3/3** 文件集 / 字节 / SHA256 一致，包内相对 Markdown 链接均存在，MIT 全文一致、入口映射和 mandate 可达。清单：`candidate-installed-file-audit.json`；原始安装日志 `logs/candidate-install-{single,combined}.log`。
- 此门通过时尚未 merge；无新增失败，允许进入整合。

## 合并及合并后独立验收

- **无冲突 no-ff merge：`2cdc144032a07c155edc60c12569cac15117099a`**。第一父 `e84f779d78755937a59d46364e14cc6496aa2b03`，第二父 `15791e08aa3a85934c70891ccc832087102d27b8`；保留源分支与全部原提交。
- `git diff 15791e0 HEAD -- README.md skills scripts tests` 完全为空（exit 0），没有整合时暗改候选产品、测试或 #49/#54 成果，见 `logs/postmerge-product-diff.log`。
- 从实际 merge HEAD 的 Git archive 导出干净最终树，组合 `tests/test_spec48_ticket{49,50,54}.py`：**68 passed / exit 0**，见 `logs/postmerge-snapshot-combined.log`。这是三票组合测试，不声称安装两技能即可执行 #54 的全部能力。
- 最终全套：**7 failed / 136 passed / 44 subtests passed**，exit 1；checker：**同 9 条历史断链**，exit 1。完整失败 nodeid 与完整诊断仍和 e84f779 基线精确相同，见 `postmerge-comparison.json` 与 `logs/postmerge-{full,checker}.log`，未屏蔽新失败。
- 实际 merge HEAD 最终快照再次用真实 CLI 1.7.4 安装：单独 swarm **3/3**，组合入口 **27/27** 与 swarm **3/3**；全文件集与逐字节相等，SHA256、包内相对 Markdown 链接、MIT 全文、mandate 和入口到 swarm 的安装布局映射全部通过。原始日志 `logs/postmerge-install-{single,combined}.log`，审计 `postmerge-installed-file-audit.json`，不是复用小修前安装或 copytree 模拟。
- `git diff --check e84f779 HEAD` exit 0，见 `logs/postmerge-diff-check.log`。最终 notes 将仅使用 `git add -f -- .agents/notes/ticket-50-merge-verification.md` 纳入提交；证据目录保持本地可追溯，不强制加入。
- 补充在真实 integration 工作树（非快照）运行 #50 全部票测：**21 passed / exit 0**；工作树 checker 仍与基线完整 9 条诊断精确相同（exit 1），暂存记录 `git diff --cached --check` exit 0。见 `logs/final-worktree-{ticket50,checker}.log` 与 `logs/final-staged-diff-check.log`。树内保留原始大证据使 rglob 较慢，但检查已完整结束。

## 未解决项与结论边界

- **本票五 AC ACCEPT；F1 已修复并独立复验；无新增产品阻断项。**
- 历史 7 个测试失败 / 9 条 evidence tar.gz 断链仍未修复，不能称整库全绿。
- 曾中止一次污染的 worktree 组合运行，完整保留记录；经最终干净提交快照重跑排除验收环境问题，不把中止视为通过。
- 未执行真实 swarm / 模型派发、数学求解、长期无人值守、付费 GPU、SSH 或全宿主交互；静态/安装通过不证明数学正确或模型遵从。
- 未派发 agent、未修改产品/测试、未改旧 review、未写 orchestrator notes、未 push / PR / issue / 清 worktree。仓库身份 `rolex <torolex@163.com>`。
