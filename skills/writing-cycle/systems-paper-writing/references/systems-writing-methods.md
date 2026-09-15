# 系统论文写作方法

Writer 侧的系统论文逐节执行方法，供 [SKILL.md](../SKILL.md) 第 4 节使用。规划槽位（尚未填写的 outline worksheet）在 [paper-plan 的 systems-blueprints](../../paper-plan/references/systems-blueprints.md) 与 [systems-patterns](../../paper-plan/references/systems-patterns.md)——本文件负责把已有材料写成稿，不重复规划模板。

改编自 Orchestra `systems-paper-writing`（`SKILL.md`、`references/section-blueprints.md`、`references/writing-patterns.md`、`references/checklist.md`）与 ARIS `writing-systems-papers`，许可见共置 `LICENSE-Orchestra.txt`／`LICENSE-ARIS.txt`；采用边界记录在仓库 `docs/upstream-sources-and-licenses.md`。所有页数区间为历史示例，投稿前现场核对当前官方 CFP。

## 目录与篇幅

典型 10–12 页系统论文的分配（示例，按当前 venue 规则调整）：

| 章节 | 页数 | 内容职责 |
|---|---|---|
| Abstract | ~0.25 | 150–250 词，5 句 |
| S1 Introduction | 1.5–2 | 问题 → Gap → 洞见 → 贡献 |
| S2 Background & Motivation | 1–1.5 | 术语 + 观测 |
| S3 Design | 3–4 | 架构 + 模块 + alternatives |
| S4 Implementation | 0.5–1 | 原型、LOC、关键工程决策 |
| S5 Evaluation | 3–4 | setup + end-to-end + microbenchmark／ablation + scalability |
| S6 Related Work | 1 | 按方法分组，显式比较 |
| S7 Conclusion | 0.5 | 3 句 |

章节顺序是系统论文的成熟结构，不因篇幅紧张而删除 Design 或 Evaluation 的实质内容；压缩先从 Implementation 与 Related Work 的冗余开始。

## 结构模式选择

动笔前先定一个 governing pattern，它决定 Introduction 与 Design 的骨架；四个成熟模式的完整框架、选择表与反模式在 [systems-patterns](../../paper-plan/references/systems-patterns.md)，此处只列选择依据：

| 情况 | 模式 | 作用 |
|---|---|---|
| 能枚举现有系统的具体缺陷 | Gap Analysis（G1–Gn → A1–An → 逐对实验） | 形成可追溯的 gap—answer 契约 |
| 有生产数据、trace 或实测 | Observation-Driven（O1–On → 洞见 → 组件） | 把动机锚在可检查的证据上 |
| 有多个跨技术面的贡献 | Contribution List（编号 + §N） | 审稿人可计数核对 |
| 有一个强比较性主张 | Thesis Formula（X 对处于环境 Z 的 Y 更好） | 全篇服务一个可记结论 |

Thesis 公式是可组合的顶层结构，可与其余三种叠加。反模式（feature dump、先方案后问题、含糊贡献、缺 alternatives）在动笔时逐条回避。

## Abstract（5 句）

```text
S1 背景与重要性：问题领域是什么，为什么重要。
S2 缺口：现有方法的具体局限。
S3 Thesis：「X 对处于环境 Z 的 Y 更好」（Irene Zhang 公式）。
S4 方法摘要与 headline 结果：只写证据支持的数字。
S5 影响或可得性：开源、部署或后续价值。
```

- 摘要必须自包含：不使用正文才定义的术语，不前置引用（Gernot Heiser）。
- thesis 句是审稿人最可能引用的一句，必须能独立成立。
- 没有部署或开源事实时，S5 改为真实的适用场景，不编造部署与获奖。

## S1 Introduction（1.5–2 页）

1. **问题**（~0.5 页）：点明领域与规模、成本、延迟等具体数字，说明为什么真实。
2. **Gap 分析**（~0.5 页）：列出 G1–Gn，每项一句、可被证据检验；用现有系统的假设或失败条件支撑。
3. **关键洞见**（1 段）：Thesis 句 + 系统名 + 一句差异化描述。
4. **贡献**（~0.5 页）：3–5 条编号、可检验的贡献，每条带 §N 交叉引用。

写作动作按 territory→niche→occupy 三步（CARS 结构）推进：建立领域 → 指出缺口 → 占据缺口。每个 Gap 都必须能追到正文里的回答与实验，否则删除或标为未解决。

## S2 Background & Motivation（1–1.5 页）

1. **技术背景**（~0.5 页）：只写理解贡献所需的最小集合，逐词 define-before-use；术语超过 0.5 页说明读者定位有问题。
2. **观测**（~0.5–1 页）：O1–O3，每条给出数据图／表来源；严格区分观测、解释与设计推论。观测必须来自真实轨迹或测量，采样与覆盖范围的局限显式写出。

每个观测下方写一句设计推论，并在 Design 中回指「Motivated by O1（§2）」；没有观测支撑的动机写成假设而不是事实。

## S3 Design：design rationale 与 alternatives（3–4 页）

1. **架构总览**（~0.5 页）：先画架构图，再逐组件一句话职责与一次典型请求／数据流走查。架构图就是本节的 page-one figure。
2. **逐模块设计**（~2–2.5 页）：每个模块写清「解决什么问题」→「选了什么、为什么」→「考虑了哪些替代方案、各自的 trade-off」→「机制如何工作」。
3. **设计取舍汇总**（~0.5–1 页）：复杂系统用决策表固定回顾。

```text
| 决策 | 本工作选择 | 替代方案 | 未选原因 |
|------|-----------|----------|----------|
| [策略] | [X] | [Y] | [技术原因] |
```

每个主要决策至少讨论一个真实替代方案；理由是技术性的，不是「实现更难」。替代方案没有对比测量时只能写成 rationale，不能伪装成实测证据。设计选择与 §5 的 ablation 一一对应，让读者能验证哪个决策带来哪部分收益。

## S4 Implementation（0.5–1 页）

- 段落 1：语言、LOC、依赖与部署形态。
- 段落 2：非显然的关键工程决策与性能关键优化，说明取舍。
- 段落 3（可选）：真实部署经验与教训。
- 只写已经实现的内容；纯设计提议放在 Design 并标为 proposed。工程日志式的细节删掉。

## S5 Evaluation 写作（3–4 页）

完整方法（baseline 公平性、复现、统计、结果诚实性）见 [系统评价方法](evaluation-methods.md)；本节只定写作结构。

1. **Setup**（~0.5 页）：testbed 硬件、baseline、负载、metric、关键配置，足以复现。
2. **End-to-end 对比**（~1–1.5 页）：X 对 baseline 在真实负载上的整体行为。
3. **Microbenchmark／Ablation**（~1–1.5 页）：逐个隔离设计决策的贡献。
4. **Scalability**（~0.5 页）：规模维度增大时的行为；无证据时按 [evaluation-methods](evaluation-methods.md) 记缺口。

每个实验块都用 **三处一致** 规则（Irene Zhang）：

```text
§5.X [实验名]
Hypothesis：我们预期 [系统] 在 [metric] 上 [优于／持平] [baseline]，
因为 [§3 的设计理由]。

图 N 显示 [关键发现]；[系统] 在 [负载] 上相对 [baseline] 达到 [实际数字]，
因为 [回到设计的解释]。

Conclusion：[系统] 在 [metric] 上相对 [baseline] [优于／持平] [实际数字]，
支持的范围仅限 [证据实际建立的范围]；失败或不确定结果照实说明。
```

图 caption 单独写出关键发现，让 caption 脱离正文也可读。结论只陈述证据支持的范围：微基准的结果不升级为系统整体结论，单一负载不升级为普遍结论。

## S6 Related Work（1 页）

按方法／路线分组，不按论文逐条罗列。每组写「这一类做什么」→「其局限」→「本工作如何不同」。比较 4 个以上系统时用比较表。所有差异陈述必须准确且可核对，不贬低也不夸大。

## S7 Conclusion（0.5 页）

3 句：问题、方案、关键结果。之后可加 2–3 句未来工作。不引入新信息，不提出未经证据支持的泛化。

## 写作质量纪律

- **维护读者状态**（Gernot Heiser）：像 OS 维护进程状态一样维护读者认知，不引入无上下文的术语，前置引用要显式给指针（「as we show in §N」）。
- **define-before-use**：缩写首次出现即展开；全文系统名大小写一致；术语只有一个定义处。
- **可信陈述**：有数字才说「显著」；不写无证据的 hedge（「we believe」）。
- **图与表**：正文先引用后出现；caption 自包含；评估图 caption 含关键发现；字体在打印后 ≥8pt；灰度可辨；全篇图风格一致。
- **LaTeX**：引用格式统一；`Section~\ref{...}` 不断行；参考文献元数据完整；日志无 overfull hbox 堆积。
- **架构图**：前 3 页内出现，锚定设计段。

## 常见问题与修正

| 症状 | 修正 |
|---|---|
| 读起来像 feature list | 用 thesis 公式或 Gap 分析给每个 feature 一个职责 |
| 评价深度不足 | 补 ablation 隔离每个设计决策（须有真实实验） |
| 被评「incremental」 | 强化 G1–Gn，绑定证据与现有系统的失败条件 |
| Design 过长 | 工程细节下移到 Implementation，Design 保持设计层 |
| Motivation 薄弱 | 补真实观测与具体数字，无数据则降级为假设 |
| Related Work 像书目 | 按方法分组，逐组写显式区别 |
| 只有 microbenchmark | 补端到端；无法补时记 evidence gap，不宣称系统整体更优 |

## 学术诚信

- 不编造观测、trace、部署经验、实验数字或 venue 规则；所有数字来自实际运行或引用来源。
- 不凭记忆生成引用；未核实引用标 `[CITATION NEEDED]`，交由 `citation-audit` 核实。
- 结构性借鉴（如某个 pattern 来自某论文）在文中致谢式标注；不复制他人段落级文字。
- 当前 venue 是否要求披露 LLM 使用、是否允许 AI 署名，按 [venue 与 reviewer 方法](venue-and-reviewer.md) 现场核对。
