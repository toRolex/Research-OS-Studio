# experiment-plan

用户要把已有研究问题收成有界实验计划。本路线只规划，不跑实验。

## 适用

已有问题、Proposal 或稳定方法，用户要的是计划而不是执行。材料只够写计划时走这里；用户要的是「跑完并分析」时回到入口重匹配 experiment-bridge。

## 步骤

1. 读 `skills/validation-cycle/experiment-plan/SKILL.md` 全文，并读它点名的 references 与 templates。计划内容、阶段和产出以该正文为准。不在这里重写科研流程。
2. 只读本次相关材料。未知项标缺口，不补预算数字。
3. 计划达到「可供执行授权」前，按 [批次授权](../references/batch-authorization.md) 列出本批字段，请用户确认。确认的是这一批，不是工作区默认 `compute-policy.md`。
4. 用户确认本批后，把确认原文、时刻和全部字段写入工作区 `research-log.md` 的新段落。authorization_status 写「本批已确认」。默认政策额度保持 0，不抄进这条授权。
5. 只把计划和 tracker 写到用户允许的路径。已有计划文件先展示差异。删除或覆盖既有实验结果时停，等另一次明确批准。
6. 交付计划后停止。本路线不启动实验，不把本批确认交给 bridge 自动开跑。

## 停止

计划未达到可授权时，交付标了缺口的草稿并停止，研究日志不写运行许可。用户拒绝本批确认时，保留已有材料，不写 authorization_status。
