---
name: paper-writing
description: 从已有材料交付候选稿与审查报告后停止。
disable-model-invocation: true
---
<!-- argument-hint: "[研究材料／计划／稿件路径] [venue、交付口径、写入范围与轮数]" -->

# Paper Writing

Gates: none

用户显式调用。这是 writing-cycle 的统一写作入口：general、ML 和 Systems 材料都在本入口组织，专业规则按需读取。按材料主要贡献选择 general、ML/AI 或 Systems 专业分支；混合论文可并用对应参考。一次授权内组合内部能力，交付候选稿与审查报告后停止。阶段、能力与审查输入见 [composition-map](references/composition-map.md) 和 [专业资源索引](references/standards.md)。

## 委托继承

写入范围、venue、交付口径、轮数、审查边界和资源额度来自[研究委托合同](references/mandate.md)。构建预算按同一累计编译次数执行，失败构建也计一次；展示已用次数、上限与剩余次数，耗尽时交付当前稿与未构建原因。没有确认的写入边界或付费调用时只做只读解析并形成执行草案；越权、预算或目标变化时停那一步，同一委托的其余工作继续。ML/AI 与 Systems 专业标准按 [domain standards](references/standards.md) 按需读取；随本 Skill 安装的专业参考与来源许可均在 `references/` 和 `LICENSE-*.txt` 中。

**完成条件**：输入、venue 依据、格式与构建入口、交付口径、写入清单、轮数、审查边界与未决问题可逐项核对；没有用默认 venue、页数或预算填空。

## 单包安装与依赖

`paper-writing` 是组合入口，不是自包含的完整写作工具链。完整工作流需要通过可发现的 Skill slug 调用并安装其完整包（含被引用的专业参考）：`paper-plan`、`paper-drafting`、`paper-compile`、`paper-claim-audit`、`citation-audit`、`claim-stress-test`。按材料和阶段还需要 `academic-plotting`（含图表时）、`paper-compile-repair`（编译失败且修复在授权范围内时）、`apply-citation-fixes`（需要且获准修复引文时）及 `proof-review`（含定理、引理或证明时）。Systems／ML 专业分支所需的 `paper-plan`、`paper-drafting` 包内参考也属于依赖；仅安装本包不包含它们。`research-improvement` 是独立工作流，本入口明确不自动启动它。

缺少某阶段所需的 Skill slug 或参考资源时，只将受影响阶段标为 `blocked`，报告缺少项；其他已授权阶段可继续。单包安装不代表上述依赖齐全，不得声称已完成完整写作流程。

## 2. 顺序

审查输入按 [composition-map](references/composition-map.md)：被调用的 audit skill 自己的输入契约，不在此另定。

1. **规划与验收契约**：调用 [paper-plan](../paper-plan/SKILL.md)。写第一段前冻结可检查断言；争议按委托裁决规则处理，主要目标或结论范围改变时停该分支。过门：计划与契约有文件，或有未采纳原因。失败：关键材料冲突未决或无依据可核实 → 停受影响部分。
2. **图表**：调用 [academic-plotting](../academic-plotting/SKILL.md)。过门：每图有来源、源文件与 caption，或明确缺口。失败：缺数据或绘图能力 → 标缺口并停该图；该能力迁移与实现边界由票 #58 负责，本入口只指针引用。
3. **起草**：调用 [paper-drafting](../paper-drafting/SKILL.md)。过门：授权章节为正文，数字可回溯，缺口留在原位。遇到来源冲突或证据缺口，先在当前委托允许范围内补查或补分析；仅在仍无法解决或需改变目标/结论范围时暂停受影响部分。没有依据就保留缺口，不捏造。
4. **编译与委托内修复**：先调用 [paper-compile](../paper-compile/SKILL.md)（check-only）；错误属于本次写入范围时，调用 [paper-compile-repair](../paper-compile-repair/SKILL.md) 并继承委托授权修复，不要求再次独立点名。过门：有真实构建记录，或明确未运行；修复 diff、改动文件和复编译记录可核对。
5. **并列审查**：按 map 调用适用项。过门：每项有结论，或写明不适用／未执行。失败：缺原始结果记无法核实；缺独立能力记 `BLOCKED`。
6. **评审与修订**：fresh-context 评审后，只在授权范围内改，再调用 paper-compile。过门：每轮评审、清单、改动、复编译一一对应。失败：命题、假设或结论范围变化 → 停交用户。轮数到、预算尽或连续两轮无新发现 → 停。

## 3. 就绪

- `draft`：候选正文与审查报告即可。编译未运行不阻塞，须如实标注。
- `submission-candidate`：适用审查均已执行且未阻塞，并有真实编译与 PDF。任一缺失、失败、阻塞或契约 contested，不算就绪。仍不等于投稿或接受。

## 4. 报告与停止

按 [报告模板](templates/paper-writing-report.md) 交付。报告章节与实际材料、能力、写入一一对应。

停止：授权未确认、写入冲突、venue 或契约未决、编译修复超出授权、`submission-candidate` 缺审查或 PDF、轮数或预算到顶、用户要求停止，或各阶段已完成。交付后停止，不自动投稿、不对外承诺，也不启动跨研究改进循环。证据缺口在有效权限内处理；超出授权或没有依据时如实报告。

**完成条件**：停止原因、已写与未写清单可核对。
