# Ticket 42 implementation notes

任务：Validation 的 experiment-plan / experiment-bridge 路由与批次预授权闭环。基线 `v2/ticket-42` @ `f94fc10`，与 `integration/research-os-v2` 同提交。合同：`/tmp/research-os-v2-notes/shared-contract-approved.md`，GitHub #42 / #37。

## 决策

- 不新增 checker，不新增 runtime。授权判断留在 playbook；`scripts/check-skills.py` 只继续做路由行、反引号级联和既有政策模板字段。
- 叶 skill 正文不改。编排差额只写在 research-os playbook：已记入研究日志的本批确认，就是范围内作业的用户授权；默认 `compute-policy.md` 不是这张授权。
- 账本形状只有 `skills/general/research-os/references/batch-authorization.md` 一处。playbook 指向它，不把额度算术再抄一遍。
- 行为证明用真实 `pi -p` 在临时工作区跑，工具是 read/write/edit/bash。静态测试只锁路由和引用。

## 证据

- 红：`uv run python scripts/test_check_skills_ticket42.py` 在 playbook 落地前失败（缺路由行、缺文件）。绿：同命令 3 通过；`uv run python scripts/check-skills.py` 为 OK 39。
- 行为：`/tmp/ros42-cases/{missing,expired,scope,exact,cumul,concur,retry,unknown,delete,loop}`。宿主 `pi --session … -p`，工具 read/write/edit/bash，模型 cliproxy/grok-4.7 thinking off。拒绝场景无 `results/out.txt`。exact 与 loop 有真实 `printf` 产物 `ok`。loop 日志两笔 completed 对上 2 USD / 0.2 cpu-core-hour / 2 planned-run，第三笔 refused 且无 started_at；默认政策仍为 0；`results/run.csv` 保持 `seed result v1`。

## Deviations

- 开工时远程 `origin` 没有 `integration/research-os-v2`，本地与本分支都是 `f94fc10`。报告前该本地分支已前进到 `28d010b`（#41 idea-discovery、#43 paper-writing）。先提交本票再 merge。冲突只在路由表和 PRODUCT-MAP：两套行都保留，未交付名单去掉已落地的 idea-discovery、experiment-plan、experiment-bridge、paper-writing。merge 后重跑 check-skills、ticket38、ticket42、ticket43，全绿。
- 行为会话是被测编排者，不是当前实现会话。`pi --no-session` 不留 jsonl，已改成显式 `--session`。
- 低消耗作业是本地 `printf`，不是叶 skill 的完整科研阶段。叶正文未改，轨迹证明的是授权门，不是 experiment-bridge 全阶段科研质量。
- loop 拒绝行多写了 `reservation_status` 与 `## attempt R003 refused`。合同字段都在；多出来的行不释放额度。
