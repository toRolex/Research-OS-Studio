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
| Idea Discovery | 用户可直接提交研究方向并要求完整 Proposal；按证据组合文献、多视角候选、查新、fresh 独立评审与固定问题下收敛；完成本次目标即停止，不启动 pilot 或 Validation | `/research-os` 的 `discovery` recipe 是唯一编排入口；底层五项能力可独立调用。明细：[idea-cycle.md](idea-cycle.md) |
| Validation | 计算／实证路径以批准计划落实实验、分析、审计并形成受约束候选 Claim；数学／理论路径推导、证明、审查与显式修复。各入口完成自己的职责就停，不自动写论文 | 下方多个独立 U 入口；这是主流程名称，**不是另一个名为 validation 的 Skill**。明细：[validation.md](validation.md) |
| Paper Writing and Improvement | 从现有材料规划、起草、绘图、编译、并列适用审查和授权修订。`paper-writing` 是唯一写作组织入口；General、ML/AI 与 Systems 资源按需读取。委托内修复继承已授权范围。交付候选稿与审查报告，不自动投稿或外发 | `paper-writing`，U，已实现（#25；整合 #26/#27 的专业资源）；明细：[writing-cycle.md](writing-cycle.md) |

上述是可选路径，不是线性通关表。任意外部材料都能成为切入点；有结果不必先跑 Discovery，有稿件不必重新实验或起草，普通证明无需 Lean。

数学／理论证明路线（#55）由 `/research-os` 的 proof 配方作为唯一总控，按当前证据在推导、构造、计算、并行候选、独立审查、finding 修复与按需形式化之间交替；这些是职责独立的 Skill slug，不是固定阶段。长期证明的旧总控已移除；原有数学审计、Lean、记号、压力测试与交接资源归入 `proof-review` 的按需参考及其随包许可，未复制第二套轮次控制器。

`research-os`（U，已实现，#38）：唯一编排入口。只读请求走 route-only，零副作用。已交付 playbook：route-only、literature、discovery、experiment-plan、experiment-bridge（用户需求路由名，执行唯一进入 `run-experiment`）、paper-writing 的 general / ml / systems、proof、rebuttal、resubmit、paper-talk、improvement、pickup。Discovery 按研究委托合同迁移（#60），其完整方向到 Proposal 是可选目标；普通能力/阶段转换不逐次停下请批，资源额度、外发、破坏性操作、越权及能力定义的硬门仍须遵守。委托目标、授权范围、额度与完成条件见 [mandate.md](mandate.md)；`experiment-bridge` 是配方名而非可安装 Skill 或独立 slash 入口，唯一执行控制为 `run-experiment`。已保存的证明轮次走 proof，已有研究整体的有界改进走 improvement，新会话恢复已保存交接走 pickup（#45）。pickup 重读批准、授权和作业记录，不延长授权。`setup-research-os`（U，已实现，#3）：用户确实想初始化或补齐人类可读工作区；探索、逐问、完整草稿确认后补缺。**不是咨询或其他入口的前置门槛**。

## 按现有材料选切入点

- **方向或现成候选**：用户可直接向 `/research-os` 提交方向并要求完整 Proposal，或只做已有材料中的文献、候选、查新、独立评审或细化缺口。Discovery recipe 按证据选 Required 能力子集并允许重排/回访；缺依赖只阻塞受影响职责，fresh 独立评审不可由自查替代。完整方向到 Proposal 是可选目标；不对空方向捏造 novelty 结论。读 [idea-cycle.md](idea-cycle.md)。
- **已有主题要一次文献综合**：走已迁移的 literature route（playbook literature-review）。它按委托合同直接跑到交付并验收实际产物，不要求先 setup 或先报额度；要拿这批材料形成 Proposal 时走 Discovery recipe。也可直接点名 `research-lit`。
- **已有问题要做计划**：走已交付的 experiment-plan。它只产计划；执行授权写在研究日志，不来自默认政策。
- **已有计划要跑完并分析**：用户可用“实验桥接”表达目标；执行唯一进入 `run-experiment`。按需组合独立监控、分析与审计能力。启动前核对研究日志里的本批授权；缺授权、过期、越界或要删既有结果时停。
- **已有结果**：先看用户要解释不确定性、审计真实性，还是形成候选 Claim；分别推荐对应内部能力或已实现的 `result-to-claim`。仅想从结果衍生新方向时才考虑已实现的 `idea-generation`；不强迫重新找 Idea。读 [validation.md](validation.md)；衍生新方向再读 idea-cycle。
- **已有稿件**：按需要选引用／Claim／Proof／Stress 检查、局部修复、通用／专业写作，或 `/research-os` 的 rebuttal、resubmit、paper-talk（叶入口仍是 `rebuttal`、`resubmit-pipeline`、`paper-talk`）与 `research-improvement`。不自动起草新稿、运行实验或初始化目录。读 [writing-cycle.md](writing-cycle.md)。

本地图覆盖批准设计，不承诺未交付入口可用。安装之外的用户自定义或其他作者 Skill 不自动纳入本产品；用户明确询问时，可依据实际可读正文说明差异并标为外部能力，不冒充 Research OS 实现。用户问完整地图时，再读齐三个分支明细。
