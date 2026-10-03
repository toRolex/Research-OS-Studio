# pickup

新会话恢复已经保存的交接。本路线重查事实，不续命，不从零重跑已完成的轮次。

## 先读

1. `skills/general/research-os/PHASE-BOUNDARIES.md`：只用来判断上次离开会话的方式。五个选项的含义以该文件为准。
2. 用户给出的交接路径。证明交接读 `skills/general/research-os/playbooks/proof.md` 与其中点名的轮次文件。改进交接读 `skills/general/research-os/playbooks/improvement.md` 与已保存的改进日志。
3. 工作区里真实存在的 `compute-policy.md` 与 `research-log.md`。路径由用户或项目导航指出。文件不存在就停，并说明缺哪一份。

## 重查

批准、授权和作业分开核对，每一项都指向读到的原文：

- **批准**：交接或日志里用户确认过的范围、命题、写入路径、轮数。没有确认记录就保持未批准。
- **授权**：`compute-policy.md` 的 scope、cost_limit、compute_limit、run_limit、per_attempt 上限、concurrency_limit、retry_limit、valid_for_hours、valid_until。缺字段、单位或过期时间时，该项为 0 或未指定，不是运行许可。`valid_until` 早于本次读取时刻则授权已过期。
- **作业**：`research-log.md` 里的 batch_id、run_id、attempt_id、起止时间、结果状态和产物路径。未知消耗不按 0 释放。运行中的预留仍占额度。

无法核实并发或单编排者是否仍在写账时停止，不另造 runtime。

## 步骤

1. 列出实际打开的文件和未打开的缺口。
2. 用上面三项给出恢复后的边界：哪些已批准，哪些未批准，授权是否仍有效，哪些 attempt 已经记账。
3. 边界清楚且用户要求继续时，回到 `SKILL.md` 重匹配。证明材料进 proof，改进日志进 improvement。其他意图按新任务匹配。
4. 继续执行前重新做启动核对：已消耗 + 运行中预留的最坏消耗 + 本次最坏消耗 ≤ 额度，并核对单次、名额、并发、重试、范围和过期。恰好达到上限可以。不延长 `valid_until`。

## 完成

回复写明读过的路径、恢复出的已批准与未批准边界、授权状态和作业事实。没有这些读取证据时不声称已经续接。
