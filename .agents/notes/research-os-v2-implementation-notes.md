# integration/research-os-v2 notes（#38 + #39 + #40）

## 范围

`integration/research-os-v2` 上 `--no-ff` 合入 `v2/ticket-40` tip `90c9bf9`（其历史已含 #39 merge `9923d7d`）。不 squash。不 push，不开 PR，不关票。不改原 main 工作区。

## Decisions

- 冲突：`README.md`、`docs/README-en.md`、`skills/README.md`、`scripts/check-skills.py`。`docs/user-acceptance-guide.md` 自动合并后，汇总表第 2 行补上 #40 的零授权、清单外模型停、外部新建 `CLAUDE.md` 重新确认。中英清单都写成 setup 可建议，其余（含 `research-os`）显式；旧入口 `ask-research-os` 只作为已删除说明保留。
- 单一 `scripts/check-skills.py`。#38 路由表 / 反引号级联 / `research-os → Gates: none` / 旧 router 迁移句留在 import 期扫描。#39 叶路径基线整表保留，`GATE_SKIP` 仍是 setup 与 research-os。#40 的角色、政策、日志、setup 门（`model-confirm`、`write-confirm`）和 `--skip-suite` CLI 接在同一文件，不另建 checker。
- setup 翻转按 #40：无 `disable-model-invocation: true`，`allow_implicit_invocation: true`。半翻转（仍禁用 model invocation，或 yaml 不是 true）失败。其余 skill 缺显式或缺 yaml false 仍失败。
- 成功输出仍含「调用策略」和「门声明」。计数 U 38 / M 1（只有 setup 可建议）。
- 全仓扫描仍在 import 时执行，`--skip-suite` 才跳过。#40 的 `run_suite()` 若原样接上，会把链接解析从 `lexical_relative` 退回 `Path.resolve`，并让 `scripts/test_check_skills_ticket38.py` 的 import 断言失效。合同函数改由 `main()` 调用 `run_builtin_contract()`，不重复跑叶门（叶门已在 import 期）。
- `.agents/` 被 gitignore。本 notes 与先前 #38/#39 notes 一样 `git add -f`。

## 真实行为待验

- 静态 checker 与三套单测只证明声明、链接、路由表、叶门基线、setup 门、角色/政策/日志字段和损坏副本。不证明宿主真的停在 Gate，不证明 route-only 零副作用，不证明 setup 与真实模型清单的对话，不证明三宿主已登录或可委派。
- 模板 `research-os-models.md` 使用 `example/replace-with-live-model`。这只说明形状。checker 不把该模板当成某次真实 `pi --list-models` 确认。
- 12 条逻辑路线里，路由表只有 route-only 与 custom。其余 playbook 未交付，checker 不要求它们。

## Deviations

- `skills/README.md` 验收清单采用 #40 的八步，并加回「原先仅有 AGENTS.md、确认后外部新增 CLAUDE.md」这一条。#40 正文写的是「指令候选优先级变化则停整批」；这条是同一停点的可执行例子，不是新授权。
- 不把模板角色行或静态字段检查写成 Seam B 的真实工具轨迹。

## #44 / #45 合入

`--no-ff` 先合 `v2/ticket-44` `134c038`，再合 `v2/ticket-45` `63e3e15`。不 squash，不 push，不开 PR，不关票，不动原 main。

冲突只在 `skills/general/research-os/SKILL.md` 路由表与 `skills/README.md` 只读导航。路由行按合同顺序并入 idea-discovery、paper-writing 三变体、proof、rebuttal、resubmit、paper-talk、improvement、pickup、route-only、custom。未交付名单只留 experiment-plan、experiment-bridge。级联示例同时点名 #44 与 #45 的 playbook。README 导航保留 proof／improvement／pickup，并保留 paper-writing 按材料分变体。composition 文档未改。checker 仍是 `scripts/check-skills.py`。

#44 notes 的 Seam B 与 #45 notes 的 pickup 轨迹仍只属于各自分支的可丢弃目录。本次合并没有重跑这些轨迹，不把它们写成集成后已验。

## #42 合入

`--no-ff` 合入 `v2/ticket-42` `b163430`（功能提交 `7acd43c`）。不 squash，不 push，不开 PR，不关票，不动原 main。

冲突：`skills/general/research-os/SKILL.md`、`skills/general/research-os/references/PRODUCT-MAP.md`、`docs/user-acceptance-guide.md`。路由表保留全部 14 行：route-only、idea-discovery、experiment-plan、experiment-bridge、paper-writing general / ml / systems、proof、rebuttal、resubmit、paper-talk、improvement、pickup、custom。未交付名单改为「无」。级联示例补上 experiment-plan 与 experiment-bridge。PRODUCT-MAP 同时保留 #42 的本批授权和 #45 的 proof / improvement / pickup。验收指南保留叶门与「报告本身不是停点」，并写明默认算力政策不是本批授权。`README.md`、`docs/README-en.md`、`skills/README.md` 自动合并，#45 的交接段还在。checker 仍是 `scripts/check-skills.py`，没有第二个 checker。

#42 行为轨迹没有在这次合并重跑，也不算集成后已验。范围只以分支 notes 为准：`/tmp/ros42-cases/{missing,expired,scope,exact,cumul,concur,retry,unknown,delete,loop}`，宿主 `pi --session … -p`，工具 read/write/edit/bash，模型 cliproxy/grok-4.7 thinking off。拒绝场景无 `results/out.txt`。exact 与 loop 有本地 `printf` 产物 `ok`。loop 两笔 completed 对上 2 USD / 0.2 cpu-core-hour / 2 planned-run，第三笔 refused 且无 started_at；默认政策仍为 0；`results/run.csv` 保持 `seed result v1`。这证明授权门，不是 experiment-bridge 全阶段科研质量，也不是叶 skill 正文被改过。
