# Spec48 剩余整仓副本隔离

## 状态
- 清点：done；完整入口见 `/tmp/spec48-all-copy-isolation/REPORT.md`（交付时生成）。
- #54/#56：done；`logs/red-workcopy.log` 两 sentinel 失败 exit 1，`logs/green-workcopy.log` 4 subtests 通过 exit 0。
- policy-gates 两入口：done；`logs/red-policy.log` 两目录形态 sentinel 失败 exit 1；`logs/green-policy.log` 6 subtests 通过 exit 0。
- 串行验收、同步 integration、提交：done；实现提交 `fc61cd26b196a4fedc6923d041746c249fe23a6d`，同步 integration `9080258c323917e33af79c0a93a42c68c8473be2` 后 clean 联合 214 passed / 87 subtests，31.03s，exit 0；全套仍为既有六失败（详见下节）。最终完整 SHA/状态/命令见外置 REPORT。

## 边界与决策
- 入口：用户指定 implementation worker，明确不继续派发；直接执行。基线 `9080258c323917e33af79c0a93a42c68c8473be2`，当前 T3 隔离 worktree，不写 integration/主目录，不 push/tracker。
- 已读 Multi-Agent/model-availability/CODING_STANDARDS、pre-implement、`~/.claude/skills/tdd/{SKILL,tests,mocking}.md`、GLOSSARY 与 ADR-0005。
- 沿用已批准测试套件/副本输出合同 seam；不修改产品 checker，不把静态测试外推为科研/runtime 验收。
- work unit 顺序：清点→每一类入口 sentinel 红绿→联合/clean 全套/checker→读取 integration tip、合入自身分支并复验→报告。全部由本 worker 执行，总上下文预算 ≤20%；无新增模型调用。
- `git ls-files` 选择源路径、copy2 复制当前工作内容。初次 git add 必须 force，后续 stage 保持原有 -A，保留损坏/删除反例语义。
- policy-gates 两处内联整仓复制/初始化统一为 copy_worktree，保留其实际测试函数与损坏断言；sentinel 验证该输出 seam 的两种目的目录生命周期，不 mock copier/git/checker 内部。
- 共享 copier 仅增加目的目录可已存在（policy _damaged 的 TemporaryDirectory 本身）。所有调用使用新建/空目录，不删除任何既有证据。
- sentinel 一项测试六个入口 subtests；相比原二入口新增四个反例，仍收集 214 项。检查 ignored/untracked 排除、force-tracked notes/资产保留、index 之后工作区修改、0755 执行位、复制后 git 索引路径集合。红测只复制几十字节的小树，不使用真实大树。

## 验收证据
- 外置报告/完整命令：`/tmp/spec48-all-copy-isolation/{REPORT.md,run-verification.sh}`；日志均在同目录 `logs/`。
- `sentinel-clean.log`：1 passed / 6 subtests，0.28s，exit 0；`joint-clean.log`：214 passed / 87 subtests，31.03s，exit 0。
- `full-clean.log`：6 failed / 271 passed / 131 subtests，45.87s，exit 1。失败 nodeid 集合与 `/tmp/spec48-test-copy-isolation/expected-full-failures.txt` 精确 cmp exit 0（`verification-summary.log`）；未扩大允许集、不修既有失败，不宣称全套全绿。
- `checker-clean.log`：checker exit 1（原九条 archive 诊断），stdout 1171 字节；与 `/tmp/spec48-closed-baseline/logs/head-checker.log` 精确 cmp exit 0。
- `sync-pre-clean.log`：读取 integration tip 后在自己分支 merge，Already up to date，exit 0。实现前后 diff --check 均 exit 0。
- 代码风格验收：KISS（只选 tracked 路径）、YAGNI（不增加产品逻辑或新排除表）、DRY（policy 两段相同初始化收敛）、无 TS 变更。无删除历史证据/超时副本，无父目录测试运行。
- 有界扫描 tests/scripts：整仓入口为 #49 WorkCopy、#51 copy_tree、#54 WorkCopy、#56 WorkCopy、policy-gates 两内联入口。#58 文件不存在。#53/#59 按文件构造 fixture；#49/#54 Skill 单目录 copytree 保持不动。联合直接依赖未发现其他整仓复制。

## Deviations
- 无。
