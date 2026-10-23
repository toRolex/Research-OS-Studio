# Spec48 四切片 promotion implementation notes

## 状态

| Work unit | 状态 | 产物与验收证据 |
|---|---|---|
| 精确候选 promotion（#51/#56/#57/#58） | done | `integration/spec-48` fast-forward 到 `23a72ef8d7d58d0dd2515a92e88adf03a85054c3`；该提交含既有 checker 修复与 copy 隔离。 |
| 当前 checkout 定向验收 | done | tracked-scan 1 passed；copy sentinel 1 passed、6 subtests；#58 23 passed、52 subtests；checker stdout 1171 bytes 与既有基线逐字节一致。 |
| 精确 tracked-tree 验收 | done | `git archive` 导出的索引 `write-tree` 与候选 `HEAD^{tree}` 同为 `3a7fbb699ef009f7887d81b895844e1381129197`；联合组 238 passed、139 subtests，真实 returncode 0。 |
| 最终记录与状态 | done | 验收报告：`/tmp/spec48-promote-four/REPORT.md`；本记录单独提交，未暂存父级 notes 或证据目录。 |

## 决策

- 入口判定：按用户指定直接执行；该任务边界精确、输入候选与验收报告已给出，且明确要求唯一 writer、不继续派发。
- 只在确认工作树 clean、候选存在且当前 tip 为候选祖先后运行 `git merge --ff-only`；未 reset、clean、push、操作 tracker、主目录或 main。
- 不在集成 checkout 重跑 238 项联合组；在从精确候选 `HEAD` 导出的 tracked-only 树中验收，并以 `write-tree` 与原提交树相等证明验收载体内容精确。
- 不重跑全套或安装：源报告已对同一代码候选记录 301 节点全套为 6 个历史失败、295 通过；Skills payload 与 `14a18ce6f34b9caff1181b240e3fe28ab539552f` 无差异，故复用 `/tmp/spec48-58-checker-merger/REPORT.md` 所引用的 Skills CLI 1.7.4 安装证据（46/46 Skills、338/338 文件）。

## Deviations

- checker 验收包装器曾把含标题的 10 行输出误判成“应有 9 行”并返回 1。实际 checker returncode 为 1（符合已知基线），9 条诊断 bullet 的完整 stdout 与基线 1171 bytes 逐字节相同；因此按诊断条目而非总行数判定，无需重跑 checker。
- 本次只接受 #51/#56/#57/#58 集成切片；不代表 #48 完成或全库全绿。历史 6 个全套失败与 9 条 checker 诊断保留并明确记录，不自行关闭 issue。
