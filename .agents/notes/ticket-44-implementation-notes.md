# Ticket #44 implementation notes

## 范围

#44 只加三条编排路线：rebuttal、resubmit、paper-talk。路由行与 playbook 原子新增。叶 skill 正文、门基线、composition 文档不改。不实现其他票。

## 基线

`v2/ticket-44` 从 `integration/research-os-v2` 的 `50ae6aa` 起，开工时 `HEAD` 与该 tip 相同，无需先 merge。

## Seam（任务已指定）

- Seam A：唯一入口 `scripts/check-skills.py`。公开边界是 `parse_route_table` / `route_table_problems` / `backtick_cascade_problems`。正例读仓库里的真实路由与 playbook；反例用同一段正文的损坏副本，不另建 checker。
- Seam B：可丢弃目录里的 pi 真实工具轨迹。静态通过不当作停点或产物合同已验收。

## Decisions

- 路线名用 `rebuttal` / `resubmit` / `paper-talk`，变体 `—`，只读约束 `no`。playbook 文件与路线同名。叶目录名 `resubmit-pipeline` 留在级联路径里，不改成路线名。
- 级联用仓库根反引号路径 `skills/.../*.md`，由编排者读全文。不把叶步骤抄进 playbook。
- 叶 skill 自带门（strategy-confirm、wording-confirm、adaptation-scope、change-confirm、talk-authorization、outline-confirm）留在叶正文。playbook 只写到达该文件后按该门停。
- `paper-compile` 与 `citation-audit` 只在 resubmit 的只读检查步被点名。`paper-compile-repair` 与 `apply-citation-fixes` 只作为待转交路径，不在本路线执行。
- composition-map / composition-notes 不改。

## Deviations

- 验收指南和 README 里「产出后停止」只清本票三条路线和总则。其他票拥有的叶 skill 正文、idea/validation 验收段、许可证溯源段保持原句。
- resubmit 的编译修复和引用改写只写入口名，不写 `SKILL.md` 反引号路径。本路线不读、不执行这两份正文。
