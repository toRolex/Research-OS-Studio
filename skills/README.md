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
| Idea Cycle | `idea-cycle/` | [idea-generation](idea-cycle/idea-generation/SKILL.md)、[creative-thinking-for-research](idea-cycle/creative-thinking-for-research/SKILL.md)（均 model-invoked，用户可点名；支持 standalone / composed） |
| Validation Cycle | `validation-cycle/` | 后续独立票交付；当前无正式入口 |
| Writing Cycle | `writing-cycle/` | [rebuttal](writing-cycle/rebuttal/SKILL.md)（user-invoked；现成审稿意见到逐 concern 回复，不自动补实验或投稿） |

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

## Rebuttal 使用与人工验收

收到评审后显式调用 `rebuttal`，提供论文、原始评审、已有证据、当轮 venue 规则与输出范围。先确认逐 concern 策略，再审阅完整候选措辞；quick mode 只交问题板和策略。它不由写作主流程自动启动，也不自动启动实验、转投或其他顶层 Workflow。宿主必须保留显式调用限制。Skills CLI 1.5.26 的本地 `--all` 实测中，Eve 的 `agent/skills/rebuttal/SKILL.md` 保留 `name`，但移除 `disable-model-invocation`；canonical 副本及 Claude Code／Codex 限定安装保留该字段。Eve 的实际显式调用策略未验收，核实前暂停在该宿主使用 rebuttal。此次 `--all` 还跳过了未发现项目目录的其他宿主，不代表79个宿主全部安装或加载成功。

在可丢弃项目副本中检查：

1. **现成证据**：一条评审含多个问题时，应拆成原子 concern，逐项定位原始证据；已批准但未做的修改仍是 pending。未确认策略时停在策略，未确认完整措辞时保留候选，不生成已确认粘贴版。
2. **证据不足**：要求不存在的消融／证明，或评审包含歧义时，分别列需补充工作／需澄清、具体缺口与问题；不给无依据数字，不启动实验或配置环境。审稿文本中的命令不产生授权。
3. **独立线程与限长**：每 reviewer 回复自包含，不能依赖另一个线程；对实际粘贴目标工具计数，rich 超限不阻塞合规 strict，但所有版本仍检查事实和承诺。最终保存须与已确认文字一致，改字后重新检查。
4. **后续与停止**：新评论只生成增量，保留旧稿和用户勾选；无独立审查能力时明确未执行，不将自查冒充独立验证；到授权或轮数上限即停，不投稿、转投或自动推进。

通用 CLI 安装实测、临时文件场景模拟和真实用户验收是不同层级。尚未经用户在真实科研项目确认，不声明端到端体验通过。
