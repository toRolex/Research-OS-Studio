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
| Idea Cycle | `idea-cycle/` | [idea-generation](idea-cycle/idea-generation/SKILL.md)、[creative-thinking-for-research](idea-cycle/creative-thinking-for-research/SKILL.md)、[novelty-check](idea-cycle/novelty-check/SKILL.md)（均 model-invoked，用户可点名；支持 standalone / composed） |
| Validation Cycle | `validation-cycle/` | 后续独立票交付；当前无正式入口 |
| Writing Cycle | `writing-cycle/` | [paper-talk](writing-cycle/paper-talk/SKILL.md)（独立 user-invoked：从论文生成 slides、notes、script 并审查演讲产物；不自动发布或启动后续 Workflow） |

只有实际含 `SKILL.md` 的目录才是可安装 Skill。不为分类创建占位 Skill，不把保留的旧工程纳入这份清单。

## 初始化与人工验收

setup 先探索现有项目，推荐沿用已有工作区；只有不存在时才建议可见的 `research/`。一次询问一个必要决定，展示全部草稿，收到明确确认后才写入。它只补基础导航、项目说明、findings、日志和选定指令文件的 Research OS 区块，不配置环境，不生成研究结论，不启动 Discovery。

在可丢弃的科研项目副本中逐项验收：

1. **新项目**：选择工作区；两种指令文件都不存在时选择其一；确认前检查零写入，确认后逐项核对完整草稿。
2. **非空项目**：放入原研究材料及已有日志；选择沿用目录，确认没有搬迁、覆盖或功能重复文件。
3. **重复执行**：再次调用，已有完整基础项应无需写入；核对区块、日志、文件内容不变。
4. **内容冲突**：修改已有 Research OS 区块；应先展示差异并逐项询问，保留所有周边段落。两种指令文件都存在时只更新 `CLAUDE.md`。
5. **拒绝写入与外部变化**：完整草稿后拒绝，项目应零变化；确认后目的文件被修改或新建路径出现时，应停下并重新确认。另测原先仅有 `AGENTS.md`、确认后外部新增 `CLAUDE.md`：即使它不在原写入清单中，也应停止整批、重新选择指令文件并确认新草稿。
6. **停止边界**：最终只汇报实际路径和未解决项，无实验、环境安装、远程副作用或自动启动下一流程。

## Conference Talk 人工验收

Skills CLI 1.5.26 的本票本地安装中，Claude Code / Codex 副本完整；Eve 副本保留 `name`，但仍移除 `disable-model-invocation`。因此不能声明 Eve 已落实 `paper-talk` 的仅显式调用策略；未在宿主核实前暂停在 Eve 使用此入口，不以正文护栏代替宿主策略验证。

显式调用 `paper-talk`，提供现成论文、听众、语言、主讲时长、Q&A 预留、输出目录及格式；不要求先运行写作或 setup。

1. **论文到演讲**：确认逐页大纲后，检查实际 slides、notes、逐字 script 和 Q&A 一一对应；数字、baseline、单位、种子/样本数与局限可追溯，时间合计符合预算。无消融、demo 或链接时不补造。
2. **三产物审查**：在可丢弃副本中分别把 slides 数字改错、notes 聚合次数改错、script/Q&A 增加无依据泛化；只授权审查。报告应指出三类实际位置及源证据，保持输入不变，并给故事、密度、计时、图可读性、开场、takeaway、渐进讲解的七维结果。
3. **工具缺失**：无法生成或渲染请求格式时，检查 Markdown 仍可交付且明确未生成/未验证项；无安装动作。没有独立 reviewer 时只能标自检，无真人排练不宣称实际准时。
4. **冲突、匿名与停止**：既有文件保留、变更大纲先确认；匿名字段不被模板或精修补回。视觉修改不改变内容或 notes，原稿和精修副本分开；最终仅返回报告，不上传、发布或调用后续 Workflow。

模板的 Beamer 编译和 PPTX 语法检查不代表真实演讲材料通过；实际双格式输出、字体/动画、投影与真人排练须在用户环境逐项验收。通用 CLI 安装实测、临时文件模型场景和真实用户验收是不同层级。尚未经用户在真实科研项目确认，不声明端到端体验通过。
