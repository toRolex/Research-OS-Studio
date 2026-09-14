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
| [ARIS / Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)，wanshuiyin | `0472e530251cdbd3364c33b110063c58f819edd7` | Idea：`skills/idea-discovery/`、`research-lit/`、`idea-creator/`、`novelty-check/`、`research-review/`、`research-refine/`；实验：`experiment-plan/`、`experiment-bridge/`；写作：`paper-writing/`、`paper-plan/`、`paper-write/`、`paper-figure/`、`paper-compile/`、`rebuttal/`、`resubmit-pipeline/`、`paper-talk/` | MIT，`Copyright (c) 2026 wanshuiyin`。主要可复制来源；复制每个成熟 Skill 的完整关联资产，删除 `.aris`、provider/MCP 绑定、默认自动推进和跨主流程调用。模板需另核内嵌第三方许可。 |
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
