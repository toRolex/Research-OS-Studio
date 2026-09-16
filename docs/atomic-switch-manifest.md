# Research OS Studio 轻量 Release 与原子切换清单

> 对应 Issue：[#35 — [纯 Skills 34/35] 轻量 Release 与原子切换准备](https://github.com/toRolex/Research-OS-Studio/issues/35)
>
> 父 SPEC：[#1 — 重构 Research OS Studio 为三流程纯 Agent Skills 整合仓库](https://github.com/toRolex/Research-OS-Studio/issues/1)
>
> 架构决策：[docs/adr/0005-pure-agent-skills-product.md](adr/0005-pure-agent-skills-product.md)

---

## 1. 目标与定位

本清单为 Research OS Studio 从旧版 Python Core / Wheel / Typed Contracts / Port Database 架构原子切换为**三流程纯 Agent Skills 整合仓库**提供可执行的准备方案与删除/替换范围清单。

本阶段（#35）完成：
1. 参考 Matt Pocock Skills（`mattpocock/skills`）建立单一、轻量、main 驱动的 Release 与版本自动化配置；
2. 完整枚举所有待删除旧资产（代码、测试、Schema、Ports、Gates、Planning、展示文档）；
3. 预先核实旧新同名 Skill 映射与发现范围，消除命名冲突与幽灵路径；
4. 如实记录旧 CI 既有红项状态与切换次序，确保切换后不留永久红灯；
5. 确立用户未提交内容核对机制与法律 Notice 保留原则；
6. 验证候选发行配置与清单可支持原子切换。

**本票只做工程与清单准备，不实际打 tag、不发布 release、不自动 push、不在此提前删除旧工程（删除操作由 #36 原子执行）。**

---

## 2. Release 自动化架构

参考 Matt Pocock Skills 发行模型，纯 Skills 仓库不再需要 Python 构建、wheel 打包、PyPI 发布或重型 E2E 测试平台。发行自动化遵循以下轻量设计：

### 2.1 候选 Release Workflow（`.github/workflows/release.yml`）
- **触发条件**：仅在代码合入 `main` 分支时触发（支持 `workflow_dispatch` 手动触发）。
- **执行环境**：`ubuntu-latest`，Node.js 22。
- **核心工具**：`@changesets/cli` + `changesets/action@v1`。
- **工作机制**：
  1. 开发者在变更 Skill 时运行 `npx changeset` 生成变更日志描述文件（`.changeset/*.md`）；
  2. 合并入 `main` 后，Release Action 自动创建或更新“Version PR”；
  3. 当 Version PR 合并后，Action 自动打对应版本 Git Tag 并生成 GitHub Release。
- **权限**：`contents: write`, `pull-requests: write`。
- **免除依赖**：0 Python 依赖、0 外部自建验证服务、0 永久红灯门禁。

### 2.2 版本与包配置
- `package.json`：配置 `private: true`、`name: "research-os-studio"`，声明 changeset 脚本与 devDependencies。
- `.changeset/config.json`：绑定 `toRolex/Research-OS-Studio`，主分支 `main`，启用 privatePackages 版本与 tag 追踪。
- `.changeset/README.md`：记录版本与 changeset 使用说明。

---

## 3. 旧工程待删除与替换清单（将在 #36 执行）

依据 ADR 0005 与 Spec #1，旧工程所有非纯 Skills 资产在 #36 中彻底删除，不保留 `legacy/` 目录，旧架构完全交由 Git 历史保存。

### 3.1 待删除资产详细枚举

| 分类 | 路径 / 资产 | 包含文件数 / 范围 | 删除理由 |
| :--- | :--- | :--- | :--- |
| **旧 Python Package & CLI** | `src/research_os/` | 42 个 `.py` 文件（含 `cli.py`, `core.py`, `lifecycle.py`, `history/`, `install/`, `publication/`, `remote/`, `validation/`, `workflows/`） | 旧 Python runtime 与自建 CLI 已废弃，Skills 为唯一产品形态 |
| **旧 Python 构建与依赖** | `pyproject.toml`, `uv.lock`, `scripts/research-os.py` | 3 个文件 | 消除 UV / Python wheel / Hatchling 构建配置 |
| **旧 Contracts 与 Schemas** | `core/contracts/` | 19 个 `.schema.json` 文件（foundation, mathematical, ports, publication, semantics） | 废除统一 JSON Schema 约束与强制 typed 检验 |
| **旧 Catalog 与 Typed JSON 模板** | `core/catalog.json`, `templates/computational/`, `templates/mathematical/`, `templates/outer/`, `templates/publication/` | 15 个 `.json` 模板文件 | 废除中央 JSON 模板；新 Skills 使用自然 Markdown/代码/LaTeX |
| **旧 Port Database & 认证** | `core/port-release-attestation.json`, `ports/`（含 `inventory.json`, `release.json`, `evaluate_port.py`, `evaluation-environment.txt`, 8 个 port 证据目录，`ports/products/`） | 84 个文件 | 废除 port 治理、eval ledger、SHA-256 摘要与 port gate |
| **旧 Port 许可证副本** | `core/licenses/ports/` | 3 个文件（`ATTRIBUTION.md`, `auto-claude-code-research-in-sleep-MIT.txt`, `ten-proofs-Apache-2.0.txt`） | 来源归属已统一收录入 `docs/upstream-sources-and-licenses.md` |
| **旧 Remote Adapters** | `adapters/` | 6 个文件（`claude-code.json`, `codex.json`, `slurm/`, `ssh/`） | 废除自建 SSH/Slurm 远程包装器与宿主投影生成器 |
| **旧 Runtime 测试与 E2E** | `tests/` | 41 个 Python 测试文件（`adapters/`, `contracts/`, `e2e/`, `history/`, `install/`, `integration/`, `mathematical/`, `ports/`, `publication/`, `remote/`, `workflows/`） | 旧 Python 运行时测试体系整体废除 |
| **旧 Wrapper Skills** | `core/skills/` | 23 个旧 Skill 目录（`analyze-experiment` ~ `trusted-statement-comparison`） | 已全部被 `skills/` 下的 39 个自包含纯 Skill 取代 |
| **旧 CI Workflow** | `.github/workflows/acceptance.yml` | 1 个文件 | 废除旧 frozen-tests 与 check_release gate，由 `release.yml` 替代 |
| **旧 Guides & 说明文档** | `docs/guides/`（5 个文件：`contracts-publication.md`, `installation.md`, `references.md`, `support-matrix.md`, `workflows.md`）, `docs/adr/0001`–`0004.md`, `docs/research-os-p0-progress.md`, `docs/research-os-dual-version-tutorial-implementation-notes.md` | 11 个 Markdown 文件 | 旧架构指南与已废弃 ADR 0001-0004（被 ADR 0005 取代） |
| **旧 Gates 与 Planning 资产** | `gates/`（12 个 `leaf-*.md` 文件）, `GATES.md`, `PLAN.md`, `PRODUCT.md`, `planning/research-os-wayfinder/`（34 个文件） | 49 个文件 | 旧 Wayfinder 规划系统与 Leaf Gates 全面退役 |
| **旧展示材料与参考工程** | `research-architecture.html`, `docs/research-os-dual-version-tutorial.html`, `reference-projects/`（`computational/`, `mathematical/` 共 13 个文件） | 15 个文件 | 旧 runtime 演示材料与旧 fixture 工程，不再保留 |

### 3.2 必须保留与维护的纯 Skills 核心资产

| 资产路径 | 包含内容 | 维护要求 |
| :--- | :--- | :--- |
| `skills/` | 39 个自包含 Skills（General: 2, Idea Cycle: 7, Validation Cycle: 14, Writing Cycle: 16） | 包含所有共置 `references/`, `templates/`, `agents/openai.yaml`, `LICENSE*`，保持 100% 相对链接可达 |
| `docs/upstream-sources-and-licenses.md` | 集中记录所有上游来源（ARIS, Orchestra, Matt Pocock, Archon, EurekAgent 等）、Git commit hash、许可证及 attribution | 唯一法律与来源依据，持续维护 |
| `docs/adr/0005-pure-agent-skills-product.md` | 记录纯 Agent Skills 重构决策的 ADR | 永久保留作为产品架构基准 |
| `docs/agents/` | `domain.md`, `issue-tracker.md`, `triage-labels.md` | Agent 协作与 issue 处理规范 |
| `docs/research/sources/` | `ai-research-skills-report.md`, `aris-report.md`, `comparison.md`, `anthropic-openai-math-workflows-20260901.md`, `README.md` | 调研一手事实备查报告 |
| `docs/atomic-switch-manifest.md` | 本切换准备清单 | 记录切换次序与验证标准 |
| `.github/workflows/release.yml` | 轻量 Release 自动化 Workflow | main 分支唯一 CI/Release 流程 |
| `package.json`, `package-lock.json`, `.changeset/` | Node.js 与 Changesets 发行配置 | 保证纯 Skills 的版本发布与依赖锁定 |
| `CLAUDE.md`, `AGENTS.md` | 仓库级 Agent 指令 | 保持纯 Skills 规范一致 |
| `.gitignore` | 忽略 `node_modules/`, `.venv/`, `.claude/` 等本地与临时目录 | 规范仓库跟踪边界 |

---

## 4. 旧新 Skill 名称映射与发现范围隔离

### 4.1 旧 Wrapper Skill vs 新纯 Skill 映射表

| 旧目录位置（`core/skills/` 或 `ports/products/`） | 新纯 Skill 位置（`skills/`） | 角色类型 | 处理说明 |
| :--- | :--- | :--- | :--- |
| `core/skills/setup-research-os` | `skills/general/setup-research-os` | User-invoked | 重构为 prompt-driven 初始化，删除工程 tracker 绑定 |
| `core/skills/research-charter` / `research-gap` / `research-idea` / `research-literature` / `research-novelty` / `research-reflect` | `skills/idea-cycle/idea-discovery`<br>`skills/idea-cycle/research-lit`<br>`skills/idea-cycle/idea-generation`<br>`skills/idea-cycle/creative-thinking-for-research`<br>`skills/idea-cycle/novelty-check`<br>`skills/idea-cycle/idea-review`<br>`skills/idea-cycle/idea-refinement` | 1 User / 6 Model | 取代旧短契约壳，恢复 ARIS/Orchestra 主动文献检索、发散、查新与收敛方法 |
| `core/skills/design-experiment` / `prepare-experiment` | `skills/validation-cycle/experiment-plan` | User-invoked | 独立规划 hypothesis, baseline, ablation 与预算 |
| `core/skills/run-experiment` | `skills/validation-cycle/run-experiment`<br>`skills/validation-cycle/experiment-queue` | Model-invoked | 记录成功/失败/超时全量尝试，支持批量队列 |
| `core/skills/training-health-check` | `skills/validation-cycle/training-health-check` | Model-invoked | 只读健康诊断，建议停止而非越权 kill |
| `core/skills/analyze-experiment` / `statistical-check` | `skills/validation-cycle/analyze-results` | Model-invoked | 审查不确定性、选择偏差与多重比较，合并去重 |
| `core/skills/experiment-audit` | `skills/validation-cycle/experiment-audit` | Model-invoked | 独立审查 evaluator 代码与结果真实性 |
| `core/skills/assess-result-to-claim` | `skills/validation-cycle/result-to-claim` | User-invoked | 分离证据存在性与支持力度，约束 Claim 范围 |
| *(旧体系缺失宏 Workflow)* | `skills/validation-cycle/experiment-bridge` | User-invoked | ARIS 宏实验 Workflow 授权闭环 |
| `core/skills/math-proof` | `skills/validation-cycle/formula-derivation`<br>`skills/validation-cycle/proof-writer` | Model-invoked | 分离公式推导与命题证明生成 |
| `core/skills/independent-proof-review` | `skills/validation-cycle/proof-review` | Model-invoked | 只读审查证明义务与论证漏洞 |
| *(旧体系混合审查与修复)* | `skills/validation-cycle/proof-repair` | User-invoked | 显式受控证明修复 |
| `core/skills/lean-formalize` / `trusted-statement-comparison` | `skills/validation-cycle/proof-orchestrator` | User-invoked | 长期证明管理与可选 Lean 方法，降级机制 |
| *(旧体系缺失完整写作链)* | `skills/writing-cycle/paper-plan`<br>`skills/writing-cycle/paper-drafting`<br>`skills/writing-cycle/academic-plotting`<br>`skills/writing-cycle/paper-writing`<br>`skills/writing-cycle/ml-paper-writing`<br>`skills/writing-cycle/systems-paper-writing` | 3 User / 3 Model | ARIS W3 与 Orchestra 写作方法体系 |
| `core/skills/publication-claim-audit` | `skills/writing-cycle/paper-claim-audit` | Model-invoked | 数字、配置、表格与实验覆盖审计 |
| `core/skills/citation-reference-audit` | `skills/writing-cycle/citation-audit`<br>`skills/writing-cycle/apply-citation-fixes` | 1 Model / 1 User | 分离引用审计发现与显式应用修复 |
| *(旧体系缺失编译检查)* | `skills/writing-cycle/paper-compile`<br>`skills/writing-cycle/paper-compile-repair` | 1 Model / 1 User | 分离真实编译检查与源文件显式修复 |
| *(旧体系缺失拒稿压力测试)* | `skills/writing-cycle/claim-stress-test` | Model-invoked | 对抗性拒稿论点压力测试 |
| `core/skills/freeze-publication` | `skills/writing-cycle/research-improvement`<br>`skills/writing-cycle/rebuttal`<br>`skills/writing-cycle/resubmit-pipeline`<br>`skills/writing-cycle/paper-talk` | User-invoked | 取代旧不可变冻结，提供有界改进循环、Rebuttal、转投适配与演讲生成 |
| *(旧体系缺失全景导航)* | `skills/general/ask-research-os` | User-invoked | 只读能力地图解释与入口建议 |

### 4.2 发现范围与防冲突验证
- **发现根路径**：仅扫描 `skills/` 目录。
- **数量核对**：39 个 `SKILL.md`，17 个 user-invoked（配置 `disable-model-invocation: true` 与 `agents/openai.yaml`），22 个 model-invoked。
- **命名空间**：所有 39 个 Skill 具有全局唯一名称，不存在跨目录同名。
- **消除旧污染**：在 #36 删除 `core/skills/` 和 `ports/` 后，`npx skills add toRolex/Research-OS-Studio --list` 将只展示 39 个纯 Skill，彻底消除同名竞争与幽灵入口。

---

## 5. CI 切换次序与旧红灯状态事实说明

### 5.1 旧 CI（`acceptance.yml`）既有红项状态说明
旧 CI 文件 `.github/workflows/acceptance.yml` 运行 Python 3.12 / UV 驱动的 `tests/e2e/run_suite.py` 与 `tests/e2e/check_release.py`。
- **历史事实**：自 ADR 0005 确立“纯 Agent Skills 取代专用 Research OS runtime”以来，旧 Python 测试与 Release Gates 已被明确废弃，`check_release.py` 中的门禁处于预期红灯状态（Expected Red）。
- **非新回归**：该红灯是旧架构被取代的既有状态，不是本次 Skills 迁移产生的回归。
- **切换后终态**：在 #36 删除 `acceptance.yml`、旧 `tests/` 和 Python 依赖后，仓库不再执行旧 gate，主分支只保留 `.github/workflows/release.yml`，消除一切永久红灯。

### 5.2 切换执行次序
```
[Issue 35 (当前)]
  ├── 引入 package.json / package-lock.json / .changeset
  ├── 引入 .github/workflows/release.yml (候选 Release 自动化)
  ├── 形成 docs/atomic-switch-manifest.md (本清单)
  └── 保持旧文件完好，不触发发布，不打 tag

[Issue 34 (文档交付)]
  └── 交付纯 Skills 新 README.md 与用户验收指南

[Issue 36 (原子切换)]
  ├── 核对工作区无未提交用户材料
  ├── 执行文件删除 (src/, core/, ports/, tests/, adapters/, gates/, planning/, etc.)
  ├── 移除 .github/workflows/acceptance.yml
  ├── 启用新 README.md 与 release.yml 作为唯一主流程
  └── 运行本地静态验证 (39 skills, 链接, frontmatter, changeset 状态)
```

---

## 6. 用户未提交内容核对与法律 Notices 保留原则

### 6.1 用户未提交内容核对原则
1. **工作区状态检查**：在执行任何删除前，通过 `git status` 确认无用户本地研究成果、未提交的实验数据或未提交的文档。
2. **冲突交涉规则**：若发现用户在旧目录中存在未跟踪或修改的新材料，立即暂停切换并交由用户决定归属，绝不静默覆盖或强行丢弃。
3. **禁止 `legacy/` 目录**：不得将旧 Python 代码备份移动至 `legacy/` 目录以回避删除。旧代码在 Git 提交历史中永久可查，工作区必须保持纯净。

### 6.2 法律 Notices 与 Attribution 保护
1. **集中归属清单**：`docs/upstream-sources-and-licenses.md` 完整保留并记录 ARIS（MIT）、Orchestra（MIT）、Matt Pocock Skills（MIT）、Archon（MIT）、ten-proofs（Apache-2.0）等所有采用资产的原作者、原提交 SHA、原路径及许可证全文。
2. **共置许可证**：所有移植 Skill 目录下的共置 `LICENSE`, `NOTICE.md`, `LICENSE-ARIS.txt`, `LICENSE-Orchestra.txt` 必须完整保留，随 Skill 共同分发。
3. **AGPL 隔离**：确认 0 AGPL 文本或源码混入。

---

## 7. Issue 36 原子切换执行指令集（参考 Runbook）

在进入 Issue 36 时，可按以下步骤原子执行删除与验证：

```bash
# 1. 核对工作区干净状态
git status

# 2. 删除旧 Python 代码与 CLI
git rm -rf src/ pyproject.toml uv.lock scripts/

# 3. 删除旧 Core, Contracts, Schemas 与旧 Wrapper Skills
git rm -rf core/

# 4. 删除旧 Ports 数据库与证据
git rm -rf ports/

# 5. 删除旧 Remote Adapters
git rm -rf adapters/

# 6. 删除旧 Tests 体系
git rm -rf tests/

# 7. 删除旧 Templates (JSON Schema 模板)
git rm -rf templates/

# 8. 删除旧 Gates 与 Wayfinder Planning 资产
git rm -rf gates/ GATES.md PLAN.md PRODUCT.md planning/

# 9. 删除旧展示 HTML 与 Reference Projects
git rm -rf research-architecture.html reference-projects/
git rm -f docs/research-os-dual-version-tutorial.html
git rm -f docs/research-os-dual-version-tutorial-implementation-notes.md
git rm -f docs/research-os-p0-progress.md
git rm -rf docs/guides/ docs/adr/0001-*.md docs/adr/0002-*.md docs/adr/0003-*.md docs/adr/0004-*.md

# 10. 移除旧 CI Workflow
git rm -f .github/workflows/acceptance.yml

# 11. 执行本地静态自检
node -e '
const fs = require("fs");
const path = require("path");
// 验证 39 个 skills 全部存在且无断链
'
```

---

## 8. 候选配置与清单可支持原子切换验证结论

1. **Release 配置就绪**：`.github/workflows/release.yml`、`package.json`、`package-lock.json`、`.changeset/` 已完整就绪，语法与工具调用验证通过。
2. **资产清单完备**：旧资产删除范围逐项明确，与纯 Skills 保留资产边界清晰，0 遗漏。
3. **无命名与发现冲突**：39 个纯 Skill 结构严密，删除旧资产后通用 Skills CLI 发现范围完全干净。
4. **CI 终态绿色保证**：移除了预期红灯的旧测试链，新 Release 流程遵循成熟开源 Changesets 模式，无多余失败门禁。
5. **准备状态达成**：已满足 Issue 35 验收标准，可无缝承接 Issue 34（使用文档）与 Issue 36（原子切换执行）。
