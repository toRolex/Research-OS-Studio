# Spec48 product candidate promotion implementation notes

## 状态

| Work unit | 状态 | 产物与验收证据 | 下一步 / 阻塞 |
|---|---|---|---|
| 精确源并入隔离候选 | done | 候选分支 `t3/integrate-product-candidate` 起于 `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e`；no-ff 合入源 `9945b67d585ccede0f09ae7321e192c90e0b77ec`。 | 无 |
| 产品树与定向合同复验 | done | 产品 `skills/` 与 `fd3d5e165423f9e4f3e7d335796d0552619a6cb7` 相同；源差异仅两个测试与源 notes。#49 22 passed + 2 subtests、argv 1 passed；A/B 3 passed、C 7 passed + 16 subtests、D 5 passed + 30 subtests；逐命令真实 rc 均为 0。checker 实际 rc=1，1171 字节与原 baseline `cmp` rc=0（原 9 条）。命令树外 TMPDIR 串行执行，单条 timeout 175s。 | 无；不重跑完整 suite。 |
| integration fast-forward | 待验收 | integration checkout 开工时精确基线 `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e` 且 clean；候选产品树与指定父提交一致。 | 提交本 notes 后重新预检 clean/祖先关系，再仅用 `--ff-only`。 |
| 本次记录与交接报告 | 进行中 | 目标报告 `/tmp/spec48-product-promotion/REPORT.md`。 | 完成 integration 预检与 fast-forward 后写入最终 SHA/双亲/clean/证据边界。 |

## 决策

- 入口判定：按用户明确授权直接执行；输入 SHA、集成目标、唯一 writer、禁止操作和验收边界均已给定。用户禁止继续派发，因此本轮不派发。
- 当前 T3 worktree 是独立候选分支，精确起于 integration 的本地 tip；不另建或操作第二候选。candidate 内仅 no-ff 合入精确源，不对 integration 执行任何重置或清理。
- 复用三份指定报告中的完整 suite / 真实 41 包安装 / checker 证据，不重复全套；本轮仅复验用户指定的短测试和合同节点。六项历史 suite 失败与九条 archive checker 诊断必须保留，不能称全绿或 #60 完成。
- 仅新增本文件并单独暂存/提交；不改产品文件、不 push、不操作 tracker、main 或主目录，不改 allowlist/历史证据、不关票。

## Deviations

- 无（截至当前）。
