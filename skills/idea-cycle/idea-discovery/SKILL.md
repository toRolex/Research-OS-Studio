---
name: idea-discovery
description: "从研究方向走完主动检索、多视角候选、查新、独立评审与固定边界收敛，交付发现报告与 Proposal。"
disable-model-invocation: true
---
<!-- argument-hint: "[研究方向；可附 brief 路径、参考论文、已有材料、入围候选上限、预算与输出位置]" -->

# Idea Discovery Workflow

用户显式调用的顶层 Workflow：在一次授权内组合已交付的 Idea Cycle 内部能力，走完 ARIS Discovery 主链，交付 **`IDEA_DISCOVERY.md`** 与 **`RESEARCH_PROPOSAL.md`**。

## 调用与授权
Gate: output-path | before=report-write | approval=explicit-user | source=SKILL.md#调用与授权

- **User** 决定研究方向、非目标、可选 brief 与参考论文、进入查新与评审的候选上限、总预算、检查点策略、输出位置，以及每一步是否继续。
- **Agent** 组织阶段、调用内部能力、核对每个阶段的真实返回，并把各章节合入单一权威报告；不代替内部能力裁决，不把它们的实质结论改写成摘要。
- **输入**：研究方向（一行描述或 brief），可选参考论文、已有文献／笔记／结果、失败记录，以及数据、算力、时间、venue 等约束。setup 与固定目录不是前置条件。
- **输出**：默认 `IDEA_DISCOVERY.md`（单一权威发现报告）与 `RESEARCH_PROPOSAL.md`（最终 Proposal）。路径由用户确认；目的文件已存在时先展示差异并保留原件。
- **写入范围**：仅本次获准的报告与 Proposal 路径。研究材料、原始候选、文献、代码、数据只读。默认不写统一 JSON、状态记录、门控输出、HTML、manifest 或来源认证材料。
- **资源范围**：只使用宿主已有且本次授权的能力。公开检索不授权上传未公开材料、付费服务、新凭据、远程写入或安装科研环境；缺工具时如实降级并保留缺口。
- **停止条件**：Proposal 交付即停止。pilot、`experiment-plan`、Validation、Writing 或其他顶层 Workflow 由用户另行点名；是否继续完全由用户决定。

**完成条件**：方向、材料实际读到范围、非目标、约束、总预算、输出路径与检查点策略均已明确，或逐项标为缺口；未知项不被默认值填满。

## 阶段检查点
Gate: stage-checkpoint | before=next-phase | approval=explicit-user | source=SKILL.md#阶段检查点

每个阶段结束设检查点：展示该阶段结果、当前淘汰与缺口、下一阶段拟调用的内部能力及剩余预算，然后默认停下，等用户选择**继续／调整／停止**。只有用户在调用时明确授权“一次走完并给出预算”才连续执行；即便如此，每个阶段仍以自身完成条件结束，用户确认记录写入报告，遇到换题、扩大授权或外部副作用时回到用户。不得把“无回复”当作继续授权。

## Phase 0：方向、brief 与参考论文

1. 读取项目中的研究 brief（可用 [brief 模板](templates/research-brief.md)），提取问题陈述、背景与已读文献、已尝试与失败记录、约束、目标类型、非目标与已有结果。同时给出一行方向时，brief 提供细节，方向界定范围。
2. 没有 brief 时，从用户方向提取同一组信息；关键约束不明则一次问一个必要问题，其余标为未知。
3. 给了参考论文（本地路径、URL 或 arXiv）时，用宿主已有能力读取可访问部分，记录：做了什么、关键结果、作者承认的局限与开放问题、可改进方向、对应代码库（如有）。找不到全文时保留缺口，不凭记忆补写。
4. 记录本次的能力授权、总预算、候选上限与检查点策略。

**完成条件**：方向、材料位置与读到范围、参考论文摘要（若给）、约束、非目标、预算、输出路径与检查点策略齐全或标缺口；参考论文未被误当作已核实证据。

## Phase 1：文献 Landscape（组合 `research-lit`）

以方向、已有材料与 brief 调用 `research-lit`，传 `composed: <IDEA_DISCOVERY.md>#文献 Landscape`。

**完成条件**：该章节已合入，或缺口已按 [组合说明](references/composition-notes.md) 记录；每个请求的来源都有实际结果；landscape 每条结论可追溯到已读材料或标为推断；覆盖缺口与未执行检索显式列出。

## Phase 2：候选生成与筛选（组合 `idea-generation`）

把同一组原材料、Phase 1 landscape 与固定边界交给 `idea-generation`，传 `composed: <IDEA_DISCOVERY.md>#候选池与筛选`。

**完成条件**：`#候选池与筛选` 已合入；每个已选视角都有候选或具名缺口；每个原始候选都有去向与依据；非重复可行池已交给 Phase 3。

## Phase 3：逐候选查新（组合 `novelty-check`）

对进入查新的每个候选调用 `novelty-check`，传 `composed: <IDEA_DISCOVERY.md>#查新结论`。

**完成条件**：`#查新结论` 已合入；每个入围候选都有 closest-work 比较或具名证据缺口；检索日志区分已尝试／成功／不可用；裁决与依据可追溯。

## Phase 4：独立评审（组合 `idea-review`）

把存活的原始候选、原始文献与查新材料交给 `idea-review`，传 `composed: <IDEA_DISCOVERY.md>#独立评审`。

**完成条件**：`#独立评审` 已合入；有实际评审返回及原文定位，或 REVIEW UNAVAILABLE 被明确记录；未解决问题未被共识抹去。

## Phase 4.5：固定边界收敛（组合 `idea-refinement`）

把存活候选、逐字 Problem Anchor、原始材料与 Phase 4 findings 交给 `idea-refinement`，明确授权它写入 `RESEARCH_PROPOSAL.md`，并传 `composed: <IDEA_DISCOVERY.md>#收敛与 Proposal`。

**完成条件**：`RESEARCH_PROPOSAL.md` 已写入获准路径，`#收敛与 Proposal` 已合入；Anchor 每轮保留、双路线取舍与未解决弱点可查。

## Phase 5：交付报告并停止

把各阶段章节合入 `IDEA_DISCOVERY.md`：执行摘要、方向与边界、文献 Landscape、候选池与筛选、查新结论、独立评审、收敛与 Proposal、淘汰与未解决问题、交付与停止。各章节内容原样合入，不改写内部能力的实质结论。

按 [报告模板](templates/discovery-report.md) 补全；确认每个章节存在或已标缺口，然后报告实际路径、失败的写入、未启动项（pilot、`experiment-plan`、Validation、Writing）与待用户决定事项。

**完成条件**：`IDEA_DISCOVERY.md` 与 `RESEARCH_PROPOSAL.md` 存在于获准路径或如实报告写入失败；报告只建议下一步。交付后按上方停止条件停下。

## 组合与降级

阶段到内部能力、canonical 章节的对照与缺口降级只见 [组合说明](references/composition-notes.md)。
