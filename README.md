# Research OS Studio

遵循 Matt Pocock Skills 理念的纯 Agent Skills 整合套件：直接安装到科研项目中，把研究拆解为人类主导、边界明确的科研工作流，由 AI 在单次授权范围内生成候选方案、代码与草稿，而将研究判断、关键输入、结果验收与推进决策始终保留在用户手中。

## 核心设计原则

- **纯 Agent Skills**：Skills 即产品本体。无需克隆产品源码、无需构建 Python wheel、无需 UV 运行环境、无需自建专有安装器或 CLI。
- **三大科研主流程**：涵盖科研全生命周期的核心流程：
  1. **Idea Discovery（构思与查新）**：从研究方向出发，主动检索文献、多视角生成候选、严格查新、独立评审与收敛，交付清晰 Proposal 后停止。
  2. **Validation（实验与理论验证）**：计算/实证路径实现有界实验计划、受限执行、健康监控、结果分析、独立审计与 Claim 约束；数学/理论路径完成公式推导、证明起草、只读审查、显式修复与长期证明。
  3. **Paper Writing and Improvement（论文写作、打磨与衍生）**：从原始研究证据起草正文、制作学术图表、真实编译、并列多维审计（Claim、Citation、Proof、Stress）、独立整篇评审、授权改进循环、Rebuttal 答辩、转投适配与学术演讲。
- **用户绝对控制与零自动跨流程推进**：顶层 Workflow 之间绝不自动跨阶段推进；内部能力严格限定在单次授权与文件写入范围内；计算与环境所有权始终归用户所有。
- **Markdown-First**：成果以自然 Markdown、标准 LaTeX、原生代码与数据格式交付，不强制统一 JSON 包装或 SHA-256 摘要协议。

---

## 快速开始

### 1. 安装 Skills 套件
在你的科研项目根目录中，使用通用的 [Skills CLI](https://github.com/vercel-labs/skills) 即可完成安装：

```bash
# 查看仓库中所有可发现的 Skills 清单
npx skills@latest add toRolex/Research-OS-Studio --list

# 将整套 Research OS Skills 安装到当前项目
npx skills@latest add toRolex/Research-OS-Studio --all
```

> **限定宿主安装**：若仅需面向特定 Agent 宿主（如 Claude Code 或 Codex），可使用 `--agent` 参数：
> ```bash
> npx skills@latest add toRolex/Research-OS-Studio --skill '*' --agent claude-code --agent codex --yes
> ```

### 2. 项目安全初始化（Setup）
安装完成后，在 Agent 宿主中显式调用 `setup-research-os`（例如在 Claude Code 中输入 `/setup-research-os`）：

```text
/setup-research-os
```

`setup-research-os` 采用安全、对话式的初始化流程（**探索 → 展示发现 → 逐项确认决策 → 展示拟写入完整草稿 → 用户确认后写入 → 校验 → 停止**）：
- 自动探索项目已有目录与材料，推荐沿用既有结构（若无则推荐 `research/` 工作区）；
- 优先更新既有 `CLAUDE.md` 或 `AGENTS.md`，不产生重复冲突文件；
- 仅补齐缺失的基础导航和项目说明，**绝不覆盖**用户既有研究材料；
- **不配置**用户的 Python、Lean、LaTeX、GPU 或云环境，不创建假数据或假研究结论，不自动启动任何研究流程。

### 3. 智能入口导航（Ask）
如果你不确定当前研究阶段该选用哪个 Skill，可以直接显式调用 `ask-research-os`（例如 `/ask-research-os`）：

```text
/ask-research-os
```

- **只读推荐**：根据你提供的研究方向、现有实验结果或论文草稿，推荐最适合的切入点并解释原因；
- **零副作用**：只提供咨询与指引，不修改任何文件，不自动启动所推荐的 Workflow；
- **非强制前置**：已知晓目标 Skill 的用户可直接点名调用，无需每次通过 Router。

---

## 完整 Skill 能力地图（39 个 Skills）

Research OS Studio 包含 39 个自包含 Skill，分为 General、Idea Cycle、Validation Cycle 和 Writing Cycle 四大类：
- **User-invoked（U，17 个）**：由用户显式点名启动的完整 Workflow 或独立管理入口，互不自动调用；
- **Model-invoked（M，22 个）**：在当前顶层 Workflow 授权职责内调用的内部能力；用户亦可显式点名作为独立能力（Standalone）使用。

| 分类 | Skill 名称 | 调用方式 | 核心职责与边界 |
|---|---|---|---|
| **General** | [setup-research-os](skills/general/setup-research-os/SKILL.md) | User (U) | 对话式初始化科研工作区与 Agent 指令，展示草稿并确认，不覆盖已有文件，不配置环境 |
| | [ask-research-os](skills/general/ask-research-os/SKILL.md) | User (U) | 只读入口导航与地图咨询；根据方向/数据/草稿推荐切入点，不写文件不自动执行 |
| **Idea Cycle** | [idea-discovery](skills/idea-cycle/idea-discovery/SKILL.md) | User (U) | 完整 Idea 发现 Workflow：文献检索→候选生成→查新→独立评审→收敛，交付 Proposal 后停止 |
| | [research-lit](skills/idea-cycle/research-lit/SKILL.md) | Model (M) | 主动检索与文献综合，区分候选/已核实/未核实来源，保留精确出处 |
| | [idea-generation](skills/idea-cycle/idea-generation/SKILL.md) | Model (M) | 多视角生成候选 Idea，执行去重与硬约束筛选，保留暂存与淘汰理由 |
| | [creative-thinking-for-research](skills/idea-cycle/creative-thinking-for-research/SKILL.md) | Model (M) | 针对构思瓶颈进行认知转换与正交发散，输出可检验的机理洞见 |
| | [novelty-check](skills/idea-cycle/novelty-check/SKILL.md) | Model (M) | 针对候选核心 Claim 主动检索 closest prior work，有据查新，不因模糊相似误杀 |
| | [idea-review](skills/idea-cycle/idea-review/SKILL.md) | Model (M) | 独立评审者直接读取原始文献与候选，输出客观评分、主要弱点与质疑 |
| | [idea-refinement](skills/idea-cycle/idea-refinement/SKILL.md) | Model (M) | 固定 Problem Anchor，比较最小可行路线与前沿路线，不偷偷换题，输出可执行方案 |
| **Validation** | [experiment-plan](skills/validation-cycle/experiment-plan/SKILL.md) | User (U) | 从研究问题制定有界实验计划（hypothesis、baseline、metric、ablation、预算），产出后停 |
| | [experiment-bridge](skills/validation-cycle/experiment-bridge/SKILL.md) | User (U) | 宏实验 Workflow：一次授权内完成实现、sanity、执行、监控、分析与审计，不扩预算 |
| | [run-experiment](skills/validation-cycle/run-experiment/SKILL.md) | Model (M) | 在批准范围内执行实验代码，保留 baseline 及成功/失败/超时全部 attempts |
| | [experiment-queue](skills/validation-cycle/experiment-queue/SKILL.md) | Model (M) | 管理批量实验作业队列与调度，跟踪运行状态与资源消耗 |
| | [monitor-experiment](skills/validation-cycle/monitor-experiment/SKILL.md) | Model (M) | 只读监控运行进程与硬件事实（running/completed/crashed），不做科学推论 |
| | [training-health-check](skills/validation-cycle/training-health-check/SKILL.md) | Model (M) | 诊断 NaN、发散、OOM、loss 停滞等训练异常，建议停止，不擅自 kill 任务 |
| | [analyze-results](skills/validation-cycle/analyze-results/SKILL.md) | Model (M) | 分析全样本与失败记录，评估统计不确定性与多重比较，不作单 metric 机械排名 |
| | [experiment-audit](skills/validation-cycle/experiment-audit/SKILL.md) | Model (M) | 独立审计实验代码、evaluator 与结果真实性，检查 fake ground truth / phantom results |
| | [result-to-claim](skills/validation-cycle/result-to-claim/SKILL.md) | User (U) | 将实验结果转换为范围受限的候选 Claim，区分证据存在与支持力度，收窄过宽结论 |
| | [formula-derivation](skills/validation-cycle/formula-derivation/SKILL.md) | Model (M) | 公式链推导、假设/近似说明与不变量推导，保留完整推导步骤与误差界 |
| | [proof-writer](skills/validation-cycle/proof-writer/SKILL.md) | Model (M) | 针对固定命题起草数学证明，保留失败路线与 gaps，不把未完成尝试当作成功 |
| | [proof-review](skills/validation-cycle/proof-review/SKILL.md) | Model (M) | 只读审查证明结构、引理依赖与边界情况，报告错误与反例，不改动源码与 LaTeX |
| | [proof-repair](skills/validation-cycle/proof-repair/SKILL.md) | User (U) | 显式授权的有界证明修复，反例推翻时不擅自修改命题假设，限定轮数与修改范围 |
| | [proof-orchestrator](skills/validation-cycle/proof-orchestrator/SKILL.md) | User (U) | 长期复杂命题（Single Obligation）续接管理；支持 Lean 形式化辅助，无 Lean 自动降级 |
| **Writing Cycle** | [paper-writing](skills/writing-cycle/paper-writing/SKILL.md) | User (U) | 完整通用 W3 写作 Workflow：规划→图表→起草→编译→并列审查→授权修订，产出候选稿后停 |
| | [ml-paper-writing](skills/writing-cycle/ml-paper-writing/SKILL.md) | User (U) | ML 专业写作 Workflow：严格遵循实验报告、seeds/runs、error bars、compute、limitations 纪律 |
| | [systems-paper-writing](skills/writing-cycle/systems-paper-writing/SKILL.md) | User (U) | Systems 专业写作 Workflow：5 句摘要、设计 alternatives、end-to-end / microbenchmark / scalability |
| | [paper-plan](skills/writing-cycle/paper-plan/SKILL.md) | Model (M) | 构建 Claim—Evidence 矩阵、论文大纲与叙事结构，防止故事脱离数据 |
| | [paper-drafting](skills/writing-cycle/paper-drafting/SKILL.md) | Model (M) | 基于现成计划与原始数据起草学术正文，数字与结论全程可追溯 |
| | [academic-plotting](skills/writing-cycle/academic-plotting/SKILL.md) | Model (M) | 从真实数据生成定量图表，制作标明性质的示意图，保留可复现绘图脚本 |
| | [paper-compile](skills/writing-cycle/paper-compile/SKILL.md) | Model (M) | 在用户既有 LaTeX 环境中执行真实编译检查，报告构建日志与警告，不修改源文件 |
| | [paper-compile-repair](skills/writing-cycle/paper-compile-repair/SKILL.md) | User (U) | 显式授权的 LaTeX 编译修复：展示 diff，确认后修复并复验，不掩盖未解决警告 |
| | [citation-audit](skills/writing-cycle/citation-audit/SKILL.md) | Model (M) | 三维引用审计（身份/元数据/正文语境），报告幻觉引用与错位引用，只读不改 bib |
| | [apply-citation-fixes](skills/writing-cycle/apply-citation-fixes/SKILL.md) | User (U) | 显式授权应用引用修复：展示精确 diff 后修正正文引用标记或 BibTeX 条目 |
| | [paper-claim-audit](skills/writing-cycle/paper-claim-audit/SKILL.md) | Model (M) | 全篇数字、比较、配置、表格、caption 及实验覆盖范围的一致性审计 |
| | [claim-stress-test](skills/writing-cycle/claim-stress-test/SKILL.md) | Model (M) | 构造整篇最强拒稿攻击，对照原材料逐点独立裁决，暴露论证脆弱点 |
| | [research-improvement](skills/writing-cycle/research-improvement/SKILL.md) | User (U) | 跨流程有界改进循环：对代码、结果、Claims、草稿执行有界 review-repair-rereview |
| | [rebuttal](skills/writing-cycle/rebuttal/SKILL.md) | User (U) | 审稿意见回复：将意见原子化为 concern，映射证据，区分可答/待澄清/需补工作 |
| | [resubmit-pipeline](skills/writing-cycle/resubmit-pipeline/SKILL.md) | User (U) | 论文转投适配：新目录适配新 venue 规则与模板，完整保留旧稿与旧构建基线 |
| | [paper-talk](skills/writing-cycle/paper-talk/SKILL.md) | User (U) | 从论文生成学术演讲 slides、speaker notes 与逐字 script，审查演讲产物 |

---

## 典型科研工作流

### 1. 从研究方向到立项方案（Idea Discovery）
```text
用户提出方向/简报
      ↓
/idea-discovery
  ├─ Phase 1: research-lit（主动检索文献、标注已核实/未核实来源）
  ├─ Phase 2: idea-generation & creative-thinking（多视角发散、认知转换、筛选）
  ├─ Phase 3: novelty-check（检索 closest prior work，精准查新）
  ├─ Phase 4: idea-review（独立 reviewer 直接读文献与候选，指出漏洞）
  └─ Phase 4.5: idea-refinement（固定 Problem Anchor，收敛出最小可行与前沿方案）
      ↓
交付 IDEA_DISCOVERY.md 与 RESEARCH_PROPOSAL.md（工作流停止，由用户决定后续步骤）
```

### 2. 从假设到受约束结论（Validation）
- **计算/实证研究**：
  1. 运行 `/experiment-plan`：固定 hypothesis、baseline、评估指标与计算预算；
  2. 运行 `/experiment-bridge`：在单次授权内执行实验代码，监控运行与训练健康，收集全量 attempts 并进行统计分析与审计；
  3. 运行 `/result-to-claim`：将实验证据转化为范围收紧的科学 Claim（不夸大泛化范围）。
- **数学/理论研究**：
  1. 调用 `formula-derivation` 梳理推导链与近似假设；
  2. 调用 `proof-writer` 起草证明；
  3. 调用 `proof-review` 进行只读审查；若有 gap 则显式运行 `/proof-repair`；
  4. 长期复杂证明可调用 `/proof-orchestrator`（无 Lean 环境普通推导，有 Lean 环境形式化辅助）。

### 3. 论文写作、打磨与后续发布（Writing Cycle）
- **论文起草与制作**：
  - 通用论文：运行 `/paper-writing`（规划→起草→学术图表→编译→并列审计→授权修订）；
  - ML 论文：运行 `/ml-paper-writing`（涵盖 seeds、error bars、compute、limitations 规范）；
  - Systems 论文：运行 `/systems-paper-writing`（涵盖 design rationale、end-to-end、scalability 规范）。
- **专项审计与修复**：
  - 编译问题：`paper-compile` 发现错误 → 显式运行 `/paper-compile-repair` 修复；
  - 引用问题：`citation-audit` 发现错漏 → 显式运行 `/apply-citation-fixes` 修复；
  - 全篇审计：运行 `paper-claim-audit` 与 `claim-stress-test` 进行最严苛压力测试。
- **投后与衍生**：
  - 收到审稿意见：显式运行 `/rebuttal` 生成受证据约束的答辩回复；
  - 转投其他会议：显式运行 `/resubmit-pipeline` 适配新模板并保留旧稿；
  - 学术报告：显式运行 `/paper-talk` 生成高质量 slides 与讲稿。

---

## 边界、安全与用户控制原则

1. **环境所有权保持在用户端**：
   Research OS 不会在用户系统中擅自安装或配置 Python、Lean、LaTeX、R、CUDA/GPU 驱动、SSH 密钥或 Slurm 环境。如果某项能力所需工具缺失，Skill 将如实报告缺失项并在受限范围内安全降级，绝不假报成功。
2. **零自动越权推进**：
   所有顶层 Workflow（User-invoked）在完成当前职责并交付报告后立即停止。一个顶层工作流绝不会自动触发另一个顶层工作流（例如 Discovery 完成绝不自动跑实验，实验完成绝不自动写论文，写作完成绝不自动投稿）。
3. **高成本与破坏性操作二次确认**：
   涉及远程执行、GPU 算力消耗、第三方 API 付费、文件重写或外部发布的行为，必须预先声明修改范围与预算，并获得用户明确确认。
4. **真实科研验收声明**：
   本仓库中各 Skill 已经过严格的代码架构审核、静态一致性检查与模拟场景验证。然而，**静态测试与模拟场景审查绝不等于用户在真实科研环境中的端到端体验验收**。详见 [用户手工验收指南](docs/user-acceptance-guide.md)。

---

## 详细文档索引

- [用户手工验收指南](docs/user-acceptance-guide.md)：涵盖全流程各票场景的手工验收步骤、测试用例与边界核验
- [完整产品地图与状态表](skills/general/ask-research-os/PRODUCT-MAP.md)：各 Skill 角色、触发条件、设计边界与交付状态
- [Skills 目录总览](skills/README.md)：Skills 目录结构、清单与宿主限制说明
- [上游来源与许可证说明](docs/upstream-sources-and-licenses.md)：所有移植与借鉴上游开源项目（ARIS, Orchestra 等）的详细 Attribution 与 License 信息

## 许可证

本项目基于 MIT 许可证开源。各 Skill 的共置许可证与上游引用详见 [docs/upstream-sources-and-licenses.md](docs/upstream-sources-and-licenses.md)。
