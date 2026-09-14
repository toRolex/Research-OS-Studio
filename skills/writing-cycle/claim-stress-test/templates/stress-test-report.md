# 裁决规则与报告模板

在 SKILL 第 4 步使用。先核对审查是否有效完成，再机械映射分类；执行者不重新作论文质量判断。

## 未完成分支

按顺序取首个适用项；保留原始发现，不把未完成改成成功。

1. 实际 reviewer 调用失败、输出截断/无效（漏指控、标签/严重度非法、计数矛盾、证据说明缺失等）或报告交付失败：`ERROR`，记录具体阶段与可用结果。
2. fresh 独立审查能力不可用，或原材料缺失/不可读导致无法完整评估整篇攻击：`BLOCKED`，列必需补充项。没有 PDF 但源文件完整可读不构成本条件。
3. 已实际检查完整授权稿件，确认没有理论性主张或 scope/generality Claim：`NOT_APPLICABLE`，记录检测依据。
4. 两个 reviewer 均完成、原子点分类与覆盖完整：使用下表。若审查开始后才发现核心材料不可用，仍回到 BLOCKED，而不是从不完整分类推出 PASS。

## 有效完成后的互斥裁决表

`U` 是 still_unresolved 点集合，`P` 是 partially_answered 点集合。answered_by_current_text 的严重度不影响裁决。每个有效非空分类组合只命中一行；执行者按实际条目计数，不采用裁决者自行宣告的顶层结果。

| 完整条件 | 裁决 | 理由 |
|---|---|---|
| U 中至少一个 critical | `FAIL` | unresolved_critical |
| U 非空，且 U 中无 critical（P 任意） | `WARN` | unresolved_major_or_minor |
| U 为空，且 P 中至少一个 major 或 critical | `WARN` | partial_major_or_critical |
| U 为空，P 非空，且 P 全是 minor | `PASS` | defense_survives_with_minor_partial_only |
| U 为空，P 为空（全部 answered） | `PASS` | defense_survives |

注意单个 partially_answered major 也只能 WARN；多个 partial major、partial critical 同样 WARN。任何 still_unresolved 都不能 PASS；unresolved critical 与任意 partial 组合仍 FAIL。PASS-with-minor-partial 仍必须列出残余问题，不等于完全无问题。

---

# Claim Stress Test Report — 论文标题

- 日期、原稿范围、是否暂定稿、是否仅源文：
- standalone / composed；报告目标：
- 执行者、攻击 reviewer、裁决 reviewer 的实际可知身份与来源：
- fresh 隔离方式与未知能力项：
- Verdict：PASS / WARN / FAIL / NOT_APPLICABLE / BLOCKED / ERROR
- 映射命中行与理由（或未完成原因）：

## 输入与实际覆盖

列稿件/附录/宏/证明/图表/原始支撑路径、两位 reviewer 实际读取情况、未读或缺失原因；可选六轴分支记录额外范围及完成情况。

## Net assessment

裁决者原文。不以执行者的乐观总结替换。

## Attack memo（逐字）

完整单段英文 memo，记录实际词数；尚无有效攻击时如实说明，不能补造。

## Adjudication（逐点，保留全文）

### Point P_n：短标签

- Attack claim：具体指控
- Verdict：answered_by_current_text / partially_answered / still_unresolved
- Evidence (or lack of)：原文件定位与解释
- Severity if unresolved：critical / major / minor
- If unresolved, recommended fix：具体建议

重复至覆盖全部原子点；附总点数 N、三类计数 X/Y/Z、未解决 critical 名称和 partial 的严重度分布。实际不足三点须带 reviewer 解释。

## Top action items（优先顺序，最多三项）

引用裁决者建议，区分研究级 open problem/限制与写作级范围修正，注明尚未实施。有意立场的可持续性判断也保留。

## 独立审查原始记录

保留实际攻击/裁决任务正文、完整路径清单、两位 reviewer 的完整回复和失败说明；扩展分支附六个原始探测及合成任务/回复。composed 放进父报告同一节或附录，不仅转述结果。没有实际调用的阶段写未执行。

## 停止说明

本次只输出攻击、裁决与建议；稿件和研究证据未改，未调用其他审计/Workflow。PASS 仅意味着这条攻击未击倒当前稿件，不代表数字/引用/证明专项通过、科研正确或已获接受。
