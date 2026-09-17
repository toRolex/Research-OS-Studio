---
name: idea-discovery
description: "从研究方向走完主动检索、多视角候选、查新、独立评审与固定边界收敛，交付发现报告与 Proposal 后停止。用户显式调用；不运行 pilot、实验计划、Validation 或 Writing。"
disable-model-invocation: true
---
<!-- argument-hint: "[研究方向；可附 brief 路径、参考论文、已有材料、入围候选上限、预算与输出位置]" -->

# Idea Discovery Workflow

用户显式调用的顶层 Workflow：在一次授权内组合已交付的 Idea Cycle 内部能力，走完 ARIS Discovery 主链，交付 **`IDEA_DISCOVERY.md`** 与 **`RESEARCH_PROPOSAL.md`** 后停止。不运行 pilot，不制定实验计划，不进入 Validation 或 Writing。Orchestra 构思框架通过已交付的 `idea-generation` 与 `creative-thinking-for-research` 进入候选发散，不另造薄弱流程。

## 调用与授权

- **User** 决定研究方向、非目标、可选 brief 与参考论文、进入查新与评审的候选上限、总预算、检查点策略、输出位置，以及每一步是否继续。
- **Agent** 组织阶段、调用内部能力、核对每个阶段的真实返回，并把各章节合入单一权威报告；不代替内部能力裁决，不把它们的实质结论改写成摘要。
- **输入**：研究方向（一行描述或 brief），可选参考论文、已有文献／笔记／结果、失败记录，以及数据、算力、时间、venue 等约束。setup 与固定目录不是前置条件。
- **输出**：默认 `IDEA_DISCOVERY.md`（单一权威发现报告）与 `RESEARCH_PROPOSAL.md`（最终 Proposal）。路径由用户确认；目的文件已存在时先展示差异并保留原件。
- **写入范围**：仅本次获准的报告与 Proposal 路径。研究材料、原始候选、文献、代码、数据只读。默认不写统一 JSON、状态记录、门控输出、HTML、manifest 或来源认证材料。
- **资源范围**：只使用宿主已有且本次授权的能力。公开检索不授权上传未公开材料、付费服务、新凭据、远程写入或安装科研环境；缺工具时如实降级并保留缺口。
- **停止条件**：Proposal 交付即停止。不启动 pilot、`experiment-plan`、Validation、Writing 或其他顶层 Workflow；是否继续完全由用户决定。

**完成条件**：方向、材料实际读到范围、非目标、约束、总预算、输出路径与检查点策略均已明确，或逐项标为缺口；未知项不被默认值填满。

## 阶段检查点

每个阶段结束设检查点：展示该阶段结果、当前淘汰与缺口、下一阶段拟调用的内部能力及剩余预算，然后默认停下，等用户选择**继续／调整／停止**。只有用户在调用时明确授权“一次走完并给出预算”才连续执行；即便如此，每个阶段仍以自身完成条件结束，用户确认记录写入报告，遇到换题、扩大授权或外部副作用时回到用户。不得把“无回复”当作继续授权。

## Phase 0：方向、brief 与参考论文

1. 读取项目中的研究 brief（可用 [brief 模板](templates/research-brief.md)），提取问题陈述、背景与已读文献、已尝试与失败记录、约束、目标类型、非目标与已有结果。同时给出一行方向时，brief 提供细节，方向界定范围。
2. 没有 brief 时，从用户方向提取同一组信息；关键约束不明则一次问一个必要问题，其余标为未知。
3. 给了参考论文（本地路径、URL 或 arXiv）时，用宿主已有能力读取可访问部分，记录：做了什么、关键结果、作者承认的局限与开放问题、可改进方向、对应代码库（如有）。找不到全文时保留缺口，不凭记忆补写。
4. 记录本次的能力授权、总预算、候选上限与检查点策略。

**完成条件**：方向、材料位置与读到范围、参考论文摘要（若给）、约束、非目标、预算、输出路径与检查点策略齐全或标缺口；参考论文未被误当作已核实证据。

## Phase 1：文献 Landscape（组合 `research-lit`）

以方向、已有材料与 brief 调用 `research-lit`，传 `composed: <IDEA_DISCOVERY.md>#文献 Landscape`，由它执行实际检索、来源核实与综合。

- 保留它的候选／已核实／未核实标签、阅读深度、检索日志与覆盖缺口；未核实材料不承载无保留结论。
- 有检索能力时必须有真实查询，不能接受空 queries 计划。无可用检索能力时按 supplied-material synthesis 继续，把覆盖范围限定为已供材料。
- 无任何可用证据时，接收覆盖／缺口报告并**停止本阶段的综合**，不推断“无文献存在”。

**完成条件**：每个请求的来源都有实际结果；landscape 每条结论可追溯到已读材料或标为推断；覆盖缺口与未执行检索显式列出。

## Phase 2：候选生成与筛选（组合 `idea-generation`）

把同一组原材料、Phase 1 landscape 与固定边界交给 `idea-generation`，传 `composed: <IDEA_DISCOVERY.md>#候选池与筛选`。保留其 fan-out 与筛选方法。

- 宿主与授权允许时按视角并行 fan-out；否则顺序执行并如实标注“单上下文顺序生成”，不声称独立模型。
- 卡住时可在生成职责内使用已安装的 `creative-thinking-for-research`（Orchestra 认知方法）；未安装时五视角与共置框架仍可完成本轮，不自动安装。
- 保留完整原始候选池与每个候选的去向（保留／合并／暂存）及具体理由；只有已知事实违反用户硬约束才暂存，不用“不够有趣”“已经有人做过”淘汰。
- 按用户候选上限挑出进入查新的非重复可行池；排序只用用户指定的客观字段，不暗示科学价值排名。

**完成条件**：每个已选视角都有候选或具名缺口；每个原始候选都有去向与依据；非重复可行池已交给 Phase 3，生成者未作独立评审。

## Phase 3：逐候选查新（组合 `novelty-check`）

对进入查新的每个候选调用 `novelty-check`，传 `composed: <IDEA_DISCOVERY.md>#查新结论`；授权与宿主允许时可并行。它直接读原始候选而非生成者摘要，围绕核心 Claim 主动检索 closest prior work。

- 保留 Claim → 具体位置 → 重叠 → 关键区别 → 未知 的比较、来源核实与检索日志。
- 裁决为 PROCEED／PROCEED WITH CAUTION／ABANDON／EVIDENCE GAP；**ABANDON 必须点名具体已发表工作**，不因模糊相似误杀。
- 有独立复核能力时按 `novelty-check` 的 Phase C 做一次只读独立核实；否则标 **single-agent assessment; independent verification not performed**。
- 被近邻覆盖的候选如实淘汰并保留理由；EVIDENCE GAP 给出最小补证动作，不永久 inconclusive。

**完成条件**：每个入围候选都有 closest-work 比较或具名证据缺口；检索日志区分已尝试／成功／不可用；裁决与依据可追溯。

## Phase 4：独立评审（组合 `idea-review`）

把存活的原始候选、原始文献与查新材料交给 `idea-review`，传 `composed: <IDEA_DISCOVERY.md>#独立评审`。评审者直接从原始材料形成裁决，生成者自查、回顾性 reflection 或生成者排名都不能替代。

- 无独立评审者或原文不可达时，标 **REVIEW UNAVAILABLE / EVIDENCE GAP**，交付已完成部分并停止裁决；不伪造评审返回。
- 保留 findings 的原文定位、逐轮回应、裁决依据、条件性 Claim 矩阵与未解决问题；裁决只是建议。

**完成条件**：有实际评审返回及原文定位，或 REVIEW UNAVAILABLE 被明确记录；未解决问题未被共识抹去。

## Phase 4.5：固定边界收敛（组合 `idea-refinement`）

把存活候选、逐字 Problem Anchor、原始材料与 Phase 4 findings 交给 `idea-refinement`，明确授权它写入 `RESEARCH_PROPOSAL.md`，并传 `composed: <IDEA_DISCOVERY.md>#收敛与 Proposal`。

- Anchor 逐字保留；改变问题、目标人群、成功标准或预算视为 drift，回到用户决定，不偷偷换题。
- 比较最小可行与前沿路线，给出选用与舍弃理由；最多五轮“修订—独立复核”，无进展或预算耗尽即停。
- **不制定实验计划与 tracker**；1–3 个 Claim 驱动验证草图只保留在 Proposal 内，且明确未执行。
- 报告只链接最终 Proposal，不复制其同义全文；逐轮修订记录并入 `#收敛与 Proposal` 章节。

**完成条件**：`RESEARCH_PROPOSAL.md` 已写入获准路径，Anchor 每轮保留、双路线取舍与未解决弱点可查；未启动任何实验。

## Phase 5：交付报告并停止

把各阶段章节合入 `IDEA_DISCOVERY.md`：执行摘要、方向与边界、文献 Landscape、候选池与筛选、查新结论、独立评审、收敛与 Proposal、淘汰与未解决问题、交付与停止。各章节内容原样合入，不改写内部能力的实质结论。

按 [报告模板](templates/discovery-report.md) 补全；确认每个章节存在或已标缺口，然后报告实际路径、失败的写入、未启动项（pilot、`experiment-plan`、Validation、Writing）与待用户决定事项。

**完成条件**：`IDEA_DISCOVERY.md` 与 `RESEARCH_PROPOSAL.md` 存在于获准路径或如实报告写入失败；报告只建议下一步，不自动启动另一顶层 Workflow。交付后停止。

## 组合与降级

阶段到内部能力、canonical 章节的对照与缺口降级见共置 [组合说明](references/composition-notes.md)。要点：

- 各内部能力只在本阶段职责内工作，支持 standalone／composed；路径存在本身不是 composed 信号，必须显式传 `composed:`。
- 任一能力缺失或返回不可用时，按 `references/composition-notes.md` 的降级规则保留缺口并停止该类型工作，不用生成者自查或模型共识顶替。

## 禁止事项

- 不运行 pilot、不设 GPU／时长／轮数 pilot 常量、不调用 `experiment-plan`、不产出实验计划或 tracker。
- 不启动 Validation、Writing、`run-experiment`、`experiment-bridge` 或其他顶层 Workflow。
- 不写统一 JSON、状态机记录、门控脚本输出、HTML 渲染、manifest、SHA/digest/receipt 或来源认证材料。
- 不覆盖研究材料与已有报告，不安装科研环境，不上传未公开材料，不做付费或远程写入、投稿、发布或 Git push。

## 来源

主链改编自 ARIS／wanshuiyin `skills/idea-discovery/SKILL.md`，revision `0472e530251cdbd3364c33b110063c58f819edd7`：保留 Phase 0 brief、Phase 0.5 参考论文、Phase 1–4.5 组合顺序、逐候选查新、独立评审、固定 Problem Anchor 收敛、单一权威交付物与阶段性淘汰记录；删除 pilot 与 GPU 预算、`AUTO_PROCEED` 自动推进、实验计划、`run_state`/证据门、HTML 渲染、provider/MCP 与跨主流程调用。Orchestra 构思框架经已交付的 `idea-generation`、`creative-thinking-for-research` 进入发散。版权与完整许可见 [ARIS MIT](LICENSE)；来源版本、作者与采用范围集中记录于仓库来源说明，使用本 Skill 无需访问上游或产品仓库。
