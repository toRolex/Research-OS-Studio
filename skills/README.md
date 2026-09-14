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

## 分类与当前清单

目录约定是 `skills/<category>/<skill>/SKILL.md`，资源与 Skill 共置。分类用于导航，不规定调用顺序。

| 分类 | 目录 | 当前正式 Skill |
|---|---|---|
| General | `general/` | [setup-research-os](general/setup-research-os/SKILL.md)（user-invoked） |
| Idea Cycle | `idea-cycle/` | [idea-generation](idea-cycle/idea-generation/SKILL.md)、[creative-thinking-for-research](idea-cycle/creative-thinking-for-research/SKILL.md)、[novelty-check](idea-cycle/novelty-check/SKILL.md)、[idea-review](idea-cycle/idea-review/SKILL.md)、[idea-refinement](idea-cycle/idea-refinement/SKILL.md)（均 model-invoked，用户可点名；支持 standalone / composed） |
| Validation Cycle | `validation-cycle/` | [experiment-plan](validation-cycle/experiment-plan/SKILL.md)（user-invoked；将已有问题转为有界实验计划，产出后停止）、[run-experiment](validation-cycle/run-experiment/SKILL.md)、[experiment-queue](validation-cycle/experiment-queue/SKILL.md)、[monitor-experiment](validation-cycle/monitor-experiment/SKILL.md)、[training-health-check](validation-cycle/training-health-check/SKILL.md)、[experiment-audit](validation-cycle/experiment-audit/SKILL.md)、[proof-orchestrator](validation-cycle/proof-orchestrator/SKILL.md)（除 experiment-plan、proof-orchestrator 外均 model-invoked，用户可点名；支持 standalone / composed） |
| Writing Cycle | `writing-cycle/` | [paper-plan](writing-cycle/paper-plan/SKILL.md)（model-invoked，用户可点名；支持 standalone / composed）、[academic-plotting](writing-cycle/academic-plotting/SKILL.md)（model-invoked，用户可点名；支持 standalone / composed）、[paper-compile](writing-cycle/paper-compile/SKILL.md)（check-only，model-invoked，用户可点名；standalone / composed）、[paper-compile-repair](writing-cycle/paper-compile-repair/SKILL.md)（user-invoked，显式授权修复） |

只有实际含 `SKILL.md` 的目录才是可安装 Skill。不为分类创建占位 Skill，不把保留的旧工程纳入这份清单。

### 现成候选的评审与改进

`idea-review` 让独立评审者直接读取原始候选及文献，保留 findings、证据、裁决依据与未解决问题；不改候选。`idea-refinement` 在已授权修订范围内保持固定 Problem Anchor，比较最小可行与前沿路线，输出完整 Proposal 与逐轮改进理由；独立方法评审与修订分工明确。二者均可直接用于现成材料，不要求先运行生成流程，也不自动互相启动。

手工验收：提供一个有明显弱点的现成候选、原始文献和约束；先点名 review，核对 reviewer 实际原文定位与问题，再点名 refinement，核对每轮 Anchor 原样保留、双路线取舍及未解决项。限制一轮修订、零实验预算，应只得到方法及验证草图。另测缺原文、缺独立 reviewer、已有同名输出和 composed 章节授权：应准确暴露缺口、保留已有材料并停止，不配置环境或自动实验。实现期场景结果不替代用户真实科研验收。

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
