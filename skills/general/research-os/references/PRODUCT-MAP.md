# Research OS 产品地图

## 读图与状态

这是 Issue #1 及其已批准 35 票方案的完整科研能力地图；分类仅服务发现。工程准备、全量审核、文档、Release 与旧工程删除票不是科研入口。下表是入口真相；命中分支再读明细，不一次加载全部分流程表。

- **已实现**：本发行包含正式 Skill 正文；不等于当前宿主已安装、已加载或真实科研验收通过。
- **计划**：批准范围，尚未进入本发行。表中的代码名称是规划名称，不是可执行命令；写“名称待定”的能力标签尤其不能当作 Skill 名。后续正文审核可能拆分、合并或改名。
- **宿主可用性**：另行报告“已确认／未核实／已确认不可用”，注明实际正文、入口注册信息或用户确认等依据。模型自动发现清单会隐藏 user-invoked 入口，不能据其缺席断言未安装。即便文件存在，宿主加载与调用策略仍可能未核实。
- **user-invoked（U）**：人类显式选择的 Workflow／独立入口，互不自动启动。
- **model-invoked（M）**：当前已授权职责中的内部能力，也可由用户点名 standalone；composed 时贡献父报告。M 不等于只读，生成、绘图等写入仍受各自边界约束。

## 三条主流程

| 主流程 | 用户目的与停止点 | 主入口与状态 |
|---|---|---|
| Idea Discovery | 从方向主动检索、多视角生成、查新、独立评审、固定问题下收敛；交付发现报告与 Proposal 后停止，不启动 pilot 或 Validation | `idea-discovery`，U，已实现（#8）。明细：[idea-cycle.md](idea-cycle.md) |
| Validation | 计算／实证路径以批准计划落实实验、分析、审计并形成受约束候选 Claim；数学／理论路径推导、证明、审查与显式修复。各入口完成自己的职责就停，不自动写论文 | 下方多个独立 U 入口；这是主流程名称，**不是另一个名为 validation 的 Skill**。明细：[validation.md](validation.md) |
| Paper Writing and Improvement | 从现有材料规划、起草、绘图、编译、并列适用审查和授权修订；交付候选稿与审查报告后停止，不补实验或投稿 | `paper-writing`，U，已实现（#25）；ML 专业入口 `ml-paper-writing`，U，已实现（#26）；Systems 专业入口 `systems-paper-writing`，U，已实现（#27）。明细：[writing-cycle.md](writing-cycle.md) |

上述是可选路径，不是线性通关表。任意外部材料都能成为切入点；有结果不必先跑 Discovery，有稿件不必重新实验或起草，普通证明无需 Lean。

`research-os`（U，已实现，#38）：唯一编排入口。只读请求走 route-only，零副作用。`setup-research-os`（U，已实现，#3）：用户确实想初始化或补齐人类可读工作区；探索、逐问、完整草稿确认后补缺。**不是咨询或其他入口的前置门槛**。

## 按现有材料选切入点

- **只有方向**：想形成完整 Proposal，推荐已实现的 `idea-discovery`；也可先点名候选生成／创意思考做局部构思，或对已选候选单独查新／评审／收敛，而非对空方向捏造 novelty 结论。读 [idea-cycle.md](idea-cycle.md)。
- **已有结果**：先看用户要解释不确定性、审计真实性，还是形成候选 Claim；分别推荐对应内部能力或已实现的 `result-to-claim`。仅想从结果衍生新方向时才考虑已实现的 `idea-generation`；不强迫重新找 Idea。读 [validation.md](validation.md)；衍生新方向再读 idea-cycle。
- **已有稿件**：按需要选引用／Claim／Proof／Stress 检查、局部修复、通用／专业写作或独立后续入口（`rebuttal`、`resubmit-pipeline`、`paper-talk`、`research-improvement`）；不自动起草新稿、运行实验或初始化目录。读 [writing-cycle.md](writing-cycle.md)。

本地图覆盖批准设计，不承诺未交付入口可用。安装之外的用户自定义或其他作者 Skill 不自动纳入本产品；用户明确询问时，可依据实际可读正文说明差异并标为外部能力，不冒充 Research OS 实现。用户问完整地图时，再读齐三个分支明细。
