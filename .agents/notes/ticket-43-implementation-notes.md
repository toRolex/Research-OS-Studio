# Ticket #43 implementation notes

## 范围

#43：`paper-writing` 的 general / ml / systems 三个 playbook、路由行、静态正反例，以及本路线 README / PRODUCT-MAP / 验收指南。不改三份既有 composition-map。不实现其他票。不改原 main 工作区。不 push、不开 PR、不关票。

## 基线

本 worktree `v2/ticket-43` 起点 `50ae6aa`，与 `integration/research-os-v2` 相同。尚未开发，无需先 merge。报告前再 merge 当时的 integration tip 并重测。

## Seam

公共入口仍是 `scripts/check-skills.py`。本票行为挂在已有路由解析之后：`paper_writing_route_problems`（仓库路由行）与 `paper_writing_variant_problems`（单个 playbook 正文）。测试只调用这两个函数和仓库里的真实路由表，不测私有拆分。

## 合同（测试里的独立字面量）

- 三行：`(paper-writing, general|ml|systems)`，只读约束 `no`，playbook 为 `playbooks/paper-writing-<variant>.md`。
- 每份 playbook 用反引号点名本变体入口 skill、其 composition-map，以及规划 / 图表 / 起草 / 编译检查 / claim / citation / stress / 条件性 proof-review。
- ML 另点实验报告、reviewer、venue 清单。Systems 另点写作方法、评价、checklist、venue，以及 paper-plan 的 systems blueprints / patterns。
- 专业变体的反引号不得出现另外两个写作入口的 `SKILL.md`。通用变体不得出现 ML / Systems 入口的 `SKILL.md`。
- 三份都点名 `paper-compile-repair` 与 `apply-citation-fixes` 为另行点名，并保留「授权」字样，让叶上的门继续生效。
- composition-map 原文不改。Playbook 只引用。

## Decisions

- 触发词：general 用「写论文」；ml 用「机器学习」；systems 用「系统论文」。材料口径写在适用条件。只读意图仍由既有 route-only 优先，不在本票改写。
- 级联路径用仓库根相对路径的反引号，继续走 #38 的 `skills/general/research-os/` 扫描，不把扫描范围扩到全仓。
- 候选稿三例不在本 worktree 伪造。真实 pi 轨迹只证明读路径；授权前停止，不把轨迹说成叶合同已交付。

## Deviations

- 专业入口不经通用，用「不得出现另外两个写作入口的 `SKILL.md` 反引号」表达。playbook 仍可用「通用写作入口」这种自然语言，避免把禁令本身级联成一次读取。
- 三例候选稿与审查报告没有真实研究材料，不在本 worktree 伪造。真实 pi 只跑授权前读路径。叶合同的完整交付记为待验。
- 英文 README 原有一行 `└` 后是替换字符。改 Writing Cycle 图时一并换成正常 `└─`。这是本路线图，不是顺手修无关文档。

## 集成合并（#37）

`integration/research-os-v2`（`4640e88`）对 `v2/ticket-43`（`66a3ae2`）`--no-ff`。唯一冲突是 `skills/general/research-os/SKILL.md` 路由表：两边都改了 `idea-discovery` 与 `custom` 之间的同一段。保留 #41 的 idea-discovery 行，并原子加上 paper-writing 的 general / ml / systems 三行。未交付名单去掉这两条已交付路线，仍留 experiment-plan、experiment-bridge、proof、rebuttal、resubmit、paper-talk、improvement、pickup。

`PRODUCT-MAP.md` 自动合并后同时保留 Idea 的 `/research-os` 编排句和 Writing 的三变体句。三份既有 composition-map 未改。checker 仍只有 `scripts/check-skills.py`，`paper_writing_route_problems` 接在既有路由扫描之后。

合并后 `uv run python scripts/check-skills.py` 通过（U 38 / M 1）。`scripts/test_check_skills_ticket43.py` 5、`scripts/test_check_skills_ticket38.py` 21、`tests/test_check_skills_policy_gates.py` 3、`tests/test_config_contract.py` 6，共 35 项通过。这些只证明路由行、playbook 级联字面量和门基线。

真实行为仍缺：本次合并没有新的工具轨迹。三变体没有用真实材料各走一遍；授权前零写入、确认后按叶合同交付候选稿与审查报告、以及投稿／上传停在硬门前，都没有行为证据。票不关。
