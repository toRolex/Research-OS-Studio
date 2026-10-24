# 来源与采用范围

- 上游：`cursor/plugins` 仓库的 `pstack` 目录，固定 revision `88d47514b82e7c44f00f2b2a72ff6dd12158038c`，路径 `pstack/skills/interrogate/`。
- 许可：上游根 LICENSE 为 MIT License，Copyright (c) 2026 Lauren Tan；全文随本技能共置于本目录 [LICENSE](../LICENSE)。采用前已核对上游具体文件正文适用该许可。
- 采用范围：
  - `references/rubric.md`、`references/code-quality-review.md`、`references/lead-judgment.md`：上游正文原样保留（机制保真对照依据）。
  - `references/reviewer-prompt.md`：改自上游同名文件——补充只读约束与研究材料占位，机制（severity/finding/evidence/suggestion、空审查合法）保留。
  - `SKILL.md`：保留独立 reviewer、findings 合并去重与来源记录、分歧保留、主审四桶判断与输出格式；模型/实例配置按下述差异适配，正文为宿主中立与科研适配重写。
- 适配差异（有意偏离上游处）：
  1. 删除 Cursor 专属机制：`~/.cursor/rules/pstack-models.mdc`、固定模型默认表（`claude-opus-5-5-xhigh`、`grok-4.7-xhigh-fast`）与 Task tool 细节。全局角色仍各一行；本次reviewer集合默认以唯一 `reviewer:` 绑定派两个隔离fresh实例，显式多模型集合另列有效授权来源，来源不足或缺隔离能力标blocked。same-model不冒充多模型，不以串行代跑/自查冒充独立审查；方法与主审综合职责保留。
  2. 删除上游的 PR/open PR 语境表述；本技能始终只读，不自动修订，修复由调用者的研究委托按授权另行组织。
  3. 新增 `references/research-review.md`（科研审查 lens），覆盖证明义务、等强未证引理、数值候选状态与「共识不是数学证据」；上游 rubric 与 code-quality lens 保留用于代码变更审查。
