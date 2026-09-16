# 历史调研证据索引

> 本文件记录 Issue #25 时的历史归档，不再作为搬运 revision、许可证或产品 gate 的当前真源。六仓 revision 后经核对存在仓库错位，且本文件的 digest／port hard gate 属于已被 ADR-0005 取代的旧架构。后续采用决定以 `docs/upstream-sources-and-licenses.md` 为准。

Issue #24 指定的四份分析材料已从原工作树的 `analysis/` 目录恢复到本目录。下表固定归档副本、原始报告路径、生成报告时审计的上游完整 revision，以及归档副本 SHA-256；不能仅凭日期或浮动分支替代这些 revision。

| artifact | 归档副本与原始报告路径 | 审计来源与完整 revision | SHA-256 |
|---|---|---|---|
| 六仓库横向对比 | `comparison.md` ← `analysis/COMPARISON.md` | `https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git@be4ba4755bf1b52220f25e13b2293b5956590070`；`https://github.com/Orchestra-Research/AI-research-SKILLs.git@0c5d4e13bbb397d80d5cb6cfa29f2eaa1a681f1b`；`https://github.com/aiming-lab/AutoResearchClaw.git@fb96df897dfb99797a77623aa0dd9ee178fe89d2`；`https://github.com/THU-Team-Eureka/EurekAgent.git@228791fb499afffb54b46200aca536f79142f117`；`https://github.com/frenzymath/Archon-Horizon.git@773a52944ba4747a18bd4ae9ade53fff041adcbc`；`https://github.com/karpathy/autoresearch.git@94d8093ed21d20a790830318190095b9f5036ce8` | `598ec19a832406cee5187984ea905e2766e3d3099283a57d12c05cf2fe7e5e2e` |
| ARIS 静态分析 | `aris-report.md` ← `analysis/ARIS/REPORT.md` | `https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git@be4ba4755bf1b52220f25e13b2293b5956590070` | `bb21316c89932d5d69100b96a28303fe59411126e5fab97d6ee6e53a530510e7` |
| AI-research-SKILLs 静态分析 | `ai-research-skills-report.md` ← `analysis/AI-research-SKILLs/REPORT.md` | `https://github.com/Orchestra-Research/AI-research-SKILLs.git@0c5d4e13bbb397d80d5cb6cfa29f2eaa1a681f1b` | `145f59d3c0cf664c0b9108320e519c9c03495475414155f9ed9e77eb4aca7ab9` |
| Anthropic/OpenAI 数学工作流 | `anthropic-openai-math-workflows-20260901.md` ← `analysis/anthropic-openai-math-workflows-20260901.md` | `https://github.com/anthropics/formal-math.git@2bafb8c88f177284a2123b5fefa2ff84e2365eb6`；`https://github.com/openai/ten-proofs.git@94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6` | `982c421522ce88bc7beb6da6e2d617914569cd4f52865ae6147c67db98d6e25f` |

四份归档副本已与上述原始报告逐字节核对；digest 与表中记录一致。上游仓库 URL 与 commit 是报告结论的重放锚点，归档副本是后续实现引用的仓库内稳定入口。

## 原型可达性

- Artifact 最小契约：commit `3428eb72aa31ed532a036909e857e768441c0bcb`，path `prototypes/artifact-min-contract-prototype.html`，对象类型 `commit`，内容可读取。
- Project/Workstream/Publication：commit `6c24ac721af4ccdbc8c57eb980abe006477d477a`，path `minimal-project-workstream-publication-prototype.html`，对象类型 `commit`，内容可读取。
- 两个原型均为契约决策先例，不是生产运行 seam。

## 状态真源说明

GitHub Issues 及其原生 parent/blocked-by/status 关系是当前真源。本归档形成时的 `planning/research-os-wayfinder/`（MAP.md、tracker.json、tickets、resolutions）是早期 local-markdown 历史快照，已在 #36 原子切换中随旧 Wayfinder 规划系统一并删除，仅存于 Git 历史。当前现场存在 T10 `closed` 但 `blocked_by: [T07]` 且 T07 仍 `open` 的矛盾；不改写历史快照，也不将它用于当前阻塞判断。后续实施以 GitHub Issue 状态为准。

## Port hard gate

任何 port 必须先提供 source repository URL、完整 commit、source path、retrieval time、SPDX/license evidence、NOTICE 要求、逐文件 baseline hash、原始流程、依赖、keep/modify/delete/add ledger、不可变来源快照、baseline/adapted eval、reviewer 与人工 `preserve|adapt|reject` 决定。缺来源或许可证证据返回结构化 `BLOCKED`（exit code 3）；`reject` 源码不得进入产品树；评分不能抵消硬门。
