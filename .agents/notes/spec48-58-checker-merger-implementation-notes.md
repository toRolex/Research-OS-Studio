# Spec48 #58 + checker merger implementation notes

## Status

| Work unit | 状态 | 产物 / 验收证据 | 下一步 |
|---|---|---|---|
| 按序合并已验收候选 | done | 当前 worktree 从 `86caa4fd76792b056f31d5c083fb7cd918760a4c` 起；#58 `14a18ce6f34b9caff1181b240e3fe28ab539552f` 以 no-ff 合入为 `335993383223688e086875b23755473105f8db64`，checker `9844d331ac318bad82c9a5eb62257a91e10ad222` 以 no-ff 合入为 `d8d76914d0c65e31f3f4efdac0f3e5e4cc692ceb`。自动合并无冲突标记。 | 无 |
| 合并候选复验 | done | `/tmp/spec48-58-checker-merger/commands.jsonl` 与 `logs/` 记录真实 subprocess 输出和 returncode。scandir sentinel 1 passed；六入口 copier sentinel 1 passed / 6 subtests；#58 定向 23 passed / 52 subtests；联合 238 passed / 139 subtests。全套实际收集 301 个 node ID，执行唯一 node 集合与 collection 精确一致；6 failed / 295 passed / 183 subtests，失败 node 列表与基线文件精确相同。checker 仍为原 9 条诊断，1171-byte stdout 与历史基线 `cmp` 完全一致。 | 无 |
| integration tip / 交付核验 | done | 最终 tip `86caa4fd76792b056f31d5c083fb7cd918760a4c` 已显式 merge（Already up to date）；受影响切片 29 passed / 58 subtests。相对 #58 候选 `skills/` diff 为空，`git diff --check` 通过，#55B 非祖先。报告：`/tmp/spec48-58-checker-merger/REPORT.md`。 | 将候选交 parent 后续唯一 writer；本 worker 不写 integration。 |

## 因果与取舍

- 仅在此独立 T3 worktree 做 Git 合并；不写 integration ref/主目录、不 push、不碰 tracker、不再派发，也不合 #55B。
- 按要求先合 #58 完整候选，再 no-ff 合 checker tracked-scan 修复。Git 自动合并 checker 文件；因此没有需要手工取舍的冲突。复核时须确认 #58 的 `research_asset_problems`、迁移合同与研究资源测试仍在，且 tracked Markdown 的有界祖先枚举及 scandir 哨兵测试保留。
- #58 候选已有的 46 Skills / 338 文件完整安装 hash 证据可复用，前提是本次合并后 `git diff <#58候选> HEAD -- skills/` 仍为空；不重复复制或安装 payload。
- 验证均串行，进程捕获 stdout/stderr 与真实 returncode，单条子进程硬超时 175 秒，`TMPDIR` 放在 `/tmp`。历史六条全套失败与 checker 九条诊断只按精确 node 集合 / 原始 stdout 比较，不按总数量推断。
- 首次 node-set 辅助比较曾把 `-vv` 输出中重复出现的 36 条状态行误报成重复 node；修正为比较唯一 node 集合后，301 个 collection IDs 与 301 个执行 IDs 精确相等，六条失败也与历史列表逐项一致。该记录是验证器解析修正，不是产品测试失败。

## Deviations

- 无产品代码冲突或人工冲突解决；未重写 checker 合同。诊断器路径收窄与 tracked copier 测试均按各自候选原样保留。
