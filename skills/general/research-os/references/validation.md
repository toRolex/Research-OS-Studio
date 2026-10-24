# Validation

状态词见 [PRODUCT-MAP.md](PRODUCT-MAP.md)。目标是计划、跑实验、解释结果、形成候选 Claim，或走数学／理论证明时阅读。

## 计算／实证

### 独立用户入口

| 入口 | 角色／状态 | 选择依据、结果与停止边界 |
|---|---|---|
| `experiment-plan` | U／已实现（#9） | 已有研究问题尚缺可执行计划；明确 hypothesis、baseline、metric、ablation、固定评价面、修改范围、预算和失败含义，只产计划 |
| `run-experiment`（“实验桥接”为 Research OS 需求路由名） | U／已实现（#10、#56） | 已有获批计划，需在本批授权内实现、code review、sanity、正式／批量运行与初步收集；唯一执行控制。监控、健康诊断、分析、审计与 Claim 判断仍由独立能力承担；不要求先用本产品规划 |
| `result-to-claim`（Results-to-Claims） | U／已实现（#14） | 已有外部或本产品结果，需判断能说什么；区分 Evidence 存在、统计可信度、支持程度与 Claim scope，将部分支持缩窄为可辩护主张。最终采用由用户决定，产出候选 Claim 就停 |

### 内部能力与局部点名入口

| 能力 | 角色／状态 | 职责边界 |
|---|---|---|
| `run-experiment`、`experiment-queue` | M／已实现（#10、#56） | run-experiment 唯一负责执行控制、review、sanity、运行与初步收集；queue 独立管理批量；使用当前批准计划／修改范围／资源，保留 baseline 及成功、失败、无效、超时全部 attempts |
| `monitor-experiment` | M／已实现（#11） | 观察 running/completed/crashed 等事实；不判 Claim，不自动分析或控制作业 |
| `training-health-check` | M／已实现（#11） | 固定观测中的 NaN、发散、OOM、停滞、日志缺失；只诊断与建议，不自行 kill／重启 |
| `analyze-results` | M／已实现（#12） | baseline、全部 attempts 与失败记录；重复试验、不确定性、选择偏差、多重比较；单 metric winner 不是科学结论 |
| `experiment-audit` | M／已实现（#13） | protocol conformance 与独立真实性审查分开；直接读 evaluator、代码和原始结果，查 fake ground truth、phantom results、遗漏 attempts、scope overclaim；默认只报告，不修代码或补实验 |

已有结果时，运行是否结束、训练是否健康、统计是否可信、结果是否真实、能支持何种 Claim 是不同问题，不推荐重跑全部流程。付费、远程写入、高成本操作需对应 Workflow 的必要授权，Research OS 不配置 Python／GPU／SSH／Slurm 等环境。

## 数学／理论

| 入口／能力 | 角色／状态 | 选择依据与边界 |
|---|---|---|
| `formula-derivation` | U／已实现（#16） | 独立推导入口；委托组合时保持公式、假设与解释边界，不自动升级为证明或调用其他叶 Skill |
| `proof-writer` | U／已实现（#16） | 独立证明构造入口；固定命题，保留失败路线与教训，不把尝试当证明成功 |
| `proof-review` | U／已实现（#17） | 独立只读审查入口；每次 fresh 读取当前证明并返回 findings，不改命题、证明或 LaTeX |
| `proof-repair` | U／已实现（#17；#55 委托迁移） | 独立调用补齐有限修复契约；在 `/research-os` proof 委托中继承既有写域与额度，只按 finding 修复，命题／假设变化仍由用户决定。必须 fresh 复审；审查能力缺失时不得声称完成 |
| 证明审计、独立意见、记号与交接方法 | `proof-review` 随包参考（非总控） | 按当前审查分支读取；独立审查必须由真实隔离 reviewer 执行，提示模板不授权外发或新额度 |
| Lean premise／lemma search、LSP、Mathlib 规范与 kernel／build 检查 | `proof-review` 的按需参考，不是独立 Skill 或前置门 | 仅当前分支涉及 Lean 时按 proof-review 索引读取随包方法；premise 搜索结果是候选，需读 signature；LSP 是快速反馈，kernel／build 才是形式化检查。无 Lean 继续普通推导／证明，形式化标未验证；不安装工具链或引入 Archon runtime |
