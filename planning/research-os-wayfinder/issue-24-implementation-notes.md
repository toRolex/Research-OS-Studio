# Research OS P0 实施记录

## 目标

在 `research-skills-system` 独立 worktree 中实现 GitHub Issue #24：交付可安装、provider-neutral、用户控制 workflow 推进、具备 typed Artifact 与 deterministic validators 的 Research OS P0，并以计算研究和数学研究两条 reference project 产出论文/PDF及不可覆盖 Publication。

## 基线

- 2026-09-06：通过 `gh issue view` 获取 Issue #24 与 Map #1 原文；GitHub Issue 为当前真源。
- 2026-09-06：现有仓库是 3-workflow walking skeleton，含 Charter、基础 Artifact validation、Publication freeze、安装历史和 Claude/Codex fail-closed adapter。
- 2026-09-06：冻结 UV 环境下现有 40 项 unittest 全部通过。

## 初始计划

1. 先固定 shared contracts、artifact type 规范、catalog 与统一 validator seam。
2. 并行补齐 canonical workflows、model-invoked disciplines、port records 和 templates。
3. 建立 computational 与 mathematical 两条 deterministic reference execution seam。
4. 集成 manuscript/PDF 与完整 Publication profile。
5. 重建 Adapter projections、历史 replay、远端 BLOCKED 语义和文档。
6. 以 negative fixtures、完整 E2E、独立 harsh review 收口。

## 决策

- 使用 tree-5 orchestrated 模式；各 leaf 以互斥文件所有权工作，主会话只负责 contract、验证和集成。
- `GATES.md` 是根验收账本；每个 leaf/branch 另有 gates 文件。
- gap audit 后固定 URI profile、JSON Pointer scope algebra、Evidence 内嵌 `supports`、Assurance fixed refs、Project principal roles、结构化 migration ranges、staged Publication freeze 和动态 Validation Report。
- 当前缺少产品代码应判 `FAIL / NOT IMPLEMENTED`；只有已实现能力因外部前置条件不可用时才能判 `BLOCKED`。
- 数学 leaf 经多轮 hostile review 加固：未闭合 gap/counterexample 阻断 candidate；review 绑定真实 statement/proof bytes 与 project root；Lean statement comparator 使用保守 kernel probe/builtin closure；axiom 绑定目标 declaration；隔离树重做 probe；sources/config/digests/失败 history 固定；bool 不得冒充整数。
- Lean P0 能力准确限定为无外部依赖、封闭 builtin 命题、可信执行环境中的 `isolated-rebuild`；principal 仅 caller-declared，toolchain 仅 direct executables，TOCTOU 模型非对抗。当前主机无 Lean/Lake，因此真实 E2E 为 BLOCKED/3，不能用 mock 52 tests 代替发布门。
- 不把真实随机模型调用作为 CI 成功条件；workflow execution 使用固定 request/candidate Artifact seam，skills 负责 agent 行为契约，validators 负责可复现事实。
- PDF 产出必须是真实可识别 PDF 字节，不依赖系统 LaTeX；reference project 使用 deterministic 薄 renderer，论文源与 PDF 同时固定进 Publication。
- Lean 若本机固定工具链不可用，核心行为是退出码 3 的结构化 BLOCKED；若可用则必须执行真实 `lake build` 与审计。

## Deviations

- `wt-switch-create` skill 文档引用的原生 `EnterWorktree` 工具在本会话不可用。保守改用 `wt switch --create ... --no-cd --format=json` 创建 worktree，并对所有操作使用绝对路径固定目标，避免误写主 worktree。
- OpenCLI GitHub adapter 只提供登录能力，不能读取 Issue。完成 adapter gate 后改用已安装 `gh` CLI 获取 Issue 原文。
- 第一版 Wave A workflow 试图让 port leaf 自行选择和集成未明确批准的外部来源，被安全门拒绝。保守拆出 port 工作，先只并行实现不需要新外部代码的六个本地模块；社区 port 必须基于用户已给 spec/map 中明确指向且仓库已有审计证据的具体来源，或等待明确批准。
- 2026-09-06：用户明确批准只读拉取并最小适配四个固定来源：`wanshuiyin/Auto-claude-code-research-in-sleep`、`Orchestra-Research/AI-research-SKILLs`、`anthropics/formal-math`、`openai/ten-proofs`；禁止执行上游代码或整体 fork。接纳过程固定完整 commit，只复制获准且通过许可证审查的最小文件集合，评价仅运行本地编写的静态/结构化 harness。
- 2026-09-06：用户明确批准在临时、隔离的 `ELAN_HOME` 中安装官方 elan/Lean 4，并对 `leanprover/lean4:v4.19.0` reference 执行真实正向验收；不得把工具可用性或结构测试冒充 kernel replay 成功。
