# improvement

对已有研究材料做一轮有界 review → repair → re-review。规模大本身不进入本路线；用户要的是在固定轮数和写入范围内改进整体工作时才进入。

## 先读

按路径读完：

1. `skills/writing-cycle/research-improvement/SKILL.md`
2. `skills/writing-cycle/research-improvement/references/loop-methods.md`
3. `skills/writing-cycle/research-improvement/references/composition-map.md`
4. `skills/writing-cycle/research-improvement/templates/improvement-log.md`

组合能力只在 `composition-map.md` 里点名。读那份映射，不把表抄进本文件，也不启动映射末尾列出的顶层入口。

## 阶段角色

Role: orchestrator

持有授权、轮次、单一账本与亲核。

Role: reviewer

每轮 fresh 独立审查。

Role: implementer

代码修复与获准补实验执行。

Role: analyst

分析修复与结果核对。

Role: writer

正文修复与报告。

Role: prover

仅适用的证明修复／核对；不扩大叶授权。

## 步骤

1. 先过 `research-improvement` 的 loop-authorization 门。scope、写入范围、最大轮数、资源预算、副作用、正面结论标准和停止条件逐项确认。未确认的项不执行。
2. 冻结基线：Claims 或草稿、方法与代码、原始结果、当前 diff、历史 findings。已有改进日志是待核实输入，不是已成立结论。
3. 每一轮由 fresh reviewer 直接读当前 primary artifacts。同上下文自查标成自查，不冒充独立审查。
4. 只在写入范围内做最小修复，并留下验证证据。补实验另过 experiment-topup 门；进入该分支必须先完整读 [批次授权](../references/batch-authorization.md)，再核本批研究日志，不把 loop 授权或默认政策当运行许可。每次启动同时核 scope、valid_until、per_attempt 单次额度、已消耗＋运行中最坏预留＋本次最坏消耗的累计额度、run_count_basis=attempt 的剩余名额、concurrency_limit 与 retry_limit；无法核实任何一项就停在作业前。名额按 attempt 计，失败、超时、无效也占名额；未知消耗保留预留。单编排者先记预留、结束按原始命令证据补实账。重试额度不代替修复轮数；叶 skill 的科研步骤不在此重写。
5. 用 `skills/writing-cycle/research-improvement/templates/improvement-log.md` 的骨架写本轮日志。原始审查回应逐字保留。日志写入用户授权的位置；没有授权时只在对话交付。

## 完成

报告能对上实际读取和修改：轮次、分数轨迹、已修与未解决 findings、停止原因。达到轮数、预算、名额或正面结论后停止。不自动开始下一轮，也不自动进入投稿或新的顶层 Workflow。
