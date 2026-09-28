# 审核报告: skills 按 writing-for-agents 标准（2026-09-28 会话产物）

范围：`Research OS Studio/skills/{general,idea-cycle,validation-cycle,writing-cycle}`，39 个 SKILL.md（4144 行）+ 资源文件（合计 15894 行）。配套执行 spec 见 `2026-09-28-skills-writing-for-agents-remediation-spec.md`。

## Must-fix（有实证的 variance/criterion 违规）

**M1 · 数学系双 skill 无 per-step completion criterion**
`formula-derivation`（297 行）、`proof-writer`（239 行）是全目录仅有的两个"完成条件"计数为 0 的文件，唯一完成判定挤在开头一段（formula-derivation L21 前置 "Completion means…"）。中文系每个 section 都有 `**完成条件**：`。
→ 修法：照抄 proof-review 的模式（L34,42,52,60 每步一个），把判定拆到每个 Step。

**M2 · "来源与适配"变更日志错置（23 文件 / 2503 行，占 SKILL.md 总量 60%）**
5 个重型文件：ml-paper-writing 19 处"删除/适配/保留"、systems 16、resubmit 16、paper-writing 15、idea-discovery 14。对 agent 执行是 no-op；上游 commit SHA 写进正文（ml:192 `773a52…`、systems:173-174、paper-writing:156、experiment-bridge:104）。另有 4 个纯署名文件：creative-thinking-for-research、idea-generation、experiment-plan、rebuttal。权威位置 `docs/upstream-sources-and-licenses.md` 已存在，正文是第三份 cache。
→ 修法：全目录删除该节；attribution 并入 upstream 文档。

**M3 · 4 个 skill 无任何完成条件标记**
`novelty-check`（仅 4 处 "Complete when" 散点 L30,42,52,95，无统一格式）、`research-lit`、`analyze-results`、`training-health-check`。需人工确认后补齐。

**M4 · 数学系模板全内联，无 references/templates/**
`formula-derivation`:194-243（40 行 Markdown 包骨架 `# Derivation Package`/Target/Status/…）、`proof-writer`:158-224（3 个 output-mode 分支）内联在正文；两目录只有 LICENSE，无 references/ 无 templates/。对照 proof-orchestrator 有 7 个 references/。
→ 修法：披露到各自 templates/，预计 297→~120 行。

## Should-fix（模式级）

**S1 · 边界禁令三重复述（决策 3C 适用点）**
同一句"不自动启动其他顶层 Workflow"出现 3 次的实例：
- paper-writing:12 + :141 + :160
- ml-paper-writing:12 + :174 + :195
- experiment-bridge:10 + :90 + :92
- proof-orchestrator:17 + :101 + :115

计数（"不自动启动/不启动/停止条件/即停止"）：ml-paper-writing 11、research-improvement 9、systems 8、paper-writing 8、run-experiment 8、experiment-bridge 6、proof-orchestrator 5。固定四点位：①开头"职责与授权"②中段授权门③"停止条件"节④文末"来源与适配"。
→ 修法：每处保留禁令但配对正面目标行为；单一权威位置 + leading word 指向。

**S2 · paper-writing 三胞胎 ~51% 逐字重复（本次不做，单独立票）**
归一化去重行：paper-writing 80 行、systems 91、ml 107；两两交集 41/41/34 行。整节克隆：授权门（pw:27-39 = ml:25-39 = sys:25-38）、编译检查（pw:82-90 = ml:102-110 = sys:97-105）、并列审查表（pw:92-110 = ml:112-131 = sys:107-125）、独立评审+授权 revision（pw:112-120 = ml:133-141 = sys:127-135）、停止条件（pw:130-143 = ml:161-176 = sys:145-159）、报告产物（pw:122-128 = ml:153-159 = sys:137-143）。领域专属仅 systems §5（83-95 证据面）、ml §4（72-89 ML 报告纪律）。

**S3 · paper-claim-audit ≈ claim-stress-test 同构 1/3（本次不做）**
边界块（audit:14-18 ≈ stress:14-18）、fresh-reviewer 规则（audit:34 ≈ stress:36）、状态映射表+交付/停止（audit:44-64 ≈ stress:52-62）几乎同构；差异只在方法核（七类失真 vs 攻击+独立裁决）。

**S4 · slide-templates.md 752 行双 branch 塞一文件（本次不做，单独立票）**
Beamer 与 PPTX 两 branch 合计一文件，按 branching 规则应拆分。

## Nit（顺手级）

- `run-experiment` 缺 "## 3" 标题，L53-64 挂在 "## 2" 下，两个完成条件（L51、L64）语义重叠
- README L174 "共 25 个 Skill" stale（实际 39）——纯数字错误，顺手修
- 5 个 description 弱开头（非动词/用途式）：creative-thinking-for-research（场景先行）、proof-review、proof-writer、research-improvement、ml-paper-writing（缩写开头）

## 已核实无需动

- frontmatter 39/39 合规：全有 name + description；17 user-invoked 全带 `disable-model-invocation: true`（字面小写）且各有 `agents/openai.yaml`（find 计数 = 17）；22 model-invoked 正确省略
- 调用模式与 README 零不一致（先前"proof-review 声明矛盾"为假阳性，其 model-invoked 正确）
- "中英夹杂 description" 被机械检查推翻：39 个全是中文含拉丁术语，无双语重复
- 披露纪律：30/39 有 references/、33/39 有 templates/；两者全缺仅 ask-research-os、formula-derivation、proof-writer（前者本就 34 行无需披露）
- `idea-generation` description 是全目录最佳范本（动作在前 + trigger + 一句边界）

## 机械检查全量数据

39 个 SKILL.md 清单（skill | mode | refs/tmpl | criterion | source | lines）：

| Skill | mode | refs/tmpl | criterion | source | lines |
|---|---|---|---|---|---|
| general/ask-research-os | USER | –/– | yes | NO | 34 |
| general/setup-research-os | USER | R/T | yes | yes | 84 |
| idea-cycle/creative-thinking-for-research | model | R/– | yes | yes | 62 |
| idea-cycle/idea-discovery | USER | R/T | yes | yes | 113 |
| idea-cycle/idea-generation | model | R/T | yes | yes | 77 |
| idea-cycle/idea-refinement | model | R/T | yes | yes | 62 |
| idea-cycle/idea-review | model | R/T | yes | yes | 48 |
| idea-cycle/novelty-check | model | R/T | NO | NO | 104 |
| idea-cycle/research-lit | model | R/T | NO | NO | 94 |
| validation-cycle/analyze-results | model | R/T | NO | yes | 86 |
| validation-cycle/experiment-audit | model | R/T | yes | yes | 140 |
| validation-cycle/experiment-bridge | USER | R/T | yes | yes | 106 |
| validation-cycle/experiment-plan | USER | –/T | yes | yes | 148 |
| validation-cycle/experiment-queue | model | –/T | yes | yes | 138 |
| validation-cycle/formula-derivation | model | –/– | yes* | NO | 297 |
| validation-cycle/monitor-experiment | model | R/T | yes | yes | 71 |
| validation-cycle/proof-orchestrator | USER | R/– | yes | NO | 117 |
| validation-cycle/proof-repair | USER | R/T | yes | NO | 82 |
| validation-cycle/proof-review | model | R/T | yes | NO | 68 |
| validation-cycle/proof-writer | model | –/– | yes* | NO | 239 |
| validation-cycle/result-to-claim | USER | R/T | yes | yes | 99 |
| validation-cycle/run-experiment | model | –/T | yes | yes | 154 |
| validation-cycle/training-health-check | model | R/T | NO | yes | 89 |
| writing-cycle/academic-plotting | model | R/T | yes | NO | 84 |
| writing-cycle/apply-citation-fixes | USER | R/– | yes | NO | 90 |
| writing-cycle/citation-audit | model | R/T | yes | NO | 92 |
| writing-cycle/claim-stress-test | model | R/T | yes | NO | 62 |
| writing-cycle/ml-paper-writing | USER | R/T | yes | yes | 196 |
| writing-cycle/paper-claim-audit | model | R/T | yes | NO | 64 |
| writing-cycle/paper-compile-repair | USER | R/T | yes | NO | 77 |
| writing-cycle/paper-compile | model | R/T | yes | NO | 53 |
| writing-cycle/paper-drafting | model | R/– | yes | yes | 80 |
| writing-cycle/paper-plan | model | R/T | yes | NO | 84 |
| writing-cycle/paper-talk | USER | R/T | yes | yes | 102 |
| writing-cycle/paper-writing | USER | R/T | yes | yes | 160 |
| writing-cycle/rebuttal | USER | R/T | yes | yes | 108 |
| writing-cycle/research-improvement | USER | R/T | yes | yes | 127 |
| writing-cycle/resubmit-pipeline | USER | R/T | yes | yes | 77 |
| writing-cycle/systems-paper-writing | USER | R/T | yes | yes | 176 |

`*` formula-derivation / proof-writer 的 criterion 仅指唯一前置段（非 per-step）；其余 35 个为 per-section `**完成条件**：`。idea-discovery 另有抽样证据：禁令四处重复 L10/20/93/106-109；idea-generation 三处重复"生成者非评审者" L8/14/71、授权重复 L19/45-47/70-73。
