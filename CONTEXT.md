# Research OS 领域上下文

本仓库发布可安装到独立科研项目的纯 Agent Skills 套件。Skills 是产品本体；产品没有 Research OS 专用 runtime、CLI、统一 schema/validator、中央 planner 或自动跨主流程推进。

## 规范领域词汇

以下术语是规范名称。实现、测试、Issue 和文档不得用未定义的同义词替代其语义。

- **Research Project**：用户已有或新建的科研项目。它拥有自己的材料、环境、目录和 Git 历史；Research OS 只在用户确认后补齐人类可读工作区。
- **Research Workspace**：Research Project 内由 setup 记录位置的人类可读导航、研究日志与 Workflow 产物集合。默认建议 `research/`，但不强制迁移已有文件，也不是隐藏 runtime 状态。
- **Skill**：可由 Agent 宿主发现和执行的自包含能力，连同自身 references、templates、assets 和必要 scripts 构成产品发行单元。
- **Workflow**：用户显式调用、职责有界的顶层或独立 Skill。它可在当前授权内调用内部 Skill，产出候选材料和报告后停止；不得自动进入另一条顶层 Workflow。
- **Internal Skill**：由 Workflow 在当前职责、写入范围和资源授权内调用的局部能力；也可被高级用户明确点名单独运行。它不得扩大研究目标、预算或外部副作用。
- **Idea Discovery**：主动检索文献、生成多视角候选、查新、独立评审并收敛为可验证 Proposal 的主流程；完成后停止，不自动开始 Validation。
- **Validation**：通过计算／实证实验或数学／理论方法形成受证据约束结论的主流程；环境与资源由 Research Project 所有，不自动进入写作。
- **Paper Writing and Improvement**：依据原始研究材料规划、起草、绘图、编译、审计和修订论文的主流程；不自动投稿、宣布接受或触发后续 Workflow。
- **Research Material**：Markdown、代码、数据、CSV、图片、LaTeX、Lean 等保持自然格式的项目文件。文件存在不自动等于论断成立，Research OS 不用统一 JSON Artifact 包装它们。
- **Claim**：研究者拟表达的范围受限主张。Claim 是否成立由证据、独立审查和用户判断约束，不由 Workflow 完成、文件格式或模型共识推出。
- **Evidence**：用于支持或限制 Claim 的原始结果、推导、来源或观察。定位和解释必须可供审查，但不要求 Research OS 维护额外 digest、receipt 或 content pin。
- **Source Record**：集中记录上游仓库、作者、核对 revision、原路径、采用内容、许可证和 attribution 的维护信息；它不是 port database、来源认证协议或运行时 gate。
- **Router**：只读 Skill，用于解释能力地图并推荐入口；不修改研究材料，也不执行推荐的 Workflow。

## 关键边界

1. 三条主流程是产品地图，不是状态机；用户决定何时调用、停止或转入下一条流程。
2. setup 只探索、展示、询问、起草、确认并补齐缺失内容；不安装 Skills、配置环境、覆盖现有材料或创建具体 Idea／Claim／Evidence／论文。
3. Skills 优先完整搬运许可证兼容的成熟资产并最小适配；许可证不兼容或证据不足时只 clean-room 借鉴公开思想。
4. Research OS 不提供专用 CLI、Python/Node runtime、wheel、统一 contracts/validators、Adapters、SHA/digest/receipt、Publication freeze 或 port gates。
5. GitHub Issues 是规划和状态真源；来源与许可证决定集中记录于 `docs/upstream-sources-and-licenses.md`。
6. 未经用户确认，不执行付费资源、远程写入、投稿、发布、Git push 或破坏性操作；外部能力缺失时如实报告。
7. 用户真实科研项目验收前，不声称端到端体验或科研质量已经通过。
