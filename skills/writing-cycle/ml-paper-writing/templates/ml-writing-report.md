# ML Paper Writing 报告

这是 [ML Paper Writing](../SKILL.md) 的自然 Markdown 报告骨架，不是机器 schema，也不替代候选稿与审查报告本身。按实际读到的原始材料填写；无法定位的项写 `unknown`，缺失的科学事实写可见缺口，不要省略。被组合能力贡献对应章节，不另建重复主报告。

**Input / 材料范围**：[实际读取的路径：结果表、日志、配置、代码、已有计划／稿件]
**Venue**：[用户指定值；未指定写「未指定，不设默认 venue，合规未核对」]
**稿件格式与构建入口**：[LaTeX／Markdown · 真实命令；无引擎／Markdown 时写实际降级状态]
**交付口径**：draft / submission-candidate（选择实际口径）
**Write scope**：[本次批准写入的文件／目录（含临时构建目录）；未确认项]
**Revision rounds**：[批准上限 vs 实际使用]
**Resources / budget**：[每轮可用资源与预算上限；付费渲染、AI 图像生成、远程写入或外部服务是否逐项获批]
**补实验**：不在本 Workflow 授权内；需补实验的 Claim 与最小下一步：[…]
**Style-ref**：[是否采用用户本地参考；读取范围；未采用原因]
**Independent review**：[独立 reviewer 是否实际执行；模型族隔离是否满足；未执行原因与影响]

## 规划与验收契约

- Plan（如适用）：[路径 · 章节数 · 图表计划 · 未解决缺口]
- 验收契约：[status accepted／contested · 断言数 · 协商轮数 · `## Disputed` 原文（如有）]
- ML 专属断言核对：[runs／seeds、误差量与方法、超参与选择、compute、Limitations、失败结果处理逐条 satisfied／violated／disputed]
- 契约断言核对：[逐条结果；用户豁免记录]

## 实验报告核对

| 实验／比较 | 支持的 Claim | runs／seeds | 不确定性量与方法 | 设置与划分 | compute | 状态 |
|---|---|---|---|---|---|---|
| | | | | | | 完整／缺口／单次运行 |

- 缺口标记与位置：[`[EVIDENCE NEEDED]`、`[SEED COUNT NEEDED]`、`[COMPUTE NEEDED]` 等 → 确切句子／表格单元／caption]
- baseline 与调参公平性：[匹配／不一致项及原文]
- 失败／无效／超时运行：[清单与处理方式]
- Limitations：[章节位置 · 点名的真实限制 · 与 headline Claim 的 scope 关系]

## 图表

- 数据图：[图号 · 数据来源 · 源脚本 · caption · 误差带定义]
- 示意图：[图号 · 性质标注 · 结构源]
- 手工图（未生成）：[清单与缺口]
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

- 每轮 PDF／稿件对照路径：
- 未应用的发现及原因：
- 命题／假设／结论范围变化：[无；如有，用户决定记录]

## venue 与投稿前清单

- 官方来源与访问日期：[author guide／CFP／style files／checklist URL + 日期；未知项]
- 适用项逐条：[满足／缺口／不适用及理由]
- 模板冲突与用户决定：[逐项]
- ethics／consent／license／disclosure：[由用户回答，不由本 Workflow 代答]

## 未解决项与停止

- 未完成／失败项：[状态 · 材料定位 · 最小下一步]
- 需要补实验的 Claim：[未授权，交用户决定]
- 停止原因：[授权到期／轮数到限／预算耗尽／材料不足／关键事实缺失／用户要求停止／完成]
- 已写入清单 vs 批准清单：[一致／差异]
- 未启动的 Workflow（`paper-writing`、`systems-paper-writing`、`paper-compile-repair`、`apply-citation-fixes`、`proof-repair`、`rebuttal`、`resubmit-pipeline`、`paper-talk`、跨研究改进循环均未启动）：[实际逐项核对]
- User options：[接受候选稿 / 继续修订 / 将需补实验的 Claim 交用户另行处理（如转交 `research-improvement`） / 显式调用专用修复或转投入口 / 停止]

> 本报告只记录事实、审查发现与修订记录。编译成功与审查通过不证明论文论断成立、可投稿或已被接受；是否投稿、发布或接受由用户决定。
