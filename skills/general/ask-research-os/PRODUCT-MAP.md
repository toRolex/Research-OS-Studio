# Research OS 产品地图

## 读图与状态

这是 Issue #1 及其已批准 35 票方案的完整科研能力地图；分类仅服务发现。工程准备、全量审核、文档、Release 与旧工程删除票不是科研入口。

- **已实现**：本发行包含正式 Skill 正文；不等于当前宿主已安装、已加载或真实科研验收通过。
- **计划**：批准范围，尚未进入本发行。下表中的代码名称是规划名称，不是可执行命令；写“名称待定”的能力标签尤其不能当作 Skill 名。后续正文审核可能拆分、合并或改名。
- **宿主可用性**：另行报告“已确认／未核实／已确认不可用”，注明实际正文、入口注册信息或用户确认等依据。模型自动发现清单会隐藏 user-invoked 入口，不能据其缺席断言未安装。即便文件存在，宿主加载与调用策略仍可能未核实。
- **user-invoked（U）**：人类显式选择的 Workflow／独立入口，互不自动启动。
- **model-invoked（M）**：当前已授权职责中的内部能力，也可由用户点名 standalone；composed 时贡献父报告。M 不等于只读，生成、绘图等写入仍受各自边界约束。Router 本身不调用它们。

状态快照：本票交付时，General 的 `setup-research-os`、`ask-research-os`，Idea Cycle 的 `idea-generation`、`creative-thinking-for-research`、`novelty-check`，以及 Validation 计算／实证路径的 `experiment-plan`、`experiment-bridge` 与其真实组合的 `run-experiment`、`experiment-queue`、`monitor-experiment`、`training-health-check`、`analyze-results`、`experiment-audit` 已有正式 Skill 正文。此表是发行说明，不是运行时状态数据库；入口交付、改名或角色变更时维护者同步更新，使用时以可读取的真实安装正文核实关键行为。

## 三条主流程

| 主流程 | 用户目的与停止点 | 主入口与状态 |
|---|---|---|
| Idea Discovery | 从方向主动检索、多视角生成、查新、独立评审、固定问题下收敛；交付发现报告与 Proposal 后停止，不启动 pilot 或 Validation | `idea-discovery`，U，计划（#8） |
| Validation | 计算／实证路径以批准计划落实实验、分析、审计并形成受约束候选 Claim；数学／理论路径推导、证明、审查与显式修复。各入口完成自己的职责就停，不自动写论文 | 下方多个独立 U 入口；这是主流程名称，**不是另一个名为 validation 的 Skill** |
| Paper Writing and Improvement | 从现有材料规划、起草、绘图、编译、并列适用审查和授权修订；交付候选稿与审查报告后停止，不补实验或投稿 | `paper-writing`，U，计划（#25）；ML／Systems 专业入口另列 |

上述是可选路径，不是线性通关表。任意外部材料都能成为切入点；有结果不必先跑 Discovery，有稿件不必重新实验或起草，普通证明无需 Lean。

## General

| 入口 | 角色／状态 | 何时选择与边界 |
|---|---|---|
| `ask-research-os` | U／已实现（#32） | 不确定选哪个入口；只解释、推荐并停止 |
| `setup-research-os` | U／已实现（#3） | 用户确实想初始化／补齐人类可读工作区；探索、逐问、完整草稿确认后补缺，不覆盖材料、不配置科研环境、不启动研究。**不是咨询或其他入口的前置门槛** |

## Idea Cycle：从方向或候选开始

| 能力 | 角色／状态 | 适用输入与职责 |
|---|---|---|
| 文献检索与综合（名称待定） | M／计划（#4） | 主题或已有文献；主动检索，区分候选、已核实与未核实来源，输出有出处的综合 |
| `idea-generation` | M／已实现（#5） | 现成文献、笔记或已有结果；多视角候选、去重及硬约束筛选，保留暂存／淘汰理由；不是独立评审 |
| `creative-thinking-for-research` | M／已实现（#5） | 构思卡在单一表述、表面类比或二选一；认知转换产生可检验洞见；不是候选池裁决 |
| `novelty-check` | M／已实现（#6） | 已有候选核心 Claim；主动寻找 closest prior work、核实身份、对比关键区别并独立复核；缺证据时说明具体补证动作，不因模糊相似误杀 |
| `idea-review` | M／计划（#7） | 原始候选和文献；独立 reviewer 直接读取材料，不以生成者摘要或自查代替裁决 |
| `idea-refinement` | M／计划（#7） | 候选与评审 findings；固定 Problem Anchor，比较最小可行与前沿方案，不偷偷换题 |

完整路径是用户选择 `idea-discovery` 后在一次授权内组合这些内部能力，不是 Router 逐项启动。仅想发散、认知转换或查新时可直接点名相应已实现 M 能力；它们不等于已交付完整 Discovery。

## Validation：计算／实证

### 独立用户入口

| 入口 | 角色／状态 | 选择依据、结果与停止边界 |
|---|---|---|
| `experiment-plan` | U／已实现（#9） | 已有研究问题尚缺可执行计划；明确 hypothesis、baseline、metric、ablation、固定评价面、修改范围、预算和失败含义，只产计划 |
| `experiment-bridge` | U／已实现（#15） | 已有获批计划，需一次授权完成实现、code review、sanity、正式／批量运行、监控、收集、分析审计与授权 tracker 更新；不要求先用本产品规划。消融仅建议，不自行扩预算／下一轮；不启动独立 `result-to-claim` |
| `result-to-claim`（Results-to-Claims） | U／计划（#14） | 已有外部或本产品结果，需判断能说什么；区分 Evidence 存在、统计可信度、支持程度与 Claim scope，将部分支持缩窄为可辩护主张。最终采用由用户决定，产出候选 Claim 就停 |

### 内部能力与局部点名入口

| 能力 | 角色／状态 | 职责边界 |
|---|---|---|
| `run-experiment`、`experiment-queue` | M／已实现（#10） | 完整实现、review、sanity、运行与初步收集链；使用当前批准计划／修改范围／资源，保留 baseline 及成功、失败、无效、超时全部 attempts |
| `monitor-experiment` | M／已实现（#11） | 观察 running/completed/crashed 等事实；不判 Claim，不自动分析或控制作业 |
| `training-health-check` | M／已实现（#11） | 固定观测中的 NaN、发散、OOM、停滞、日志缺失；只诊断与建议，不自行 kill／重启 |
| `analyze-results` | M／已实现（#12） | baseline、全部 attempts 与失败记录；重复试验、不确定性、选择偏差、多重比较；单 metric winner 不是科学结论 |
| `experiment-audit` | M／已实现（#13） | protocol conformance 与独立真实性审查分开；直接读 evaluator、代码和原始结果，查 fake ground truth、phantom results、遗漏 attempts、scope overclaim；默认只报告，不修代码或补实验 |

已有结果时，运行是否结束、训练是否健康、统计是否可信、结果是否真实、能支持何种 Claim 是不同问题，不推荐重跑全部流程。付费、远程写入、高成本操作需对应 Workflow 的必要授权，Research OS 不配置 Python／GPU／SSH／Slurm 等环境。

## Validation：数学／理论专业路径

| 入口／能力 | 角色／状态 | 选择依据与边界 |
|---|---|---|
| `formula-derivation` | U／计划（#16） | 澄清公式链、假设、近似与解释；生成职责，不降格为审计 |
| `proof-writer` | U／计划（#16） | 固定命题的证明或明确 gaps；保留失败路线与教训，不把尝试当证明成功 |
| `proof-review` | M／计划（#17） | 只读现成证明，直接报告错误／gaps；可用户点名，不改命题、证明或 LaTeX |
| `proof-repair` | U／计划（#17） | 用户希望修复已知 gaps；明确 scope、写入范围、轮数及工具授权，命题／假设变化由用户决定 |
| `proof-workflow` | U／计划（#18） | 单个复杂长期 obligation 的延续工作；其真实内部组合以后续正文为准，**不宣称它原生调用 `proof-writer`／`proof-review`** |
| Lean premise／lemma search、LSP、Mathlib 规范与 kernel／build 检查 | 专业内部方法／计划（#18），不是独立已安装 Skill | premise 搜索结果是候选，需读 signature；LSP 是快速反馈，kernel／build 才是形式化检查。无 Lean 继续普通推导／证明，形式化标未验证；不安装工具链或引入 Archon runtime |

## Writing Cycle：从材料或现成稿件开始

### 写作内部能力

| 能力 | 角色／状态 | 选择依据与边界 |
|---|---|---|
| `paper-plan` | M／计划（#19） | 已有材料需 Claim—Evidence 结构、叙事、缺口和写作边界；故事不反向制造证据 |
| `paper-drafting` | M／计划（#20） | 现成计划与原始 Claims／Evidence／结果；起草可追溯正文，与总 Workflow `paper-writing` 不同 |
| 学术绘图／figure（名称待定） | M／计划（#21） | 真实数据图与标明性质的示意图；保留可编辑／复现来源。ARIS／Orchestra 方法经比较适配，不许伪造数据 |
| 论文编译检查（名称待定） | M／计划（#22） | 使用已有构建环境产生真实 build／error 记录，可能产生构建文件但不改源码；不等于论文正确性审查 |
| `citation-audit` | M／计划（#23） | 分开核实引用身份、元数据与语境支持；只报告，不改 BibTeX 或正文 |
| `paper-claim-audit` | M／计划（#24） | 数字、比较、配置、表格、caption、实验覆盖；不替代证明或一般论证审查 |
| `claim-stress-test` | M／计划（#24） | 整篇文章最强拒稿论点；攻击者与裁决者分离，不自封最终结论 |
| 独立论文评审与授权 revision（具体拆分／名称待定） | 内部能力／计划（#24、#25） | reviewer 直接读原始材料，修订只在当前父 Workflow 批准的范围内；不借独立高权限入口自动扩权 |

Claim、Citation、Proof（理论内容适用）、Stress 与独立评审是并列按需检查，不是线性证据链。用户已有稿件时只选所需检查／修订，不要求先运行计划、起草或 W3。

### 独立用户入口与专业扩展

| 入口 | 角色／状态 | 选择依据与边界 |
|---|---|---|
| `paper-writing` | U／计划（#25） | 通用完整 W3：plan、draft、figures、compile、适用 audits、独立评审与授权 revision；不是 drafting 薄壳 |
| `ml-paper-writing` | U／计划（#26） | ML 实验报告：seeds、error bars、compute、limitations 等专属方法；复用内部资产，不自动调用 user-invoked W3 |
| `systems-paper-writing` | U／计划（#27） | Systems 的 design rationale、implementation、end-to-end、microbenchmark、scalability；不与 ML 合并、不自动启动通用 W3 |
| 论文编译修复（名称待定） | U／计划（#22） | 已知编译错误且希望改源码；显式确认范围后修复并复验，与 check-only 分离 |
| 引用修复应用（名称待定） | U／计划（#23） | 已有引用 findings 且希望替换／删除／修正文或 BibTeX；先展示拟修改范围并获授权，与 detect 分离 |
| `research-improvement` | U／已实现（#28），跨流程可选 | 对方法、代码、全部结果、Claims、草稿、diff、历史 findings 做有界 review／repair／re-review；高权限可写入口，在明确 scope、写入范围、轮数、资源及副作用授权内补分析／改稿，补实验须另行授权并在运行数名额内；承接 W3 `auto-paper-improvement-loop` 与 W2 `auto-review-loop` 方法，不是只读 M discipline，不自动启动 experiment-bridge、paper-writing 或专项修复入口 |
| `rebuttal` | U／计划（#29） | 现成审稿意见与论文证据；原子化 concern、映射证据、区分可答／待澄清／需补工作；补实验另行授权 |
| `resubmit-pipeline` | U／计划（#30） | 现成稿件换 venue；新目录适配并保留旧投稿，使用内部检查；不要求先运行本产品写作流程 |
| Conference Talk（最终名称待定） | U／计划（#31） | 已完成论文到 slides、notes、script；合并或择优 ARIS paper-talk 与 Orchestra presenting-conference-talks，只保留一个入口；审查演讲产物，不是重复审计原论文 |

指定 venue 时，对应写作入口应使用最新官方 guidelines／模板，用户模板冲突交给用户决定。Router 只说明此要求，不替用户联网下载模板、编译、改稿或投稿。Rebuttal、Resubmit、Talk 彼此独立；Workflow 完成不等于论文被接受。

## 按现有材料选切入点

- **只有方向**：想形成完整 Proposal，可条件性推荐计划中的 Idea Discovery；当前已实现的候选生成／创意思考适合局部构思，仍需相应输入，不能代替尚未交付的完整检索与独立评审。已选候选再查新，而非对空方向捏造 novelty 结论。
- **已有结果**：先看用户要解释不确定性、审计真实性，还是形成候选 Claim；分别推荐对应内部能力或 `result-to-claim`，均清楚标计划。仅想从结果衍生新方向时才考虑已实现的 `idea-generation`；不因完整 Validation 未实现而强迫重新找 Idea。
- **已有稿件**：按需要选引用／Claim／Proof／Stress 检查、局部修复、通用／专业写作或独立后续入口；都标明当前计划状态，不自动起草新稿、运行实验或初始化目录。

本地图覆盖批准设计，不承诺未交付入口可用。安装之外的用户自定义或其他作者 Skill 不自动纳入本产品；用户明确询问时，可依据实际可读正文说明差异并标为外部能力，不冒充 Research OS 实现。
