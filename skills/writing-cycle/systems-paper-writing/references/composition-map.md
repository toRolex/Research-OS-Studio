# Composition Map

`systems-paper-writing` 在一次授权内组合哪些已交付内部能力、在哪一步、以何种产出贡献正文报告。被组合能力只在本次确认的职责、写入范围和资源授权内工作；本映射不是自动调用链，不授予被组合能力之外的权限，也不允许本 Workflow 启动任何其他 user-invoked 顶层 Workflow。

| 本 Workflow 阶段 | 组合的内部能力 | 贡献的正文报告章节 | 不做的事 |
|---|---|---|---|
| 规划 | [paper-plan](../../paper-plan/SKILL.md)（Systems 分支读取 [systems-blueprints](../../paper-plan/references/systems-blueprints.md)、[systems-patterns](../../paper-plan/references/systems-patterns.md)） | 计划摘要、Claim—Evidence、Gap—Answer、叙事与缺口 | 不反向制造证据，不执行实验，不建平行计划 |
| 图表 | [academic-plotting](../../academic-plotting/SKILL.md) | end-to-end／microbenchmark／ablation／scalability 数据图、比较表、架构示意图与复现说明 | 不伪造数据，不插值，不安装环境 |
| 正文起草 | [paper-drafting](../../paper-drafting/SKILL.md)（写作纪律见 [systems-writing-methods](systems-writing-methods.md)） | 系统论文逐节候选正文与可追溯映射 | 不改证据，不编造数字／引用，不代替总 Workflow |
| 评价面与就绪自检 | 本 Workflow 自身 + [evaluation-methods](evaluation-methods.md) | 系统证据面状态、缺口清单、fairness／复现／三处一致核对 | 不补做实验，不外推缺失数据 |
| Venue 现场核对 | 本 Workflow 自身 + [venue-and-reviewer](venue-and-reviewer.md) | 当期官方规则来源、track、匿名与披露状态 | 不缓存年度规则，不代用户选择 track |
| 编译检查 | [paper-compile](../../paper-compile/SKILL.md) | 真实构建状态、错误位置、PDF 核验 | 不改源码，不安装工具，不用旧 PDF 冒充成功 |
| 数字／比较审查 | [paper-claim-audit](../../paper-claim-audit/SKILL.md) | 逐 Claim 数字、配置、聚合、delta、caption、覆盖范围对账 | 不替代引用／证明／整篇论证，不自动改稿 |
| 引用审查 | [citation-audit](../../citation-audit/SKILL.md) | 身份、元数据、语境三轴逐条发现 | 默认不改 bib／正文；改动需写入授权与逐项批准 |
| 证明审查 | [proof-review](../../../validation-cycle/proof-review/SKILL.md)（仅含定理／引理／证明时） | 证明义务、逻辑缺口、反例、影响范围 | 不修证明，不编译，不自动调用 `proof-repair` |
| 整篇拒稿论证 | [claim-stress-test](../../claim-stress-test/SKILL.md) | 最强拒稿攻击、独立裁决与严重度 | 不自封最终结论，不自动改稿 |
| 独立整篇评审与授权 revision | 本 Workflow 自身（fresh-context 独立 reviewer） | 分级评审、修订清单、逐项改动、复编译与轮次记录 | 不改命题／假设／结论范围，不越出授权写入范围，不无限循环 |

被组合能力不可用或超出本次授权时，在正文报告对应章节如实标注缺口并停止该分支，不伪造其输出，不以执行者摘要代替其直接读取。审查能力之间并列按需，不由本 Workflow 自动串联成线性通过链。

`paper-writing`（通用 W3，#25）与 `ml-paper-writing`（#26，计划）是并列的 user-invoked 顶层入口，本 Workflow 不调用它们，它们也不调用本 Workflow。`paper-compile-repair`、`apply-citation-fixes`、`proof-repair`、`rebuttal`、`resubmit-pipeline`、`paper-talk`、`research-improvement` 同样需要用户另行点名，本 Workflow 不启动它们。
