# proof

跨会话续接一个已固定的证明 obligation。本路线只调度已有证明合同，不重写证明引擎，也不另建状态机。

## 先读

按路径读完这些正文，再动手：

1. `skills/validation-cycle/proof-orchestrator/SKILL.md`
2. `skills/validation-cycle/proof-writer/SKILL.md`
3. `skills/validation-cycle/proof-review/SKILL.md`
4. `skills/validation-cycle/proof-repair/SKILL.md`

续接还要读用户指定的旧轮次目录里实际存在的 `task.md`、`local-proof.md`、`audit.md`、`next.md`、`handoff.md`。文件名不同时按内容角色定位。缺文件就列出缺口，不按记忆补。

## 阶段角色

Role: orchestrator

轮次授权与交接。

Role: prover

固定命题的本地证明与获准修复。

Role: reviewer

fresh 只读证明审查；串行自查明示非独立。

## 步骤

1. 固定命题、量词、假设和允许引用的来源。新增假设或弱化结论只提议。旧轮次授权不继承。
2. 经过 `proof-orchestrator` 的 round-scope 门：本轮唯一 obligation、新输出目录、有限尝试预算，都要本轮明确授权。旧目录只读。
3. 有上一轮材料时，只继承已经核对过的结论、失败路线和未解决项。上轮写着「完成」不能盖住缺口。外部答案原文保持未审，直到相关步骤被重新核对。
4. 本轮本地尝试沿 `proof-writer` 的固定命题合同：命题不变，缺口、失败路线和教训留下。自查沿 `proof-review` 的只读义务，自查不写成独立审查。
5. 用户另行授权修复时才进入 `proof-repair`。反例成立时停止，不改命题、不加隐藏条件。
6. 阻塞或用户要求交接时，才按 `proof-orchestrator` 第 5 节准备手动交接包。远程、上传、付费先过 external-action 门。

## 完成

本轮目录里能读到精确命题、继承状态、唯一 obligation、已核对结论和停止原因。没有这些文件时，只在对话交付诊断并停止。不自动进入论文或改进路线。
