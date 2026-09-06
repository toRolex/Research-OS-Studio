# Research OS 领域上下文

本仓库定义并发布可安装到独立科研项目的 Research OS P0。它是 provider-neutral 的 Agent Skills、共享契约、确定性 validator、项目设置与薄平台 Adapter 集合；不是中央 planner、自动科研 runtime、scheduler 或具体科研项目。

## 规范领域词汇

以下术语是规范名称。实现、测试、Issue 和文档不得用未定义的同义词替代其语义。

- **Project**：一个独立科研项目的边界与配置容器。它可以包含多个 Workstream 和多份 Publication，不保存全局 phase、current focus 或自动 next-step。
- **Workstream**：Project 内可独立推进、暂停或并行的局部研究工作容器。不同 Workstream 不靠隐式状态通信，只通过 Artifact 交接。
- **Artifact**：带 typed contract、稳定 target、可选 provenance/relations/assurance 的项目文件产物。它是 workflow 与 Workstream 之间唯一规范交换接口；失败现场和旧版本不可静默覆盖。
- **Claim**：对研究对象、结果或贡献的版本化断言，是一等 Artifact。Claim 的成立不由 workflow 完成或单一 verified 状态自动推出。
- **Evidence**：被明确定位、固定范围并用于支持 Claim 的一等 Artifact。Evidence 与 Claim 通过单向 `supports` 关系连接；supports 不表示证明、真值或全局可信度。
- **Assessment**：独立、不可覆盖的 Assurance 结论 Artifact。它固定 subject、dimension、scope、method、evidence、assessor、verdict 和 validity。
- **Publication**：经用户确认后创建的封闭、版本化发布投影。它固定主要公开文本、成员集、Claim、Evidence、条件、限制、外部引用 receipts 和纳入的 Assessments；冻结后不可覆盖，替代/撤回只能包外追加。
- **workflow**：只能由用户显式调用的有边界流程。它读取用户指定的 pinned Artifact，在预算内产生 candidate Artifact 和报告，列出零到多个下一步后停止，不自动调用另一个 user workflow。
- **discipline**：只在当前 workflow 内由模型调用的局部能力。它不得改变研究语义、statement、评价标准或预算，不得跨 workflow、接受成果、冻结 Publication 或把失败改写为通过。
- **validator**：只判断可复现的确定性事实并生成结构化 Validation Report 的工具。稳定退出码为 `0=pass`、`1=validation failure`、`2=usage/configuration error`、`3=blocked/external prerequisite unavailable`；validator 不代替研究判断或 human acceptance。
- **Adapter**：把 provider-neutral Core 投影到具体平台、探测能力、映射调用并执行阻止的薄层。它不得复制或改写 contract、validator、研究语义、预算、gate 或停止规则；Core 删除 Adapter 后仍可阅读、验证和手工执行。
- **port**：逐项接纳外部社区能力的可审计记录。它必须固定来源仓库 URL、完整 commit、source path、retrieval time、SPDX/license evidence、NOTICE、逐文件 baseline hash、原流程、依赖、keep/modify/delete/add ledger、来源快照、baseline/adapted eval、reviewer 与人工 `preserve|adapt|reject` 决定。
- **target**：定位 Artifact、Publication 或外部材料的结构化 locator，不是 Research OS 自造 ID。支持合法 `git` 或 `uri`；固定 Git 使用完整 commit，跨仓库还需无凭据绝对获取 URI；固定 URI 内容记录 SHA-256。禁止绝对路径、目录、`.`、`..`、fragment、缩写 commit 和 floating branch/tag/latest。

## 关键架构约束

1. 用户拥有研究语义、目标、成功标准、预算追加、statement 修改确认、workflow 间推进、正式接受与 Publication 冻结权。
2. P0 采用 provider-neutral Core、typed file Artifact handoff 和确定性 validators，不引入中央 planner、全局 phase、自动循环或专用运行时。
3. Assurance 采用六个不可线性化维度：`structural_conformance`、`empirical_reproducibility`、`mathematical_argument_review`、`formal_verification`、`independent_review`、`human_acceptance`。新 Artifact revision 不继承旧 Assessment；同维度重叠 scope 的有效冲突必须阻塞 gate。
4. Publication 冻结是显式用户行为。内容无法固定、成员不封闭、外部 receipt 缺失或必需 gate 阻塞时 hard block。
5. 缺少 port 来源或许可证证据时 hard block；`reject` 的源码不能进入产品树。评分不能抵消硬门。
6. GitHub Issues 是当前规划和状态真源。旧 Wayfinder `MAP.md`、`tracker.json` 和本地 tickets 是历史快照；发现 closed/open 或 blocked-by 矛盾时不得用快照改写当前状态，必须以 GitHub Issue 关系为准并保留矛盾记录。

## 证据边界

- `docs/research/sources/comparison.md`、`docs/research/sources/aris-report.md`、`docs/research/sources/ai-research-skills-report.md` 与 `docs/research/sources/anthropic-openai-math-workflows-20260901.md` 是实现前审计材料；`docs/research/sources/README.md` 固定其原始路径、上游完整 revision 与 digest。
- `prototypes/artifact-min-contract-prototype.html`（commit `3428eb72aa31ed532a036909e857e768441c0bcb`）与 `minimal-project-workstream-publication-prototype.html`（commit `6c24ac721af4ccdbc8c57eb980abe006477d477a`）只用于契约决策验证，不是生产运行 seam。
- 分析、原型和规划完成不等于 P0 产品完成；后续实现仍必须通过契约、许可、validator、两条 reference project 与 E2E 验收。
- **验收证据边界**：fixture 中的 researcher、reviewer、user 是固定测试角色。其 candidate、review 和 human-acceptance 输入只验证契约，不代表真实学术判断、社区 port 接纳或产品发布许可；产物线通过不得替代独立发布 gate。
