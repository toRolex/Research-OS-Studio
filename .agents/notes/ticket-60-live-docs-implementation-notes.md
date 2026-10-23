# #60 活文档子切片 implementation notes

## 状态

- 活文档合同对齐（README、中英清单、skills 索引、用户验收指南、GLOSSARY）：done；五个指定活文档通过差异审阅，未改控制器/Skill 正文/历史验收资料。
- 静态核验与差异记录：done；`git diff --check` 与 `uv run python -m unittest scripts.test_check_skills_ticket46` 通过。`uv run python scripts/check-skills.py` 仅报 9 个 `docs/acceptance/**` 历史归档包链接缺失/未追踪；按范围未触碰这些链接或 checker。
- integration 合并与提交：done；提交在 `t3/update-live-docs`，并显式核对/合并 `integration/spec-48` tip（`0bd38385b9a7b3aa51872af415aee78ef2778bcf`，已包含）；未改 integration 或主目录。
- 交付报告：进行中；`/tmp/spec48-ticket60-docs/REPORT.md` 已写，待最后状态同步 commit 后补确切最终 SHA 与差异范围；不表述为 #60 完成。

## 入口与范围

用户要求该独立子切片直接实现且不再派发，因此由本 worker 在指定隔离 worktree 完成。仅修正活文档中与 #48 Spec 已确认合同冲突的普通阶段审批、固定八角色前置、品牌化宿主门和旧 39 数量；保留只读、主要目标替换、外发/破坏性/超额硬门与当前兼容入口。#55B/C 未确认合并，整体安装验收和真实研究质量不在本切片范围。

## 决策记录

- 不把原有 39 改造成产品承诺，也不为数字增删 Skill；目录清单按仓库实际树核验。
- 活文档区分目标合同、当前兼容/迁移状态、静态检查、实际安装与未验证的真实科研质量。
- 仅同步 Spec 明确确认的领域术语，不新增 ADR，不更改产品方向、控制器或 Skill 正文。
- 文档回归测试最初因英文核心原则标题不再以既有 `Human in the Loop` 前缀开头而触发 StopIteration；保留既有标题、仅更新其合同文字后，#46 的 9 项测试通过，因此无需改测试。

## Deviations

- 无。
