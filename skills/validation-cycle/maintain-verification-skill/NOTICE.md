# NOTICE — maintain-verification-skill 来源与适配

## 上游

- 仓库：<https://github.com/cursor/plugins>
- 子树：`pstack/`
- revision：`88d47514b82e7c44f00f2b2a72ff6dd12158038c`
- 原文路径：`pstack/skills/maintain-verification-skill/SKILL.md`
- 许可：MIT，`Copyright (c) 2026 Lauren Tan`；完整许可文本见同目录 `LICENSE`（与上游 `pstack/LICENSE` 字节一致，git blob `6b5400237fdf6545be0b8fae370d6f2fcff8fb25`，SHA256 `bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e`）。

## 采用与适配范围

保留上游机制：clean/changed/blocked 三态结果、只改验证 skill 自身目录的编辑范围、每特征一个只读源读子代理并发源读波、协调者统一驱动的现场驱动轮、doctor 前置/证据存活/不留残留三条不变量、`verified-unreachable` 需具体前置条件、triage 区分文档漂移/harness 缺口/产品缺陷、一轮已证明修正的交付规则、运行记录留 scratch 不提交。

本仓适配：

- 改为宿主中立：去掉 `.cursor/skills/` 专属路径与 Cursor 品牌绑定；源读波缺少子代理能力时标 blocked，不以串行自查冒充独立复核。
- 增加研究委托合同（「委托继承」小节）：授权内项目内动作自动进行，越权、超额、未授权全局安装或外部上传仍需用户决定。
- 增加与形式化维护能力的分工边界：行为验证维护与形式化检查重新对齐分别由本 Skill 与 `maintain-formal-verification-skill` 承担。
- 增加执行失败、不可达与未执行覆盖的如实报告要求，清理后保留证据。
- 本 Skill 独立安装即可执行；索引体检依据本文的目录 glob 与 README 相对链接规则完成，不依赖创建能力的文件。
- 未复用上游其他文件；本目录只含正文、许可与宿主元数据。
