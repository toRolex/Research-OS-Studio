---
name: ml-paper-writing
description: 从已有 ML 研究材料交付会议候选稿与审查报告后停止；旧平行入口兼容。
disable-model-invocation: true
---
<!-- argument-hint: "[ML 研究材料／结果目录／计划／稿件路径] [venue、交付口径、写入范围与轮数]" -->

# ML Paper Writing

Gates: none

用户显式调用的 ML/AI 写作 Workflow。它是旧平行入口兼容层：新委托优先走 [paper-writing](../paper-writing/SKILL.md)，本入口继续可独立使用并继承同一委托。一次授权内交付候选稿与审查报告后停止。面向 NeurIPS／ICML／ICLR／ACL／AAAI／COLM 一类会议，不设默认 venue。阶段、能力与审查输入见 [composition-map](references/composition-map.md)。许可证见随包 [LICENSE](LICENSE)。

## 委托继承

写入范围、venue、交付口径、轮数、审查边界和资源额度来自[研究委托合同](../../general/research-os/references/mandate.md)。构建预算按同一累计编译次数执行：初次、失败、自产错误修复后、审查后和陈旧 PDF 纠正后的构建共用该预算，失败构建也计一次；展示已用次数、上限、剩余次数，耗尽时交付当前稿与未构建原因。没有确认的写入边界或付费调用时只做只读解析并形成执行草案；越权、预算或目标变化时停那一步，同一委托的其余工作继续。

**完成条件**：输入、venue 依据、格式与构建入口、交付口径、写入清单、轮数、审查边界与未决问题可逐项核对；没有用默认 venue、页数或预算填空。

## 2. 顺序

审查输入按 [composition-map](references/composition-map.md)：被调用的 audit skill 自己的输入契约，不在此另定。

1. **解析**：读原始 ML 材料并冻结范围。过门：输入清单、可改范围、venue 依据与歧义已列。失败：缺最小输入 → 请求后停。
2. **规划与验收契约**：调用 [paper-plan](../paper-plan/SKILL.md)。断言覆盖 [experiment-reporting.md](references/experiment-reporting.md)，不在此重列。第 3 轮仍被拒则标 `contested` 并交用户 tie-break。过门：计划与契约有文件，或有未采纳原因。失败：contested 且无裁决 → 停，不算 `submission-candidate`。
3. **实验报告**：先读 [experiment-reporting.md](references/experiment-reporting.md)。缺口用可见标记写在确切句子、表格或 caption。不跑实验。过门：每个拟写数字有原始定位或明确缺口。失败：材料没有的值保持缺口。
4. **图表**：调用 [academic-plotting](../academic-plotting/SKILL.md)。过门：每图有来源、源文件与 caption，或明确缺口。失败：缺数据或绘图能力 → 标缺口并停该图。
5. **起草**：调用 [paper-drafting](../paper-drafting/SKILL.md)。过门：授权章节为正文，数字可回溯，缺口留在原位。失败：核心来源冲突 → 停受影响章节。
6. **编译与委托内修复**：调用 [paper-compile](../paper-compile/SKILL.md)（check-only）。过门：有真实构建记录，或明确未运行。失败：错误在本次写入范围外 → 停受影响分支。范围内错误调用 `paper-compile-repair` 并继承委托授权修复，不要求再次独立点名。
7. **并列审查**：按 map 调用适用项。过门：每项有结论，或写明不适用／未执行。失败：缺原始结果记无法核实；缺独立能力记 `BLOCKED`；未关的证据／seed／compute 标记在，除非用户接受为剩余风险。
8. **评审与修订**：对照 [reviewer-expectations.md](references/reviewer-expectations.md)。只在授权范围内改，再调用 paper-compile。过门：每轮评审、清单、改动、复编译一一对应；最终 PDF 来自当前源码的获准成功构建，旧 PDF 不代替最新稿，未构建的修改不继承先前 PDF 审查。失败：命题、假设或结论范围变化 → 停交用户。轮数到、预算尽或连续两轮无新发现 → 停。
9. **venue**：指定时读 [venue-checklists.md](references/venue-checklists.md)，并按 [venue-and-format](../paper-drafting/references/venue-and-format.md) 核对当前官方规则。过门：每项有来源、不适用或未完成原因。失败：未指定 venue → 报告「venue 合规未核对」，不设默认会议。

## 3. 就绪

- `draft`：候选正文与审查报告即可。编译未运行不阻塞，须如实标注。
- `submission-candidate`：适用审查均已执行且未阻塞，有真实编译与 PDF，且实验报告缺口已关闭或被用户接受。任一缺失、失败、阻塞或契约 contested，不算就绪。仍不等于投稿或接受。

## 4. 报告与停止

按 [报告模板](templates/ml-writing-report.md) 交付。报告章节与实际材料、能力、写入一一对应。

停止：授权未确认、写入冲突、关键实验事实缺失且证据缺口未按委托处理、venue 或契约未决、编译修复超出授权、`submission-candidate` 缺审查或 PDF、需要未授权补实验、轮数或预算到顶、用户要求停止，或各阶段已完成。交付后停止，不自动投稿、不对外承诺，也不启动 `research-improvement`。证据缺口可在授权内补查或补分析；没有依据就保留缺口，不捏造。

**完成条件**：停止原因、已写与未写清单可核对。
