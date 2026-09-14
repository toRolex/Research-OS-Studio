# 上游来源、许可证与采用边界

本清单服务后续 Skill 搬运和人工采用判断。它是法律与维护信息，不是 port database、来源认证协议或运行时 gate；Git commit 仅用于说明本次核对所见版本。核对日期：2026-09-08。

## 采用规则

- **可复制**：许可证明确兼容时，优先复制完整 `SKILL.md` 及其实际依赖的 references、templates、assets、必要 scripts，再做最小适配；保留版权与许可证文本。
- **仅借鉴**：许可证不兼容、未明确授权，或只需要 runtime 中的抽象方法时，只依据公开行为和接口 clean-room 重写，不复制源码、Skill 文本或结构性表达。
- **来源异常**：revision、路径或许可证无法在对应上游重放时不得复制；先修正来源，再作决定。
- 仓库级许可证不自动覆盖 vendored templates/assets；复制前逐项读取其内嵌许可证、README 或 attribution。
- 不搬运中央 runtime、自动跨主流程推进、无限循环、provider harness、隐藏状态、统一 schema/validator、hash/digest/receipt 或 port ledger。

## 来源清单

| 来源与作者 | 本次核对 revision | 拟采用 Skill／方法与原路径 | 许可证、attribution 与决定 |
|---|---|---|---|
| [Matt Pocock Skills](https://github.com/mattpocock/skills)，Matt Pocock | `3cca18b368ae95cdbdebbff572ccafa662551015` | setup 方法：`skills/engineering/setup-matt-pocock-skills/SKILL.md`、`domain.md`、`issue-tracker-*.md`、`triage-labels.md`；只读路由方法：`skills/engineering/ask-matt/SKILL.md`、`PHASE-BOUNDARIES.md` | MIT，`Copyright (c) 2026 Matt Pocock`。可复制完整相关资产并最小改造成 `setup-research-os`／`ask-research-os`；保留 MIT notice。 |
| [ARIS / Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)，wanshuiyin | `0472e530251cdbd3364c33b110063c58f819edd7` | Idea：`skills/idea-discovery/`、`research-lit/`、`idea-creator/`、`novelty-check/`、`research-review/`、`research-refine/`；实验：`experiment-plan/`、`experiment-bridge/`、`run-experiment/`、`experiment-queue/`、`monitor-experiment/`、`training-check/`、`analyze-results/`、`experiment-audit/`、`result-to-claim/`；写作：`paper-writing/`、`paper-plan/`、`paper-write/`、`paper-figure/`、`paper-compile/`、`rebuttal/`、`resubmit-pipeline/`、`paper-talk/` | MIT，`Copyright (c) 2026 wanshuiyin`。主要可复制来源；复制每个成熟 Skill 的完整关联资产，删除 `.aris`、provider/MCP 绑定、默认自动推进和跨主流程调用。模板需另核内嵌第三方许可。 |
| [Orchestra AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs)，Claude AI Research Skills Contributors / Orchestra Research | `773a52944ba4747a18bd4ae9ade53fff041adcbc` | `20-ml-paper-writing/{ml-paper-writing,systems-paper-writing,academic-plotting,presenting-conference-talks}/`；`21-research-ideation/{brainstorming-research-ideas,creative-thinking-for-research}/`；可参考 `0-autoresearch-skill/` 的有界循环方法和 `22-agent-native-research-artifact/` 的 provenance 方法 | MIT，`Copyright (c) 2025 Claude AI Research Skills Contributors`。写作／构思 Skill 可复制完整资产后最小适配；venue templates 逐目录核许可。`0-autoresearch-skill` 的强制 `/loop`、自动写作和 01–19 runtime/tool-specific 手册不搬运。 |
| [AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw)，Aiming Lab | `be4ba4755bf1b52220f25e13b2293b5956590070` | 只借鉴 `researchclaw/pipeline/stages.py` 的 stage/gate 方法、`docs/HITL_GUIDE.md` 的 HITL 决策方法、`researchclaw/literature/verify.py` 的 citation verification 方法 | MIT，`Copyright (c) 2026 Aiming Lab`。本产品不需要其 23-stage runtime；不复制 runner、自动 rollback/pivot/refine、`--auto-approve` 或环境编排代码。若后续复制独立 verifier，必须先记录精确原路径和随附依赖。 |
| [EurekAgent](https://github.com/THU-Team-Eureka/EurekAgent)，THU-Team-Eureka | `fb96df897dfb99797a77623aa0dd9ee178fe89d2` | 只借鉴 evaluator 隔离思想：示例 `examples/*/hidden_eval_dir/evaluate.py`，容器与 grader 参考 `src/docker/container.py`、`src/eval_grader/server.py`；公开 Skills 位于 `.claude/skills/{generate-inputs,implement-approach,prepare-workspace,propose-approaches}/` | AGPL-3.0。**仅 clean-room 借鉴公开思想**；不复制任何源码、Skill 文本、LangGraph、grader server、Docker runtime 或 hooks。 |
| [Archon-Horizon](https://github.com/frenzymath/Archon-Horizon)，FrenzyMath | `c8885e05f1d0dff40f727ec45d5238b3c80b6336` | 只借鉴 workspace-first Lean、fresh-context review、read-only enforcement、checkpoint/resume 方法；当前实现路径包括 `src/archon_horizon/orchestration/orchestrator.py`、`src/archon_horizon/runlog.py` | Apache-2.0；NOTICE：`Archon Horizon Copyright 2026 FrenzyMath`，并要求关注 `THIRD_PARTY_NOTICES.md`。排除 orchestrator、ledger/inbox/dashboard/provider harness 等 runtime。历史报告声称的顶层 `hgraph/`、`subagents/compile.py` 在本次 revision 不存在，因此不得按旧路径复制。 |
| [karpathy/autoresearch](https://github.com/karpathy/autoresearch)，Andrej Karpathy | `228791fb499afffb54b46200aca536f79142f117` | `program.md` 的固定修改范围、固定时间预算、固定 metric、keep/discard、crash/timeout 记录方法；`README.md` 的公开设计说明 | README 声明 MIT，但本次树无 `LICENSE` 文件，GitHub API 为 `NOASSERTION`。按**许可证证据不足**处理：暂不复制 `program.md` 正文，只 clean-room 借鉴上述公开方法；上游补齐明确许可后再复核。 |

## 已采用资产

- `skills/general/setup-research-os/`：2026-09-12 重新核对 Matt Pocock Skills 官方 HEAD，仍为上表 `3cca18b368ae95cdbdebbff572ccafa662551015`。完整阅读原 `setup-matt-pocock-skills/SKILL.md`、五个共置 Markdown 种子、`agents/openai.yaml` 及根 MIT 许可后改编。保留 prompt-driven 探索、推荐逐问、完整草稿确认、CLAUDE/AGENTS 优先级和原位区块更新；以自包含科研工作区种子替换工程 tracker/triage/domain 配置，增加重复执行、冲突、写入后验证和明确停止边界。没有移植 tracker 远程操作或其他 Skill 调用。MIT 全文与 `Copyright (c) 2026 Matt Pocock` 随 Skill 的 `LICENSE` 一起发行，宿主元数据保留显式调用策略。

## 已采用的候选生成能力

2026-09-12 通过官方 GitHub API 重新解析上表 ARIS 与 Orchestra 的固定 revision，并读取完整原文、递归目录树、实际调用引用及仓库 MIT 许可；此日期表示采用复核，不声称所列版本为最新 HEAD。下列三个原 Skill 目录在该版本均只有 `SKILL.md`，没有额外共置 references/templates/assets 或单独第三方资产许可。

| 本仓 Skill | 上游原路径、作者与实际采用内容 | 共置许可与适配边界 |
|---|---|---|
| `skills/idea-cycle/idea-generation/` | ARIS / wanshuiyin，`skills/idea-creator/SKILL.md`：landscape 操作、五视角 fan-out、完整实质生成提示、方法先行、信息价值及客观合并；Orchestra / Claude AI Research Skills Contributors，`21-research-ideation/brainstorming-research-ideas/SKILL.md`：完整十个操作框架、自查、选择表、常见陷阱及有界组合方法。revision 分别为 `0472e530251cdbd3364c33b110063c58f819edd7`、`773a52944ba4747a18bd4ae9ade53fff041adcbc`。 | `LICENSE-ARIS.txt`、`LICENSE-Orchestra.txt` 保存完整 MIT notices；方法资源随 Skill 分发。删除上游固定模型/GPU、review provider、wiki/runtime 及自动 pilot；质量 kill filters 改为疑问注释，生成者只去重与依据硬约束暂存，独立评审不属于本能力。 |
| `skills/idea-cycle/creative-thinking-for-research/` | Orchestra / Claude AI Research Skills Contributors，`21-research-ideation/creative-thinking-for-research/SKILL.md`，revision `773a52944ba4747a18bd4ae9ade53fff041adcbc`：保留八个认知框架、完整操作步骤、示例、自查、creative-block guide 和四阶段组合 protocol。 | `LICENSE-Orchestra.txt` 保存完整 MIT notice。保留 bisociation、representational change、structure-mapping、Boden、negation/TRIZ、Polya、adjacent possible、Janusian 独有方法；纠正示例中“超越信息论极限”等过度断言、年代推断 prior work 及自动 handoff；验证表述限定为候选测试设计。 |

原始调用关系为 ARIS `idea-discovery → idea-creator`，后者原版再调用 novelty/review、实验和 wiki；Orchestra 两个 ideation 能力仅在正文建议配合，没有 ARIS 到 Orchestra 的原生调用实现。本仓组合是有意适配：两个默认 model-invoked 能力均支持用户点名 standalone；`idea-generation` 可在当前授权生成职责内使用已安装的 `creative-thinking-for-research`，后者只返回洞见。两个 Skill 各自资源自包含，无中央 runtime，亦不自动启动顶层 Workflow。构思自查与回顾性 reflection 均不替代独立 idea-review；最终科研采用仍由用户决定。

## 已采用的运行监控与训练健康 Skill

`skills/validation-cycle/monitor-experiment/` 与 `skills/validation-cycle/training-health-check/` 均为 model-invoked 内部能力，用户可点名 standalone，被父 Workflow 调用时只在授权职责内贡献对应章节。2026-09-13 通过官方 GitHub API 重新解析 ARIS revision `0472e530251cdbd3364c33b110063c58f819edd7`，全文读取两个 `SKILL.md`、递归目录树，以及其引用的 `skills/shared-references/{external-cadence,output-composition,experiment-integrity}.md` 与实际调用方 `skills/experiment-bridge/SKILL.md`。两个原目录在该版本均只有 `SKILL.md`，无共置 references/templates/assets 或独立第三方许可；仓库根 MIT 覆盖两者。

| 本仓 Skill | 上游原路径、作者与实际采用内容 | 共置许可与适配边界 |
|---|---|---|
| `skills/validation-cycle/monitor-experiment/` | ARIS / wanshuiyin，`skills/monitor-experiment/SKILL.md`：保留“外部等待只自判机器可查完成、绝不重跑质量裁决”的核心分离，以及读取进程／调度状态、日志尾部、输出文件与退出证据的监控方法。 | `LICENSE` 保存完整 MIT notice。删除 `/loop`/CronCreate 自调度与定时重入、固定 SSH/screen/vast.ai/Modal 供应商假设、Feishu 通知、W&B 强制读取、成本提醒及结果比较／下一步建议；改为环境中立、只读、每次调用一次被动观测，状态仅限 running/completed/crashed/unknown，缺观测如实标 unknown。新增 `references/observation-sources.md` 与 `templates/run-status-report.md`。 |
| `skills/validation-cycle/training-health-check/` | ARIS / wanshuiyin，`skills/training-check/SKILL.md`：保留 NaN/Inf、发散、停滞的可检查信号、多 checkpoint 趋势优先于单点噪声、模糊降级和观察间隔自适应思想；从同 revision `experiment-bridge` 的 W&B 调用点及训练检查“质量 vs 进程健康”分层补充 OOM 与日志完整性。 | `LICENSE` 保存完整 MIT notice。按父 spec 重命名并重写为只诊断：删除 CronCreate 自调度、Codex MCP 裁决、`tools/watchdog.py` 分层、固定 model/W&B 依赖和“kill training”动作；诊断为 `no anomaly detected`／`anomaly detected`／`insufficient observation`／`indeterminate`，只给建议，停止／重启由用户执行。新增 `references/health-signals.md` 与 `templates/health-report.md`。 |

调用边界沿用 `output-composition` 的显式 composed 信号与 standalone 默认：无父 Workflow 的 `composed:` 指令时只输出自身报告，父 Workflow 存在时只贡献命名 canonical report 的对应章节。两者都不自调度、不创建后台轮询；按父 spec 移除上游 `external-cadence` 的定时等待，改为用户或授权父 Workflow 决定是否再次观测。`experiment-integrity` 的“执行者不评审自己的实验”在此仅体现为两项能力都不判断科研结论，不构成强制隔离声明。

## 已采用的查新 Skill

`skills/idea-cycle/novelty-check/` 属于 Idea Cycle，默认 model-invoked，也支持用户点名 standalone；被 Workflow 调用时只贡献已授权的查新报告，不自动推进科研流程。

- **来源**：wanshuiyin / ARIS，`skills/novelty-check/SKILL.md`，revision `0472e530251cdbd3364c33b110063c58f819edd7`。2026-09-12 从官方仓库重新核对；当日 HEAD `f1bd907b58f653131ebe6807c482e2554e07f9b9` 的该正文与采用版本一致。该 Skill 目录没有共置 references/templates/assets。
- **采用**：保留 A–D 全流程、Claim 分解、多源三种查询、closest-work 比较、独立复核、六条防误杀判断原则、组合/发现型新颖性及报告字段。查新专用身份核实方法参考同 revision 的 `skills/shared-references/citation-discipline.md` 的检索、身份核对、语境支持部分；不采用其中标明其他来源的末尾段落或无关 BibTeX 编辑职责。
- **适配**：删除固定 provider/MCP、中央 `verify_papers.py`、`.aris` tracing/schema 和过期年份；按现有宿主能力核实来源，以共置 `references/source-verification.md` 与 `templates/novelty-report.md` 自包含交付。明确授权、standalone/composed、硬预算及停止边界，补充有具体补证动作的 EVIDENCE GAP，避免证据缺失时强制放行。数值评分改为用户按需。
- **调用核对**：上游 `skills/idea-discovery/SKILL.md` Phase 3 实际调用 `novelty-check`；上游查新引用的 `integration-contract.md`、`citation-discipline.md`、`review-tracing.md` 及 `tools/verify_papers.py` 已阅读。保留核实与独立复核职责，不继承其 runtime、自动 pilots、receipt 或后续 Workflow 调用。
- **许可**：MIT，`Copyright (c) 2026 wanshuiyin`；完整 notice 随 Skill 放在 `LICENSE`，安装后仍保留。新增报告模板和引用规则为上述方法的局部适配，不依赖中央文档运行。

## 已采用的候选评审与方法改进

2026-09-12 从 ARIS 官方 GitHub API 重新解析 `0472e530251cdbd3364c33b110063c58f819edd7` 并完整读取下述正文、目录树、直接引用与 MIT 许可；采用固定版本，不声称是最新 HEAD。两个原 Skill 目录都只有 `SKILL.md`，没有额外共置 references/templates/assets 或第三方资产。

| 本仓 Skill | 上游原路径与采用内容 | 共置许可与适配 |
|---|---|---|
| `skills/idea-cycle/idea-review/` | wanshuiyin / ARIS，`skills/research-review/SKILL.md`：上下文采集、独立 adversarial 初评、逻辑/证据/叙事/贡献四面审查、证据反驳、同 reviewer 有界澄清、条件性 Claim 矩阵、优先行动与完整对话记录。 | MIT 全文及 `Copyright (c) 2026 wanshuiyin` 放在 `LICENSE`。将含论文/结果的宽泛 review 限定为现成 Idea；保留实质评审任务与后续提问，按需披露到共置 reference/template。删除固定 provider/MCP、安装指令、tracing/runtime；仅评审报告写入，reviewer 不修订候选。 |
| `skills/idea-cycle/idea-refinement/` | wanshuiyin / ARIS，`skills/research-refine/SKILL.md`：固定五字段 Problem Anchor、完整 Phase 1 方法开发、MVP/frontier 双路线、十一项机制具体化、1–3 项 Claim 驱动验证草图、七轴独立方法评审、Anchor/Simplicity Check、证据 pushback、逐轮完整 Proposal 与改进记录。 | 同 revision、同 MIT notice，随 `LICENSE` 发行。原方法开发段、修订检查及完整 Proposal 模板搬入共置 references/templates 后最小适配；保留七轴实质评价与可选原权重。移除 provider、JSON checkpoint、中央输出协议、强制分数停止、自动实验/跨流程调用；领域不适用项明确说明。 |

**调用关系复核**：原 `idea-discovery` Phase 4 实际调用 `research-review`；Phase 4.5 调用 `research-refine-pipeline`，后者 Phase 1 调用 `research-refine`、Phase 3 再调用 `experiment-plan`。本票保留前两项研究职责，未复制 pipeline 的自动规划/执行链。本仓二者均为 model-invoked Internal Skills，用户可点名 standalone，明确授权时 composed；review 不自动启动 refinement，refinement 自带局部独立方法评审任务，无 sibling Skill 安装依赖。

**引用与取舍**：完整读取 `reviewer-routing.md`、`reviewer-independence.md`、`review-scope-limits.md`、`external-cadence.md`、`review-tracing.md`、`integration-contract.md`、`output-composition.md`、`output-versioning.md`、`output-manifest.md`、`output-language.md`、`taste-calibration.md`。采纳原始材料直达 reviewer、同 reviewer 续轮、standalone/composed 明确信号与完整原始交互记录；舍弃安装、provider routing、`.aris`、中央 helper/schema/manifest、自动状态恢复与越权写入。独立性规则优先于原 refine 中传作者 key-changes 摘要的示例。`taste-calibration.md` 含其他来源归因，不复制该文件；七轴来自 `research-refine`，只有用户提供人工精选参照时才可报告有参照评分，缺少即说明未校准。

场景材料（公开现成候选、论文、原实验代码）仅临时用于实现期验证，不随产品分发；用户真实研究效果与端到端体验仍待用户验收。

## 已采用的实验计划 Workflow

`skills/validation-cycle/experiment-plan/` 为独立 user-invoked Workflow，只将已有问题转为可授权执行的计划，不运行实验。2026-09-12 通过官方 GitHub API 重新解析以下固定 revision；这是采用复核，不声称最新 HEAD。

- **可复制来源**：wanshuiyin / ARIS，`skills/experiment-plan/SKILL.md`，revision `0472e530251cdbd3364c33b110063c58f819edd7`。全文阅读原正文和递归目录树；该目录仅有 `SKILL.md`，无共置 references/templates/assets 或额外第三方许可。根 MIT 全文随本 Skill 的 `LICENSE` 发行。
- **完整方法与最小适配**：保留 Phase 0–5 的 Problem Anchor、主/支持/反主张、最小可信证据、五类实验 block、主文/附录/删去划分、strong baselines、simplicity/deletion 与 frontier necessity、每 block 全部字段、五阶段顺序、风险缓解、计划与 tracker 全部原字段及最终检查表。原内联输出模板移到共置 `templates/experiment-plan.md`，未缩写为契约壳；新增固定评价面、判别性比较、逐 criterion 原始证据、硬预算和负/无效/不确定/运行失败区分。
- **引用与真实调用核对**：全文阅读原 `skills/shared-references/{output-versioning,output-manifest,output-language,output-composition}.md`，以及实际调用方 `skills/research-refine-pipeline/SKILL.md` 和消费计划的 `skills/experiment-bridge/SKILL.md`。前者 Phase 3 调用 experiment-plan；后者读取 plan/tracker 后实现与部署，并非 experiment-plan 的必需执行依赖。本仓不复制这些调用者或协议：以确认输出路径、不覆盖和用户语言替代固定目录/自动 latest-copy/manifest；删除 provider 工具名单、权限失败改用 shell 的绕过指令和自动后续 Workflow 建议。独立 user-invoked 入口不提供由另一 Workflow 自动调用的 composed 模式；用户可以直接把既有材料作为输入，无前置流程 gate。
- **仅借鉴 autoresearch 方法**：Andrej Karpathy，revision `228791fb499afffb54b46200aca536f79142f117`；重新全文读取 `README.md`、`program.md` 并核对目录树。该版本 README 声明 MIT，但树内仍无 LICENSE；延续许可证证据不足决定，不复制正文、训练实现或资源。只独立表达 baseline-first、固定修改面、固定时间/metric 和保留失败尝试思想；不采用无限循环、自动 commit/reset 或超时自动 kill。训练/评估运行时不作为本 Skill 依赖。
- **仅借鉴评价职责分离**：THU-Team-Eureka / EurekAgent，revision `fb96df897dfb99797a77623aa0dd9ee178fe89d2`；全文读取公开 `README.md` 的设计与评价接口说明，核对固定版本 LICENSE 存在及 GitHub AGPL-3.0 识别。只依据公开思想独立表述候选与评价职责分离；不读取后搬运 AGPL Skill/源码、容器/grader/hook/runtime，也不声称 Skill 指令本身能提供强制隔离。

## 已采用的实验执行能力

`skills/validation-cycle/run-experiment/` 与 `skills/validation-cycle/experiment-queue/` 属于 Validation Cycle，默认 model-invoked 的内部能力；可由当前 Validation Workflow 在已授权职责内组合，用户也可点名 standalone。两者只贡献一次授权范围内的执行与 attempt 记录，不自动启动监控、分析、审计、Results-to-Claims 或写作。

- **来源**：wanshuiyin / ARIS，`skills/run-experiment/SKILL.md`（该目录仅 `SKILL.md`）与 `skills/experiment-queue/SKILL.md`（另有 `scripts/queue_manager.py`、`scripts/build_manifest.py`），revision `0472e530251cdbd3364c33b110063c58f819edd7`。2026-09-14 通过官方 GitHub API 重新解析 revision、逐文件目录树与仓库 MIT 许可；同时阅读 `experiment-bridge/SKILL.md`、`monitor-experiment/SKILL.md`、`training-check/SKILL.md` 及 `shared-references/compute-env-contract.md`、`shared-references/external-cadence.md` 以核对真实调用关系。
- **采用**：保留计划解析与按 milestone 实现、代码 review、sanity-first、baseline-first、按规模选择单次/批量执行、OOM 有限重试、停滞清理、波次依赖、预期输出完成判定、状态持久化与 resume、完整 attempt 收集。
- **适配**：删除 Vast.ai/Modal/`serverless-modal` provider 绑定、`mcp__codex` 固定审查、自动 deploy、无限调试/自动重试、自动 ablation/下一 Workflow、`.aris`/`nohup`/`screen` 调度和 `queue_manager.py` 常驻 scheduler；改为纯 Markdown 的作业清单、状态表与宿主已有执行工具。新增候选实现/evaluator 隔离、真实 ground truth、执行前确认、付费/远程/高成本授权、停止/重启权限、成功/失败/无效/超时 attempt 留存和演练/真实验收区分；`run-report.md` 与 `batch-manifest.md` 为局部适配模板。
- **调用核对**：上游 `experiment-bridge` Phase 4 按 job 数在 `run-experiment` 与 `experiment-queue` 间路由，Phase 5 收集初步结果并调用 `training-check`；本票只实现路由所需的两个执行能力，监控/分析/审计/Claims 属后续独立票，未在此虚构调用。上游 queue 引用的 `compute-env-contract.md`、`external-cadence.md` 已阅读，只保留其中与执行边界相关的有界性方法。
- **许可**：MIT，`Copyright (c) 2026 wanshuiyin`；完整 notice 随两个 Skill 的 `LICENSE` 一起发行。

## 已采用的独立实验审计 Skill

`skills/validation-cycle/experiment-audit/` 属于 Validation Cycle，默认 model-invoked，也支持用户点名 standalone；被 Workflow 调用时只贡献已授权的审计章节，不自动推进科研流程。

- **来源**：wanshuiyin / ARIS，`skills/experiment-audit/SKILL.md`，revision `0472e530251cdbd3364c33b110063c58f819edd7`。2026-09-14 从官方 GitHub API 重新核对；当日 HEAD `f1bd907b58f653131ebe6807c482e2554e07f9b9` 的该正文与采用版本逐字一致。该 Skill 目录没有共置 references/templates/assets。
- **采用**：保留“执行者只收集路径、独立审查者直接读取并判定”的核心原则，A–F 检查（ground truth provenance、score normalization、result existence 与数字对应、dead code、scope、evaluation type），以及 fake ground truth、phantom results、insufficient scope 的失败模式说明。`references/integrity-checks.md` 与 `templates/audit-report.md` 逐条承载这些检查问题和报告字段，均为上述方法的局部适配。
- **适配**：删除 Codex／Manual Review MCP 后端与 reviewer 路由、`.aris/` trace/receipt、`EXPERIMENT_AUDIT.json` 机器输出、`/loop`/`/schedule` 定时包装及 pipeline 自动调用；改为使用宿主已有的独立审查能力，不可用时如实降级为 single-agent assessment。补充 protocol conformance 与 independent experiment integrity 双证据线、授权与写入边界、standalone/composed、finding 分级与停止条件；不修改代码、不重跑实验、不写中央状态。
- **许可**：MIT，`Copyright (c) 2026 wanshuiyin`；完整 notice 随 Skill 放在 `LICENSE`。
- **仅借鉴**：[EurekAgent](https://github.com/THU-Team-Eureka/EurekAgent)（AGPL-3.0，revision `fb96df897dfb99797a77623aa0dd9ee178fe89d2`）的 evaluator 隔离与权威评价思想只作 clean-room 参考，未复制其源码、Skill 文本、grader、容器、runtime 或 hooks。
- **已排除**：同 revision 的 ARIS `skills/integrity-forensics/SKILL.md` 是 SHA-pin 薄启动器，依赖 `git clone`、eval gate、`.aris/forensics/*.json` 与 append-only obligations ledger；这些 runtime、hash/receipt 和 typed gate 属于父 spec 明确排除的范围，因此不搬运。

## 已采用的长期证明与可选 Lean 方法

`skills/validation-cycle/proof-orchestrator/` 为 user-invoked 独立 Workflow，只续接本轮授权的一个 obligation；保留上游清晰名称，不提供中央 orchestrator runtime。

- **ARIS 来源**：wanshuiyin / `skills/proof-orchestrator/`，revision `0472e530251cdbd3364c33b110063c58f819edd7`。2026-09-13 通过官方 GitHub API 重新读取完整 `SKILL.md`、`NOTICE.md`、六份共置 references（`dispatch-prompts.md`、`stress-tests.md`、`notation-audit.md`、`deepseek-routing.md`、`proof-audit-rubric.md`、`audit-output-contract.md`）及根 MIT 许可；该目录无其他 templates/assets。本机 ARIS checkout 的版本不同，未以本机内容替代固定来源，也未改动其已有工作。
- **采用与修改**：中文适配保留目标／假设冻结、本地完整尝试→正确性自查→表达、跨轮只读来源与失败路线、最小阻塞交接、原始返回与已审结论分离、八种提示、17 类问题、四级严重度、九项核查、完整 side conditions／反例方法、七行记号评分及全部阈值、目标向下推导与符号编辑顺序。`deepseek-routing.md` 改为供应商中立的 `independent-review.md`；保留真实模型身份核对、独立性标签与负面意见，用户豁免不改变数学真值。移除固定 provider/MCP、宿主目录、ledger、统一 JSON/hash、submission gate 与自动重试；用本轮普通 Markdown 说明承载续接事实，补充有限预算、写前冲突及环境边界。
- **真实调用关系**：上游本体自己完成本地尝试、自查和表达，外部交接／第二意见为可选分支；不是 `proof-writer → proof-checker` 的调用链。已核对原正文的全部调用引用及 `tests/test_proof_suite_integration.py`。上游对 writer/checker 的说明是职责分流和既有论文 gate 归属，本仓不导入这些依赖或伪装其科研验收效力。
- **ARIS 许可与 NOTICE**：完整 MIT，`Copyright (c) 2026 wanshuiyin`，随 Skill 的 `LICENSE` 分发；原 `NOTICE.md` 逐字保留。NOTICE 声明其 `proof-orchestrator` 套件改编自 shenmuxing / EtaSkill revision `f49ce5dd6b0bfb7565c35063e10aa1ac42a480e9`，由该贡献唯一版权人将这一适配贡献重新许可为 ARIS MIT。采用依据为 ARIS 所附明确再许可声明，并非把 EtaSkill 整仓 MPL-2.0 改判 MIT；本仓没有复制 EtaSkill 原仓库的其他文件。原 NOTICE 的版权身份叙述属于上游原声明，本段说明本地适配，不冒称其版权身份。
- **Archon 方法核对**：同日复核官方 `frenzymath/Archon-Horizon` revision `c8885e05f1d0dff40f727ec45d5238b3c80b6336`。完整阅读 `src/archon_horizon/skills/{leansearch,lean-check,mathlib-orientation,mathlib-conventions}/SKILL.md`（各目录只有该文件）、相关 `horizon`、`agents/prompts.py`、`skills/registry.py`、`commands/search.py`、`search/{workspace,index,mcp_server}.py`、`commands/check.py` 及 `LICENSE`、`NOTICE`、`THIRD_PARTY_NOTICES.md`。Apache-2.0，`Copyright 2026 FrenzyMath`；仅借鉴公开操作思想，不复制其 Skill、模板或实现，因此不分发 Archon／第三方代码。
- **Lean 表达与边界**：本仓独立撰写共置 `references/lean-methods.md`，结合 Lean／Mathlib 官方文档核对，说明现有工具链前置、候选搜索与原 signature 阅读、LSP 快速反馈、实际 kernel/build 覆盖、传递公理及编码命题忠实性。上游四项是按需指导，不是四个现成独立 Workflow；本地文本索引不是类型统一，外部 LSP 服务不等于本地 `lean_search`。不采用 check 包装器、共享锁、指纹／缓存、blueprint、hgraph、horizon-waiting、ledger、inbox 或 dashboard；不安装 Lean／Mathlib，不配置用户环境。

## 已采用的论文规划 Skill

`skills/writing-cycle/paper-plan/` 默认 model-invoked，支持外部研究材料 standalone 与父报告章节 composed。2026-09-13 完成原文、调用关系及许可复核；日期表示采用核对，不表示下列 revision 是最新 HEAD。

- **ARIS / wanshuiyin**，revision `0472e530251cdbd3364c33b110063c58f819edd7`：完整读取 `skills/paper-plan/SKILL.md`（其目录只有此文件）、`skills/paper-writing/SKILL.md`，以及前者直接引用的 `skills/shared-references/{writing-principles,venue-checklists,integration-contract,reviewer-independence,assurance-contract,output-versioning,output-manifest,output-language}.md`、`tools/extract_paper_style.py` 与根 MIT 许可。官方 GitHub API 解析固定树并提供上述正文；本机另一个 checkout 的 `df729a3f942e4a97646d212eb8aee1144ab5e31b` 不混作本次采用版本。
- **Orchestra / Claude AI Research Skills Contributors**，revision `773a52944ba4747a18bd4ae9ade53fff041adcbc`：采用该版本 clean 本机源，官方 API 解析 revision、根 LICENSE 与本机逐字一致。完整读取 `20-ml-paper-writing/ml-paper-writing/SKILL.md`、其全部五份 references 和 `templates/README.md`，以及 `systems-paper-writing/SKILL.md` 与全部五份 references。具体年度 LaTeX templates/assets 不在本票复制范围，未以仓库 MIT 为其概括授权；本 Skill 不附带第三方 venue 模板。
- **保留方法**：ARIS Claim—Evidence 矩阵、三类灵活结构、完整逐节/图表规划和六项独立评审检查；Orchestra 叙事三支柱、五句摘要、引言及 hero figure/数学呈现方法；Systems 的逐段蓝图、design alternatives、implementation、end-to-end / microbenchmark / ablation / scalability 与四种写作模式。共置于 `references/{narrative-framing,section-planning,systems-blueprints,systems-patterns}.md`。保留实质操作与检查对象，不搬运全文起草/润色、编译、投稿职责及未核实的具体论文历史/award 举例。
- **局部适配**：`references/style-reference.md` 保留 opt-in 骨架抽取、槽位覆盖与评审隔离，替换 Python/hash 缓存；`references/venue-and-citations.md` 将年度清单改为最新官方规则现场核对、模板冲突用户决定及引用身份/元数据/语境分别核实；`templates/paper-plan.md` 是 Markdown-first 输出模板。证据存在不等于支持，反证/失败结果及无 style-ref 时的缺口也必须保留；不把结构偏好变成补实验授权。去除默认 ICLR、固定页数、provider/MCP、隐藏状态、manifest、自动覆盖和跨主流程启动。
- **调用核对**：ARIS `paper-writing` Phase 1 原生调用 `paper-plan`，后者调用跨模型独立评审并在 opt-in 时调用 style helper；Orchestra ML/Systems 是正文互指，不是 ARIS 原生子调用。本仓 Systems 资源分支是有意局部组合，不调用尚未交付的顶层写作入口。独立评审直接读取原始研究材料；style 来源（包括原请求中的 URL）、profile 和 style-gap 留在作者侧，普通证据缺口仍完整提供。composed 的 style 中间结果默认不持久化，额外文件需另获明确路径授权。
- **许可与 attribution**：Skill 内 `LICENSE-ARIS.txt` 保留 `Copyright (c) 2026 wanshuiyin` 及完整 MIT；`LICENSE-Orchestra.txt` 保留 `Copyright (c) 2025 Claude AI Research Skills Contributors` 及完整 MIT。ARIS 原文致谢 [Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills)、[claude-scholar](https://github.com/Galaxy-Dawn/claude-scholar)、[Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) 的方法影响；本票未直接复制这些仓库或 ARIS 标明来自后两者的 citation 四条，引用规划采用已读 Orchestra 方法。style-gap 原想法保留 @zhangpelf / ARIS #217 致谢。Orchestra 资源内已有写作方法作者与来源 attribution 保留。

## 已采用的学术图表能力

`skills/writing-cycle/academic-plotting/`（Writing Cycle，Issue #21）组合两方方法，默认 model-invoked，支持用户点名 standalone 与职责受限 composed；不自动启动写作总流程。

- **2026-09-13 采用复核**：通过官方 GitHub API 重新解析 ARIS `0472e530251cdbd3364c33b110063c58f819edd7` 与 Orchestra `773a52944ba4747a18bd4ae9ade53fff041adcbc`，完整读取下列正文与共置资源、仓库 MIT 许可及调用位置。这是固定采用版本，不声称最新 HEAD；本地旧 analysis 目录不是对应上游 checkout，未使用其父仓 revision。
- **ARIS / wanshuiyin**：`skills/paper-figure/SKILL.md`（目录仅此文件）。采用图表计划、保护已有手工图、每图独立源脚本、比较表／符号定义、LaTeX 引用片段、实际导出后复核、五项 caption／比较质量审查。共置 `references/table-and-review.md` 保留表格／引用／审查方法；其余融入主 Skill。去除固定 Codex/MCP reviewer、批跑未知脚本及无依据的自动生成比例承诺；不复制该正文明确标为 Anthropic Claude Science、pedrohcgs、Imbad0202 或 baoyu 来源的清单／样式／决策树文本，未将 ARIS MIT 当作第三方独立许可。相应数据类型、样式和证据约束使用 Orchestra 资产及本票要求。
- **Orchestra / Claude AI Research Skills Contributors**：`20-ml-paper-writing/academic-plotting/SKILL.md` 与完整 `references/{data-visualization,diagram-generation,style-guide}.md`。保留上下文抽取、九种数据图模式、六段示意图设计、四种完整视觉风格、示例、配色、字体／版式／可访问性及 LaTeX 集成；视觉风格从主文披露到 `references/diagram-styles.md`。该目录无额外 templates/assets/scripts 或独立第三方许可文件。新增 `templates/figure-note.md` 是组合职责的自然格式记录模板，不是统一 schema。
- **正文级职责适配**：ARIS `paper-figure` 将架构图留给手工／其他能力，Orchestra 默认 Gemini 生成示意图；本仓合并为一个图表入口，以来源可查的数据图及明确非实验证据的可编辑示意图分支保留两方独有方法。去除 Gemini/模型版本绑定、凭据配置和固定三次远程请求，已有本地能力优先；AI 生成须显式上传／费用／尝试授权，提示词与 PNG 不冒称可编辑或像素复现。修复 Orchestra 示例中不存在的 `COLORS["red"]`、SD 误称 CI、默认自动 log／拟合／回归、负指标截断及任意数值标百分比；venue 数值降为历史示例，调色板不保证所有色觉条件可辨。
- **真实调用关系**：已完整读取 ARIS `skills/paper-writing/SKILL.md`，其 Phase 2 调用 `paper-figure` 做数据图／表，Phase 2b 分别路由到 illustration／figure-spec／Mermaid；后者不是原 `paper-figure` 的内部自动调用，本票不移植这些 runtime／额外 Skill。Orchestra 原 `academic-plotting` 仅建议配合 `ml-paper-writing`；核对 `ml-paper-writing` 与 `systems-paper-writing` 的图表相关正文，未发现它们调用 `academic-plotting` 的指令。两方组合是本仓适配，不伪称原生跨仓调用。
- **许可随包**：`LICENSE-ARIS.txt` 保存 MIT 与 `Copyright (c) 2026 wanshuiyin`；`LICENSE-Orchestra.txt` 保存 MIT 与 `Copyright (c) 2025 Claude AI Research Skills Contributors`。未搬运第三方 venue 模板、图像资产或外部实验数据。
- **审核边界**：完成 `writing-for-agents`／`SKILL-MECHANICS` 的触发、角色、输入输出、写入授权、停止、资源完整性、幽灵依赖、逐分支披露及成熟方法保真自核，并修复顾问指出的三处定量示例问题后进入 inventory。临时真实绘图／缺库检查与静态检查不作为中央测试平台提交，也不等于用户科研验收。

## 已采用的论文编译与显式修复

- **来源与许可**：wanshuiyin / [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)，`skills/paper-compile/SKILL.md`，本次采用 revision `df729a3f942e4a97646d212eb8aee1144ab5e31b`。2026-09-13 通过官方 GitHub API 核对该 revision、完整正文、目录与根 `LICENSE`；正文和许可与本地 checkout 字节一致。该版本的编译目录仅有 `SKILL.md`，没有共置 references/templates/assets 或第三方模板。MIT，`Copyright (c) 2026 wanshuiyin`；完整 notice 分别随两个 Skill 的 `LICENSE` 发行。此记录不更改其他 Skill 已采用的版本。
- **拆分**：`skills/writing-cycle/paper-compile/` 保留默认 model-invoked 的 check-only，支持用户点名 standalone 或在已授权父 Workflow 中贡献报告；`skills/writing-cycle/paper-compile-repair/` 是独立 user-invoked 修复，逐文件、具体 diff、构建与最多三轮预算均须用户确认。检查不修改原稿或快照源，亦不自动启动修复；两个包各自携带构建方法、异常诊断、PDF 检查及 Markdown 报告模板，互不构成安装前置。
- **采用方法**：完整保留入口/引擎/文献后端发现、多遍编译、八类异常诊断、有界修复与无进展复核、五项视觉检查、页数及正文/参考文献/附录边界、孤立章节检测、匿名/字体嵌入/大小/VERIFY 检查和全部报告维度。依赖图改为递归追踪并保留条件不明文件；当期官方 venue 规则取代过期固定页数与大小门槛；PDF 实际解析取代仅以 100KB 判断有效性。
- **边界适配**：新空输出与普通文件快照取代清理原构建，保留真实退出码、所有失败日志和残余警告。完整审阅的闭合输入可在有界、明确授权的宿主执行；复杂或不明可执行输入需已有可验证隔离，否则停止。前后内容核对不冒充 OS 写保护。删除自动安装、固定 Codex 插件、自动后续 Workflow/投稿及远程副作用，不引入用户环境配置或中央 runtime。
- **调用核对**：已阅读上游 `paper-writing/SKILL.md`，其 Phase 4 实际调用 `paper-compile` 并期待自动修复；`resubmit-pipeline/SKILL.md` Phase 4 也调用它。后者提到的 `COMPILE_REPORT.json` 与实际 compile 正文 Markdown 输出不一致，本仓以实际正文为准，不移植 JSON、自动缩页或 Overleaf push。其余写作、改进、引用审计中的编译提及不构成本仓自动调用许可。

## 已采用的引用审计与显式修复能力

- **来源**：wanshuiyin / [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)，`skills/citation-audit/SKILL.md`，固定 revision `df729a3f942e4a97646d212eb8aee1144ab5e31b`。2026-09-13 核对本地官方上游 checkout 的 origin、HEAD、tracked 原文与根 MIT LICENSE；完整读取 502 行原正文。该目录只有 `SKILL.md`，没有共置模板、脚本或额外资产；不声称该 revision 为在线最新版本。
- **直接引用资源**：完整读取同 revision 的 `skills/shared-references/{citation-discipline,reviewer-independence,external-cadence,review-tracing,integration-contract,assurance-contract}.md`。采用前两者的具体查询、多源身份核对、BibTeX 获取与字段核实、版本区分、逐处 claim 原文支持、fresh 独立审查方法。`citation-discipline.md` 末尾注明 Anthropic／Apache-2.0 来源的 Output Discipline 段落未采用；其余资源仅用于核对边界，不复制其中的调度、provider、tracing、schema、hash 或 verifier 机制。
- **本仓发行单元**：`skills/writing-cycle/citation-audit/` 保留逐条三轴及每处语境检查、显式 uncited、soft-only 的 bib 冻结与正文 REMOVE 特例；只输出授权 Markdown 报告，支持 standalone／composed，内部调用只贡献父报告。`skills/writing-cycle/apply-citation-fixes/` 从原混合修改职责拆出 user-invoked 入口，所有修改先展示精确 diff 并获授权；重读来源与影响集合，冲突停止，部分批准／拒绝／未核实分别处理，写后重新核对三轴及所有受影响引用。
- **适配**：每个发行单元独立携带 `references/verification-methods.md`；detect 另含自然 Markdown 报告模板。保留完整实质检索和核实方法，去除固定 provider／MCP、隐藏状态、JSON、render、自动编译与自动修改绑定。没有来源或独立 reviewer 能力时披露未核实，未找到不等于不存在；replacement 先查原始来源与具体 claim 支持，预算不足不扩大授权。没有新增中央资源依赖。
- **真实调用核对**：原 `paper-writing/SKILL.md` Phase 5.8／6 调用三轴审计；`resubmit-pipeline/SKILL.md` Phase 1 detect-only 调用带 soft-only；`paper-talk/SKILL.md` Phase 4.2 审查 slides／notes／script；`overleaf-sync` 将新引用和 key 变化路由到重审，`integrity-forensics` 引用其修复方法。本仓保留局部审计与影响范围方法，不继承父流程自动推进、合成论文 adapter、同步或提交 gate。
- **许可**：MIT，`Copyright (c) 2026 wanshuiyin`；完整根 LICENSE 分别随两个 Skill 的 `LICENSE` 发行，覆盖改编正文、方法资源与报告模板的上游 attribution。未复制具有另行许可标注的第三方段落或资产。

## 已采用的论文 Claim 审计与压力测试

2026-09-13 仅核对本地 ARIS checkout，未联网、fetch 或 pull。实际 HEAD 为 `df729a3f942e4a97646d212eb8aee1144ab5e31b`，origin 为 `ssh://git@ssh.github.com:443/wanshuiyin/Auto-claude-code-research-in-sleep.git`；这不是上表固定 revision `0472e530251cdbd3364c33b110063c58f819edd7`，也不声称是远端最新版本。本地仅有未跟踪目录 `skills/run-experiment-mlx/`，下列采用文件及共享引用对 HEAD 无修改；未读取或采用该未跟踪目录。

| 本仓 Skill | 上游原路径与完整保留的方法 | 共置资源与适配 |
|---|---|---|
| `skills/writing-cycle/paper-claim-audit/` | wanshuiyin / ARIS，`skills/paper-claim-audit/SKILL.md`：零上下文独立 reviewer、完整定量 Claim 抽取与逐项溯源提示、七类失真（数字膨胀、最佳 seed、配置、聚合、delta、caption、实验范围）、九种逐 Claim 状态、全量明细及整体裁决。 | 完整实质提示在 `references/audit-prompt.md`，人类可读模板在 `templates/claim-audit-report.md`。保留跨执行者模型家族与直接读取原始结果；移除固定 provider、自动改稿消费链、HTML、机器输出与认证设施；支持原生稿件/结果格式，不把配置文件或作者摘要当结果。 |
| `skills/writing-cycle/claim-stress-test/` | wanshuiyin / ARIS，`skills/kill-argument/SKILL.md`：单一最强约 200 词拒稿 memo、六个攻击轴、独立 fresh 裁决者、3–7 原子点分解、三种当前文本回应标签与三档严重度、故意立场不等于已回答、net assessment/最多三条动作；保留可选六轴探测后最多两轴合成一段攻击。 | `references/attack-prompt.md`、`adjudication-prompt.md`、`axis-probes.md` 保留完整提示及广度分支；`templates/stress-test-report.md` 集中报告与互斥裁决。用职责清晰的产品名替换 kill-argument；攻击与裁决分离，只有当次逐字攻击跨越上下文；默认 detect-only，建议不自动实施。 |

两份上游 Skill 正文（分别 349、437 行）已完整读取；原目录均仅有 `SKILL.md`，无遗漏的共置 scripts/templates/assets 或内嵌第三方许可。两份发行目录各自携带根 MIT `LICENSE` 全文：`Copyright (c) 2026 wanshuiyin`。新增提示/模板是上述方法的局部适配，不依赖中央文档或另一 Skill 安装目录运行。

**直接共享引用核对**：完整读取同一实际 revision 的 `skills/shared-references/{external-cadence,review-tracing,integration-contract,assurance-contract,reviewer-independence,reviewer-routing,fan-out-pattern}.md`。采用对两个原语有效的 fresh/不预消化材料、跨模型独立性、原始回复保留、错误与缺证据不静默跳过、探测与最终裁决分离、顺序 fresh 探测降级及只读边界。将方法就地融入各 Skill；不搬运这些共享文件的中央 helper、安装解析链、调度器、provider 路由、模型身份认证、schema/JSON、hash/trace/receipt、HTML gate 或递归 runtime 依赖。

**真实调用关系**：本地 `skills/paper-writing/SKILL.md` Phase 4.7 / 5.5 调用 paper-claim-audit，Phase 5.6 调用 kill-argument；`skills/auto-paper-improvement-loop/SKILL.md` Step 5.5 实际委托 kill-argument 并读取结果，随后由调用者合并修复项。已读取这些调用段落，不虚构上游相互调用。本仓两项都是 model-invoked、用户可点名的 standalone / composed 能力；只返回完整报告，不移植上游调用者的自动改稿、提交 gate 或 Claim → Stress → Citation 顺序，Claim/Citation/Proof/Stress 并列按需。

**必要语义修正**：上游 kill 表的 PASS 行重叠、unresolved 与 partial 条件重叠，且漏掉单个 partial major；按其表后“任何 partial major 及以上至多 WARN”的明确规则修成互斥完备表。保留标准舍入可通过、实质 mismatch 失败；证据缺失/歧义无确定错项时明确 BLOCKED。以可读的真实稿件和适用 Claim 代替 `main.tex` / `sec/` 布局门、无 PDF 编译门、最近两次提交标题变化门及简单定理计数门；不足三个真实攻击点允许解释，不人为凑数。攻击仍须强制承诺，但不能故意抹掉决定性原文限定或编造缺失证明来制造拒稿理由。

## 已采用的 Rebuttal Workflow

- **来源**：wanshuiyin / ARIS，`skills/rebuttal/SKILL.md`，revision `0472e530251cdbd3364c33b110063c58f819edd7`。2026-09-13 通过官方 GitHub API 重新解析固定 revision、读取377行完整正文、递归目录树及根 MIT 许可；不是采用未核对版本的本地 checkout，也不声称为最新 HEAD。该目录只有 `SKILL.md`，方法、提示和模板原为内嵌正文，无额外共置第三方资产。
- **采用**：`skills/writing-cycle/rebuttal/` 保留 concern 原子化与原文锚点、类型／严重度／pivotal 策略、七类回应、共享主题和长度预算、单文档／独立线程、最小充分证据与设计选择披露、八项检查、独立压力测试提示、有界修订与 follow-up、修订承诺双向映射、quick mode。按使用时机将原内嵌方法和模板分到共置 `references/response-methods.md`、`templates/working-documents.md`，不是短契约壳或中央运行时。
- **调用核对**：完整读取相同 revision 的 `skills/shared-references/{reviewer-routing,review-tracing,integration-contract}.md`、`skills/{experiment-bridge,render-html}/SKILL.md` 及 `tools/save_trace.sh`、`skills/render-html/scripts/render_html.py`。上游 rebuttal 的条件实验调用实际可进入实现／部署／运行／监控链；自动 HTML 的审查仅关注渲染保真。两条调用、固定 provider/MCP、安装配置、trace helper、隐藏状态与摘要 sidecar 均不移植，亦不复制这些排除路径的模板或第三方依赖。
- **适配**：独立 user-invoked Workflow，`disable-model-invocation: true` 与 `agents/openai.yaml` 的隐式调用禁用策略一致。只读现成论文与结果，写用户允许的回复材料；补实验留待用户另行授权并启动，不保留自动实验开关。证据准备度与回应处理分开；用户选择策略后再拟稿，完整措辞确认后交付；strict／rich 在检查前生成，长度硬门只约束粘贴目标。没有可用独立审查者时如实声明未执行，不将自查或用户陈述升级为验证。
- **许可**：MIT，`Copyright (c) 2026 wanshuiyin`；原始完整 notice 共置于 `LICENSE` 并随 Skill 安装。新增输出模板与引用核实指导是 rebuttal 方法的局部适配，运行不依赖本来源文档。

## 已采用的 Conference Talk

`skills/writing-cycle/paper-talk/` 是唯一演讲入口，独立 user-invoked。2026-09-13 通过官方 GitHub API 重新解析以下固定 revision、读取目录树、完整正文和 MIT 许可；不是宣称采用最新 HEAD。本地 ARIS checkout HEAD 不同，因此采用下列官方固定版本，不以本地 HEAD 代替来源核对。

| 来源、作者与 revision | 原路径及实际采用内容 | 共置资源与适配 |
|---|---|---|
| ARIS / wanshuiyin，`0472e530251cdbd3364c33b110063c58f819edd7` | `skills/paper-talk/SKILL.md`；其真实调用的 `paper-slides/SKILL.md`、`slides-polish/SKILL.md`、`paper-claim-audit/SKILL.md`、`citation-audit/SKILL.md`。保留大纲确认、完整 notes/逐字 script/Q&A、独立只读审查、演讲质量七维、逐页 triage/fresh review、Beamer/PPTX 修复 catalog、数字七类问题、引用三轴、匿名及导出完整性。五个 Skill 目录均只有正文，无额外共置资产。 | 方法共置于 `story-and-delivery.md`、`visual-polish.md`、`talk-audit.md` 及两份材料/报告模板。保留 baseline、notes 不变和独立性要求；新增 Beamer 源位置分支，不套用 PPTX shape 模型。MIT 全文在 `LICENSE-ARIS.txt`。 |
| Orchestra / Claude AI Research Skills Contributors / Orchestra Research，`773a52944ba4747a18bd4ae9ade53fff041adcbc` | `20-ml-paper-writing/presenting-conference-talks/SKILL.md` 及唯一共置 `references/slide-templates.md`，两份完整阅读。保留四类逐页结构、Systems 请求 walkthrough、demo 录像备用、结果讲解、Dahlin 三层叙事、完整 Beamer 和可编辑 PPTX 模板。 | `story-and-delivery.md` 与 `slide-templates.md` 保留完整方法和模板；修复原 PPTX 固定七页、类型参数无效、占位元数据、双标题与图片拉伸。原文“受 ARIS paper-slides 启发、独立实现”的归属在此保留。MIT 全文在 `LICENSE-Orchestra.txt`。 |

ARIS 实际关联的 `skills/shared-references/{reviewer-independence,experiment-integrity,assurance-contract,effort-contract,integration-contract,reviewer-routing,review-tracing,external-cadence,citation-discipline}.md` 与 `tools/extract_paper_style.py` 已全文核对。只保留审查独立性、证据范围及抽象风格参考方法；不搬运 provider/MCP、固定模型、`.aris`、helper resolver、网络风格提取器、SHA/trace/receipt、统一 JSON、合成论文审查 adapter、自动通知/发布或环境安装。`citation-discipline.md` 末尾标明来自 Anthropic 的 Apache-2.0 段落，以及许可链未充分明确的 insleep/LOOPS 派生段不在复制范围内。

两源比较后以 ARIS 的完整准备与审查链作为入口，以 Orchestra 的结构与双格式模板补齐 Systems 演讲；不另发行 `presenting-conference-talks`、`paper-slides` 或 `slides-polish` 竞争入口。所有档位审查实际 slides、notes、script；视觉深度受本次预算控制，不沿用上游低档跳过内容审计。故事/密度/计时等审查与数值/引用审查并列，审查和修订分权。自然 Markdown 可独立交付；缺二进制/渲染/独立 reviewer 时如实注明，不认证 conference-ready。

模板没有附带第三方主题文件、论文图表或外部 Dahlin PDF；其中 `metropolis` 等是对用户已有工具的可选依赖，不随本 Skill vendoring。Dahlin 的方法归属保留，不复制外链 PDF 正文。参考论文、用户模板、图表和录像的复用仍需用户授权，两个 MIT notice 不代替这些素材的权利许可。

## 已解决的 revision／路径矛盾

旧 `docs/research/sources/README.md` 的六仓 revision 与仓库错位，不能在所列上游解析。错位关系可由当前上游 heads 复现：旧 ARIS SHA 实属 AutoResearchClaw，旧 AutoResearchClaw SHA 实属 EurekAgent，旧 EurekAgent SHA 实属 autoresearch，旧 Archon SHA 实属 Orchestra；旧 Orchestra 与旧 autoresearch SHA 当前均无法在对应仓库解析。上表取 2026-09-08 各官方默认分支完整 head，替代该索引作为后续搬运起点。

Archon 旧报告还把 `hgraph/` 与 `subagents/compile.py` 作为可复制路径；本次官方树没有这些路径。后续只能依据当前 `src/archon_horizon/...` 重新定位并审核，不得使用旧 checkout 路径。

## 三类独立采用验证

| 类别 | 抽样资产 | 依据清单的决定 |
|---|---|---|
| 可复制 | Matt `setup-matt-pocock-skills` | revision、原路径、作者和 MIT notice 完整；复制完整相关资产、保留 notice、最小语义适配。 |
| 仅借鉴 | EurekAgent evaluator | AGPL-3.0 与目标搬运策略不兼容；只写独立新表达，不读取后照抄源码或 Skill 文本。 |
| 来源异常 | Archon `hgraph/` | 旧索引 checkout/path 与官方当前树不一致；阻止复制，先用当前 revision 重新定位。 |

## 替换与迁移边界

- 本文与纯 Skills 产品规范取代 `CONTEXT.md`、`PRODUCT.md`、`GATES.md`、`docs/adr/0001`–`0004` 中关于 provider-neutral Core、typed Artifact contracts、digest/SHA、Publication freeze、validator、Adapter 和 port hard gate 的产品约束。
- 后续迁移可删除已提交的旧 Python package、CLI、wheel、contracts、validators、Adapters、ports database、runtime tests、旧 gates/guides/CI；Git 历史即旧实现存档，不建立 `legacy/`。
- 发现同名 Skill 时先正文级比较：上游名称清晰则保留；职责重复则择优或合并并保留双方独有方法；职责含混才重命名。不得让旧短契约壳遮蔽新搬运的成熟正文。
- 旧 CI 只在对应产品资产删除后同步移除或改成轻量 Skills 发行检查；迁移期间失败不得通过伪造兼容层、恢复旧 runtime 或降低新产品边界来消除。
- 不提前删除目标 worktree 中用户未提交内容。任何批量删除前先检查 `git status`，只处理已提交旧产品资产和本 Ticket／后续 Ticket 明确拥有的文件。
