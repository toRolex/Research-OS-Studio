# #60 契约修复串行 merger 第一小片 implementation notes

## 状态

| Work unit | 状态 | 产物与验收证据 | 下一步／阻塞 |
|---|---|---|---|
| W1：在独立 worktree 串行合并指定基准、C07 与 #45 fixture，并核验两源交叉 | done | 合并候选 `b93492ceb477167ecbc5b37b087e8b89068908ef`；`/tmp/spec48-contract-fix-merger-1/REPORT.md`；回归日志见同目录 `logs/` | 仅候选，不 promotion；其余 A/B/C/安装引用仍在途，由 parent 后续编排 |

## 入口判定与边界

- 入口判定：直接执行。用户限定了两个固定源、串行合并次序、验证清单和候选输出，属于单个可验收 merger unit；用户禁止继续派发。
- 仅合并基准 `f7b03400a4b77bc77265e9076199977815163a87`、C07 源 `72b09012edb5c8c7d4d2bac8daeeb5babbf5f588` 与 #45 fixture 源 `7dc64cb8bb5e72cab518df2c8499c1d194353529`。不写 integration/主目录，不 push、不操作 tracker、不继续派发、不 promotion。
- 仅审查这两源实际 diff 和相互影响；不拉未提交内容，也不研究仍在途的 A/B/C/安装引用修复。

## 实施决策与核验

- 初始 worktree clean，位于 `t3/serial-merger-slice`。基准 `f7...` 是当前 `14d9c6e` 的后代，因此按指定 `git merge` 快进；随后两个源均按要求 `--no-ff` 合并，保留各自 merge boundary。
- C07 实际 diff 删除活文档中旧专业入口的兼容调用承诺；上游来源段保留旧路径、revision 与方法沿革并明确标为历史，同时指向现行 Research OS discovery、paper-writing 与许可资源。新增 discovery 安装后合同测试通过。
- D 源 `skills/general/research-os` 目录树对象为 `7578ab8bb1dcab878c2dbf1235c62f7d7f920e5a`，与测试过的 D 源 tip 字节树相同；因此继承其缓存 Skills CLI 安装证据有依据。本候选上的 Discovery 回归也实际运行并通过，安装测试没有 skip。
- #45 fixture 仅修改 `scripts/test_check_skills_ticket45.py`：slug `proof-review` 展开为真实 `proof-review/SKILL.md` 以进入级联 checker；正例无诊断，临时副本改为不存在的 `references/missing-handoff.md` 后断言产生诊断。未复活 `proof-orchestrator` 控制器或增加产品依赖。#55、M、policy 回归通过。
- 验证日志位于 `/tmp/spec48-contract-fix-merger-1/logs/`。最终 checker 返回 1，但与 D integration 基线日志逐字节相同（cmp=0）：只有既有 9 条缺失 acceptance tarball 引用，无新增诊断。

## Deviations

- `uv run --offline --no-project pytest` 在当前离线环境无法 spawn `pytest`（rc=2）；改用项目约定的 `uv run --offline --no-project python -m unittest` 执行同一 unittest 模块。
- 合并 policy 模块的首次 unittest 调用因测试辅助模块 `spec48_workcopy` 不在 import path 返回 rc=1；补充 `PYTHONPATH=tests` 后同组重跑，29 tests 全部通过。未改产品代码或测试导入行为。
- 静态 checker 保留已记录的 rc=1；通过与基准日志精确 cmp 验证没有带入新问题，不在本小片修历史归档。
