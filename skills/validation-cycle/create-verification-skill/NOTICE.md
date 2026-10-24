# NOTICE — create-verification-skill 来源与适配

## 上游

- 仓库：<https://github.com/cursor/plugins>
- 子树：`pstack/`
- revision：`88d47514b82e7c44f00f2b2a72ff6dd12158038c`
- 原文路径：`pstack/skills/create-verification-skill/SKILL.md`
- 许可：MIT，`Copyright (c) 2026 Lauren Tan`；完整许可文本见同目录 `LICENSE`（与上游 `pstack/LICENSE` 字节一致，git blob `6b5400237fdf6545be0b8fae370d6f2fcff8fb25`，SHA256 `bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e`）。

## 采用与适配范围

保留上游机制：先采访仓库后生成、启动就绪判据（可用而非进程有响应）、doctor 前置检查、真实用户路径与副作用旁证的证据标准、只杀自己启动的实例、证据在清理后存活的清理语义、特征映射播种与四个固定小节、交付前自证、未执行即草稿、替身差距逐项记录。

本仓适配：

- 改为宿主中立：去掉 `.cursor/skills/` 专属路径与 Cursor 品牌绑定，写为项目本地 `verify-<app>/`，派发与独立复核按当前会话真实可用的子代理能力决定，缺时标 blocked。
- 增加研究委托合同（「委托继承」小节）：授权内项目内动作自动进行，越权、超额、未授权全局安装或外部上传仍需用户决定。
- 增加与形式化能力的分工边界：本 Skill 只做软件行为验证，不冒充数学定理验证；形式化对象由 `create-formal-verification-skill` 负责。
- 增加执行失败、项目不可达与草稿的如实报告要求，清理后保留证据。
- 增加随附 helper `helpers/feature-map-lint.py`（本仓新写，MIT，随本 Skill 发行）用于特征索引一致性检查。
- 上游 `references/feature-map-example/` 三个示例文件改写为本仓示例（机制保留：索引加每特征文件、四个固定小节、Gotchas 记录前置缺失）；未复用上游其余文件。

## 分工

形式化检查（代码性质、形式模型、定理编码）由 `create-formal-verification-skill` 与 `maintain-formal-verification-skill` 承担；本 Skill 不做范围内每种情况的检查，也不把行为验证冒称定理成立。
