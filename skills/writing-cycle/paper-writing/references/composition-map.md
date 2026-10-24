# Composition Map

`paper-writing` 在一次授权内组合哪些内部能力、在哪一步、以何种产出贡献正文报告。被组合能力在委托合同授权内工作；本映射只授权写作职责内的组合，不自动启动 [research-improvement](../../research-improvement/SKILL.md)。

| 本 Workflow 阶段 | 组合的内部能力 | 贡献的正文报告章节 | 不做的事 |
|---|---|---|---|
| 规划 | [paper-plan](../../paper-plan/SKILL.md) | 计划摘要、Claim—Evidence、叙事与缺口 | 不反向制造证据，不执行实验，不建平行计划 |
| 图表 | [academic-plotting](../../academic-plotting/SKILL.md) | 数据图／示意图／比较表、来源与复现说明 | 不伪造数据，不安装环境，不启动写作总流程 |
| 正文起草 | [paper-drafting](../../paper-drafting/SKILL.md) | 逐节候选正文与可追溯映射 | 不改证据，不编造数字／引用，不代替总 Workflow |
| 编译检查与委托内修复 | [paper-compile](../../paper-compile/SKILL.md) → 授权内 [paper-compile-repair](../../paper-compile-repair/SKILL.md) | 真实构建状态、错误位置、精确修复 diff、改动文件、复编译结果 | 不改源码范围外的文件，不安装工具，不用旧 PDF 冒充成功 |
| 数字／比较审查 | [paper-claim-audit](../../paper-claim-audit/SKILL.md) | 逐 Claim 数字、配置、聚合、delta、caption、覆盖范围对账 | 不替代引用／证明／整篇论证，不自动改稿 |
| 引用审查与委托内修复 | [citation-audit](../../citation-audit/SKILL.md)；授权内 [apply-citation-fixes](../../apply-citation-fixes/SKILL.md) | 身份、元数据、语境三轴逐条发现；继承授权后展示并应用精确修复 | 只读审查仍不修改；修复不越委托写入范围 |
| 证明审查 | `proof-review`（按可发现的 Skill slug 调用；仅含定理／引理／证明时） | 证明义务、逻辑缺口、反例、影响范围 | 不修证明，不编译，不自动调用 `proof-repair` |
| 整篇拒稿论证 | [claim-stress-test](../../claim-stress-test/SKILL.md) | 最强拒稿攻击、独立裁决与严重度 | 不自封最终结论，不自动改稿 |
| 独立整篇评审与授权 revision | 本 Workflow 自身（fresh-context 独立 reviewer） | 分级评审、修订清单、逐项改动、复编译与轮次记录 | 不改命题／假设／结论范围，不越出授权写入范围，不无限循环 |

被组合能力不可用或超出本次授权时，在正文报告对应章节如实标注缺口并停止该分支，不伪造其输出，不以执行者摘要代替其直接读取。审查能力之间并列按需，不由本 Workflow 自动串联成线性通过链。

审查输入：按被调用的 audit skill 自己的输入契约读，不在编排器里另定输入范围。**委托内继承**：`paper-compile-repair` 和 `apply-citation-fixes` 在当前委托已授权该职责、文件和副作用时直接承接，不要求再次独立点名；只读审查仍只读，越权修复停那一步。`proof-repair` 的迁移由证明能力票处理，本入口只记录缺口。跨研究改进循环由 `research-improvement` 独立负责，本 Workflow 不启动、不重复其入口。

## 专业分支

依据用户请求和论文主要贡献选 General、ML/AI、Systems；混合论文只读取对应分支资源。ML/AI 的实验报告、reviewer 期望、venue checklist 与报告模板见 [专业资源索引](standards.md)；Systems 的逐节写作、评价、checklist、venue/reviewer 方法与报告模板也由该索引按需指向。领域参考不启动实验或补证流程；需要新实验时走相应 Validation 路线并遵守运行授权。
