---
name: research-improvement
description: 在用户显式授权的一次有界循环内对研究工作整体执行 review → repair → re-review：直接读取 Claims、草稿、方法与代码、原始结果、当前 diff 与历史 findings，在批准范围内修代码、补分析、改稿或补实验并复审，保留全过程与未解决 findings 后停止。
license: MIT
disable-model-invocation: true
metadata:
  category: writing-cycle
  invocation: user
argument-hint: "[研究材料范围：Claims/草稿/方法代码/原始结果/当前 diff/历史 findings] [轮数、写入范围、资源预算与副作用授权]"
---

# 研究工作有界改进循环

用户显式启动的高权限 Workflow：在一次确认的授权内，对研究工作整体循环 **review → repair → re-review**，直到策略认可的正面结论或轮数上限。它同时读取并修复研究本体与论文表达——Claims、草稿、方法与代码、原始结果、当前 diff、历史 findings——因此不是只读审计：它会在批准范围内修改代码、补分析、改稿，并在另行授权时补实验。有界：轮数、写入范围、资源与副作用上限固定；没有无限循环，不因重试隐藏地扩大预算，不自动启动其他顶层 Workflow。

本 Skill 承接 W3 的 `auto-paper-improvement-loop`（论文 review → fix → recompile）与 W2 的 `auto-review-loop`（研究 review → implement → re-review）两条上游方法：保留 fresh reviewer、直接读原文、逐轮修复与完整留存原始回应；删除固定 provider/MCP、reviewer 私有线程记忆、机器 JSON 状态、自证式停止与跨 Workflow 自动推进。方法细节见 [轮次方法](references/loop-methods.md)，内部能力组合见 [组合映射](references/composition-map.md)。

## 1. 调用、角色与授权门

- **User**：拥有研究目标、材料、预算、环境与外部副作用的最终决定权。用户确认 scope、写入范围、最大轮数、资源预算、副作用与停止条件，并可随时要求停止或改变轮次授权。
- **本 Workflow**：持有循环、审查调度与修复执行。在当前授权内读取原始材料、实施修复、复审并交付正文报告；交付后停止。
- **Reviewer**：fresh 独立审查者，直接读取当前 primary artifacts；不看执行者的修复摘要或「本轮改了什么」，每轮重新开始。
- **被组合的内部能力**：只在本次职责、写入范围和资源授权内工作，贡献本 Workflow 正文报告的对应章节。

在第一次写入或运行前，逐项列出并等待用户明确确认；未确认项默认「不执行」：

- **材料 Scope**：要审的研究问题、材料集合与明确排除项；Claims/草稿、方法或代码、原始结果、当前 diff、历史 findings 各自的路径。
- **写入范围**：允许修改的精确文件/目录与操作类别（代码、分析、正文、BibTeX、证明、实验脚本），以及允许新建的文件与输出位置。目录级笼统许可不推导出任意文件写权限。
- **最大轮数**：一个整数上限。一轮 = 一次 fresh 审查（第 3 节）+ 一批受其驱动的最小修复（第 4 节）+ 该批修复的验证；第 6 节的复审即下一轮的 fresh 审查，不另占轮数。首轮直接审查已冻结的基线；失败或未完成的轮同样计数。达到上限后不再开始新一轮，因此最后一轮修复可能只经第 4 节验证、未经 fresh 复审，报告须如实标明。
- **资源预算**：compute、存储与时间；付费 API/GPU、远程机器、SSH/Slurm/云与凭据使用逐项确认。时间预算按 wall-clock 计，覆盖审查、修复、验证与报告写作，起算点为开始读取材料（第 2 节）前；若排除用户确认等待时间，须在报告的资源段显式写明。
- **外部副作用**：远程写入、网络外发、投稿、发布、push 与破坏性操作逐项确认；默认全部不执行。授权写入范围内的本地修改是预期工作，不计为外部副作用。
- **补实验授权**：默认**不补实验**；只有用户显式授权并确认本次运行数名额时，才在第 5 节的名额内执行，并在授权门列出名额值。
- **正面结论标准**：本轮固定的分数阈值与 verdict 词表（达标需两者同时满足）；不由执行者自行选定。
- **停止条件**：哪些情况必须停下来交给用户决定。

**完成条件**：以上各项均可逐项核对，未授权字段明确写「不执行」而不是默认同意；不存在用默认轮数、默认预算或默认副作用填空。

## 2. 冻结基线与读取原始材料

先只读地建立本轮基线，不依赖执行者摘要：

1. **Claims 与草稿**：完整读取当前正文，不只读摘要、目录或作者自述。
2. **方法与代码**：读取实际实现、evaluator、数据划分与实验配置，核对正文描述是否与代码一致。
3. **原始结果**：直接读取结果文件、日志与表格来源，而不是转述过的数字。
4. **当前 diff**：记录基线的版本或 diff 范围以及后续每轮变更，使「改了什么」可回放。
5. **历史 findings**：收集既有审查、未解决问题与既往轮次记录，作为待核实输入，不当作已成立结论。

冻结基线快照（例如原始 PDF、结果或代码的只读副本，或约定的比较起点），使后轮不覆盖基线；后续修改不回写基线。文件缺失或不可读时列出缺项并请求最小输入，不按记忆补造材料。

**完成条件**：五类材料各有可定位来源；基线快照与 diff 起点已记录；缺失项已如实列出并标明影响。

## 3. 独立审查：fresh reviewer 直读 primary artifacts

每轮开始时由 fresh reviewer 直接读取当前材料，给出可核对的裁决。审查输出至少包含：分数、verdict（如 ready / almost / not ready 三档，具体词表由本次约定）、按严重度排序的 weaknesses，以及每条 weakness 的最小修复方向。完整原始回应逐字保留，不摘要、不改写。

**独立性**：每轮使用全新审查上下文；给 reviewer 的输入只有 primary artifacts（第 2 节的 Claims/正文、方法与代码、原始结果、本轮前 diff、历史 findings 原文）与本次问题，不包含「上一轮已修好什么」、执行者解释或修复承诺。上一轮的问题清单只用于追踪，不作为评审证据。审查者不可用时标 `independent review not performed`，降级为单执行者评估，不把自查或用户陈述升级为验证。

**组合只读能力**（在本次授权职责内，按其自身边界工作）：数字与配置—[paper-claim-audit](../paper-claim-audit/SKILL.md)、引用—[citation-audit](../citation-audit/SKILL.md)、整篇拒稿论证—[claim-stress-test](../claim-stress-test/SKILL.md)、证明—[proof-review](../../validation-cycle/proof-review/SKILL.md)、实验完整性—[experiment-audit](../../validation-cycle/experiment-audit/SKILL.md)、统计—[analyze-results](../../validation-cycle/analyze-results/SKILL.md)。它们只报告、不修文件，发现并入本轮 finding 列表。

**完成条件**：本轮每条 finding 可定位到原始材料，且 reviewer 原话已保留；未执行独立审查时已如实标注；没有用执行者摘要代替原文。

## 4. 有界修复

对每条 finding 判定修复、拒绝或未解决：在 scope 内、有可核对的原文证据、且能在写入范围内最小修复的进入修复；越出写入范围的编辑记 rejected，同一 finding 另记 unresolved/blocked 并在第 7 节给出最小决策（是否扩大写入范围或放弃）；需要新证据而当前未授权、或需用户决定的记 unresolved/blocked（第 5、7 节）——rejected 与 unresolved 都不伪装成已修。对每条被接受的 finding 做**最小修复**，按严重度排序，先去重再动手。四类修复各自受第 1 节写入范围约束：

1. **代码**：只改获批的实现范围，保留 evaluator、真实标签、split 与停止阈值。
2. **分析**：补统计、误差与失败记录，不改变原始结果。
3. **正文**：修正数字、比较、范围、caption 与叙事；claim 校准双向进行——真正超出证据的收窄到支持范围，已被证据支持的直接陈述而不叠加对冲。
4. **实验**：只在第 5 节授权内进行。

**写入纪律**：每处修改前重新核对目标原文与唯一锚点；冲突即停并重新确认。路径与操作都受约束（例如冻结 BibTeX 或证明结构时，拒绝新增引用、新定理环境或新数值），被拒绝的编辑记入日志而非静默丢弃。保留表格中的不利数字；引用与结果不得编造。修复模式与 claim 校准清单见 [轮次方法](references/loop-methods.md)。

**验证**：正文类修改用 [paper-compile](../paper-compile/SKILL.md) 做 check-only 复核真实 build，或使用项目已有的构建/测试；代码类修改运行项目已有的测试或最小可复现检查；分析类修改按 [轮次方法](references/loop-methods.md) 重新对账数值。记录实际命令、退出码与产物位置，不把「过滤日志后无输出」当成功。证明结构变化按需做重述回归。

本 Workflow 自行执行修复，不自动启动任何 user-invoked 顶层入口（`experiment-bridge`、`paper-writing`、`paper-compile-repair`、`apply-citation-fixes`、`proof-repair`、`result-to-claim`、`rebuttal`、`resubmit-pipeline`、`paper-talk` 等；其中 `paper-writing`（计划 #25）与 `result-to-claim`（计划 #14）尚未交付，其余为已交付入口）；需要它们时把精确问题与范围交回用户另行点名。

**完成条件**：每条已修复项有位置、原文与验证证据（预算中途耗尽而标 `unverified` 的须在报告中写明）；被拒绝或未修复项有理由；写入未越出确认范围；验证结果如实记录。

## 5. 授权内的补实验

默认不补实验。未获补实验授权时，把需要新证据的 finding 记为 **unresolved/blocked**，说明理由与最小决策，不运行任何任务；该 finding 不中断本轮其余范围内的修复与验证，并在第 7 节交付——只有它成为任何正面结论的唯一路径、或用户要求时，才按第 6 节提前停止。

获得授权且确认了本次运行数名额后，才在名额内组合 [run-experiment](../../validation-cycle/run-experiment/SKILL.md)（单次或少量）、[experiment-queue](../../validation-cycle/experiment-queue/SKILL.md)（多作业批次）、[monitor-experiment](../../validation-cycle/monitor-experiment/SKILL.md) 与 [training-health-check](../../validation-cycle/training-health-check/SKILL.md)：保留 baseline 与全部 attempt（成功、失败、无效、超时），**运行数名额按 attempt 计数，失败、无效与超时同样占名额**，名额用完即停。这里「运行」指产生新数据／新结果或占用付费、远程、GPU 资源的执行；仅对既有原始结果做复算、重绘或统计重算属第 4 节的分析类修复，不占名额。`experiment-bridge` 是用户显式调用的顶层 Workflow，本 Workflow 不启动它；需要完整新实验计划时交回用户。

**完成条件**：每次运行都可回溯到本次确认；未授权项有明确去向且零副作用；没有隐藏的远程或付费动作，也没有自动下一轮。

## 6. 复审与停止门

每轮修复后，下一轮的 fresh 审查即本轮修复的复审；记录分数与 verdict 的逐轮变化，并与上一轮 artifacts 的原始 diff 对照，确认问题是被真正解决而不是被措辞绕过。若已达最大轮数不再开新一轮，则最后一轮修复的快照与第 4 节验证即为最终状态。

在任一条成立时停止并进入第 7 节：

- reviewer 给出策略认可的正面结论（分数与 verdict 同时达标）；
- 达到本次确认的最大轮数；
- 资源预算或补实验运行数名额用完（含中途耗尽：停止新编辑与运行，保留已落盘修改并标为未验证，不为补验证超预算）；
- 新一轮无实质改善或出现分数回退，且下一步需要用户决策；
- 某项修复必须越出写入范围或未授权实验／外部副作用才能继续，且已无其他可推进的范围内修复（补实验类以第 5 节的唯一路径／用户要求条件为准）；
- 材料冲突、不可读或 reviewer 不可用使本轮无法成立；
- 用户要求停止。

多条停止条件同时命中时全部记录，并标明首要原因；涉及未授权写入、实验或外部副作用的停止优先于其他原因，其后依次为轮数与预算用尽、无实质改善、需要用户决策；正面结论、用户要求停止与材料／reviewer 阻塞各自记明，不参与上述排序。

停止后不自动开始新一轮、不扩大预算、不把「本轮未发现阻断问题」写成科研真理或用户接受。

**完成条件**：停止原因、已用轮数与预算、每轮分数轨迹均可核对；没有任何未经再次确认的新轮次。

## 7. 未解决 findings 与不越权声明

- 逐条列出未解决 findings：原文定位、证据、为何未修、需要用户决定的最小问题。
- 保留失败路线、被拒绝的编辑与负向结果；不把未完成写成完成，不隐藏 weaknesses。
- 明确声明本 Workflow 是**可写**改进入口：列出实际修改的文件路径，以及实际运行的验证命令与结果，避免被误读为只读审计。

**完成条件**：未解决项与已解决项分开且各有证据；实际写入与未执行项都写明。

## 8. 报告与产物

用 [改进循环日志](templates/improvement-log.md) 组织正文报告（自然 Markdown，不是机器 schema）：授权与范围、基线、逐轮原始审查回应（逐字）、findings 与修复位置、验证证据、资源与副作用、未解决项、停止原因。默认在对话返回完整草稿；落盘只写用户授权的位置，不预填空目录或状态文件。

**完成条件**：报告与实际读取、修改的材料一一对应；轮次、预算与未解决项可核对；输出后停止。

## 来源与适配

改编自 wanshuiyin / ARIS 的 `skills/auto-review-loop/SKILL.md` 与 `skills/auto-paper-improvement-loop/SKILL.md`，revision `0472e530251cdbd3364c33b110063c58f819edd7`（两个目录均仅有 `SKILL.md`，无共置 references/templates/assets）。上游仓库 MIT 许可，完整 notice 见 [LICENSE](LICENSE)，采用边界记录在仓库 `docs/upstream-sources-and-licenses.md`；使用本 Skill 不依赖上游仓库、中央 runtime 或其其他 Skill。

保留：有界 review → repair → re-review 循环、fresh reviewer 与逐轮重新审查、reviewer 直接读取 primary artifacts、分数/verdict/最小修复的裁决结构、完整原始回应留存、claim 双向校准与叙事缺陷修复、重编译验证与重述回归、原始快照保留与分数轨迹。适配：删除 `AUTO_PROCEED` 自动推进、Codex/MCP 固定 provider 与 threadId 记忆、`REVIEW_STATE.json`/`ACQUITTAL_LOG.jsonl`/SHA/trace/receipt、`render-html`/通知/`result-to-claim` 自动调用、无限循环与自证式 acquittal、固定 reviewer 模型与 `codex exec` 后端、跨 Workflow 自动 handoff；改为显式授权门（scope/写入范围/轮数/预算/副作用/停止条件）、有界修复、未授权补实验的显式处理、被拒绝编辑的日志与停止后不自动续轮。
