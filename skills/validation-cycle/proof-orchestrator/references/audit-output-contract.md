# 证明审计输出约定

用于 `<本轮目录>/audit.md`；用户结论写入自然 Markdown 的 `report.md`。聊天版可更短，但保留相同判决和问题语义。以下字段描述证据，不是运行状态机；本轮只覆盖一个有界 obligation，不给出科研验收结论。

分类、严重度及检查依据见[证明审计准则](proof-audit-rubric.md)；独立性核验见[独立意见](independent-review.md)；触发符号检查时附[固定七行计分表](notation-audit.md)。

## Markdown 完整内容

```md
# 证明审计

Target: <本轮目标、文件、章节及边界>
Verdict: PASS | WARN | FAIL | BLOCKED | NOT_APPLICABLE | ERROR
Claim status: PROVABLE AS STATED | PROVABLE AFTER WEAKENING / EXTRA ASSUMPTION | NOT CURRENTLY JUSTIFIED
Reviewer route: <实际路线；未调用则写未调用>
Reviewer model: <经核实的实际模型；未知写 unknown>

## 命题重述

<明确假设、量词、参数定义域、极限次序、常数依赖及结论>

## 子目标检查

| ID | 子目标 | 位置 | 核查结果 | 依据或缺口 |
|----|--------|------|----------|------------|

## 自查

<执行器实际检查的推导、引用前提及结论；区别已证明、引用、猜想、修订后和无支持的陈述>

## 独立意见

<是否请求、是否取得、实际路线/模型及身份依据；未取得则直说>
<执行器模型家族；审查者模型家族；cross-family / same-family / none / unknown>
<审查者原始判决及原始意见位置；逐项列本地验证、争议和未解决项>

## 问题

| ID | 严重度 | 分类 | 位置 | 摘要 | 最小修复 |
|----|--------|------|------|------|----------|

<按下节展开每个严重问题>

## 反例检查

<全部尝试、已验证反例或候选；候选的待核查内容>

## 建议修复

<最小诚实修复：补推导、加假设、弱化命题、补引用并核对前提、拆分引理>

## 剩余风险

<未检查事项、仍依赖的外部材料、缺失来源、范围限制>
```

## 问题记录

每个严重问题保留全部字段：

```md
### I<n>：<短标题>

- Severity: FATAL | CRITICAL | MAJOR | MINOR
- Category: <17 类分类标签之一>
- Status: INVALID | UNJUSTIFIED | UNDERSTATED | OVERSTATED | UNCLEAR
- Impact: GLOBAL | LOCAL | COSMETIC
- Location: <文件:行号或章节/明确步骤>
- Claimed step: <证明声称什么>
- Problem: <为什么推不出>
- Counterexample: YES | NO | CANDIDATE；<细节及核验>
- Downstream effect: <哪些后续结果失效>
- Minimal repair: <补推导 / 加假设 / 弱化结论 / 引用结果并验证条件>
```

这里的 Status 描述数学问题性质，不驱动阶段迁移。轻微问题可保留在表内；所有 FATAL、CRITICAL、MAJOR 必须展开，避免缺失影响和修复依据。

## 判决映射

- `NOT_APPLICABLE`：输入无定理、引理、命题、推论或证明内容。
- `BLOCKED`：必需来源不可读、缺失，或所请求审查因路线/授权不足无法完成；注明究竟阻断哪一部分，不抹去已经完成的自查。
- `PASS`：当前范围全部证明子目标均已落实。
- `WARN`：仅轻微问题，或主要问题已有明确依据说明主结论仍成立。
- `FAIL`：存在致命或关键问题，或可能影响主结论的主要问题。
- `ERROR`：审查工具或过程故障；不能解释为数学判决。

`PROVABLE AFTER WEAKENING / EXTRA ASSUMPTION` 只能用于已展示相应修订证明的情况；仅提出修复建议时仍为 `NOT CURRENTLY JUSTIFIED`。原命题与建议修订版分列，不能静默更换前提或结论。

## 独立性及异议

独立性从实际身份推导，不靠路线名称或提示文字自报：实际核实的模型家族与执行器不同才写 `cross-family`，相同写 `same-family`；执行器自查写 `none`；身份或家族未核实写 `unknown`。跨家族也只是附加证据，不保证数学正确。

保留审查者原始判决；执行器的本地验证另写，不改写原始负面意见为认可。严重问题可以有证据地标为争议，未核验反例可以降为候选，但未解决的外部 FATAL/CRITICAL 不得被隐藏为干净的 PASS。应呈现具体争议与未解决影响。

用户可选择停止追查或豁免后续处理；豁免不使命题成立，不消除证据缺口，也不把审查意见变成证明。报告同时写明用户决定和仍未解决的数学问题。

## 完成条件

命题边界、全部子目标、九项检查、判决依据、严重问题字段、反例及风险齐全；自查与独立意见清楚分开；未完成工作如实标注。本地结果直接依本约定写 `report.md`，仅在收到外部答案时读取[回传审计模板](dispatch-prompts.md)。报告说明当前结论、证据、缺口和可选下一步，不把流程完成包装成证明成功。
