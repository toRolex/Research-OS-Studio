# NOTICE — create-formal-verification-skill 来源与适配

## 上游

- 仓库：<https://github.com/cursor/plugins>
- 子树：`pstack/`
- revision：`88d47514b82e7c44f00f2b2a72ff6dd12158038c`
- 原文路径：`pstack/skills/create-formal-verification-skill/SKILL.md`
- 许可：MIT，`Copyright (c) 2026 Lauren Tan`；完整许可文本见同目录 `LICENSE`（与上游 `pstack/LICENSE` 字节一致，git blob `6b5400237fdf6545be0b8fae370d6f2fcff8fb25`，SHA256 `bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e`）。

## 采用与适配范围

保留上游机制：从代码选目标、让问题决定工具、好检查的判据（忠于代码、能够失败、发现即发现、范围诚实、不依赖工具可读、重跑便宜、与代码同步）、生成项目本地 verify skill、交付前在划痕改动上自证、交接内容。

本仓适配：

- 改为宿主中立：去掉 Cursor 专属命令、个人规则目录与固定模型绑定；派发与独立复核按当前会话真实可用的子代理能力判定，缺失时标 blocked，不以串行代跑冒充独立。
- 增加四类对象区分（代码性质、形式模型、数学定理、普通测试）与不强制全链形式化的边界。
- 增加外部假设、材料、依赖版本、实际覆盖、同步状态与变化失效判断的记录要求。
- 增加原问题、编码定义与定理／检查声明的对应审计，明确占位符、编译成功与有限数值结果不能冒充原定理成立。
- 增加故障暴露证据与「未执行即草稿」的交付状态要求。
- `references/tool-selection.md`、`references/assumption-ledger.md`、`references/correspondence-audit.md`、`templates/formal-verification-record.md` 为本仓新增的共置资源，不复制上游其他文件。

普通数学证明的生成、审查与修复不在本 Skill 范围，仍由 proof 族能力承担。
