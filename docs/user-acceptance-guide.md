# Research OS Studio 用户手工验收指南

本指南面向在真实科研项目中验收 Research OS Studio 纯 Agent Skills 套件的用户与维护者。指南汇总了已批准 35 票重构方案中全部科研能力的验收场景、输入边界、预期行为、工具缺失降级与停止条件。

> **免责与验收状态声明**：
> 本仓库所有 39 个自包含 Skill 均已通过实施期的静态架构检查、frontmatter 规范核验、内部链接可达性验证与合成场景测试。然而，**静态检查与模拟场景审查绝不等于用户在真实科研环境中的端到端体验验收**。用户应在可丢弃的测试项目副本中，依据本指南逐项核实实际行为。

---

## 一、验收准备与环境所有权原则

### 1. 基础环境与工具所有权
- **环境所有权归用户所有**：Research OS 不会且不得自动为用户安装或配置 Python、Lean、LaTeX、R、CUDA/GPU 驱动、SSH 密钥或 Slurm 调度器。
- **工具缺失如实报告**：当 Skill 需要的外部工具（如 `pdflatex`、`lean`、`web_search` 或特定 Python 库）不存在时，Skill 必须如实报告工具缺失缺口并安全降级，**绝不伪造执行成功**。
- **高成本与破坏性操作边界**：涉及 GPU 算力消耗、付费 API 调用、远程代码执行、文件重写或外部发布的行为，必须预先明确修改范围与资源预算，并在操作前获得用户明确授权。
- **零自动跨流程推进**：所有 User-invoked 顶层 Workflow 在完成当前职责并输出报告后必须立即停止，**绝不自动启动下一条主流程**。

### 2. 准备可丢弃的测试工作区
在独立的临时目录中克隆或创建测试项目，不要直接在未经备份的重要科研仓库中进行首次破坏性测试：

```bash
mkdir -p /tmp/research-os-test-project
cd /tmp/research-os-test-project
git init
```

### 3. 安装套件并列举验证
使用通用 Skills CLI（不使用自建安装器，不要求 clone 本仓库、不要求 Python wheel / UV）：

```bash
# 1. 检查 GitHub 仓库可发现的 Skills 清单（应列出全部 39 个 Skill）
npx skills@latest add toRolex/Research-OS-Studio --list

# 2. 安装全部 Skills 到当前测试项目
npx skills@latest add toRolex/Research-OS-Studio --all

# 或限定安装到指定宿主（如 Claude Code / Codex，非交互）
npx skills@latest add toRolex/Research-OS-Studio --skill '*' --agent claude-code --agent codex --yes
```

> **本地开发分支验证**：若验证尚未 push 的本地分支，使用本地绝对路径替代 `toRolex/Research-OS-Studio`：
> `npx skills@latest add /path/to/Research-OS-Studio --list`
> `npx skills@latest add /path/to/Research-OS-Studio --all`

---

## 二、通用入口（General）验收场景

### 1. `setup-research-os`（#3 项目安全初始化）
`setup-research-os` 是对话式的初始化 Workflow，采用 **Explore → Present → Ask → Draft → Confirm → Write → Verify → Stop** 八步闭环。

- **场景 1.1：全新空项目初始化**
  - **操作**：在空目录中运行 `/setup-research-os`。
  - **核验**：
    1. 自动探索并建议创建默认的 `research/` 目录；
    2. 当 `CLAUDE.md` 和 `AGENTS.md` 均不存在时，主动询问用户选择创建哪一个；
    3. 展示拟写入的完整草稿（包含项目基础导航、研究日志、工作区说明及 Agent 指令区块）；
    4. 用户确认前**零文件写入**；
    5. 用户确认后写入文件，验证存在性后立即停止，不配置环境、不生成假研究数据、不启动研究流程。
- **场景 1.2：非空既有科研项目（沿用目录，不搬迁）**
  - **操作**：在已有论文草稿、代码和数据的项目中运行 `/setup-research-os`。
  - **核验**：
    1. 自动识别已有工作目录（如 `docs/`、`experiments/` 或自定义目录），推荐沿用已有结构；
    2. 绝不强制搬迁或删除用户既有文件；
    3. 仅补齐缺失的导航和指令区块。
- **场景 1.3：重复执行（幂等性，不覆盖）**
  - **操作**：在已初始化的项目中再次运行 `/setup-research-os`。
  - **核验**：检测到基础文件与指令区块均已完整，报告“无需额外写入”，已有内容和研究日志**零修改、零覆盖**。
- **场景 1.4：内容冲突处理与差异展示**
  - **操作**：手动修改既有指令文件中的 Research OS 区块内容，再次运行 `/setup-research-os`。
  - **核验**：展示当前内容与推荐草稿的精确 diff，逐项询问用户决定（保留当前、原位更新或手动合并），保留所有周边无关段落。当两个指令文件都存在时，优先更新 `CLAUDE.md`。
- **场景 1.5：拒绝写入与外部突发变动防护**
  - **操作**：
    - 展示草稿后输入拒绝，核验项目保持零修改；
    - 在展示草稿与确认写入的间隙，模拟外部新建或修改目标文件（如外部新增了 `CLAUDE.md`），核验 setup 立即停止整批写入，重新扫描并要求重新确认。

### 2. `ask-research-os`（#32 只读入口导航与地图咨询）
`ask-research-os` 是纯只读 Router，帮助用户在 39 个 Skill 中选择切入点。

- **场景 2.1：从不同科研起点咨询**
  - **操作**：分别输入三种常见起点向 `/ask-research-os` 提问：
    1. “我只有一个模糊的研究想法，想找文献并形成方案” → 应推荐 `idea-discovery` 或 `research-lit`；
    2. “我已有实验代码和跑出来的 CSV 数据，想知道能得出什么结论” → 应推荐 `analyze-results`、`experiment-audit` 或 `result-to-claim`；
    3. “我已有初稿，但投 NeurIPS 需要检查实验报告和算力说明” → 应推荐 `ml-paper-writing` 或专项审计。
- **场景 2.2：只读与零执行边界核验**
  - **核验**：
    1. 给出推荐理由与输入输出要求后立即停止；
    2. 全程**零文件写入**、**零修改**；
    3. **绝不自动启动**所推荐的任何 Workflow；
    4. 明确指出用户可直接点名运行目标 Skill，无需每次通过 Router。

---

## 三、Idea Cycle（构思与查新）验收场景

### 1. `research-lit`（#4 主动文献检索与综合）
- **操作**：提供研究主题或初步关键词，调用 `research-lit`。
- **核验**：
  1. 主动调用联网搜索工具（如 `web_search`）检索学术论文；
  2. 严格区分**候选来源（Candidate）**、**已核实来源（Verified）**与**未核实来源（Unverified）**；
  3. 文献结论必须附带论文标题、作者、年份或 DOI 等具体出处；
  4. **工具缺失降级**：当无网络或无检索工具时，安全降级为“用户提供材料综合（Supplied-Material Synthesis）”，明确标注未检索外部数据库，不凭空捏造论文。

### 2. `idea-generation` & `creative-thinking-for-research`（#5 候选生成与认知转换）
- **操作**：提供文献摘要或研究背景，调用 `idea-generation`。若遇到构思瓶颈，调用 `creative-thinking-for-research`。
- **核验**：
  1. 从多个正交视角（如理论机理、系统瓶颈、跨领域迁移等）生成多个候选 Idea；
  2. 记录每个候选的初步优势与硬约束筛选过程，保留**暂存与淘汰理由**，防止重复踩坑；
  3. 认知转换输出可检验的机制洞见而非泛泛空谈；
  4. **角色分离**：生成者不充当最终评审者，不宣称自己生成的 Idea 已被证实。

### 3. `novelty-check`（#6 基于原始文献的新颖性查新）
- **操作**：提供一个候选 Idea 的核心 Claim，调用 `novelty-check`。
- **核验**：
  1. 围绕核心 Claim 主动检索**最相近先验工作（Closest Prior Work）**；
  2. 逐项比对技术路线、适用假设与性能边界；
  3. 建议放弃或修改方向时，必须指出具体先验论文与明确证据，**不因模糊的技术词汇相似而误杀创新方向**；
  4. 证据不足时明确提出具体查新缺口与补证要求。

### 4. `idea-review` & `idea-refinement`（#7 独立评审与固定锚点收敛）
- **操作**：提供候选 Idea 与参考文献，先调用 `idea-review`，再调用 `idea-refinement`。
- **核验**：
  1. **独立评审**：Reviewer 直接读取原始文献和候选方案全文，指出技术漏洞、不可行假设与潜在未解决问题；
  2. **固定问题锚点**：Refinement 在修改方案时，必须严格保留原始 **Problem Anchor**（研究核心问题），防止在迭代过程中“偷偷换题”；
  3. **双路线取舍**：对比最小可行验证路线（MVP）与前沿进阶路线（Frontier），给出权衡依据。

### 5. `idea-discovery`（#8 完整 Idea 发现 Workflow）
- **操作**：显式调用 `/idea-discovery`，输入研究方向 brief。
- **核验**：
  1. 完整串联 Phase 0（读取 brief）→ Phase 1（文献检索）→ Phase 2（候选生成）→ Phase 3（查新）→ Phase 4（独立评审）→ Phase 4.5（锚点收敛）；
  2. 默认在各 Phase 间停下等待用户确认（除非获得显式“一次走完”授权）；
  3. 最终在工作区交付单一 `IDEA_DISCOVERY.md` 发现报告与 `RESEARCH_PROPOSAL.md` 研究方案；
  4. **越权防御**：交付后立即停止，**绝不自动运行 pilot 代码、绝不自动创建实验计划、绝不自动跨入 Validation 流程**。

---

## 四、Validation Cycle（实验与理论验证）验收场景

### 1. 计算与实证研究路径

- **`experiment-plan`（#9 制定有界实验计划）**
  - **操作**：提供研究假设，调用 `/experiment-plan`。
  - **核验**：产出包含 Hypothesis、Baseline 对照、评估 Metrics、Ablation 方案、固定不变评价面、允许修改代码范围、计算资源预算与失败判据的计划，产出后立即停止，不执行任何代码。
- **`run-experiment` & `experiment-queue`（#10 授权执行与队列管理）**
  - **操作**：在单次授权的资源限额内运行实验。
  - **核验**：
    1. 严格在允许修改的文件范围内运行；
    2. 记录并保留 baseline 及所有 attempts（包括成功、失败、无效和超时记录），**不让最优结果抹杀完整实验历史**。
- **`monitor-experiment` & `training-health-check`（#11 运行监控与训练健康诊断）**
  - **操作**：对运行中的训练或实验任务进行状态监控。
  - **核验**：
    1. `monitor-experiment` 只汇报客观运行状态（running / completed / crashed），不做主观科学结论；
    2. `training-health-check` 检查 Loss 曲线、NaN、梯度发散、GPU OOM、日志停滞等异常；
    3. 健康检查仅提出停止或调优建议，**绝不在未经用户授权时擅自 kill 进程或重启任务**。
- **`analyze-results`（#12 结果全样本分析与统计可信度）**
  - **操作**：提供多轮实验原始数据，调用 `analyze-results`。
  - **核验**：
    1. 同时纳入 baseline、全部 trials 与失败尝试进行分析；
    2. 审查统计不确定性（标准差、置信区间）、重复随机种子、选择性偏差与多重比较问题；
    3. 拒绝将单一指标偶然胜出（Single Metric Winner）包装为科学结论。
- **`experiment-audit`（#13 独立实验真实性与完整性审计）**
  - **操作**：调用 `experiment-audit` 审查实验产物。
  - **核验**：
    1. 独立 Reviewer 直接读取 evaluator 代码、原始日志与输出文件；
    2. 检查是否存在 Fake Ground Truth（评价指标作弊）、Phantom Results（虚构未运行结果）、漏报失败尝试或过宽 Claim；
    3. 只读输出审计报告，不擅自修改代码或补跑实验。
- **`result-to-claim`（#14 结果到范围受限候选 Claim）**
  - **操作**：提供分析与审计报告，调用 `/result-to-claim`。
  - **核验**：
    1. 严格区分“数据文件存在”与“数据是否充分支持结论”；
    2. 将部分支持或存在边界的结论收窄为可辩护的候选 Claim（例如限定数据集、限定算力范围）；
    3. 产出候选 Claim 清单后停止，最终采纳与否由用户决定。
- **`experiment-bridge`（#15 宏实验 Bridge Workflow）**
  - **操作**：提供已批准的实验计划，显式调用 `/experiment-bridge`。
  - **核验**：
    1. 在一次授权内串联实现、sanity 验证、正式执行、监控、结果分析与审计；
    2. 严格受限于批准的资源预算与文件修改范围；
    3. 产出全流程总结后停止，**绝不自动进入 Paper Writing 写作阶段**。

### 2. 数学与理论研究路径

- **`formula-derivation`（#16 普通公式推导）**
  - **操作**：给出初始公式、物理/数学假设与推导目标，调用 `formula-derivation`。
  - **核验**：梳理完整推导公式链，明确标出每一步所用假设、近似条件与不变量，给出误差界，不要求 Lean 环境。
- **`proof-writer`（#16 证明起草）**
  - **操作**：给出待证固定命题与已知条件，调用 `proof-writer`。
  - **核验**：生成严密的数学证明正文；若遇到无法跨越的逻辑缺口，明确标注 Proof Gaps，保留失败路线与教训，不把未完成尝试宣称为成功。
- **`proof-review`（#17 只读证明审查）**
  - **操作**：提供包含潜在漏洞的数学证明文本，调用 `proof-review`。
  - **核验**：
    1. 独立审查证明逻辑，检查未明假设、循环论证、边界漏洞或反例；
    2. **纯只读**：在回复中输出审查意见，**绝不修改原证明文件、LaTeX 或代码**。
- **`proof-repair`（#17 显式授权证明修复）**
  - **操作**：针对 `proof-review` 发现的缺口，显式调用 `/proof-repair`。
  - **核验**：
    1. 必须先明确修复范围、最大轮数与允许修改的文件段落；
    2. **反例推翻原则**：若命题被已确认的反例推翻，严禁在未经用户允许的情况下擅自修改命题或暗中添加条件，必须停止并提示用户重新审视命题；
    3. 修复后调用内部复审，未通过则如实标记未解决。
- **`proof-orchestrator`（#18 长期复杂证明管理与可选 Lean）**
  - **操作**：针对单个复杂长期义务（Single Obligation），调用 `/proof-orchestrator`。
  - **核验**：
    1. 在新目录中记录继承状态与尝试历史，不污染旧轮次；
    2. **无 Lean 环境降级**：无 Lean 工具链时，正常执行普通数学推导，并显式标注“未执行 Lean 形式化验证”，绝不强行安装工具链；
    3. **已有 Lean 环境辅助**：若有 Lean 环境，必须先读取引理 signature，以 kernel / build 结果为准，带有 `sorry` 的声明不得标记为形式化通过；
    4. 支持生成自包含的手动交接包（Manual Handoff Package）。

---

## 五、Writing Cycle（论文写作、打磨与衍生）验收场景

### 1. 写作内部能力与专项审计

- **`paper-plan` & `paper-drafting`（#19, #20 论文规划与起草）**
  - **核验**：`paper-plan` 建立 Claim—Evidence 映射矩阵，确保论文叙事严格由真实数据支撑；`paper-drafting` 从原始数据与计划起草正文，所有数字、表格与结论均可追溯至实验产物。
- **`academic-plotting`（#21 学术图表制作）**
  - **核验**：从真实实验数据生成图表，严格区分定量数据图与概念示意图；必须保留可复现的绘图源码（如 Matplotlib 脚本）与原始数据引用，绝不伪造数据点。
- **`paper-compile` & `paper-compile-repair`（#22 论文编译检查与显式修复）**
  - **核验**：
    1. `paper-compile`：在用户既有 LaTeX 环境中执行真实构建，如实报告编译退出码、PDF 产物与警告日志，不修改任何源文件；
    2. `paper-compile-repair`：用户显式授权后，展示精确 diff，在限定轮数（如 ≤3 轮）内修复 LaTeX 语法错误；编译成功不代表论文结论正确。
- **`citation-audit` & `apply-citation-fixes`（#23 引用审计与显式修复）**
  - **核验**：
    1. `citation-audit`：从**文献身份（Identity）**、**元数据准确性（Metadata）**与**正文语境支撑度（Context Support）**三维度审计引用，只读输出报告，不擅自修改 BibTeX 或正文；
    2. `apply-citation-fixes`：用户显式授权后，展示修改 diff，精确修复正文 cite 标记或补齐 BibTeX 条目。
- **`paper-claim-audit` & `claim-stress-test`（#24 证据审计与压力测试）**
  - **核验**：
    1. `paper-claim-audit`：逐一核对正文中所有数字、对比结论、实验配置、表格、caption 与实验原始记录的一致性；
    2. `claim-stress-test`：模拟最严苛的审稿人构造对抗性拒稿论点，由独立裁决者对照原材料逐一判定论证脆弱点。

### 2. 完整写作 Workflow 与专业扩展

- **`paper-writing`（#25 通用 W3 写作 Workflow）**
  - **操作**：显式调用 `/paper-writing`，提供完整研究材料。
  - **核验**：有序执行规划→图表→起草→编译检查→并列审计→独立整篇评审→授权修订；交付候选稿与审查报告后立即停止，**绝不自动提交投稿，绝不自动补跑实验**。
- **`ml-paper-writing`（#26 ML 专业写作 Workflow）**
  - **操作**：显式调用 `/ml-paper-writing`。
  - **核验**：
    1. 严格执行 ML/AI 领域实验报告规范：每次对比必须明确 random seeds 数量、runs 统计不确定性（error bars）、超参调优范围、算力消耗（compute budget）、复现性与独立的 Limitations 章节；
    2. 发现数据缺失时，正文显式标注 `[SEED COUNT NEEDED]` 或 `[COMPUTE NEEDED]` 等可见缺口，**严禁用默认值掩盖，绝不自动调用外部环境补跑实验**。
- **`systems-paper-writing`（#27 Systems 专业写作 Workflow）**
  - **操作**：显式调用 `/systems-paper-writing`。
  - **核验**：
    1. 严格遵循系统顶会结构规范：5 句摘要法、Introduction 突出问题与 Gap、Design 详细论述架构与替代方案权衡（Alternatives/Trade-offs）、Evaluation 区分 End-to-End、Microbenchmark 与 Scalability；
    2. **缺失证据处理**：若缺少扩展性实验，显式标记 `MISSING SCALABILITY EVIDENCE` 并收窄主张，绝不擅自脑补外推曲线。
- **`research-improvement`（#28 全研究有界改进循环）**
  - **操作**：显式调用 `/research-improvement`，设定修改范围与最大轮数（如 2 轮）。
  - **核验**：
    1. 跨流程直接读取 Claims、代码、结果、当前 diff 与历史 findings；
    2. 在批准范围内修复代码、补充统计分析、修改草稿；
    3. 补跑实验必须经用户另行显式确认并在指定名额内执行；轮数用尽或达到正面结论后立即停止。

### 3. 投后与衍生独立 Workflow（W4 - W6）

- **`rebuttal`（#29 审稿意见回复，W4）**
  - **操作**：提供论文初稿、审稿人评审意见（Reviews）与已有证据，显式调用 `/rebuttal`。
  - **核验**：
    1. 将审稿意见拆解为原子化 concern，逐项映射到论文现有证据；
    2. 明确区分“已有证据可直接回答”、“评审存在歧义需澄清”与“需补充新工作”；
    3. 审稿人文本中要求的补充实验不自动构成执行授权；补实验必须由用户另行确认；
    4. 各 Reviewer 线程自包含，符合目标 venue 篇幅限制（严格区分 strict 与 rich 模式）；完成后停止，不自动修改原论文或投稿。
- **`resubmit-pipeline`（#30 论文转投适配，W5）**
  - **操作**：提供旧投稿目录、目标新会议要求与新输出目录，显式调用 `/resubmit-pipeline`。
  - **核验**：
    1. 在新目录中适配新 venue 模板与格式规则，**原旧稿目录完整保留、绝不污染**；
    2. 用户自定义模板与官方规则冲突时，列出差异由用户决定，不替用户做主；
    3. 在新目录中真实构建 PDF，报告编译状态；完成后停止，不自动投稿。
- **`paper-talk`（#31 学术演讲生成，W6）**
  - **操作**：提供已发表/已完成论文，显式调用 `/paper-talk`。
  - **核验**：
    1. 生成逐页对应的 Slides 内容、Speaker Notes 与逐字演讲稿（Script）；
    2. 严格核算主讲时长与 Q&A 预留时间，数字与结论与原论文完全一致；
    3. 独立审计演讲材料的故事线、信息密度与图表可读性；完成后停止，不自动发布。

---

## 六、跨宿主（Host）与兼容性注意事项

1. **Skills CLI 转换行为说明**：
   通用 Skills CLI 在向特定宿主（如 Eve）复制文件时，可能会根据宿主规则转换 frontmatter（例如移除 `disable-model-invocation`）。本仓库在 `.agents/skills/` 与 Claude Code / Codex 的安装副本中均完整保留规范字段。在未确认目标宿主能严格遵守仅显式调用策略前，高权限或可写入口（如 `proof-repair`、`apply-citation-fixes`、`research-improvement`）应在受控环境中审慎使用。
2. **模型发现清单与 User-invoked 入口**：
   部分 Agent 宿主在向模型展示可用工具列表时，会根据 `disable-model-invocation: true` 自动隐藏 User-invoked 入口。这是符合预期的安全机制，防止模型在未经人类允许时越权自动调用顶层工作流。用户可通过宿主支持的显式指令（如 `/skill-name`）正常调用。

---

## 七、验收汇总检查表

本检查表与正文中逐项的 Skill 名称枚举是发布时点快照，以 `skills/` 目录树为唯一真源；`scripts/check-skills.py` 在 CI 校验 README 层清单与目录树一致。

| 序号 | 验证项 | 预期表现 | 验收判定 |
|---|---|---|---|
| 1 | **CLI 清单发现** | `skills add ... --list` 列出全部 39 个 Skill，无遗漏、无重复、无幽灵入口 | [ ] 通过 |
| 2 | **Setup 不覆盖** | `setup-research-os` 遇到既有材料零覆盖，遇到冲突展示 diff，拒绝则零改动 | [ ] 通过 |
| 3 | **Ask 只读导航** | `ask-research-os` 推荐切入点，零文件写入，不自动触发任何工作流 | [ ] 通过 |
| 4 | **Discovery 真实查新** | `idea-discovery` 执行真实检索与查新，独立评审，交付 Proposal 后停止 | [ ] 通过 |
| 5 | **实验执行有界** | `experiment-bridge` 严格限制在批准预算和文件范围内，保留全部 attempts 历史 | [ ] 通过 |
| 6 | **结果审计与 Claim** | `experiment-audit` 独立查作弊/幻觉；`result-to-claim` 收窄不确定结论 | [ ] 通过 |
| 7 | **数学证明与修复** | `proof-review` 只读报告；`proof-repair` 遇反例不擅改命题，无 Lean 安全降级 | [ ] 通过 |
| 8 | **论文写作与编译** | `paper-writing` 闭环交付候选稿后停止；编译与引用修复均需显式授权 diff | [ ] 通过 |
| 9 | **ML/Systems 专业规范** | ML 强制 seeds/compute 纪律；Systems 强制 5 句摘要/alternatives/scalability | [ ] 通过 |
| 10 | **W4-W6 独立后续** | `rebuttal`、`resubmit-pipeline`、`paper-talk` 独立可用，互不自动串联 | [ ] 通过 |
| 11 | **工具缺失与边界** | 缺失外部环境（LaTeX/Lean/GPU）如实报告并降级，不假报成功，不自装环境 | [ ] 通过 |
