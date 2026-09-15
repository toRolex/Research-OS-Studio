# Systems Paper Writing 报告

这是 [Systems Paper Writing](../SKILL.md) 的自然 Markdown 报告骨架，不是机器 schema，也不替代候选稿与审查报告本身。按实际读到的原始材料填写；无法定位的项写 `unknown`，不要省略。被组合能力贡献对应章节，不另建重复主报告。

**Input / 材料范围**：[实际读取的路径]
**Venue**：[用户指定值；未指定写「未指定，不设默认 venue」]
**Venue 规则来源**：[当前官方 CFP／模板页 · 读取日期]
**稿件格式与构建入口**：[LaTeX／Markdown · 真实命令；无引擎／Markdown 时写实际降级状态]
**交付口径**：draft / submission-candidate（选择实际口径）
**Write scope**：[本次批准写入的文件／目录（含临时构建目录）；未确认项]
**Revision rounds**：[批准上限 vs 实际使用]
**Resources / budget**：[每轮可用资源与预算上限；付费渲染、AI 图像生成、远程写入或外部服务是否逐项获批]
**Style-ref**：[是否采用用户本地参考；读取范围；未采用原因]
**Independent review**：[独立 reviewer 是否实际执行；模型族隔离是否满足；未执行原因与影响]

## 系统证据面

| 证据类 | 状态 | 材料定位 | 缺口与最小补证动作 |
|---|---|---|---|
| 真实观测／生产数据 | 已有／部分／缺失 | | |
| Working prototype | 已有／部分／缺失 | | |
| End-to-end 对比 | 已有／部分／缺失 | | |
| Microbenchmark／ablation | 已有／部分／缺失 | | |
| Scalability | 已有／部分／缺失 | | |

- 缺失证据是否授权补做：[否／是（授权范围）]
- 依赖缺失证据的主张：[清单 · 已收窄到何范围／未进入就绪判定]

## 规划与验收契约

- Plan（如适用）：[路径 · 章节数 · Gap—Answer 映射 · 图表计划 · 未解决缺口]
- 验收契约：[status accepted／contested · 断言数 · 协商轮数 · `## Disputed` 原文（如有）]
- 契约断言核对：[逐条 satisfied／violated／disputed-at-negotiation；用户豁免记录]

## 系统结构自检

- Thesis（X 对处于环境 Z 的 Y 更好）：[原文]
- 贡献 C1–Cn 与 §N 映射：[清单]
- 每个主要设计决策的 alternatives：[决策 → 替代方案 → 未选原因；缺失项]
- 三处一致覆盖：[实验块 → 假设／结论／caption 是否一致]
- Related Work 分组：[方法组 → 本工作区别]
- 篇幅与当期 venue 规则：[符合／超出／未知]

## 图表

- 架构图：[图号 · 位置 · 结构源]
- 数据图：[图号 · 证据类（E2E／ablation／scalability）· 数据来源 · 源脚本 · caption]
- 比较表／示意图：[用途 · 性质标注]
- 手工图（未生成）：[清单与缺口]
- 灰度／可读性／风格一致：[核对结果]
- 未执行／工具缺失：[项与原因]

## 正文

- 章节：[清单 · 实际写入路径]
- 数字与结论追溯：[关键数字 → 原始结果文件定位]
- 缺口（未编造）：[缺失证据／引用／用户决定项]

## 编译

- 构建：[命令 · 实际退出码 · 错误原文与位置]
- PDF：[路径 · 页数 · 核验逐项结果]
- 未检查／未运行：[项与原因]
- 源码是否被本阶段修改：[否／仅在本 Workflow 授权修订内]

## 并列审查

| 审查 | 实际状态 | 结论与定位 | 缺口 |
|---|---|---|---|
| paper-claim-audit | 执行／不适用／未执行 | | |
| citation-audit | 执行／不适用／未执行 | | |
| proof-review | 执行／不适用／未执行 | | |
| claim-stress-test | 执行／不适用／未执行 | | |

- 未核实项与补证动作：
- 独立审查是否实际执行：[是／否；否时说明 `single-agent assessment; independent verification not performed`]

## 独立评审与修订轮次

| Round | Score | 关键弱点（CRITICAL／MAJOR／MINOR） | 已应用改动 | 复编译结果 |
|---|---|---|---|---|
| Round 0（基线） | | | — | |
| Round 1 | | | | |
| Round 2 | | | | |

- Reviewer 判据覆盖：novelty／significance／design／implementation／evaluation／clarity
- 每轮 PDF／稿件对照路径：
- 未应用的发现及原因：
- 命题／假设／结论范围变化：[无；如有，用户决定记录]

## 未解决项与停止

- 未完成／失败项：[状态 · 材料定位 · 最小下一步]
- 停止原因：[授权到期／轮数到限／预算耗尽／材料不足／关键证据缺口／用户要求停止／完成]
- 已写入清单 vs 批准清单：[一致／差异]
- 未启动的 Workflow（`paper-writing`、`ml-paper-writing`、`paper-compile-repair`、`apply-citation-fixes`、`proof-repair`、`rebuttal`、`resubmit-pipeline`、`paper-talk`、`research-improvement` 均未启动）：[实际逐项核对]
- User options：[接受候选稿 / 授权补做缺失证据后重跑 / 继续修订 / 显式调用专用修复入口 / 停止]

> 本报告只记录事实、审查发现与修订记录。编译成功与审查通过不证明系统论断成立、可投稿或已被接受；是否投稿、发布或接受由用户决定。
