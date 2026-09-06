# ADR-0004：社区 port 的来源与许可硬门

- 状态：已接受
- 日期：2026-09-04
- 范围：外部社区能力接纳

## 决策

Research OS 采用 port-first、minimal adaptation。每次 port 只接纳一个明确能力，不整体 fork 自动科研 runtime。接纳前必须固定 source repository URL、完整 commit、source path、retrieval time、SPDX/license evidence、NOTICE 要求、逐文件 baseline hash、原始流程、依赖、keep/modify/delete/add ledger、不可变来源快照、baseline/adapted eval、reviewer 和人工 `preserve|adapt|reject` 决定。

来源证据或许可证证据缺失时，validator 必须输出结构化 `BLOCKED`，退出码为 3；不得以评分、代码质量或人工猜测绕过硬门。`reject` 的源码不得进入产品树。所有被接纳内容必须保留原流程说明、改造理由和对照评估，优先只删除自动跨 workflow 推进、provider 绑定及与 Core 冲突的部分。

## 原因

社区资产的来源、许可和行为差异不可从名称或 README 推断。完整 provenance 和 baseline/adapted eval 才能让接纳决定可重放、可审计，并防止 port-first 滑向无证据重写。

## 后果

- `ports/<port-id>/PORT.yaml` 是每项接纳的规范记录。
- 评估只排序候选，不能抵消来源、许可或越权 blocker。
- 被拒绝的源码可以留在外部评估区或记录中，但不能被产品构建和发布流程拾取。

## 证据

`CONTEXT.md`、`PRODUCT.md`、`planning/research-os-wayfinder/resolutions/D04.md`，以及 `docs/research/sources/comparison.md` 中对参考仓库许可证和自动推进风险的审计。
