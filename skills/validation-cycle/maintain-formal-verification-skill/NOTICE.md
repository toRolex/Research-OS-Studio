# NOTICE — maintain-formal-verification-skill 来源与适配

## 上游

- 仓库：<https://github.com/cursor/plugins>
- 子树：`pstack/`
- revision：`88d47514b82e7c44f00f2b2a72ff6dd12158038c`
- 原文路径：`pstack/skills/maintain-formal-verification-skill/SKILL.md`
- 许可：MIT，`Copyright (c) 2026 Lauren Tan`；完整许可文本见同目录 `LICENSE`（与上游 `pstack/LICENSE` 字节一致，git blob `6b5400237fdf6545be0b8fae370d6f2fcff8fb25`，SHA256 `bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e`）。

## 采用与适配范围

保留上游机制：四种结果（in sync、updated、bug、blocked）、只改验证的编辑范围、按代码而非按结果更新、重跑后区分验证漂移与代码 bug、用破坏变体证明更新后的检查仍能失败、同步 commit 的推进规则、报告结构。

本仓适配：

- 改为宿主中立：去掉 Cursor 专属命令、个人规则目录与固定模型绑定；独立复算缺少子代理能力时标 blocked，不以串行自查冒充独立。
- 增加外部假设、材料与依赖版本的同步，以及变化后旧通过失效（stale）的判定。
- 增加原问题、编码定义与定理声明对应审计的重做要求，明确占位符、编译成功与有限数值结果不能升级为原定理成立。
- 与 `create-formal-verification-skill` 的分工写明：项目本地 skill 处理使用期改动，本 Skill 处理合并、未用该 skill 的编辑与累积漂移。
- 未复用上游其他文件；本目录只含正文、许可与宿主元数据。

普通数学证明的审查与修复不在本 Skill 范围，仍由 proof 族能力承担。
