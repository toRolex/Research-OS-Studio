# 安装、显式更新与历史恢复

当前源码已完成本地 P0 构建验收。15 workflows、8 disciplines 与 8 个用户最终 digest 接纳的 community ports 已进入 canonical catalog／release inventory。真实 Claude/Codex host 与 SSH／SLURM 仍须在相应环境单独验收。

## 1. 构建并安装持久隔离工具

在 Research OS 仓库根执行：

```bash
(
  set -e
  uv lock --check
  uv sync --frozen
  BUILD_DIR="$HOME/research-os-builds/$(git rev-parse HEAD)"
  mkdir -p "$(dirname "$BUILD_DIR")"
  mkdir "$BUILD_DIR"
  uv build --wheel --out-dir "$BUILD_DIR"
)
```

构建成功后，将下面的占位符替换为输出的精确 wheel 路径，再安装：

```bash
uv tool install /replace/with/exact/persistent/wheel/path.whl
```

`BUILD_DIR` 必须是新的持久绝对目录；已存在时 `mkdir` 失败，子 shell 立即停止，不继续构建。安装前替换为本次 build 打印的精确 wheel 路径；不要使用 `dist/*.whl` 一类可能同时匹配多个旧版本的模式。以上示例适用于 macOS/Linux shell。保留 wheel、SHA-256、源码完整 commit 和兼容 Python／Lean 等工具链记录。

`uv tool install` 把 CLI 放入持久隔离环境，不替科研项目修改依赖，也不在科研项目中创建 Research OS Python runtime、`pyproject.toml` 或 lockfile。uv 的 tool 环境与 executable 目录由平台及 `UV_TOOL_DIR`／`UV_TOOL_BIN_DIR` 配置决定；分别用 `uv tool dir`、`uv tool dir --bin` 查询，不硬编码 `~/.local/...` 或 Unix `bin/`。若 executable 不在 PATH，安装警告会给出当前 shell 命令；用户也可显式运行 `uv tool update-shell`，但安装流程不自动修改 shell 配置。

依赖 Python 3.12+ 和 Git；构建后端固定 hatchling 1.27.0，项目 `uv.lock` 不得被验收改写。离线复现还要求本机已有 Python、构建后端及依赖缓存；`--frozen` 不等于网络绝对隔离。

## 2. 通用 Skills 复制与显式 setup

可以通过宿主通用 Skills 安装机制，将选定 `core/skills/<workflow>/` **复制**到科研项目的 skill 目录；不要 symlink，不引入 Research OS 专用 plugin/global runtime。canonical Core 没有平台调用策略，因此直接复制文本**不证明宿主可强制用户入口隔离**。

推荐从已安装的独立 wheel 调显式 setup，生成与 canonical digest 绑定的投影。

```bash
PROJECT=/replace/with/persistent/absolute/research-project
mkdir -p "$PROJECT"
git -C "$PROJECT" init
research-os setup-research-os --project "$PROJECT"
```

`PROJECT` 是必须替换的占位符。
setup 复制版本化 Core、templates、reference 与 manifest；创建 `.research-os/install-manifest.json`、项目设置以及 `.research-os/projections/{claude-code,codex}/manifest.json` 和平台 skills。不会开始研究 workflow。已有同内容可校验，冲突／来源不足拒绝；不要用 setup 覆盖漂移文件。安装源须可验证：wheel RECORD 或干净固定 checkout；dirty checkout 的 provenance 不是通过证据。

## 3. 单次 workflow 与固定输入

用户先准备 typed Artifact，验证、提交，再把 path／SHA-256（计算 handoff 还包括完整 commit）写入 request。每条 CLI 调用仅一个 workflow。输出是 candidate，不自动接受、继续、生成 Assessment 或冻结。

完整 request 是测试生成的普通 JSON 文件，而非隐藏 runtime 状态；运行 [reference 复现](references.md) 后逐个查看 `requests/`，再按自己的输入编写新 request。未知顶层字段、路径穿越、浮动 revision 或不匹配 digest 应拒绝。

## 4. 显式 side-by-side 更新

为新版本使用另一组持久 uv tool 目录，避免 `uv tool install` 以新约束替换现有同名工具：

```bash
OLD_TOOL_DIR="$(uv tool dir)"
OLD_BIN_DIR="$(uv tool dir --bin)"
NEW_TOOL_DIR=/replace/with/new/persistent/tools/v-next
NEW_BIN_DIR=/replace/with/new/persistent/bin/v-next

(
  set -e
  test -x "$OLD_BIN_DIR/research-os"
  test "$NEW_TOOL_DIR" != "$NEW_BIN_DIR"
  mkdir -p "$(dirname "$NEW_TOOL_DIR")" "$(dirname "$NEW_BIN_DIR")"
  mkdir "$NEW_TOOL_DIR"
  mkdir "$NEW_BIN_DIR"
  UV_TOOL_DIR="$NEW_TOOL_DIR" UV_TOOL_BIN_DIR="$NEW_BIN_DIR" \
    uv tool install /replace/with/exact/new/wheel/path.whl
  "$NEW_BIN_DIR/research-os" update-research-os \
    --project "$PROJECT" --environment v-next
)
```

新目录和 wheel 路径均须替换。`OLD_TOOL_DIR`／`OLD_BIN_DIR` 从初装时同一 uv 配置查询；若初装使用自定义环境变量，查询时保持该配置，并将实际目录记录到持久安装记录中。上述示例适用于 macOS/Linux shell。新目录已存在或任一步失败时，子 shell 立即停止，不执行后续安装或更新；失败残留目录也不得原样重用。保留旧 wheel/digest、工具目录和兼容工具链，不运行 `uv tool upgrade`，也不让自动更新覆盖旧安装。`uv tool` 隔离的是 CLI 工具环境，不等于恢复模型、API、GPU 或 Lean 等外部 runtime。

输出环境在 `.research-os/environments/v-next/`，停止原因 `installed_explicit_activation_required`。不自动切换现有 skills、不覆盖旧 run／Artifact／Publication、不运行新 workflow。没有隐式 activation 命令承诺；用户审阅后自行选择工具与项目投影。名称冲突／已有安装漂移 fail-closed。

## 5. 导出历史项目快照（不是工具版本回滚）

先将安装投影、运行记录和冻结包提交到科研项目 Git。用户选择**完整 40 字符 commit**，用所选版本 CLI 导出至不存在的新持久绝对目录。

```bash
RESTORED_PROJECT=/replace/with/new/persistent/absolute/restored-project
"$OLD_BIN_DIR/research-os" export-research-os \
  --project "$PROJECT" --commit FULL_40_CHARACTER_COMMIT \
  --output "$RESTORED_PROJECT"
```

`FULL_40_CHARACTER_COMMIT` 和路径均为占位符。命令恢复固定 commit 的项目 bytes，不读取脏工作树，不执行历史 Python／shell；结果含 `.research-os/history-restore.json` 并标记 read-only。它不会自动找回旧 Research OS wheel、工具环境、模型、外部 API、GPU 或 Lean。真正复验旧版本须使用保留且校验过 digest 的旧 wheel、独立持久工具目录和兼容前置条件；不得覆盖当前安装。

两条新增产物 E2E 均在真实冻结后执行 side-by-side update 与恢复，逐文件比较旧安装、研究材料及 Publication 字节；计算路径还比较失败 run。测试的 Git commit 仅在临时科研项目，不提交产品仓库。
