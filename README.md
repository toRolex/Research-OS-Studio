<div align="center">

# Research OS Studio

**安装到普通科研项目的 provider-neutral Agent Skills、typed Artifact 契约与确定性 validator**

[![Build Status](https://img.shields.io/github/actions/workflow/status/toRolex/Research-OS-Studio/acceptance.yml?style=flat-square&label=Build)](https://github.com/toRolex/Research-OS-Studio/actions)
![Python](https://img.shields.io/badge/Python->=3.12-3776ab?style=flat-square&logo=python&logoColor=white)
[![uv](https://img.shields.io/badge/uv-managed-DE5FE9?style=flat-square)](https://docs.astral.sh/uv/)
![Dependencies](https://img.shields.io/badge/runtime%20dependencies-0-success?style=flat-square)

[概述](#概述) • [快速开始](#快速开始) • [使用](#使用) • [验收](#验收) • [支持矩阵](#支持矩阵) • [文档](#文档)

</div>

Research OS Studio 是一个可安装到任意科研项目的 portable core：**15 个用户显式调用的 workflow、8 个模型在 workflow 内调用的 discipline**、typed Artifact 契约、确定性 validators 与薄 Adapter。每个 workflow 读取用户固定的输入，产出 candidate／报告／下一步选项后停止——**没有中央 planner、自动科研循环或隐式接受**，研究语义、预算、推进与发布权始终在用户手中。

> [!NOTE]
> 当前是已通过本地 P0 构建与发布门的候选实现。`validate-repository` 与 `validate-ports` 均 PASS，8 项 community ports 已由用户对固定 acceptance request 作最终 digest 接纳，固定 Lean 4.19 reference 已真实 PASS。Claude/Codex live host 与 SSH／SLURM 真实环境仍是条件性 **BLOCKED / NOT_EVALUATED**——不影响本地 Core/skills 构建完成，但不能据此声称真实宿主或集群验收。

## 概述

**是什么**

- 一套以 Markdown／JSON／Git 为材料的 Agent Skills，通过 wheel 安装进普通科研项目，不修改项目自身依赖。
- 唯一的规范交接是 **typed Artifact**：outer／math 输入固定 path + SHA-256；需要仓库历史身份的 computational handoff 另固定完整 40 字符 Git commit。
- **确定性 validators**：只判断可复现事实，稳定退出码 `0/1/2/3`，不代替研究判断或 human acceptance。
- **薄 Adapter**：把 provider-neutral Core 投影到 Claude Code／Codex，探测能力、映射调用并执行阻止；删掉 Adapter 后 Core 仍可阅读、验证和手工执行。
- **不可变 Publication**：用户最终 digest 确认后冻结，封闭成员、不可覆盖，替代／撤回只能包外追加。

**不是什么**

- 不是网页产品、中央 scheduler 或自动科研 runtime（`research-architecture.html` 只是历史架构展示）。
- 不承诺自动文献搜索、自动修订研究目标、自动发表、GPU／远端费用可靠计量或 hostile executable 安全沙箱。完整非承诺清单见 [PRODUCT.md](PRODUCT.md)。

## 特性

- **用户掌握推进权**：workflow 只能由用户显式调用，输入逐项 pin 死；输出是 candidate，建议不是授权。
- **六轴 Assurance**：`structural_conformance`、`empirical_reproducibility`、`mathematical_argument_review`、`formal_verification`、`independent_review`、`human_acceptance` 互不线性化，不汇总成分数。
- **预算硬停止**：`seconds`/`cost_usd`/`tokens`/`gpu_hours`/`attempts`/`rounds` 六维预算；失败现场与 ledger 不可删除重写。
- **Port-first 治理**：社区能力逐项固定来源、完整 commit、SPDX 许可、baseline hash、keep/modify/delete/add ledger 与人工 `preserve|adapt|reject` 决定；缺来源或许可证证据即 hard block。
- **两条真实 reference 产物线**：计算（CPU 常数均值 baseline，期望 MSE=1.25）与数学（普通证明 + 固定 Lean 4.19 形式化），从 wheel 安装走到 PDF、freeze 与历史恢复。
- **零运行时依赖**：薄 Python CLI，冻结 `uv.lock`，构建后端固定 hatchling 1.27.0。

## 快速开始

需要 Git、[uv](https://docs.astral.sh/uv/) 与 Python 3.12+。

### 1. 构建并安装持久隔离工具

```bash
git clone https://github.com/toRolex/Research-OS-Studio.git
cd Research-OS-Studio
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

`BUILD_DIR` 是新的持久绝对目录；目录已存在或构建失败时，子 shell 会立即停止，不覆盖旧构建。安装时替换为本次输出的**精确 wheel 路径**，不要用可能命中多个旧版本的 `*.whl`。以上示例适用于 macOS/Linux shell。`uv tool install` 建立持久隔离 CLI 环境，不修改科研项目依赖，也不在科研项目内保存 Python runtime／lockfile。

uv 的 tool 环境与可执行目录由平台和配置决定；用 `uv tool dir`、`uv tool dir --bin` 查询，不要把某个 Unix 默认目录当作跨平台保证。安装警告会给出当前 shell 的 PATH 命令；也可由用户显式运行 `uv tool update-shell`。安装流程不自动修改 shell 配置。

> [!WARNING]
> 不要把 dirty checkout 当成已验证安装来源：setup 只接受 wheel RECORD 或干净固定 checkout。保留 wheel、SHA-256、源码 commit 与兼容工具链记录，供旧版本复验；不要用自动 upgrade 覆盖唯一旧安装。

### 2. 准备并安装到科研项目

```bash
PROJECT=/replace/with/persistent/absolute/research-project
mkdir -p "$PROJECT"
git -C "$PROJECT" init
research-os setup-research-os --project "$PROJECT"
```

将 `PROJECT` 替换为用户选择的持久绝对路径。setup 从已安装 wheel 校验资源来源，复制 Core／templates／references，并生成项目级 Claude Code／Codex projection。**它不会启动研究、不自动更新、不安装项目内 runtime。**

## 使用

### 调用 workflow

每一步 request 由用户指定并固定输入（path + SHA-256；计算 handoff 另含完整 commit），不能把前一步的建议当作授权：

```bash
research-os workflow research-charter \
  --project "$PROJECT" --request requests/charter.json
research-os validate \
  --project "$PROJECT" charter.json
```

15 个 workflow 按研究阶段组织：

| 阶段 | workflows |
|---|---|
| 安装 | `setup-research-os` |
| 研究外循环 | `research-charter` → `research-literature` → `research-gap` → `research-idea` → `research-novelty` → `research-reflect` |
| 计算实验 | `design-experiment` → `prepare-experiment` → `run-experiment` → `analyze-experiment` → `assess-result-to-claim` |
| 数学 | `math-proof`、`lean-formalize` |
| 发布 | `freeze-publication` |

8 个 discipline（仅在 workflow 内由模型调用，无接受／预算／冻结权限）：`citation-reference-audit`、`environment-check`、`experiment-audit`、`independent-proof-review`、`publication-claim-audit`、`statistical-check`、`training-health-check`、`trusted-statement-comparison`。

> [!TIP]
> 完整可运行的 request 实例由 reference 验收保存。先跑一次[验收](#验收)里的 E2E，再查看产物目录下 `requests/` 逐个仿写。

### 冻结 Publication

```bash
research-os freeze-publication \
  --project "$PROJECT" \
  --manifest stage.json --principal YOUR_PROJECT_USER_PRINCIPAL \
  --confirm 'REPLACE_WITH_EXACT_FINAL_DIGEST_CONFIRMATION'
```

两个大写值都是占位符，不能原样使用。principal 必须已存在于固定 Project Artifact 的 `spec.principals`，且具有 `user` role；确认串必须是 preflight 要求的本次最终 digest 确认。

错误确认、成员不封闭或必需 gate 阻塞都会 hard block；已冻结的 Publication 拒绝覆盖。

### 退出码

| 退出码 | 含义 |
|---|---|
| `0` | pass |
| `1` | validation failure |
| `2` | usage / configuration error |
| `3` | blocked：外部前置条件不可用 |

结构通过不等于研究正确或 human acceptance。

## 验收

在仓库根运行。收集 runner 检查所有测试文件均已进入 suite，输出逐项 ID 与真实计数，拒绝零测试、重复 ID、import errors 和漏收集。`371` 是 runner 的最低历史收集基线；`408` 是构建期间的中间记录；`416/416` 是 2026-09-06 Lean-enabled 最终历史验收。它们不冲突，也不是永久精确上限；当前结果以本次 `collection.json`／`results.json` 为准。

```bash
uv sync --frozen
uv run --frozen python tests/e2e/run_suite.py --collect-only --output /tmp/research-os-counts
uv run --frozen python tests/e2e/run_suite.py --e2e --output /tmp/research-os-e2e
uv run --frozen python tests/e2e/run_suite.py --output /tmp/research-os-all-tests

# 综合发布门当前预期返回非零，见下方说明
uv run --frozen python tests/e2e/check_release.py --output /tmp/research-os-release-gates
```

两条 reference 的产物线从真实 wheel/setup 出发，经显式 CLI、固定输入、稿件／真实确定性 PDF，到最终 digest 确认、不可覆盖 Publication，再显式更新与旧 commit 恢复。固定研究／review／acceptance 输入仅为 fixture，**不代表真实模型评审或学术接受**。

> [!IMPORTANT]
> `check_release.py` 当前返回非零是**准确结论**：本地 Core／ports／Lean 为 PASS，但真实 SSH／SLURM 为 NOT_EVALUATED、live host execution 为 BLOCKED。不能忽略后声称完整环境发布获准，详见 [GATES.md](GATES.md)。

## 支持矩阵

| 边界 | 当前状态 |
|---|---|
| Direct CLI（15 workflows + validators） | PASS |
| Claude Code／Codex projection | 生成、digest 绑定、共享 validator PASS；真实宿主执行 BLOCKED（隔离未证实） |
| 8 disciplines | Claude 完整 model-only projection 实测；Codex 为 workflow-only，8 项明示 BLOCKED |
| 本地 CPU references（计算 + 普通数学） | E2E PASS，含失败保留、预算硬停、PDF、freeze、历史恢复 |
| 固定 Lean 4.19 reference | 官方临时 elan 真实 build／axiom audit／comparator／kernel replay PASS |
| 8 community ports | `validate-ports` PASS，用户最终 digest 接纳，`release_authorized=true` |
| SSH／SLURM | 本地协议与缺配置检查完成；真实环境 NOT_EVALUATED（缺配置探测返回结构化 exit 3） |

完整状态定义与不可推导的能力见[支持矩阵](docs/guides/support-matrix.md)。

## 文档

- [安装、显式更新、历史恢复](docs/guides/installation.md)
- [15 workflows 与准确 CLI](docs/guides/workflows.md)
- [Artifact／target／relation／Assurance、Publication、migration、ports 与 license](docs/guides/contracts-publication.md)
- [Adapter capability／支持矩阵](docs/guides/support-matrix.md)
- [计算与数学 reference 复现、证据边界](docs/guides/references.md)
- [领域词汇](CONTEXT.md) • [产品范围](PRODUCT.md) • [发布验收记录](gates/leaf-release.md) • [架构决策记录](docs/adr)
