# Research OS Wayfinder Map 创建记录

## 目标

把已经明确的 destination 和剩余架构决策绘制为 local-markdown Wayfinder map；后续每个会话只解决一个小 decision ticket。

## 决策

- 本目录不是 Git 仓库，也没有已配置 issue tracker，因此采用默认 local-markdown tracker。
- `tracker.json` 保存 parent、blocked-by、status、assignee；Markdown ticket 保存人类可读问题。
- 不创建 scheduler、状态 runtime 或 tracker 代码。

## Deviations

- Destination 已经足够明确后，主会话仍连续追问 Q13-Q16，行为退化为普通 grilling，没有及时 chart map。用户指出后停止深挖，把所有细节改为小 ticket。
- 原计划写一个 `tracker.py` 查询器，被规划阶段 skill guard 阻止。保守改为 `tracker.json` + 现成 `jq` 查询，不引入代码实现。

## T10 实施记录

- 先读取 T10、T07-T11、D01-D05 与产品约束；GitHub Issue API 因网络 EOF 不可用，未虚构 Issue 正文，改以仓库内 ticket 和既有决议为准。
- 采用细粒度数学 workflow：conjecture exploration、example/counterexample、formal statement、lemma map、proof attempts、proof review、statement revision、Lean formalization、kernel verification、paper alignment。每个 workflow 独立由用户调用，完成后停止。
- 将反例、失败尝试和 statement revision 作为版本化 artifact 保留；明确 `supersedes` 与其它 typed relations，避免隐式覆盖和中央编排。
- 将 kernel verification 设为形式证明 claim 的硬边界：必须保留固定 toolchain/依赖、build/kernel 结果、provenance 以及 axiom/`sorry` 使用记录。
- 新增 `resolutions/T10.md`，更新 T10 ticket、`tracker.json` 和 `MAP.md`；没有引入运行时代码，因此无代码测试适用。

## Issue #25 交接说明

- 本地 Wayfinder 文件属于历史规划快照，不是当前状态真源；当前规划、状态与依赖以 GitHub Issues 及其原生关系为准。
- T10 在快照中为 `closed`，但 `blocked_by: [T07]` 且 T07 仍为 `open`；该矛盾保留用于历史追溯，不应据此阻塞 Issue #25 或后续实现。
