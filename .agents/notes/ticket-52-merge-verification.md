# #52 独立整合验收（新 round）

日期：2026-10-21。入口判定：这是被明确指派的单票 review/merger，用户禁止继续派发，因此直接执行；不调用其他模型、不实现 feature。旧 `spec48-ticket52-merger-r1` interrupted、无产品交付，不作为通过依据。

## 状态与边界

| 单元 | 状态 | 产物/证据 | 下一步 |
| --- | --- | --- | --- |
| 权威材料、diff、上游职责与许可核查 | done | `candidate-full-diff.log`、`candidate-upstream-audit.json` | 五 AC 合并前通过，无阻断 |
| 干净快照、关键测试、损坏反例、真实 CLI 安装 | done | `candidate-comparison.json`、损坏副本与 `candidate-installed-audit.json` | 最终候选需再安装 |
| 合并与 49/50/52/54 联合、全套回归 | done | `c7b8f4a` no-ff；最终 `1331787f` 快照和 `final-*` 证据 | swarm 有界重派及新检查原样保留 |
| 逐 AC 结论与提交 | done（本文件提交时生效） | 下表；本验收 notes 单独提交 | 无必需待做项；限制见末尾 |

唯一写域为本 integration worktree；Git worktree 例外已获用户批准，不用 jj。不得 push/PR/issues/清 worktree；只提交本验收 notes，证据保持 ignored。每个执行单元受 20% 上下文预算约束；超限先保存并交接，不仓促认定通过。

初始 integration：`60ecb1bbb4b10308ea6b20a498654c12f30fdcef`，状态 clean。源分支 `t3/independent-interrogate-reviewers`，候选 `9326c04`（完整 SHA 由证据记录）。权威需求在 `/tmp/research-os-spec48-context/spec/#48.md`、`tickets/#52.md`，原 brief `retry-ticket-52.json`。固定上游为 `pstack@88d47514b82e7c44f00f2b2a72ff6dd12158038c/pstack`。

## 验收原则

- 独立挑战、具体 findings 去重、保留分歧、主审四桶有据判断；科研 lens 检查实际材料与证明义务，共识不等于数学证据。
- 独立及委托内本调用均只读；修复属于编排者另行按授权组织。实际子代理能力/角色配置映射，缺 subagent 必须 blocked。
- 使用 Git archive 干净快照，TMPDIR 位于快照树外，避免 #49 WorkCopy 递归复制 ignored 证据。Python 用 uv。完整比较失败 nodeid 与 checker 诊断，不按宽泛模式过滤。
- 实际通用 CLI 安装核完整文件集、逐字节、许可、相对路径及兄弟能力依赖；不是仅 `test -f`。安装/静态合同不证明科研真值或全宿主行为。

## 合并前独立判定

源完整 tip：`9326c044d73bd5075ebf8d22c946270c42faf401`；共同基线 `e84f779d78755937a59d46364e14cc6496aa2b03`。亲核全部 16 文件 diff、interrogate 正文/全部 references/YAML/LICENSE，及上游 README、正文、4 refs、LICENSE。rubric、code-quality-review、lead-judgment、MIT 与 pinned 原文逐字节一致，SHA256 见 `candidate-upstream-audit.json`；正文和 reviewer 模板适配 diff 独立留证。

- #52/#54：46 passed（exit 0）。当前 integration 基线全套 7 failed / 136 passed / 44 subtests；源候选全套也是该结果。两者票测组成不同，不把相同计数当证据；完整 7 个失败 nodeid 和完整 9 条 checker 诊断分别精确相等，见 `candidate-comparison.json` 与原始日志。
- 新独立损坏副本 A 把本调用改为自动写/修材料：局部测试 1 failed，checker 在原 9 条以外新增「缺只读」「缺不自动」。副本 B 删除科研 lens：局部测试 1 failed，checker 新增缺 research-review.md。两者均保留实际 diff、命令、退出码与完整诊断。是本轮反例重放，不冒充实施首红。
- 真实通用 CLI 1.7.4（缓存官方 CLI 入口 node 执行）发现 42 个源技能，单独 interrogate 及 research-os + interrogate 均安装成功。interrogate 完整 9 文件和入口完整 27 文件逐字节/SHA256、内部相对引用、MIT 全文通过；interrogate 无必需兄弟文件依赖，角色表是正文已声明的可选项目配置，缺失分支/缺子代理均明示。组合入口其余未安装能力指针单独列为 sibling_links，不把选装两能力称全套安装。

### 独立挑战与判断

本轮唯一 reviewer 是当前独立验收者，没有派发或模拟其他 reviewer；不把源 worker 自评算独立票数。

- **Act on：无产品阻断 findings。** 独立 challenge 确认 Step 3 使用实际子代理/项目 reviewer 能力，缺工具 blocked、不串行伪独立；Step 4 去重/来源/反向意见保留；Step 5 每条主审理由与材料位置。科研 lens 覆盖材料、义务、等强未证引理、数值候选及空 findings 非证明。
- **Noted：文本检查仅有限覆盖。** 反例证明能检测本轮损坏，不证明能理解任意矛盾句或 agent 一定遵循合同；采用人工逐条合同审查补充，不借此声称科研正确性。
- **Dismissed：原样 code-quality lens 的改进措辞必然授权修改。** 模板首段及末段明确 report only / never edit，SKILL 对整个调用始终只读；研究材料使用 research lens 替代 code-quality lens。既保留上游职责，又有明确输出边界，不构成自动修复授权。
- **分歧记录：** 没有收集到两个独立 reviewer 的相反结论，不制造 Agreement Map 共识。旧 round 无交付不计通过；源 notes 的「安装已验」在本轮只认实际重跑的文件审计。

允许进入 no-ff 整合；若仅登记/README 语义冲突则保留双方，行为复杂冲突停止交父，不暗改产品来让检查通过。

## 整合过程与新增核查

no-ff merge `c7b8f4aa69610b152c820af113a063d619f29647`：父提交为 `60ecb1bbb4b10308ea6b20a498654c12f30fdcef`、`9326c044d73bd5075ebf8d22c946270c42faf401`。四处内容冲突：README 能力行、skills/README General 行、checker MIGRATED_CONTRACT、migration-boundary；逐处并集保留 swarm 与 interrogate，入口 swarm 路线和 interrogate 指针同时存在，没有行为冲突。interrogate 产品/测试相对源 tip 无差异；swarm 产品/测试相对 integration 基线无差异，checker 的 swarm_contract_problems AST 也完全相同。

初次实际 merge 快照复验：四票联合 89 passed；全套 7 failed / 157 passed / 44 subtests；checker 同历史 9 条；精确对照为 `postmerge-comparison.json`。单独/组合 CLI 安装成功，进一步全套安装并核对 **43 个技能 / 298 文件**，不是只检查目录存在。所有文件逐字节及 SHA256 见 `postmerge-all-installed-audit.json`。

### F1：README 数量登记过期（warning，机械性整合修正）

两分支 README 都写 40，不能依相同数字假定合并后为 41。CLI 实际源候选已为 42（包含 #54 新的两技能），合并 swarm 后为 43。首次整合凭增量写成 41 是本轮的错误；全安装立即检出，未用计数充当任何通过证据。按安装真源将两 README 的 badge/标题/文字登记修正为 43，单独提交，保留历史及原日志。只改安装说明元数据，不改产品行为、断言或检查标准。随后对最终候选另起干净快照重跑，不复用更正前验证。

全安装相对引用审计剩余四条均在 setup-research-os/templates/workspace.md，逐条是用户需要填入的 `<项目说明…>` / `<findings 文件…>` / `<日志…>` / `<相对指令文件…>` 模板占位，不是运行资源断链；原文与基线相同。interrogate 引用全部真实文件可达；入口到 interrogate/swarm 的扁平安装同级路径可达，跨分类路径按既有宿主映射解析。全套许可/NOTICE/PROVENANCE 与候选源文件逐字节相等；本票新增 MIT 全文额外和 pinned 上游相等，不借此替其他历史来源声明重新做许可兼容认证。

## 最终候选独立验收

最终产品/安装说明候选 **`1331787f95a976194f68086afac81d395b40801b`**（README 数量登记提交）。其后仅提交本验收 notes，不改产品或测试。

证据根为本 worktree `.agents/notes/ticket-52-merge-evidence/`，ignored，保留不清理。复验程序 `verify.py`、完整命令/cwd/退出码索引 `commands.json`，各原始 stdout/stderr 在 `logs/`。阶段 `prepare`、`preflight`、`damaged`、`install`、`merge`、`postmerge`、`postmerge final`、`closure` 分开留证，前次日志不覆盖为最终通过结果。所有测试快照以 git archive 导出并 git init/add 建立追踪；没有把安装模拟为 copytree。TMPDIR/cache 位于证据根，始终在被测试快照树外。

- **四票联合：89 passed，exit 0**，`logs/final-combined.log`。包括 #49、#50、#52、#54 的全部票测。
- **全套：7 failed / 157 passed / 44 subtests passed，exit 1**，`logs/final-full.log`。**checker：同 9 条，exit 1**，`logs/final-checker.log`。完整 7 个失败 nodeid 与完整 9 条诊断分别和当前 integration 初始基线精确相同：`final-comparison.json` 两个 exact_match 为 true；原始完整输出可复核，没有按 evidence 等模式过滤新失败。
- **最终真实安装**：CLI 1.7.4，独立 interrogate、research-os + swarm + interrogate、以及整套三个不同可丢弃项目均 exit 0。整套 **43 技能 / 298 文件**逐字节、SHA256、文件集精确一致，其中 **52 项 LICENSE/NOTICE/PROVENANCE** 文件也逐字节一致；interrogate **9/9**、research-os **27/27**、swarm **3/3**。文件、相对链接与映射审计 `final-installed-audit.json`、`final-all-installed-audit.json`、`final-summary.json`；原安装日志 `logs/final-install-{single,combined,all}.log`。唯一未解析的四个链接已逐条确认为模板占位，非漏装，未泛过滤。
- **保真与边界**：`final-upstream-audit.json` 四项相等（3 refs + MIT）；正文与 reviewer 模板的适配 diff 见 `logs/final-upstream-*.log`。`logs/final-interrogate-source-diff.log` 为空，确认 merge/数量修正没改 #52 技能或测试；interrogate checker 函数 AST 与原候选一致，损坏反例检测逻辑未被整合稀释。
- **#50 防回归**：`final-swarm-preserved.json` 确认 swarm 全目录、#50 票测与初始 integration 无差异，checker `swarm_contract_problems` AST 完全相同。加上四票联合通过，保留有界重派、预算不足缺口、二次缺证终态缺口的新断言，未退回旧弱检查。
- **版本与整合**：两个父提交均仍是最终 HEAD 祖先，证据 `logs/final-ancestor-*.log`、`logs/final-parents.log`；实际冲突解决见 `logs/merge-resolution.log`。`logs/final-diff-check.log` exit 0。

## 逐 AC 结论

| #52 AC | 判定 | 本轮独立依据 |
| --- | --- | --- |
| 上游正文/reviewer/许可/宿主模型适配 | ACCEPT | pinned 正文与 4 refs 亲核；3 refs/MIT 字节一致；PROVENANCE 差异范围；项目 reviewer 行和宿主实际子代理前提，无固定禁用模型默认值 |
| 独立审查/findings 去重/分歧/有据主审 | ACCEPT | SKILL Step 3–5、reviewer 模板、四桶输出与 Agreement Map 实际文本；本票全部 21 测试包含在最终 89 项联合中 |
| 科研材料与证明义务/共识非证据 | ACCEPT | research-review.md 全文逐条材料/定位/义务/等强引理/数值候选/空 finding；缺科研引用独立反例被测试与 checker 检出 |
| 独立只读/委托修复归编排者 | ACCEPT | 正文委托继承/始终只读、reviewer 模板首末边界、research lens；改成自动写的独立反例被测试/checker 检出；无重新授权修复伪门 |
| 安装/引用/职责保真/无固定数学人设或开放问题门 | ACCEPT | 最终真实单装/组合/全装完整文件及许可审计；自包含 9 文件；不绑定开发者 /tmp；缺子代理 blocked，不串行冒充；未要求真实解题 |

## 结论、风险与未完成项

**#52 五项 AC 通过，已 no-ff 合入，无剩余产品阻断。F1 数量登记已按实际安装修正并以最终候选重验。** 这不是对旧 interrupted round 的追认，也不是根据模型投票得出的结论。

- 历史 7 失败 / 9 条 evidence 断链仍未修复，不能称整库全绿；完整诊断保留给对应后续任务。
- 没有执行真实多模型审查、数学证明求解、长期无人值守、多宿主交互、SSH/付费资源；静态及 CLI 通过只证明安装/结构/合同，不认证科研质量、数学真值或模型遵从性。
- 未新增 feature、未修改本票/他票产品来隐藏审查问题，只有授权的登记冲突合并与安装数量元数据修正。未派发 agent、未动主目录/源 worktree、未写 orchestrator notes、未 push/PR/issues/清 worktree。
- 仓库身份为 `rolex <torolex@163.com>`。本 notes 使用必要的 `git add -f -- .agents/notes/ticket-52-merge-verification.md` 单独提交，ignored 证据不强加到仓库。
