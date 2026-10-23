# Spec48 测试副本隔离修复

## 状态
- 定位／候选合入：done；候选 d54606a81097bd5353cc35c9878817c77dee9335，证据 `/tmp/spec48-test-copy-isolation/logs/before-and-candidate.log`。
- 单切片 red→green：done；`logs/red.log` 两入口 sentinel 断言失败，exit 1；`logs/green.log` 1 passed + 2 subtests，exit 0。fixture 同时验证所有 tracked 资产字节／tracked 状态及未提交 tracked 修改，无大型目录。
- 串行联合／checker／适用全套：done；联合 214 passed + 83 subtests（29.21s，exit 0）；checker exit 1，原 9 条诊断逐字节 cmp=0；全套 6 failed + 271 passed + 127 subtests（43.07s，exit 1），失败 nodeid 与候选原六项一致。日志 `/tmp/spec48-test-copy-isolation/logs/`。
- 提交／交接：待验收；本记录与 helper／回归同提交，最终 SHA／前后状态／退出码见 `/tmp/spec48-test-copy-isolation/REPORT.md`，由 merger 推进，不更新 integration、不 push、不动旧 ignored 树。

## 决策与范围
- 本任务是明确禁止继续派发的 implementation worker，直接执行；模型可用性已检查，未调用其他模型。
- 已批准 seam 为 Spec48 结构／合同检查，不新增 runtime。预算内依次完成定位、单切片、验证、交接。
- 原 `copytree(ROOT)` 将 ignored notes 当产品复制；全局排除 `.agents` 又会丢 tracked 小 notes。选择 `git ls-files -z` 枚举、复制当前工作文件，保留 staged/未提交的 tracked 修改，不用仅含 HEAD 的 archive。
- 仅替换 #49/#51 helper；其他票 helper 不在范围。checker 按 tracked 文件判断资源，初始化副本时 force-add 的对象仅为已枚举的 tracked snapshot。
- 验收逐项核对 KISS／YAGNI／DRY：一个共享复制函数、仅两个调用点、无产品 runtime／配置扩展。Git 独立 worktree；Python 全部 uv。未用 gh、未操作 tracker／远程。
- 全套不是绿色：六项既有失败仍受 archive 缺失约束，不通过删除证据或扩大历史允许集掩盖；后续仍归原修复工作。

## Deviations
- 无。原始日志及报告写到 `/tmp/spec48-test-copy-isolation/`，只精确 force-add 本小记录。
