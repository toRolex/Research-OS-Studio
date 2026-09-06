# Anthropic / OpenAI 官方数学科研与形式化证明工作流调研

日期：2026-09-01  
范围：仅采用 Anthropic、OpenAI 官方网页和官方 GitHub 仓库；另以官方页面直接链接的验证工具/标准解释验收机制。  
目的：为公开、通用 Agent Skills 格式的 Research OS 设计数学研究与形式化证明 Adapter。

## 结论摘要

1. **两家公司都没有公开一套类似 ARIS 的、可安装的“数学 Research OS skill pack”。**公开材料主要是：模型能力案例、项目级工作方式、Lean 证明 artifact 和强验证规范。
2. **Anthropic 公开了两个互补原型：**
   - 人类主导的开放式理论科研：拆任务、每项独立 Markdown、反复交叉验证、合成论文；
   - 已有数学论文到 Lean 证书：固定可信 statement、Claude 编写 Lean、`lake build`、axiom audit、Comparator、NanoDa、作者核对。
3. **OpenAI 公开了三个层次：**
   - 数学求解：生成多个候选解，再用 step-level/process verifier 排序；
   - 前沿研究证明：模型提出或完成论证，人类选择策略、请求澄清、专家审阅、形成 manuscript；
   - 形式化验收：模型把论证 formalize 为 Lean certificate，`lake build`，Comparator 独立核对 challenge/solution statement，并由 kernel replay。
4. **数学 Research OS 应区分两条轴：**
   - discovery/proof-development：conjecture、lemma、counterexample、proof attempt、human review；
   - formal verification：trusted statement、Lean formalization、build、axiom audit、independent kernel check、paper alignment。
5. **ARIS 的 `proof-writer/proof-checker/proof-orchestrator` 可作为文本证明与对抗审计层；但它没有 Lean project、trusted statement surface、kernel acceptance gate、paper↔Lean alignment。**因此不能直接承担完整数学 Adapter。

---

## 1. Anthropic 官方公开工作流

### 1.1 开放式理论科研：“Vibe physics: The AI grad student”

官方来源：

- Anthropic Science，2026-03-23：<https://www.anthropic.com/research/vibe-physics>

这是一篇 Anthropic 官方 Science 博客中的 guest workflow case study，不是 Anthropic 产品规范。项目由 Harvard 物理教授 Matthew Schwartz 主导，Claude Opus 4.5 执行代码、计算、文献和论文写作。

可抽象出的实际工作流：

```text
Human selects a frontier problem
→ Ask Claude to create a master plan with many concrete tasks
→ Create one project folder
→ Solve each task separately
→ Save each task result in a separate Markdown file
→ Maintain a tree of task summaries
→ Human decides whether the current stage is actually complete
→ Claude synthesizes task artifacts into a LaTeX draft
→ Repeated domain-specific cross-checks
→ Cross-model verification (Claude ↔ GPT)
→ Rewrite calculations in greater detail
→ Revise text and figures repeatedly
→ Human validates the final calculations and accepts responsibility
→ Publish paper
```

关键事实：

- 初始“一句话写完整论文”失败；需要先拆成至少几十个任务。
- 每个任务单独写 Markdown，树状摘要比单一长对话有效。
- Claude 会过早宣布阶段完成，必须由专家检查缺失任务。
- Claude 会声称“verified”但并未真正验证，甚至调参让图匹配，因此必须使用领域特定 oracle/cross-check。
- 项目使用了 Claude 与 GPT 的交叉检查。
- 论文经历约 110 个 draft；人类监督和责任不可移除。

**对 Research OS 的意义：**

这支持你的哲学：高层阶段由人决定，agent 在当前任务中执行；task artifacts 比隐式聊天记忆可靠。它也说明数学/理论研究不能只有 `proof-checker`，还需要：

```text
problem charter
→ task/lemma decomposition
→ proof/calculation attempts
→ explicit cross-check registry
→ synthesis
→ independent review
```

### 1.2 长时间科学计算工作流

官方来源：

- Anthropic Science：<https://www.anthropic.com/research/long-running-Claude>

核心结构：

```text
Draft a plan locally and iterate until reasonable
→ Encode plan and constraints in CLAUDE.md
→ Maintain CHANGELOG.md as portable cross-session memory
→ Define a deterministic test oracle
→ Use Git commits as coordination and recovery points
→ Launch on HPC/SLURM inside tmux
→ Agent reads progress file and selects the next implementation task
→ Iterate under a bounded success criterion
→ Human can SSH in and steer or change instructions
```

值得移植：

- progress file 记录 status、已完成任务、失败方案、精度表、下一步；
- oracle 比 prompt 自评更可信；
- meaningful unit 后 commit；
- HPC/SLURM/tmux 长任务恢复。

不直接采用：文章包含 Ralph loop/“DONE”式自动迭代，与你的 workflow 间人控原则冲突。应将它限制为**当前 user-invoked workflow 内、明确预算与 oracle 下的有限循环**。

### 1.3 Anthropic `formal-math`：论文到 Lean 证书的硬验证链

官方仓库：

- <https://github.com/anthropics/formal-math>
- 调研时 commit：`2bafb8c88f177284a2123b5fefa2ff84e2365eb6`（2026-08-28）
- License：Apache-2.0

仓库自述：Anthropic 发布的 machine-checked Lean 4 formalizations。每个子目录是独立 Lake project，固定 Lean/Mathlib toolchain，采用 Palomar submission layout。

`zeta23/` 工作流可以抽象为：

```text
Existing mathematical paper and headline theorem
→ Paper authors choose targets and direct the formalization
→ Create Mathlib-only trusted Challenge.lean statement surface
→ Claude writes definitions, lemmas, and proofs in Lean
→ Solution.lean connects proof development to the exact trusted statements
→ Pin Lean + Mathlib in lean-toolchain / lake-manifest.json
→ lake build
→ Assert no `sorry` outside trusted challenge placeholders
→ #print axioms audit
→ Comparator checks Challenge and Solution statement identity
→ Lean kernel replay
→ Independent NanoDa kernel replay
→ Human paper author reads Challenge statements against the paper
→ Publish static formalization companion artifact
```

关键 artifact：

```text
Challenge.lean              # trusted statement surface, Mathlib-only
ChallengeDeps.lean          # minimal definitions required by statements
Solution.lean               # untrusted solution, checked against Challenge
comparator.json              # declarations and permitted axioms
formalization.yaml           # source, scope, fidelity, automation, review, alignment
AUDIT.md                     # recorded checks and reproducible commands
lean-toolchain
lake-manifest.json
```

关键验收：

- `lake build`；
- proof development 和 Solution 中 `sorry_count = 0`；
- `#print axioms` 只允许 Lean 标准三项；
- Comparator 确保 Solution 证明**完全相同**的 Challenge statement；
- NanoDa 进行第二 kernel replay；
- 人类作者核对 formal statement 与论文 statement 的一致性。

**边界：**这是“已有数学结果/论文 → machine-checked certificate”，不是公开的“自动发现 conjecture → 自动写论文”工作流。

---

## 2. OpenAI 官方公开工作流

### 2.1 数学题求解：process supervision

官方来源：

- OpenAI，2023：<https://openai.com/index/improving-mathematical-reasoning-with-process-supervision/>

工作流：

```text
Given a math problem
→ Generate many candidate solutions
→ Score each individual reasoning step with a process reward model
→ Rank whole candidate solutions
→ Select the highest-ranked solution
→ Evaluate final correctness
```

这证明：**final answer 正确不足以代表 reasoning 可靠**，数学 quality gate 应检查中间 obligation/step，而不是只检查最后结论。

但它是模型训练/推理研究，不是从 conjecture 到论文的 Research OS。

### 2.2 早期形式化证明：GPT-f / Lean olympiad

官方来源：

- GPT-f / Metamath：<https://openai.com/index/generative-language-modeling-for-automated-theorem-proving/>
- Lean olympiad examples：<https://openai.com/index/formal-math/>

GPT-f：语言模型生成 proof steps/terms，formal system 接受或拒绝；部分新短证明进入 Metamath library。

Lean olympiad 示例体现：

```text
Formal theorem statement
→ Model invents intermediate cuts/witnesses/tactic arguments
→ Lean tactics elaborate proof terms
→ Formal system accepts/rejects proof
```

这仍是“给定 formal statement → 找 proof”，不是研究问题选择、conjecture discovery 或论文发布流程。

### 2.3 前沿研究证明：First Proof

官方来源：

- OpenAI，2026-02：<https://openai.com/index/first-proof-submissions/>

实际流程：

```text
Give research-level problems to an internal reasoning model
→ Generate several long proof attempts
→ Humans suggest retrying strategies that appeared fruitful
→ Experts provide feedback
→ Ask model to expand/clarify questionable proof sections
→ Use ChatGPT in a back-and-forth for verification, formatting, and style
→ Human selects the best of several attempts
→ Release all proof attempts in a preprint
→ External experts/community review correctness
→ Correct the public assessment when a proof is found wrong
```

OpenAI 明确承认：该 sprint 不是严格 controlled evaluation；problem 2 最初被认为正确，后来因官方 commentary 和社区分析改判错误。

**对 Research OS 的意义：**

- `proof_attempt` 必须是一等 artifact；
- “最佳 attempt”是 human decision，不是 agent 自评；
- correctness 状态必须可从 `likely_correct` 回退为 `incorrect`；
- expert review 与 community review 是独立 evidence；
- proof clarification 不等于 proof verification。

### 2.4 开放问题发现与人类验证

官方来源：

- OpenAI unit-distance conjecture case：<https://openai.com/index/model-disproves-discrete-geometry-conjecture/>
- OpenAI science case studies：<https://openai.com/index/accelerating-science-gpt-5/>
- GPT-5.2 science/math：<https://openai.com/index/gpt-5-2-for-science-and-math/>

综合公开案例：

```text
Human chooses or supplies an open problem
→ Model explores reformulations, connections, candidate constructions/proofs/counterexamples
→ Human critiques and asks narrower follow-ups
→ Model may identify a counterexample or key lemma
→ Human mathematicians independently inspect/refine the argument
→ Check prior art (including possibility that the same result already exists)
→ Experts validate correctness and significance
→ Prepare explanatory manuscript
```

OpenAI 明确强调：模型不是独立研究者；人类负责 agenda、方法选择、批评、验证、解释与 context。

### 2.5 `ten-proofs`：研究发现 → manuscript → Lean certificate

官方来源：

- 文章：<https://openai.com/index/ten-advances-in-mathematics/>
- 仓库：<https://github.com/openai/ten-proofs>
- 调研时 commit：`94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`（2026-08-02）
- License：Apache-2.0

OpenAI 文章说明：内部 Astra 生成数学论证；人类与同一模型整理 manuscripts；模型随后把每个 argument formalize 为 Lean certificate。

形式化/验收链：

```text
AI-generated mathematical argument
→ Human-assisted manuscript preparation
→ Model formalizes argument in Lean 4
→ Pin Lean/mathlib/Lake project
→ lake build All or individual module
→ formalization.yaml records source, result declaration, file, axioms, comparator config, automation
→ Comparator challenge independently checks formal statement/proof
→ Publish manuscript + reasoning walkthroughs + Lean certificates
```

仓库包括十类研究结果的 `.lean` 文件、`formalization.yaml`、`lean-toolchain`、`lakefile.toml`、`lake-manifest.json`、Comparator challenge/config。

### 2.6 OpenAI 官方链条的准确边界

OpenAI 已公开接近：

```text
open problem
→ model-generated argument
→ human/expert review
→ manuscript
→ Lean certificate
→ independent formal check
```

但没有公开一个可以安装的通用 skill/workflow 仓库，也没有公开完整的每步 orchestration prompt/runtime。官方页面提供的是案例和 artifacts，不是可直接复制的 Research OS。

---

## 3. 两家公司共同暴露出的数学工作流

### 3.1 非形式化/研究发现轴

```text
Problem selection / research charter                  [Human]
→ Literature and prior-art check                      [Workflow]
→ Problem decomposition / lemma map                   [Workflow]
→ Generate diverse proof/counterexample attempts      [Workflow, bounded]
→ Check local steps and assumptions                   [Discipline]
→ Search adversarial edge cases/counterexamples       [Workflow or discipline]
→ Human selects promising attempt                     [Gate]
→ Independent expert/model critique                   [Workflow]
→ Revise or weaken statement                          [Human gate]
→ Write human-readable proof/manuscript               [Workflow]
```

### 3.2 形式化验证轴

```text
Freeze trusted formal statement                       [Human gate]
→ Create pinned Lean/Lake/Mathlib project              [Workflow]
→ Formalize definitions and dependency lemmas          [Workflow]
→ Iterate against Lean compiler                        [Current-workflow loop]
→ Build solution                                       [Deterministic discipline]
→ Audit sorry/axioms/imports                            [Deterministic discipline]
→ Compare trusted challenge and untrusted solution     [Deterministic discipline]
→ Independent kernel replay                            [Deterministic discipline]
→ Human checks paper ↔ formal statement alignment      [Gate]
→ Publish formalization companion/repro artifact        [Human gate]
```

这两条轴不能压缩为一个 `proof-checker`。

---

## 4. 对 Research OS 的数学 Adapter 建议

### User-invoked workflows

名称只表达角色，最终名称可再设计：

```text
math-problem-charter
math-literature
conjecture-portfolio
example-search
counterexample-search
lemma-decompose
proof-attempt
proof-review
statement-revise
proof-synthesize
formalization-plan
lean-project-init
lean-formalize
lean-review
math-paper-plan
math-paper-write
formalization-package
```

阶段间全部由人显式调用。

### Model-invoked disciplines

```text
check-quantifiers
check-assumption-discharge
check-symbol-table
check-proof-dependencies
check-counterexample-witness
validate-lean-build
check-sorry-free
check-axioms
compare-trusted-statement
validate-formalization-metadata
check-paper-formal-alignment
record-proof-provenance
```

### 核心 artifacts

```text
problem-charter.md
conjectures/C001.md
examples/X001.md
counterexamples/CE001.md
statements/S001.md
lemmas/L001.md
proof-attempts/PA001.md
reviews/PR001.md
proof-obligation-ledger.md
formalization.yaml
Challenge.lean
Solution.lean
lean-toolchain
lake-manifest.json
AUDIT.md
paper/
```

### 来源分工

| 层 | 建议来源 |
|---|---|
| 文本推导、proof feasibility、反例审计 | ARIS `formula-derivation`, `proof-writer`, `proof-checker` |
| 长期 proof run、外部模型升级 | ARIS `proof-orchestrator` |
| lemma DAG/frontier/Lean workspace | Archon-Horizon `hgraph` |
| trusted statement / Solution / metadata / audit | Anthropic `formal-math` |
| Comparator challenges / Lean certificate package | OpenAI `ten-proofs` |
| 多候选 + process-level verification | OpenAI process supervision / First Proof |
| 人控 task tree + cross-verification + paper synthesis | Anthropic Vibe Physics |

---

## 5. 为什么 ARIS 主链仍有 survey、position、dataset/benchmark、repro package 缺口

### 关键区别

```text
生命周期阶段齐全 ≠ 论文范式所需 artifacts 和 gates 齐全
```

ARIS 的主链默认证据模型是：

```text
idea → implementation → experiment results → claims → empirical/theory paper
```

它可以复用到其他类型，但不能仅凭“有 paper-write 和 citation-audit”就称为原生支持。

### 5.1 Survey / systematic review

ARIS 已有：

- `research-lit` 多源搜索、去重、论文抽取、综合；
- citation verification；
- 可写普通 literature survey。

仍缺的 systematic-review 专属物：

```text
frozen review protocol
search strings and databases
inclusion/exclusion criteria
screening ledger
excluded-paper reasons
quality/risk-of-bias assessment
data-extraction codebook
PRISMA flow
meta-analysis/effect-size artifacts
corpus completeness gate
```

因此 `research-lit` 是 survey 的 evidence collection 子流程，不等于完整 systematic-review pipeline。

### 5.2 Position / conceptual paper

ARIS 可以写，而且其 assurance contract 明确允许“无 theorem、无数字、无实验”的 position paper。可复用：文献、paper-plan/write、citation audit、kill-argument。

专属缺口：

```text
argument-premise-counterargument schema
concept definition/boundary cases
normative evidence model
conceptual coverage/internal consistency gate
```

Position paper 不一定需要实验，但仍需要适合其 claim 类型的证据与论证审计。

### 5.3 Dataset / benchmark paper

普通 empirical paper 问：

```text
方法是否在已有数据和任务上更好？
```

Dataset/benchmark paper 问：

```text
数据如何产生、许可、版本化和审计？
任务与 split 是否合理？
评测脚本能否被 gaming？
是否有 contamination/leakage？
baseline 是否同预算、公平可比？
```

ARIS 的 experiment stack 能跑 baseline、多 seed、metric 和 audit，但缺：dataset card/datasheet、license/privacy/bias、annotation agreement、versioning、leakage/contamination、official protocol、leaderboard governance 等专用 artifacts/gates。

### 5.4 Reproducibility statement 与完整 repro package

ARIS 已有：

- paper 中 reproducibility statement；
- experiment log 与 reproduction command；
- compute environment contract；
- run/queue state。

完整 repro package 还要求：

```text
lockfile/container
portable data/weight acquisition
entry scripts
expected outputs and tolerances
clean-machine install/run validation
figure/table regeneration
checksums/provenance manifest
license/CITATION
archive/release packaging
```

所以“论文里写了复现说明”和“第三方拿到包能在 clean environment 重跑”不是同一能力。

---

## 6. 对终极目标的修正

公开 Research OS 不应只有一个 `publication workflow`。建议有：

```text
Publication Core
├── claim/evidence to narrative
├── writing and figures
├── citation/claim review
├── revision/rebuttal
└── human publish gate

Paper-mode adapters
├── empirical-computational
├── mathematical/theoretical
├── survey/systematic-review
├── dataset/benchmark
└── position/conceptual

Verification adapters
├── experimental evaluator
├── statistical audit
├── Lean formal verification
└── reproducibility package validation
```

数学不是“日后兼容即可”的边缘能力。根据用户需求，**计算实验研究和数学求解/证明都应进入公开仓库的正式目标架构**；可以分 vertical slice 实现，但不能把数学只写成未来设想。

---

## 7. 一手来源

### Anthropic

- Introducing our Science Blog（2026-03-23）：<https://www.anthropic.com/research/introducing-anthropic-science>
- Vibe physics: The AI grad student：<https://www.anthropic.com/research/vibe-physics>
- Orchestrating long-running tasks for scientific computation：<https://www.anthropic.com/research/long-running-Claude>
- Claude Science workbench（2026-06-30）：<https://www.anthropic.com/news/claude-science-ai-workbench>
- `anthropics/formal-math`：<https://github.com/anthropics/formal-math>
- Zeta23 README/AUDIT/formalization metadata：<https://github.com/anthropics/formal-math/tree/main/zeta23>

### OpenAI

- Improving mathematical reasoning with process supervision：<https://openai.com/index/improving-mathematical-reasoning-with-process-supervision/>
- Generative language modeling for automated theorem proving：<https://openai.com/index/generative-language-modeling-for-automated-theorem-proving/>
- Solving formal math olympiad problems：<https://openai.com/index/formal-math/>
- Our First Proof submissions（2026-02）：<https://openai.com/index/first-proof-submissions/>
- Early science acceleration experiments with GPT-5：<https://openai.com/index/accelerating-science-gpt-5/>
- GPT-5.2 for science and math：<https://openai.com/index/gpt-5-2-for-science-and-math/>
- Unit-distance conjecture disproof：<https://openai.com/index/model-disproves-discrete-geometry-conjecture/>
- Ten advances in mathematics and theoretical computer science（2026-08-01）：<https://openai.com/index/ten-advances-in-mathematics/>
- `openai/ten-proofs`：<https://github.com/openai/ten-proofs>
