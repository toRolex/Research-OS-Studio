# Leaf install 实施记录

## 目标

实现普通科研项目内的通用安装、显式更新、历史恢复，以及 Claude Code/Codex projection 数据模型。安装结果不得要求目标项目拥有 Research OS 专用 Python runtime、UV lockfile、plugin、symlink 或全局状态；平台能力不足必须结构化 fail-closed；历史恢复只读固定 Git commit，且不修改当前项目。

## 基线

- 2026-09-06：已读取 `PLAN.md`、`CONTEXT.md`、Issue #24 与 `gates/leaf-install.md`。
- 旧 walking skeleton 将完整 Python runtime、`pyproject.toml`、`uv.lock` 复制到目标项目；这违反本 leaf 的新安装边界，且实现位于冻结 facade，不能在本 leaf 修改。
- 本 leaf 因此提供独立 deep modules：资源发现/快照安装、投影模型/生成、Git 历史只读恢复；L10 再接入共享 facade。

## 决策

- 普通安装应从 Git 仓库的完整 commit 构建 `SourceBundle.from_repository`；`from_directory` 仅适用于调用方已独立验证来源的低层 seam，不能作为“pinned source”的证据。
- 安装写入使用 exclusive/no-follow 创建并在每次写前重验边界；拒绝 symlink ancestor、并发占位及路径逃逸。历史恢复拒绝含 symlink 的输出父路径，并在发布 staging 前复验。
- 安装采用 inventory + SHA-256 manifest；已有同字节文件幂等保留，不同字节文件默认阻塞；显式更新写入新的版本化 environment 目录，不覆盖 active/history。
- projection manifest 固定 adapter、capability profile、canonical skill 的版本与 digest；任何 required capability 非 `supported` 都返回 BLOCKED，不生成平台文件。
- Claude workflow projection 添加 `disable-model-invocation: true` 与 `user-invocable: true`；discipline 添加 `user-invocable: false`，不进入用户可调用 inventory。
- Codex 仅使用官方已定义的 `policy.allow_implicit_invocation: false`。当前 capability profile 不具备可验证的 discipline 私有可见性，因此选择 discipline 时结构化 `BLOCKED`；不得用未定义 `visibility` 字段冒充支持。
- 历史恢复仅接受完整 40 位 commit，通过 `git archive` 读取固定 tree；拒绝 symlink、submodule、特殊文件、不完整/漂移 manifest 和已存在输出目录；先 staging、完整校验后原子落盘。

## Deviations

- `pre-implement` 通常要求新建任务 notes；用户又严格限制只修改 Owns 与 gate。为遵守更具体的所有权限制，notes 放在 Owned 的 setup skill references 目录，不修改共享 planning notes。
