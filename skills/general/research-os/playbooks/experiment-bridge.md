# experiment-bridge（Research OS 配方）

“实验桥接”可继续作为用户表达“按计划跑实验”的目标路由名，但不是可安装或可调用的 Skill。实验的执行控制、授权账本、作业身份、恢复与初步报告只有 `run-experiment` 一个权威入口；本配方不得复制其控制步骤。

## 适用

用户已有计划或 tracker，要求在当前委托内落实并执行。仅需计划时路由到 `experiment-plan`；已知问题、计划与本批授权均齐备后，执行分支进入 `run-experiment`。规模大不自动改去 `research-improvement`。

## 配方

1. 读取 `skills/validation-cycle/run-experiment/SKILL.md` 全文、`skills/validation-cycle/run-experiment/references/composition-map.md` 与本次相关引用；不要再查找或安装旧 bridge Skill。
2. 将实现、审查、sanity、单次／批量执行、研究日志记账、恢复和初步运行报告全部交给 `run-experiment`。它是唯一执行控制，授权与额度不由本配方重新核验或复制；批次授权字段见[批次授权参考](../references/batch-authorization.md)。
3. 只在用户委托要求时，分别调用独立 `monitor-experiment`、`training-health-check`、`analyze-results`、`experiment-audit` 或 `result-to-claim`；每项只承担自身观察、诊断、分析、审计或 Claim 判断职责。缺少被要求的能力时，仅该分支标为 `blocked`，不得把缺失当作通过或已完成。
4. 把独立能力的只读结果并入统一运行报告对应章节；不得启动第二个运行控制器、重置授权、自动追加消融或开始下一 Workflow。
5. 交付用户要求的报告后停止；不自动转入写作、投稿或下一批运行。
