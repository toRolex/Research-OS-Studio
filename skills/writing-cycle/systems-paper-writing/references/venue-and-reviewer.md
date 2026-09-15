# 系统会议 venue 与 reviewer 判据

供 [SKILL.md](../SKILL.md) 第 5、7、8 节使用：理解系统会议 reviewer 如何评价论文，以及投稿前必须现场核对哪些规则。改编自 Orchestra `systems-paper-writing/references/{systems-conferences,reviewer-guidelines}.md`，许可见共置 `LICENSE-Orchestra.txt`。

## 规则现场核对，不缓存

Venue 的页数、模板、deadline、track、匿名、AI 政策与 artifact evaluation 规则逐年变化。本文件只携带**检查对象**与方法，不携带可当作权威的年度数字。凡涉及规则，按用户指定 venue 读取**当前年度官方 CFP 与模板页**，记录来源与读取日期；用户模板与官方规则冲突时由用户决定。历史表格仅供理解差异，不用于判定合规。

核对清单（每项都要有当前来源）：

- 页限（正文／参考文献／camera-ready 是否分别计算）与格式模板（USENIX 或 ACM SIGPLAN）。
- 双盲要求：作者与单位去标识、系统名是否需与公开版本不同、自引是否用第三人称、致谢是否移除。
- track 选择（Research／Operational／Frontiers 等）与 track 专属评价标准。
- 提交与评审流程特性（见下）。
- 同时投稿限制、预印本与 prior tech report 政策。
- LLM／生成式 AI 使用披露政策；AI 是否可署名。
- artifact evaluation 是否提供、何时注册、材料范围。
- 模板与字体：图在黑白打印下可辨、PDF 无缺字、字号与文本块符合当期要求。

## 系统 reviewer 的核心判据

| 判据 | reviewer 看什么 |
|---|---|
| Novelty | 新的系统设计，而非增量改进 |
| Significance | 解决重要的实际问题 |
| System design | 架构合理、设计决策有依据 |
| Implementation | 可工作的原型，而非仅模拟或提案 |
| Evaluation | 真实负载、端到端表现，微基准只是补充 |
| Clarity | 写作清楚、可复现 |

## 流程特性对写作的影响

- **Introduction prescreening**：有的会议先只读 Introduction 判断 scope、可读性与 track 契合度。Introduction 必须自足，并在首段体现 track 专属标准。
- **Rapid review（如 ASPLOS 类流程）**：先只读前 2 页。前 2 页要能独立说清问题、方法与贡献。
- **Author response**：通常只允许纠正事实与回答提问，不允许新实验；写作时避免把关键论证留到 response。
- **Artifact evaluation**：可选但被鼓励；准备可复现产物，但本 Workflow 不代替其执行。
- **Operational／Frontiers track**：Operational 看重真实部署规模与教训，Frontiers 允许评价不完整但要有清晰愿景；这会改变证据门槛，由用户确认 track。

## ML 与系统评价的差异

| 维度 | ML／AI venue | 系统 venue |
|---|---|---|
| 评价焦点 | benchmark、ablation、metric | 真实负载下的端到端系统表现 |
| 实现 | 可选 | 期望可工作系统 |
| Novelty | 新方法／洞见 | 新系统设计／途径 |
| 论文核心 | 算法与实验 | 设计、实现与评价 |
| 页限 | 通常 7–9 页 | 通常 12 页（以当期 CFP 为准） |
| 模板 | venue `.sty` | USENIX `.sty` 或 ACM `acmart.cls` |
| 复现 | checklist | artifact evaluation（可选） |

## ML → 系统转写要点

从 ML 稿件改写为系统稿件不是换模板：

- 用 Design 取代 Methods，突出架构与 trade-off；Implementation 成为核心贡献而非附注。
- 从「算法 novelty」重构为「系统设计与实现贡献」。
- 补真实负载的端到端评价与系统级 metric，微基准作为补充。
- 补部署经验或真实适用性讨论；无部署则如实说明边界。

## 系统 reviewer 的常见质疑与预防

| 质疑 | 预防 |
|---|---|
| 「这是 ML 论文，不是系统论文」 | 强调系统设计、架构决策与部署挑战 |
| 「只有微基准」 | 补真实负载的端到端评价；无法补则记 gap |
| 「没有可工作原型」 | 构建并测量真实系统，不只模拟 |
| 「部署不现实」 | 展示真实适用性并讨论实际约束 |
| 「与系统社区无关」 | 用系统术语陈述贡献，引用系统文献 |
| 「未推进 arch／PL／OS 核心」 | 显式说明对核心学科的推进 |

## 学术诚信与披露

- 不编造 venue 规则；每条规则引用当前官方来源。
- 不生成凭空引用；未核实标 `[CITATION NEEDED]`，交由 `citation-audit`。
- 按当前 CFP 决定是否需要披露 LLM 辅助写作／构思；披露要求以官方规则为准，本文件不代替。
- 结构上受某论文启发的 pattern 要标注来源，但不复制其段落文字。

## 官方资源入口

- USENIX 投稿与模板资源：<https://www.usenix.org/conferences/author-resources>
- ACM 会议模板：<https://www.acm.org/publications/proceedings-template>
- 各会议当前 CFP 以会议官网当年页面为准（OSDI、NSDI、SOSP、ASPLOS、EuroSys）。
