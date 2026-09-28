# Spec: skills 文档体系按 writing-for-agents 标准整改

> 来源会话的完整审核报告见同目录 `2026-09-28-skills-writing-for-agents-audit.md`（handoff 产物）。本 spec 固化其结论与已确认决策。

## Problem Statement

Research OS Studio 的 39 个 SKILL.md（4144 行）由多批不同血统的模板生成，累积了多种违反 writing-for-agents 标准的模式：数学系 skill 缺 per-step 完成条件、23 个文件携带对 agent 执行为 no-op 的"来源与适配"变更日志（2503 行，占总量 60%）、边界禁令同一句重复 3 次以上且多为纯 negation、部分 skill 的可披露模板全内联。这些模式导致 agent 执行时 premature completion 风险高、注意力被非执行内容稀释。

## Solution

按 writing-for-agents 标准对 4 个 skills 目录做一轮整改：补齐缺失的 per-step completion criterion、删除错置的来源变更日志（attribution 合并到唯一权威位置）、禁令全部配对正面目标行为并收敛为单一权威表述、内联模板披露到 templates/、修复结构小 bug。改动保持产品域边界（CONTEXT.md 定义的有界 Workflow、停止条件）不变——改的是表述方式，不是授权范围。

## User Stories

1. 作为运行 skill 的 agent，我想在 formula-derivation 的每个 Step 看到明确的完成条件，以便不因缺少逐段阻力而提前宣告完成
2. 作为运行 skill 的 agent，我想在 proof-writer 的每个 Step 看到明确的完成条件，以便长 sequence 中段不失去完成边界
3. 作为运行 skill 的 agent，我想让 novelty-check、research-lit、analyze-results、training-health-check 拥有可检查的完成条件，以便与其他 35 个 skill 保持同等的完成判定纪律
4. 作为运行 skill 的 agent，我不想在正文读到"删除了 mcp__codex / 保留 AUTO_DEPLOY"式的变更日志，以便注意力只花在可执行内容上
5. 作为运行 skill 的 agent，我想让"不自动启动其他顶层 Workflow"在一份 SKILL.md 中只出现一次权威表述，以便其余位置用一致 leading word 指向它而不重复展开
6. 作为运行 skill 的 agent，我想让每条硬护栏禁令配对一句正面目标行为，以便注意力落在要做什么上而非被禁行为上
7. 作为维护者，我想让上游 commit SHA、来源署名只存在于 docs/upstream-sources-and-licenses.md 一处，以便改一处即全量生效
8. 作为维护者，我想让 formula-derivation 与 proof-writer 的包骨架与 output-mode 分支外置到各自 templates/，以便正文长度回到与同族 skill 相当的水平
9. 作为运行 skill 的 agent，我想让 run-experiment 的章节编号连续（当前缺 "## 3"），以便两个完成条件不再语义重叠
10. 作为维护者，我想让 stale 的数字声明（如 README 中"共 25 个 Skill"）与目录树一致，以便清单不误导
11. 作为运行 skill 的 agent，我想让 5 个 description 弱开头的 skill 以动词/用途开头，以便触发措辞与其余 34 个 skill 同等锐利
12. 作为用户，我想让所有改动不改变任何 skill 的授权边界、调用模式或停止条件，以便 CONTEXT.md 与 README 声明的行为契约不变

## Implementation Decisions

- **M1（per-step criterion）**：formula-derivation、proof-writer 照抄 proof-review 的 per-step 模式（每个 Step 尾部一个 criterion），把现有开头单段 "Completion means…" 的判定拆散下沉。4 个缺 criterion 的 skill（novelty-check、research-lit、analyze-results、training-health-check）人工确认后补齐统一格式的 criterion。
- **M2（来源节处置）**：删除 23 个文件中的"来源/来源与适配"节。4 个纯署名文件（creative-thinking-for-research、idea-generation、experiment-plan、rebuttal）的 attribution 并入 `docs/upstream-sources-and-licenses.md` 对应条目；5 个重型 changelog 文件（ml-paper-writing、systems-paper-writing、resubmit-pipeline、paper-writing、idea-discovery）的正文 SHA 与适配记录一并归并，正文不再保留任何 changelog。
- **M3（禁令收敛，决策 3C）**：每条保留的禁令（授权边界、副作用、停止条件类硬护栏）配对正面目标行为；同一意思在单文件内只留一处权威位置（推荐"停止条件"节），其余位置以 leading word 指向。纯风格性 negation（"不要臆测"类）直接改写为正面表述。
- **M4（模板披露）**：formula-derivation:194-243 的 Markdown 包骨架、proof-writer:158-224 的 output-mode 分支外置到各自 `templates/`，正文用 context pointer 指向。
- **Nit 修复**：run-experiment 章节编号修复；README L174 "25 个 Skill" 改为 39；5 个 description 弱开头（creative-thinking-for-research、proof-review、proof-writer、research-improvement、ml-paper-writing）锐化为动词/用途开头。
- **调用模式冻结**：17 个 user-invoked / 22 model-invoked 的 frontmatter 一律不动；`scripts/check-skills.py` 清单校验必须持续通过。
- **域词汇**：全程使用 CONTEXT.md 规范术语（Workflow、Internal Skill、有界、停止条件）。

## Testing Decisions

- 每个改动后的 SKILL.md 逐个人工读一遍，验证：criterion 可检查（agent 能分辨完成与未完成）、删除来源节后正文无断裂引用、禁令配对后语义与原授权范围完全一致。
- 机械回归：重跑 `scripts/check-skills.py` 确认清单一致；grep 验证 "来源与适配" 节为 0、SHA 不再出现在 skills/ 下任何文件。
- 行数回归：formula-derivation、proof-writer 改后应显著低于当前 297/239 行（目标 ~120-150）。
- 测试先例：本仓库 CI 已有 check-skills.py 清单校验；无 SKILL.md 语义的自动化测试，靠手工验收步骤（README 已有各 skill 验收章节，不在本次范围）。

## Out of Scope

- **跨文件 duplication 重构**（原报告 S2/S3）：paper-writing / ml-paper-writing / systems-paper-writing 三胞胎 ~51% 逐字重复、paper-claim-audit ≈ claim-stress-test 同构 1/3——结构性重构牵动 README 清单与 CI，单独立票处理。
- **README.md 全面整改**（原决策 4B）：验收步骤与宿主警告应披露到 docs/ 的问题留待下次，本次只修 L174 一处纯数字错误。
- **slide-templates.md 按 Beamer/PPTX branch 拆分**（原 S4）：量大且独立，建议单独立票。
- 任何 skill 的授权边界、调用模式、停止条件、产品行为的实质变更。
- Eve 宿主兼容性、安装验收——均为独立票体系。

## Further Notes

- 审核依据：writing-for-agents（SKILL.md + SKILL-MECHANICS.md），关键杠杆为 completion criterion、negation 配对、duplication 单一真源、progressive disclosure。
- 三路探查证据（抽样 7 文件、机械检查 39 文件、血统深审）的行号级引用全部在 handoff 引用的审核报告中，执行时按图索骥。
- 决策记录（原开放问题）：Q-a 跨文件重构本次不做；Q-b attribution 并入 upstream 文档；Q-c 缺 criterion 的 skill 补齐。
- 范围为 4 个 skills 目录 + 上游文档 + README 单行；`Research OS/`（当前 cwd）仓库不在范围内。
