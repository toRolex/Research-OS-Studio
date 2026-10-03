# experiment-bridge

用户要在一次授权内把已批准计划做到分析和审计。执行步骤仍在叶 skill。

## 适用

已有计划或 tracker，用户要跑完并分析结果。只有计划还没写时，回到入口重匹配 experiment-plan。规模大不自动改去 improvement。

## 步骤

1. 读 `skills/validation-cycle/experiment-bridge/SKILL.md` 全文，并读它点名的 references 与 templates。阶段顺序、子 skill 组合和报告以该正文为准。
2. 读工作区 `research-log.md` 里本批授权，并按 [批次授权](../references/batch-authorization.md) 做启动前检查。默认 `compute-policy.md` 不是这张授权。
3. 检查同时核对：授权是否存在、valid_until 是否已过、scope 是否仍覆盖本次计划与写域、单次额度、累计额度（含仍在跑的预留）、run_count_basis=planned-run 的名额、concurrency_limit、retry_limit。未知消耗不按 0 释放。恰好打到上限可以启动。
4. 任一项失败：停下说明哪一条，不写 started_at，不跑命令，不改实验产物。
5. 全部通过后，已入账的本批确认就是范围内每次启动的用户授权。按叶 skill 执行，不重写它的阶段。每个 attempt 先记最坏预留，再启动；结束后把实际消耗和结果补上。失败、超时、无效仍占额。
6. 删除或覆盖既有实验结果前停下，即使额度还够。用户对本批额度的确认不包含这一次破坏。
7. 交付叶 skill 要求的报告后停止。不进入写作，不延长 valid_until。

## 记账

单编排者追加 attempt：run_id、attempt_id、worst_case_estimate、started_at、finished_at、actual_consumption、result_status、artifact_paths。

获准跑完后，planned-run 次数、费用和算力与授权对得上。被拒场景没有作业产物。

## 停止

缺授权、过期、范围变更、累计越界、并发或重试越界、无法核实运行中预留，都停在作业前。pickup 只重读日志和真实作业状态。
