# Validation

状态词见 [PRODUCT-MAP.md](PRODUCT-MAP.md)。目标是计划、跑实验、解释结果、形成候选 Claim，或走数学／理论证明时阅读。

## 计算／实证

### 独立用户入口

| 入口 | 角色／状态 | 选择依据、结果与停止边界 |
|---|---|---|
| `experiment-plan` | U／已实现（#9） | 已有研究问题尚缺可执行计划；明确 hypothesis、baseline、metric、ablation、固定评价面、修改范围、预算和失败含义，只产计划 |
| `experiment-bridge` | U／已实现（#15） | 已有获批计划，需一次授权完成实现、code review、sanity、正式／批量运行、监控、收集、分析审计与授权 tracker 更新；不要求先用本产品规划。消融仅建议，不自行扩预算／下一轮；不启动独立 `result-to-claim` |
| `result-to-claim`（Results-to-Claims） | U／已实现（#14） | 已有外部或本产品结果，需判断能说什么；区分 Evidence 存在、统计可信度、支持程度与 Claim scope，将部分支持缩窄为可辩护主张。最终采用由用户决定，产出候选 Claim 就停 |

### 内部能力与局部点名入口

| 能力 | 角色／状态 | 职责边界 |
|---|---|---|
| `run-experiment`、`experiment-queue` | M／已实现（#10） | 完整实现、review、sanity、运行与初步收集链；使用当前批准计划／修改范围／资源，保留 baseline 及成功、失败、无效、超时全部 attempts |
| `monitor-experiment` | M／已实现（#11） | 观察 running/completed/crashed 等事实；不判 Claim，不自动分析或控制作业 |
| `training-health-check` | M／已实现（#11） | 固定观测中的 NaN、发散、OOM、停滞、日志缺失；只诊断与建议，不自行 kill／重启 |
| `analyze-results` | M／已实现（#12） | baseline、全部 attempts 与失败记录；重复试验、不确定性、选择偏差、多重比较；单 metric winner 不是科学结论 |
| `experiment-audit` | M／已实现（#13） | protocol conformance 与独立真实性审查分开；直接读 evaluator、代码和原始结果，查 fake ground truth、phantom results、遗漏 attempts、scope overclaim；默认只报告，不修代码或补实验 |

已有结果时，运行是否结束、训练是否健康、统计是否可信、结果是否真实、能支持何种 Claim 是不同问题，不推荐重跑全部流程。付费、远程写入、高成本操作需对应 Workflow 的必要授权，Research OS 不配置 Python／GPU／SSH／Slurm 等环境。

## 数学／理论

| 入口／能力 | 角色／状态 | 选择依据与边界 |
|---|---|---|
| `formula-derivation` | M／已实现（#16） | 澄清公式链、假设、近似与解释；生成职责，不降格为审计 |
| `proof-writer` | M／已实现（#16） | 固定命题的证明或明确 gaps；保留失败路线与教训，不把尝试当证明成功 |
| `proof-review` | M／已实现（#17） | 只读现成证明，直接报告错误／gaps；可用户点名，不改命题、证明或 LaTeX |
| `proof-repair` | U／已实现（#17） | 用户希望修复已知 gaps；明确 scope、写入范围、轮数及工具授权，命题／假设变化由用户决定 |
| `proof-orchestrator`（规划名 `proof-workflow`） | U／已实现（#18） | 单个复杂长期 obligation 的延续工作；其真实内部组合以后续正文为准，**不宣称它原生调用 `proof-writer`／`proof-review`** |
| Lean premise／lemma search、LSP、Mathlib 规范与 kernel／build 检查 | 专业内部方法（#18，参见 proof-orchestrator 共置 references/lean-methods.md），不是独立已安装 Skill | premise 搜索结果是候选，需读 signature；LSP 是快速反馈，kernel／build 才是形式化检查。无 Lean 继续普通推导／证明，形式化标未验证；不安装工具链或引入 Archon runtime |
