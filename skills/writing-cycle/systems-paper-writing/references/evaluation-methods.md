# 系统评价方法与证据缺口

供 [SKILL.md](../SKILL.md) 第 5 节使用：判断系统论文的评价面是否完整、公平、可复现，并给出缺失证据时的正确处理。改编自 Orchestra `systems-paper-writing/references/{section-blueprints,checklist,reviewer-guidelines}.md`，许可见共置 `LICENSE-Orchestra.txt`。

## 系统证据面

系统论文的评价面由三类证据构成；它们回答不同问题，不能互相替代：

| 证据类 | 回答的问题 | 缺失时的后果 |
|---|---|---|
| **End-to-end** | 真实负载下整个系统的表现是否更好 | 只有微基准时不能宣称系统整体更优 |
| **Microbenchmark／Ablation** | 哪个设计决策带来哪部分收益 | 无法证明收益来自设计而非偶然 |
| **Scalability** | 规模维度增大时行为是否成立 | 不能宣称「大规模下仍有效」 |

判断每类时逐项核对：

- **End-to-end**：真实负载（不是 toy）与忠实 baseline 的对比；metric 是延迟、吞吐、成本、能耗等系统级目标；配置对所有系统一致。
- **Microbenchmark／Ablation**：每个主要设计决策都有单独隔离的测量；ablation 说明移除该组件后的影响，而不是只展示整体最优。
- **Scalability**：随 CPU 核数、节点数、集群规模、负载或数据量增加的行为；给出趋势与拐点解释，不把单点当成趋势。

## Baseline 公平性

- baseline 是当前 state-of-the-art，不是易打的 straw man。
- baseline 经过调优并在相同硬件、软件版本与配置下运行；默认未调优的对比无效。
- 报告每个系统的关键参数；不一致的参数要显式说明原因。
- 说明为什么选择这些 baseline，以及遗漏了哪些可能更强的对比。

## 测量与统计

- 排除 warmup；说明测量窗口与重复次数。
- 有不确定性：error bars、confidence interval 或多次运行，而不是单次运行。
- 选择偏差：说明结果选择标准；不隐藏不利 seed、配置或负载。
- 多重比较：比较多个配置时说明是否校正，或明确标为探索性。
- 同时给出绝对值与相对值，避免只给容易夸大的百分比。

## 结果呈现

- 每条实验结论在 **三处一致**：段首假设、段尾结论、图 caption。
- 不利、失败、不确定结果照实保留在表或正文中，不只报告最好结果。
- 解释与观测分离：先陈述数字与图表，再给设计关联，不把因果归因写成既成事实。
- 失败模式、边界条件、threat model 与 limitations 显式写出。

## 可复现性

- 说明 source 可得性（或计划），关键超参与配置值列出。
- 负载生成方式或 trace 来源写清；使用真实 trace 时标注出处与匿名化处理。
- 细节程度以「独立团队可在约两周内复现」为标准。

## 证据缺失时的处理

**任何缺失证据都记为 gap，不补造、不插值、不外推。** 是否补做由用户另行授权；本 Workflow 不运行实验、不部署、不申请资源。

| 缺失项 | 记录方式 | 对交付口径的影响 |
|---|---|---|
| Scalability 证据 | 在计划、契约核对与报告缺口清单中显式标 `MISSING SCALABILITY EVIDENCE`；说明已测规模与未测规模 | 依赖扩展性的 headline 不能进入 `submission-candidate` 就绪判定 |
| End-to-end（只有 microbenchmark） | 标为 evidence gap；不把微基准结论升级为系统结论 | 系统整体表现宣称不就绪 |
| 无 working prototype | 说明是设计提议而非已实现系统；Reality 维度判弱 | 系统论文的核心贡献不就绪 |
| 无 ablation | 说明哪些设计决策未被单独验证 | 收益归因主张降级为假设 |
| 缺独立 reviewer | 标 `single-agent assessment; independent verification not performed` | `submission-candidate` 不就绪 |

允许的处理：把主张收窄到证据实际支持的范围、在 Limitations 记录缺口、向用户给出最小补证动作。不允许的处理：编造规模曲线、用其他规模数字外推、把「未测」写成「符合预期」、或悄悄启动实验。

## 六维自检（Levin & Redell）

每条用一句话回答；任一维薄弱就在投稿前修正：

1. **Original Ideas**：真正新的是什么？
2. **Reality**：系统真的被实现并测量了吗？
3. **Lessons**：别人能从中学到什么？
4. **Choices**：每个主要决策都讨论了替代方案吗？
5. **Context**：相关工作是否公平完整？
6. **Presentation**：非本子领域读者能理解吗？

## 常见评价陷阱

| 陷阱 | 检查动作 |
|---|---|
| 把最佳 seed／最佳配置当均值 | 核对聚合口径与原始结果 |
| 相对提升算错或选择性呈现 | 重算 delta 与基数 |
| 不同配置被当作公平比较 | 核对所有系统参数一致 |
| caption 夸大正文未建立的结论 | 逐 caption 对照图与正文 |
| 实验范围被写成普遍结论 | 核对负载、规模与环境覆盖面 |
