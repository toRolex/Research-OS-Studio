# 批次授权

本文件是 experiment-plan 与 experiment-bridge 的唯一授权账本。默认政策不是本批授权。

## 默认政策

工作区 `compute-policy.md` 只给下一批的起点。未配置时范围未指定，费用、算力和运行数都是 0，有效期 0 小时。它不能启动作业，也不能填进研究日志的授权状态。

## 本批确认

计划获准时，把用户当场确认的本批授权写入工作区 `research-log.md`。字段复用政策名，并加上批次身份：

- scope：计划、允许写域、环境。未指定则本批不能执行。
- cost_limit、currency：有限非负费用与币种。
- compute_limit、compute_unit：有限非负算力。单位只能是 cpu-core-hour 或 gpu-device-hour，异构各写一行。
- run_limit、run_count_basis：非负整数。experiment-bridge 用 planned-run；research-improvement 用 attempt。本文件不改后者。
- per_attempt_cost_limit、per_attempt_compute_limit：与累计同单位，且不大于累计上限。
- concurrency_limit：非负整数。要启动时至少为 1。
- retry_limit：每个 planned run 还能追加的 attempt 次数。重试额度不代替修复轮数。
- valid_for_hours：有限非负小时。valid_until：带时区的 ISO8601。
- batch_id、plan、mode、user_confirmation、confirmed_at、confirmation_basis、authorization_status。

禁止 unlimited、负数、NaN 和无单位。not-applicable 必须写出原因。未知项停下来问，不补默认数。

setup 不改已有研究日志。本批确认是新的授权段落，不覆盖旧批次。

## 启动前

单编排者写账并启动。无法核实仍在跑的预留时停，不另造 runtime。

同时满足才可启动：

1. authorization_status 是本批已确认，且 confirmation_basis 指向用户原话或原消息，不是默认政策文件。
2. 当前时刻早于 valid_until，scope 覆盖本次计划、写域和环境。范围变了就停。
3. 本次最坏费用不超过 per_attempt_cost_limit，本次最坏算力不超过 per_attempt_compute_limit。
4. 已入账消耗 + 仍在跑的预留最坏消耗 + 本次最坏消耗 ≤ 对应累计上限。恰好等于上限可以启动。
5. planned-run 名额、并发和该 run 的剩余 retry 都还够。每个 attempt 都扣费用和算力。失败、超时、无效也入账。
6. 未知消耗保持预留，不按 0 释放。

## 每次留账

每次 attempt 追加：run_id、attempt_id、worst_case_estimate、started_at、finished_at、actual_consumption、result_status、artifact_paths。

时间与结果取自原始证据：启动前读取系统时钟并记录预留；实际命令开始、结束时间和退出码随 stdout/stderr 一起保留，再据此补账。不以文件时间或估计值回填 started_at/finished_at；缺少实测字段记 unknown，不猜时间或把缺失消耗当 0。算力实测注明覆盖的是作业进程还是包含启动器；部分覆盖不代表完整实耗，未核实份额继续保留最坏预留，不释放为新的可用额度。已有预留足以覆盖本次范围时可完成已批准步骤，但日志不能将未覆盖消耗写成已闭合。

获准后次数、费用和算力要能与授权对上。被拒时不写 started_at，也不留下作业产物。

## 硬停

缺授权、过期、范围变更、累计越界、单次越界、并发越界、重试越界，都停在作业前。

删除或覆盖既有实验结果同样停，等用户明确批准。批准只覆盖这一次破坏，不扩大额度。

pickup 重读真实授权和作业状态，不延长 valid_until。
