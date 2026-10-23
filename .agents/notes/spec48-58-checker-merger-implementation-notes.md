# Spec48 #58 + checker merger implementation notes

## Status

| Work unit | 状态 | 产物 / 验收证据 | 下一步 |
|---|---|---|---|
| 按序合并已验收候选 | done | 当前 worktree 从 `86caa4fd76792b056f31d5c083fb7cd918760a4c` 起；#58 `14a18ce6f34b9caff1181b240e3fe28ab539552f` 以 no-ff 合入为 `335993383223688e086875b23755473105f8db64`，checker `9844d331ac318bad82c9a5eb62257a91e10ad222` 以 no-ff 合入为 `d8d76914d0c65e31f3f4efdac0f3e5e4cc692ceb`。自动合并无冲突标记。 | 无 |
| 合并候选复验 | 进行中 | 外置证据目录 `/tmp/spec48-58-checker-merger/`；源代码和 tests 已合并，`git diff --check` 通过；相对 #58 候选 `skills/` diff 为空。 | 执行定向、联合、全套和 checker 精确诊断比较。 |
| integration tip / 交付核验 | 未开始 | 目标 integration tip 为 `86caa4fd76792b056f31d5c083fb7cd918760a4c`。 | 核实 tip 未变，复验必要项，提交本 notes。 |

## 因果与取舍

- 仅在此独立 T3 worktree 做 Git 合并；不写 integration ref/主目录、不 push、不碰 tracker、不再派发，也不合 #55B。
- 按要求先合 #58 完整候选，再 no-ff 合 checker tracked-scan 修复。Git 自动合并 checker 文件；因此没有需要手工取舍的冲突。复核时须确认 #58 的 `research_asset_problems`、迁移合同与研究资源测试仍在，且 tracked Markdown 的有界祖先枚举及 scandir 哨兵测试保留。
- #58 候选已有的 46 Skills / 338 文件完整安装 hash 证据可复用，前提是本次合并后 `git diff <#58候选> HEAD -- skills/` 仍为空；不重复复制或安装 payload。
- 验证均串行，进程捕获 stdout/stderr 与真实 returncode，单条子进程硬超时 175 秒，`TMPDIR` 放在 `/tmp`。历史六条全套失败与 checker 九条诊断只按精确 node 集合 / 原始 stdout 比较，不按总数量推断。

## Deviations

- 尚无。
