---
name: proof-orchestrator
description: 旧名称兼容入口；把长期证明、续接与交接任务交由 research-os proof 配方统一编排。
disable-model-invocation: true
license: MIT
metadata:
  author: Research OS Studio contributors
  upstream: wanshuiyin/Auto-claude-code-research-in-sleep
---
<!-- argument-hint: "[原数学目标；可附已有证明、审计或交接材料]" -->

# Proof Orchestrator 兼容入口

## 委托继承
Gates: none

此 Skill 保留旧名称，供已有调用者平滑进入统一数学研究入口；它不再是独立 Workflow 或第二总控。当前委托中的目标、写入范围、额度、轮次/重试、暂停/恢复与停止，唯一由 `/research-os` 的 proof 配方和研究委托合同控制。`research-improvement` 已是其自身的委托继承叶能力；本兼容入口不另建跨研究改进循环。

从 `/research-os` 级联进入时，按调用者的配方继续；直接点名旧 Skill 时，将原请求和已有材料交给 `/research-os` 的 proof 路线，不缩小目标、不重置预算、不重复索取已覆盖阶段或重试的许可。若当前安装无法到达 `/research-os`，只说明该兼容目标缺失并请求调用/安装该入口；不要在此重建旧总控。

## 保留的方法资源

下列随包材料仍是局部数学方法，可按 proof 配方当前需要读取；它们不创建独立授权、轮次或恢复机制：

- [证明审计准则](references/proof-audit-rubric.md)：逐步核对定理条件、推理、边界与原结论。
- [审计输出约定](references/audit-output-contract.md)：保留定位、状态、来源与范围等审计证据。
- [独立意见](references/independent-review.md)：说明独立审查的边界、材料和返回核验。
- [记号审查](references/notation-audit.md)：按触发条件执行七行符号审计。
- [Lean 方法](references/lean-methods.md)：可选的候选搜索、LSP 与 kernel/build 覆盖边界；Lean 不是前置条件。
- [提示模板索引](references/dispatch-prompts.md)：本地证明、续接、手动交接、独立意见、显式发送、回传审计、格式修复及聚焦重做模板。
- [压力测试](references/stress-tests.md)：维护者对数学和交接边界的回归场景。

提示模板索引继续链接到其本地 `references/prompts/` 文件；许可证与来源说明见随包的 [LICENSE](LICENSE) 和 [NOTICE](NOTICE.md)。所有本地方法、审计、Lean、符号和交接材料均随本 Skill 保留。引用其它能力时按 Skill 名称定位，并由该 Skill 读取自己的随包规则；不依赖开发源码树中的兄弟目录。

## 职责边界

- 证明构造由 `proof-writer` 承接；公式与假设尚未固定时可用 `formula-derivation`。二者保持独立职责，不互相自动启动。
- 数学审查由 `proof-review` fresh 读取当前原文并只读返回 findings；修复由 `proof-repair` 在 finding 和当前委托写域内执行。自查不代替审查，修复者不代替 reviewer。
- 形式化按需评估，不强制把整条证明链 Lean 化。交接与外部发送仍按委托中的相应决定门处理；模板本身不授权上传、付费、远程操作或新一轮额度。

完成条件：旧调用已进入 `/research-os` 的 proof 配方，或因该入口不可用而明确停止；本 Skill 未自行启动一套轮次、额度或暂停恢复控制。
