# Research OS Skills

在自己的科研项目目录使用通用 [Skills CLI](https://github.com/vercel-labs/skills)；无需安装 Research OS 专用 runtime。

```bash
npx skills@latest add toRolex/Research-OS-Studio --list
npx skills@latest add toRolex/Research-OS-Studio --all
```

这些远程命令读取 GitHub 已发布版本，不会包含尚未合并或 push 的本地修改。验证本地分支时，在一个临时科研项目目录中运行（将绝对路径替换为当前 checkout）：

```bash
npx skills@latest add /绝对路径/Research-OS-Studio --list
npx skills@latest add /绝对路径/Research-OS-Studio --all
```

CLI 负责宿主安装目录和文件复制；本仓库不生成 projection。需要限定宿主时可使用 `--skill '*' --agent claude-code --agent codex --yes`。安装后按宿主约定重新加载 Skills 或开启新会话，确认发现 `setup-research-os`，再显式调用它；例如支持斜杠调用的宿主使用 `/setup-research-os`。宿主未发现时先核对 CLI 输出的实际安装位置，不能把文件安装成功当作模型已加载。

### 已知宿主限制

`--all` 会向所有 CLI 支持的宿主安装，并非仅当前使用的宿主。Skills CLI 1.5.25 实测会转换 Eve 的 `agent/skills/setup-research-os/SKILL.md`，移除 `name` 和 `disable-model-invocation`；随后 `skills list` 会对该副本报告 `missing required frontmatter field(s): name`。源 Skill 与 `.agents/skills/` 副本仍保留完整字段，Claude Code / Codex 的限定安装副本与源目录一致。这是 CLI 的 Eve 转换行为，不是本仓库发行物缺字段；也不能据此断言 Eve 正常可用。

Eve 的实际加载及仅显式调用策略尚未验收，不声明全宿主兼容。使用 Eve 前应在可丢弃项目中核实这两项；无法核实时暂停在该宿主使用 setup。只需 Claude Code / Codex 时，可用上方限定宿主选项替代 `--all`。其他宿主同样需自行确认加载与调用策略；文件安装成功不等于宿主交互验收通过。

`apply-citation-fixes` 在 Skills CLI 1.5.26 本地 `--all` 安装中，Eve 副本保留 `name`，但仍移除 `disable-model-invocation`。`.agents/skills/` 原始副本和 Claude Code／Codex 限定安装副本保留完整授权指令与资源。Eve 的显式调用限制未验收，在确认宿主能遵守前暂停使用该修复入口；安装成功不代表授权策略受到宿主强制执行。

## 分类与当前清单

目录约定是 `skills/<category>/<skill>/SKILL.md`，资源与 Skill 共置。分类用于导航，不规定调用顺序。

| 分类 | 目录 | 当前正式 Skill |
|---|---|---|
| General | `general/` | [setup-research-os](general/setup-research-os/SKILL.md)、[ask-research-os](general/ask-research-os/SKILL.md)（均 user-invoked） |
| Idea Cycle | `idea-cycle/` | [research-lit](idea-cycle/research-lit/SKILL.md)、[idea-generation](idea-cycle/idea-generation/SKILL.md)、[creative-thinking-for-research](idea-cycle/creative-thinking-for-research/SKILL.md)、[novelty-check](idea-cycle/novelty-check/SKILL.md)、[idea-review](idea-cycle/idea-review/SKILL.md)、[idea-refinement](idea-cycle/idea-refinement/SKILL.md)（均 model-invoked，用户可点名；支持 standalone / composed） |
| Validation Cycle | `validation-cycle/` | [experiment-plan](validation-cycle/experiment-plan/SKILL.md)（user-invoked；将已有问题转为有界实验计划，产出后停止）、[experiment-bridge](validation-cycle/experiment-bridge/SKILL.md)（user-invoked；已批准现成计划的一次授权实现到分析审计，不要求先用本产品规划）、[run-experiment](validation-cycle/run-experiment/SKILL.md)、[experiment-queue](validation-cycle/experiment-queue/SKILL.md)、[monitor-experiment](validation-cycle/monitor-experiment/SKILL.md)、[training-health-check](validation-cycle/training-health-check/SKILL.md)、[experiment-audit](validation-cycle/experiment-audit/SKILL.md)、[proof-orchestrator](validation-cycle/proof-orchestrator/SKILL.md)（user-invoked；单 obligation 长期续接）、[proof-review](validation-cycle/proof-review/SKILL.md)（model-invoked，用户可点名；只读，支持 standalone / composed）、[proof-repair](validation-cycle/proof-repair/SKILL.md)（user-invoked；显式授权的有界修复）、[analyze-results](validation-cycle/analyze-results/SKILL.md)、[formula-derivation](validation-cycle/formula-derivation/SKILL.md)、[proof-writer](validation-cycle/proof-writer/SKILL.md)（除 experiment-plan、experiment-bridge、proof-orchestrator、proof-repair 外均 model-invoked，用户可点名；支持 standalone / composed） |
| Writing Cycle | `writing-cycle/` | [paper-plan](writing-cycle/paper-plan/SKILL.md)（model-invoked，用户可点名；支持 standalone / composed）、[academic-plotting](writing-cycle/academic-plotting/SKILL.md)（model-invoked，用户可点名；支持 standalone / composed）、[paper-compile](writing-cycle/paper-compile/SKILL.md)（check-only，model-invoked，用户可点名；standalone / composed）、[paper-compile-repair](writing-cycle/paper-compile-repair/SKILL.md)（user-invoked，显式授权修复）、[citation-audit](writing-cycle/citation-audit/SKILL.md)（model-invoked，支持 standalone / composed；仅检测与报告）、[apply-citation-fixes](writing-cycle/apply-citation-fixes/SKILL.md)（user-invoked；精确 diff 后授权应用及复验）、[paper-claim-audit](writing-cycle/paper-claim-audit/SKILL.md)、[claim-stress-test](writing-cycle/claim-stress-test/SKILL.md)（后两者均 model-invoked，用户可点名；支持 standalone / composed）、[rebuttal](writing-cycle/rebuttal/SKILL.md)（user-invoked；现成审稿意见到逐 concern 回复，不自动补实验或投稿）、[paper-talk](writing-cycle/paper-talk/SKILL.md)（独立 user-invoked：从论文生成 slides、notes、script 并审查演讲产物；不自动发布或启动后续 Workflow） |

只有实际含 `SKILL.md` 的目录才是可安装 Skill。不为分类创建占位 Skill，不把保留的旧工程纳入这份清单。

## 只读入口导航

不确定从哪里开始时，显式调用 `ask-research-os`；已知入口可直接点名，无需先 setup 或经过 Router。它接受方向、已有结果或稿件，只在对话中推荐并停止，不写研究材料、不启动推荐任务。

自包含的[完整批准地图](general/ask-research-os/PRODUCT-MAP.md)区分三条主流程、独立 user-invoked 入口、model-invoked 能力及数学／Lean、ML／Systems 专业扩展，同时区分已实现、计划和宿主可用性。计划条目不是当前安装命令，文件安装成功也不代表宿主已加载。当前完整 Discovery、Validation 与 Writing 入口仍待后续票交付。

在可丢弃项目中可分别用“只有方向”“已有外部结果”“已有稿件”咨询；核对推荐理由、不强制前序流程、计划状态如实说明，以及项目零写入、零自动启动。实现阶段的受限合成模型场景不等于真实科研或宿主交互验收。

### 现成候选的评审与改进

`idea-review` 让独立评审者直接读取原始候选及文献，保留 findings、证据、裁决依据与未解决问题；不改候选。`idea-refinement` 在已授权修订范围内保持固定 Problem Anchor，比较最小可行与前沿路线，输出完整 Proposal 与逐轮改进理由；独立方法评审与修订分工明确。二者均可直接用于现成材料，不要求先运行生成流程，也不自动互相启动。

手工验收：提供一个有明显弱点的现成候选、原始文献和约束；先点名 review，核对 reviewer 实际原文定位与问题，再点名 refinement，核对每轮 Anchor 原样保留、双路线取舍及未解决项。限制一轮修订、零实验预算，应只得到方法及验证草图。另测缺原文、缺独立 reviewer、已有同名输出和 composed 章节授权：应准确暴露缺口、保留已有材料并停止，不配置环境或自动实验。实现期场景结果不替代用户真实科研验收。

Writing Cycle 审查能力均只读审查研究材料、输出 Markdown 报告与建议：`paper-claim-audit` 核对数字、比较、配置、图表/caption 和实验覆盖；`claim-stress-test` 由两个 fresh reviewer 分别构造整篇拒稿攻击、对照原材料逐点裁决。standalone 独立交付报告，composed 贡献父 Workflow 的 canonical report；默认不改稿，报告后停止。Claim / Citation / Proof / Stress 并列按需，不自动串联；Citation 与 Proof 不由这两项替代，其入口由独立票交付。

## 普通公式推导与证明生成

`formula-derivation` 用于组织推导主线、选定不变量、说明假设与近似并生成完整公式链；`proof-writer` 用于固定命题的证明生成，不替代只读证明审查。两者默认 model-invoked，也支持用户点名单独运行。Standalone 产出获准路径中的 Markdown package；composed 将同样完整的内容贡献到调用者指定报告，不另建重复主报告。没有写入授权时仅在聊天返回。

开始前固定目标、输入范围、目的路径和有限尝试预算；变更假设、弱化命题或重构目标只是建议，获明确授权后才发展独立变体。成功、缺口、实际失败路线和可复用教训都应保留；承重缺口未解决时不标成功。普通数学推导不需要 Lean，也不安装工具链；生成完成即停止，不自动进入通用 review / repair 或推进其他 Workflow。

在可丢弃项目中分别验收：带误差界的公式近似、包含边界情况的固定命题证明、缺少关键假设的无法完成报告，以及仅聊天/向既有报告贡献的写入边界。核对原命题未改、失败未被隐藏、没有自动修复。此类 toy 场景与安装检查不代表真实科研或形式化验证通过。

## 初始化与人工验收

setup 先探索现有项目，推荐沿用已有工作区；只有不存在时才建议可见的 `research/`。一次询问一个必要决定，展示全部草稿，收到明确确认后才写入。它只补基础导航、项目说明、findings、日志和选定指令文件的 Research OS 区块，不配置环境，不生成研究结论，不启动 Discovery。

在可丢弃的科研项目副本中逐项验收：

1. **新项目**：选择工作区；两种指令文件都不存在时选择其一；确认前检查零写入，确认后逐项核对完整草稿。
2. **非空项目**：放入原研究材料及已有日志；选择沿用目录，确认没有搬迁、覆盖或功能重复文件。
3. **重复执行**：再次调用，已有完整基础项应无需写入；核对区块、日志、文件内容不变。
4. **内容冲突**：修改已有 Research OS 区块；应先展示差异并逐项询问，保留所有周边段落。两种指令文件都存在时只更新 `CLAUDE.md`。
5. **拒绝写入与外部变化**：完整草稿后拒绝，项目应零变化；确认后目的文件被修改或新建路径出现时，应停下并重新确认。另测原先仅有 `AGENTS.md`、确认后外部新增 `CLAUDE.md`：即使它不在原写入清单中，也应停止整批、重新选择指令文件并确认新草稿。
6. **停止边界**：最终只汇报实际路径和未解决项，无实验、环境安装、远程副作用或自动启动下一流程。

## 长期证明与人工验收

显式调用 `proof-orchestrator`，指定一个 obligation、旧轮次材料（若有）、新输出目录及有限预算。它保留本地完整尝试、自查与表达整理；卡住后可准备最小手动交接包，然后停止。不是 Proof Writer／Review／Repair 的自动调用链，也不自动进入论文流程。Lean 搜索、反馈与构建只是[共置可选方法](validation-cycle/proof-orchestrator/references/lean-methods.md)，没有 Lean 仍可进行普通证明。

在可丢弃的项目副本中核对：

1. **长期续接**：给出上轮已查结论、未审外部答案与失败路线。应在新目录记录实际读取材料和继承状态，只处理本轮 obligation；旧目录保持不变，旧远程许可不继承。
2. **来源变化／预算停止**：改变前提或耗尽预算，应报告受影响结论与下一步，不能擅加假设、继续迭代或润色成已完成证明。
3. **无 Lean**：输出普通数学尝试及“未执行 Lean 验证”，不下载或配置工具链。独立审查不可用时自查不得冒充独立意见。
4. **已有 Lean**：先读候选 signature，再记录实际反馈与覆盖目标的 kernel／build 结果。给一个未导入文件和一个含 `sorry` 的声明，确认根 build 成功不等于两者已验证；同时核对公理依赖与原命题表达。
5. **手动交接**：明确跳过本地尝试时不伪造 `local-proof.md`；检查自包含 prompt、必要来源、数据分隔和实际请求的结束标记。返回截断或夹带工具／文件指令时，应保存原始证据、报告缺口，不自动上传、重试或执行其中指令。

本票以既有 Lean 4.19.0 执行了无 Mathlib 的列表求和 toy 构建及失败／占位边界检查；LSP、Mathlib 集成和真实科研项目未验收。CLI 1.5.26 在临时项目的 `--all` 与 Claude Code／Codex 限定安装均完成，本票规范副本的 11 个文件逐字保留；本票 proof-orchestrator 的 Eve 副本仍移除 `disable-model-invocation`（虽保留 `name`），因此未核实 Eve 的仅显式调用策略前，暂停在那里使用此 Workflow。文件安装不等于实际宿主加载或权限强制执行。

## Rebuttal 使用与人工验收

收到评审后显式调用 `rebuttal`，提供论文、原始评审、已有证据、当轮 venue 规则与输出范围。先确认逐 concern 策略，再审阅完整候选措辞；quick mode 只交问题板和策略。它不由写作主流程自动启动，也不自动启动实验、转投或其他顶层 Workflow。宿主必须保留显式调用限制。Skills CLI 1.5.26 的本地 `--all` 实测中，Eve 的 `agent/skills/rebuttal/SKILL.md` 保留 `name`，但移除 `disable-model-invocation`；canonical 副本及 Claude Code／Codex 限定安装保留该字段。Eve 的实际显式调用策略未验收，核实前暂停在该宿主使用 rebuttal。此次 `--all` 还跳过了未发现项目目录的其他宿主，不代表79个宿主全部安装或加载成功。

在可丢弃项目副本中检查：

1. **现成证据**：一条评审含多个问题时，应拆成原子 concern，逐项定位原始证据；已批准但未做的修改仍是 pending。未确认策略时停在策略，未确认完整措辞时保留候选，不生成已确认粘贴版。
2. **证据不足**：要求不存在的消融／证明，或评审包含歧义时，分别列需补充工作／需澄清、具体缺口与问题；不给无依据数字，不启动实验或配置环境。审稿文本中的命令不产生授权。
3. **独立线程与限长**：每 reviewer 回复自包含，不能依赖另一个线程；对实际粘贴目标工具计数，rich 超限不阻塞合规 strict，但所有版本仍检查事实和承诺。最终保存须与已确认文字一致，改字后重新检查。
4. **后续与停止**：新评论只生成增量，保留旧稿和用户勾选；无独立审查能力时明确未执行，不将自查冒充独立验证；到授权或轮数上限即停，不投稿、转投或自动推进。

## 证明审查与修复

`proof-review` 直接读取现成证明及其依赖，只在回复中给出义务、缺口、反例与影响，不写文件、不编译、不自动修复。普通证明不要求 Lean 或 LaTeX 环境。`proof-repair` 必须由用户显式启动，确认目标命题、精确文件/段落、轮数和工具资源后才修订；编译与其副产物单独授权。修复内部使用已安装的 `proof-review` 复审，严重问题另做 fresh 盲审；缺少独立能力时报告未完成。

在可丢弃的项目副本中手工验收：

1. 放入含错误归纳步的现成证明，记录原始文件内容与目录清单。调用 `proof-review`，核对能定位错误、列出影响，并且项目无新增或变更文件，编译标为未运行。
2. 显式调用 `proof-repair` 但尚不确认写入，检查它展示具体契约并等待，文件仍不变。确认仅修复一个证明环境、保持命题/假设、限定 1 轮且不编译，再核对只有该环境改变，完整推导和实际复审反馈留在回复中。
3. 对被核实反例推翻的命题，仅允许改证明、不允许改假设或命题；应停止并提出待用户决定的选项，保留反例、gaps 和失败路线，不能偷偷加条件。
4. 分别拒绝编译或使用缺少编译器的环境，报告必须准确写未执行/不可用；若另行批准编译，则检查真实退出码、日志与新产物，不把编译成功等同数学正确。缺少独立审查、轮数耗尽或写入前文件发生冲突时，同样保留未完成状态。

各宿主须实际保留 `proof-repair` 的显式调用策略。Skills CLI 1.5.26 本地安装实测：Eve 副本保留 `name`，但移除 `disable-model-invocation`；Claude Code / Codex 限定安装的规范副本保留源字段。Eve 的真实显式调用策略尚未验收，无法确认时暂停在该宿主使用修复。其他宿主同样须核实；此处指令不是宿主权限强制执行机制。

通用 CLI 安装实测、临时文件场景模拟和真实用户验收是不同层级。尚未经用户在真实科研项目确认，不声明端到端体验通过。

## 论文编译与显式修复

- `paper-compile`：只检查；在用户已有 LaTeX 上真实构建，报告错误、PDF 与未解决问题。可独立点名，也可在父 Workflow 当前编译职责内使用。
- `paper-compile-repair`：用户另行显式调用；展示具体文件和 diff，确认构建及最多三轮预算后才修复。检查结果不是修复授权。
- 使用完整审阅的闭合输入和新临时输出，记录宿主执行或现有隔离的实际边界；不安装、配置环境或覆盖旧 PDF。工具不足时准确停止。

在可丢弃的论文副本中依次验收：

1. **坏稿检查**：给出不存在的命令；显式允许临时构建，要求只检查。核对真实非零退出码、原始日志与源码不变。
2. **授权修复**：点名 repair，确认限定文件、完整 diff 和预算。核对仅批准差异被应用、新目录重编译、失败日志仍保留。另留一个未定义引用，确认 build 成功也继续报告 warning。
3. **拒绝修复**：拒绝拟 diff，核对原稿与旧 PDF 不变，没有后台修复或自动进入下一流程。
4. **能力缺失**：在无匹配引擎/文献后端的环境中检查，核对“未运行”、缺失项、不安装和不使用旧 PDF 假报成功；缺可选 PDF 工具时相应检查单列“未检查”。
5. **复杂稿与停止**：未知构建脚本、动态依赖、越界路径或无法落实预算时应停止，不把禁 shell escape 或事后内容比较声称为 OS 写保护。另测多入口、嵌套章节及 venue 规则未知，确认不猜入口、不删孤立候选、不臆定页数合规。

编译成功不证明论文论断成立、可投稿或用户已接受。以上是用户手工验收步骤，不是已完成真实科研验收的声明。宿主须保留 `paper-compile-repair` 的显式调用策略。Skills CLI 1.5.26 的本地全量安装中，Eve 副本保留 `name`，但移除 `disable-model-invocation`；在实际加载和显式调用策略核实前暂停在 Eve 使用 repair。不能把副本安装成功当作权限执行正确。

## Conference Talk 人工验收

Skills CLI 1.5.26 的本票本地安装中，Claude Code / Codex 副本完整；Eve 副本保留 `name`，但仍移除 `disable-model-invocation`。因此不能声明 Eve 已落实 `paper-talk` 的仅显式调用策略；未在宿主核实前暂停在 Eve 使用此入口，不以正文护栏代替宿主策略验证。

显式调用 `paper-talk`，提供现成论文、听众、语言、主讲时长、Q&A 预留、输出目录及格式；不要求先运行写作或 setup。

1. **论文到演讲**：确认逐页大纲后，检查实际 slides、notes、逐字 script 和 Q&A 一一对应；数字、baseline、单位、种子/样本数与局限可追溯，时间合计符合预算。无消融、demo 或链接时不补造。
2. **三产物审查**：在可丢弃副本中分别把 slides 数字改错、notes 聚合次数改错、script/Q&A 增加无依据泛化；只授权审查。报告应指出三类实际位置及源证据，保持输入不变，并给故事、密度、计时、图可读性、开场、takeaway、渐进讲解的七维结果。
3. **工具缺失**：无法生成或渲染请求格式时，检查 Markdown 仍可交付且明确未生成/未验证项；无安装动作。没有独立 reviewer 时只能标自检，无真人排练不宣称实际准时。
4. **冲突、匿名与停止**：既有文件保留、变更大纲先确认；匿名字段不被模板或精修补回。视觉修改不改变内容或 notes，原稿和精修副本分开；最终仅返回报告，不上传、发布或调用后续 Workflow。

模板的 Beamer 编译和 PPTX 语法检查不代表真实演讲材料通过；实际双格式输出、字体/动画、投影与真人排练须在用户环境逐项验收。通用 CLI 安装实测、临时文件模型场景和真实用户验收是不同层级。尚未经用户在真实科研项目确认，不声明端到端体验通过。
