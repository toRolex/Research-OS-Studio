# 组合映射

`research-improvement` 在一次授权内组合哪些内部能力、在哪一步、以何种产出贡献正文报告。被组合能力只在原委托已覆盖的职责、写入范围和资源授权内工作；本映射不是自动调用链，也不授予被组合能力之外的权限。授权入口遵循 `research-os` 迁移边界：已迁移能力沿用委托，已迁移能力不要求另行点名；未迁移叶仍执行其自身门。此规则不自动启动另一个顶层 Workflow。

能力目录、分支依赖与安装后解析方式见[安装依赖](dependencies.md)。

| 本 Workflow 阶段 | 组合的内部能力 | 贡献的正文报告章节 | 不做的事 |
|---|---|---|---|
| 独立审查 | `paper-claim-audit` | 数字、比较、配置、表格/caption、实验覆盖的独立发现 | 不改稿，不替代引用/证明/论证审查 |
| 独立审查 | `citation-audit` | 引用身份、元数据与语境支持的发现 | 不改 BibTeX 或正文 |
| 独立审查 | `claim-stress-test` | 整篇拒稿论证与独立裁决 | 不替代数字/引用/证明专项审查，不作最终裁定 |
| 独立审查 | `proof-review` | 现成证明的义务、缺口、反例与影响范围 | 只读，不改证明、不编译 |
| 独立审查 | `experiment-audit` | protocol conformance 与独立真实性审查 | 不修代码，不重跑实验 |
| 独立审查 | `analyze-results` | 描述统计、不确定性、选择偏差与多重比较 | 不补实验，不改代码 |
| 授权内补实验 | `run-experiment` | 单次/少量运行的实现、sanity 与 attempt 记录 | 不改 hypothesis/metric/预算，不自动分析或转 Claim |
| 授权内补实验 | `experiment-queue` | 多作业批次、波次状态与失败留存 | 不引入常驻 scheduler，不自动扩预算 |
| 授权内补实验 | `monitor-experiment` | running/completed/crashed/unknown 运行事实 | 不判 Claim，不触发分析，不停止或重启作业 |
| 授权内补实验 | `training-health-check` | NaN/发散/OOM/停滞/日志完整性诊断 | 不停止或重启作业，不写研究结果 |
| 修复后验证 | `paper-compile` | 真实 build/error、PDF 与格式发现 | check-only，不改源码，不自动启动修复 |

被组合能力不可用或超出原委托授权时，在正文报告对应章节如实标注缺口并停止该分支，不伪造其输出，不以执行者摘要代替其直接读取。独立 reviewer 不可用时，review/repair/re-review 轮统一标 `blocked`；可附只读自查建议，但不计为 fresh 独立审查，也不算完成该轮。

## 本 Workflow 不启动的顶层入口

以下均为 user-invoked 顶层入口，只能由用户另行显式调用；本表不要求已迁移的内部能力再次点名。`research-improvement` 不自动启动这些顶层 Workflow、不代为授权、不据其名称暗示已执行：

- `experiment-bridge`、`experiment-plan`（完整实验计划与执行宏流程）
- `paper-writing`（通用完整写作总流程 #25）
- `paper-writing`（唯一写作组织入口；ML/AI 与 Systems 专业选项由同一入口按需读取资源）
- `paper-compile-repair`、`apply-citation-fixes`、`proof-repair`（专项修复入口）
- `result-to-claim`（#14）、`rebuttal`（#29）、`resubmit-pipeline`（#30）、`paper-talk`（#31）
- `/research-os` 的 proof 路线、`setup-research-os`、`research-os`

需要上述顶层能力时，把精确问题、当前材料定位与建议范围交回用户，由用户另行点名；委托级联到未迁移叶时，则按该叶自身声明的门处理。
