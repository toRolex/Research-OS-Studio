# 安装、显式更新与历史恢复

当前源码已完成本地 P0 构建验收。15 workflows、8 disciplines 与 8 个用户最终 digest 接纳的 community ports 已进入 canonical catalog／release inventory。真实 Claude/Codex host 与 SSH／SLURM 仍须在相应环境单独验收。

## 1. 构建独立工具环境

在 Research OS 仓库根执行 README 的 `uv lock --check`、`uv sync --frozen`、`uv build --wheel`，用 `uv venv` 与 `uv pip install --python ... <wheel>` 安装 wheel。UV pip 接口仅用于这个独立工具环境，不替科研项目修改依赖。依赖 Python 3.12+ 和 Git；构建后端已固定 hatchling 1.27.0，项目锁文件 `uv.lock` 不得被验收改写。

离线复现还需要本机已有该 Python、构建后端及其依赖缓存。`--frozen` 不等于网络绝对隔离，也不保证构建后端所有间接依赖均带锁；缺缓存应报真实失败，不声称离线可重建。

## 2. 通用 Skills 复制与显式 setup

可以通过宿主通用 Skills 安装机制，将选定 `core/skills/<workflow>/` **复制**到科研项目的 skill 目录；不要 symlink，不引入 Research OS 专用 plugin/global runtime。canonical Core 没有平台调用策略，因此直接复制文本**不证明宿主可强制用户入口隔离**。

推荐从独立 wheel 调显式 setup，生成与 canonical digest 绑定的投影。

```bash
uv run --no-project /tmp/research-os-tooling/bin/research-os setup-research-os \
  --project /absolute/research-project
```

setup 复制版本化 Core、templates、reference 与 manifest；创建 `.research-os/install-manifest.json`、项目设置以及 `.research-os/projections/{claude-code,codex}/manifest.json` 和平台 skills。不会开始研究 workflow。已有同内容可校验，冲突／来源不足拒绝；不要用 setup 覆盖漂移文件。安装源须可验证：wheel RECORD 或干净固定 checkout；dirty checkout 的 provenance 不是通过证据。

## 3. 单次 workflow 与固定输入

用户先准备 typed Artifact，验证、提交，再把 path／SHA-256（计算 handoff 还包括完整 commit）写入 request。每条 CLI 调用仅一个 workflow。输出是 candidate，不自动接受、继续、生成 Assessment 或冻结。

完整 request 是测试生成的普通 JSON 文件，而非隐藏 runtime 状态；运行 [reference 复现](references.md) 后逐个查看 `requests/`，再按自己的输入编写新 request。未知顶层字段、路径穿越、浮动 revision 或不匹配 digest 应拒绝。

## 4. 显式更新

先安装用户选择的新 wheel 到另一个工具环境。保留旧 wheel 与构建证据，然后显式安装 side-by-side 环境。

```bash
uv run --no-project /absolute/new-tooling/bin/research-os update-research-os \
  --project /absolute/research-project --environment v-next
```

输出环境在 `.research-os/environments/v-next/`，停止原因 `installed_explicit_activation_required`。不自动切换现有 skills、不覆盖旧 run／Artifact／Publication、不运行新 workflow。没有隐式 activation 命令承诺；用户审阅后自行选择工具与项目投影。名称冲突／已有安装漂移 fail-closed。

## 5. 从历史完整 commit 恢复

先将安装投影、运行记录和冻结包提交到科研项目 Git。用户选择**完整 40 字符 commit**，导出至不存在的新目录。

```bash
uv run --no-project /tmp/research-os-tooling/bin/research-os export-research-os \
  --project /absolute/research-project --commit FULL_40_CHARACTER_COMMIT \
  --output /absolute/restored-project
```

恢复选择 Git bytes，不读取脏工作树替代历史；结果含 `.research-os/history-restore.json`，标记 read-only，不执行历史 Python／shell。read-only 是恢复操作契约，不是恶意修改防护。旧字节可验证不等于旧模型、外部 API、GPU 或 Lean 环境已重放；真正重放须另行固定兼容工具链与前置条件。

两条新增产物 E2E 均在真实冻结后执行 side-by-side update 与恢复，逐文件比较旧安装、研究材料及 Publication 字节；计算路径还比较失败 run。测试的 Git commit 仅在临时科研项目，不提交产品仓库。
