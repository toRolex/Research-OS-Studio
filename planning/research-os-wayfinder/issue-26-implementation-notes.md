# Issue #26 实施记录：Portable Core Walking Skeleton

## 目标

交付可从干净项目重放的最窄完整路径：UV 冻结环境、显式 setup、`research-charter` candidate Artifact、provider-neutral validator、独立 human acceptance 后的不可覆盖 Publication，以及 Claude Code/Codex 薄投影。

## 测试 seam

- `research-os` CLI 是唯一运行与验证边界。
- 测试从临时干净项目出发，观察项目文件、结构化报告、退出码、停止行为和不可覆盖性。
- Claude Code/Codex Adapter 对同一 fixture 复用直接 CLI validator，不单独实现研究语义。

## 实现决策

- Canonical Core 放在 `core/`：三个通用 Agent Skills 与 Artifact 1.0.0 contract；provider 信息仅放在 `adapters/` 和生成投影。
- Python CLI 只使用标准库，由 UV 管理；`uv.lock` 冻结后可用 `uv sync --frozen` 重建。
- `setup-research-os` 是唯一项目写入 setup；它复制 canonical skills 到 `.claude/skills` 与 `.agents/skills`，不启动 workflow。
- `research-charter` 只读取用户指定的项目相对输入，输出 candidate Artifact 与 workflow report，随后以 `workflow_complete` 停止。
- validator 统一 JSON Validation Report，稳定退出码为 `0/1/2/3`；外部固定 Git target 在离线状态下返回 blocked。
- Publication 冻结要求精确二次确认和独立 active/pass `human_acceptance` Assessment。使用独占创建，存在即拒绝，不覆盖原文件。
- 审查后加固不可变边界：setup 先全量预检并回滚部分写入；Artifact、报告与 Publication 使用同目录临时文件、fsync 和 no-replace 原子发布；目录 fd 拒绝 symlink 跳出 Project。
- human acceptance 同时固定成员 target 与 SHA-256；冻结基于同一份已读 bytes 校验和计算摘要，成员内容变化后旧 Assessment 失效。
- validator 只支持 Artifact contract 1.0.0 与已实现 type 1.0.0，拒绝非法跨仓库 URI、未知 target 字段和损坏 JSON；setup 生成的 projection manifest 是 Adapter smoke 入口前置条件。
- Reviewer 补齐 typed spec 确定性验证、URI digest 硬门、Project 内 subject 路径约束与安全 Publication ID；同步加固 canonical JSON Schema。

## Deviations

- Ticket 要求通用 Agent Skills 安装机制，但 P0 不允许专用 installer；本切片将仓库内 `core/skills/*/SKILL.md` 作为可复制安装源，显式 setup 仅完成项目级投影。
- 当前 walking skeleton 只实现最小 Artifact 校验，不扩展到完整 relation、六轴冲突、migration 或 external-reference validator；这些属于父 Spec 后续切片。
- 为避免引入仅测试所需的外部依赖，验收测试使用 Python 标准库 `unittest`，仍全部通过 `uv run` 执行。

## 验证

- `uv sync --frozen`
- `uv run python -m unittest discover -s tests -v`
- 干净临时项目 README 路径 E2E
- `git diff --check` 与 provider-neutrality 扫描
