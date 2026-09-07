# Installation design fixes 实施记录

## 目标

修复安装文档中的临时路径、平台目录、版本恢复与 wheel 选择误导；区分历史 Lean CHECK 与可移植复验；只删除已证实死代码、合并完全相同低层路径检查并补回归覆盖。保留安全校验、历史证据和有真实语义的模块边界。

## 基线

- 2026-09-07：先执行 `git status --short --branch`、`git diff --stat`、`git diff`；当前既有隔离 worktree 干净，无未提交改动。
- 当前目录由工具提供；不创建额外 worktree，不提交、不推送、不持久安装任何工具。
- 用户指定本文件路径；按现有 planning notes 约定创建。

## 决策

- 安装建议以构建出的单一、明确版本 wheel 配合 `uv tool install`；不使用可能匹配多个旧产物的 `dist/*.whl`。
- `uv tool` 的环境与可执行目录按平台和配置决定；文档引用 `uv tool dir`、`uv tool dir --bin` 与 `uv tool update-shell`，不把某个 Unix 默认目录写成跨平台保证。
- 恢复旧版本必须安装固定旧 wheel/版本到独立持久环境，不以自动更新覆盖现有安装。
- `gates/leaf-lean419-reference.md` 保留历史命令和结果，仅明确其非可移植、非当前安装指南；新的复验说明从仓库根出发，使用用户自选持久 Lean 环境。
- 对 Python/schema 双实现优先增加 parity 回归，不改安全判定语义、不引入依赖。

## 进展

- 已完成基线状态检查并创建本记录。
- README、installation/workflows/references guides 改为持久 `uv tool install` 主路径；平台目录通过 `uv tool dir` / `--bin` 查询，PATH 由安装提示或用户显式 `uv tool update-shell` 处理。
- wheel 使用新持久 build 目录和精确文件名；拒绝 `*.whl` 多版本歧义。update 文档改为独立 `UV_TOOL_DIR` + `UV_TOOL_BIN_DIR` side-by-side，保留旧 wheel/digest/工具链，禁止自动 upgrade 覆盖。
- 历史导出明确只恢复 Git bytes，不自动重放旧工具、模型、API、GPU、Lean 环境。
- 清理常规 setup/export/workflow 中 `/tmp` 工具路径与 principal/project 占位误导；测试 `/tmp` 保留为一次性输出，并给出持久证据目录规则。
- README 收窄 commit pin 声明：outer/math 为 path+SHA-256，computational handoff 另含完整 commit。
- Lean gate 仅加历史非可移植标注，未改写 CHECK；references 增加从当前仓库根、用户自选持久 Lean 4.19 环境复验方式，未安装 Lean。
- 核实 371=runner 最低历史基线、408=中间记录、416=最终 Lean-enabled 历史结果；保留 runner/meta 测试并补解释。
- PLAN 四个不存在的 node 文档链接改指真实 `GATES.md`。
- 删除 `_fields(candidate)` 死分支与 `SKILL_IDS` 死常量。
- 两份完全相同的 symlink ancestor 检查合并到现有 `research_os.install.bundle` 底层 helper，保持语义；现有 install/history symlink 与边界测试覆盖复用路径。
- 增加 semantics 分层 parity 回归：schema 可接受而 Python invariant 拒绝的重复 boundary，以及 migration receipt schema 通过后仍须 context。
- Codex host seam 保留：它提供 fail-closed、exactly-once、receipt/input/projection 固定边界，不等同虚构 live host 能力。
- `research_os.remote.__main__` 与 worker 保留：support matrix/remote leaf 已公开 module CLI，且本地 lifecycle、transport、远端 worker 语义不同。
- Issue/path helpers 未合并：异常类型、允许值、contract 语域不同。
- 历史 port evidence harness 未改：其 digest 被 PORT/receipt/attestation 固定；canonical evaluator 与旧历史 harness 差异需新一轮证据架构决策，不能原地重写。

## 验证

- 相关回归：182 tests，全部通过，67.543s。
- 全树 collect-only：417 tests、38 files、0 collection errors。当前新增 1 个 semantics parity 测试；证明 371 是下限、408/416 是不同阶段记录，不应删除 runner/meta 测试或把 416 固化为上限。
- `git diff --check`：通过。
- 未实际安装 Lean 或任何持久工具；uv 仅按现有 lock 创建当前 worktree 的项目 `.venv` 并运行测试。

## Deviations

- 主 checkout 有 README、installation、`.gitignore` 未提交改动；隔离规则禁止在本 worktree 以 git 读取共享 checkout。已只读参考其文件内容，并在当前 worktree 独立实现；未修改或丢弃主 checkout 改动。
- 顾问曾建议删除 Codex seam/remote module 入口；经代码、测试和公开 support matrix 核实前提不成立，保守保留。
