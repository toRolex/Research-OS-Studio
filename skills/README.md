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
| Validation Cycle | `validation-cycle/` | [proof-review](validation-cycle/proof-review/SKILL.md)（model-invoked，用户可点名；只读，支持 standalone / composed）、[proof-repair](validation-cycle/proof-repair/SKILL.md)（user-invoked；显式授权的有界修复） |
| Writing Cycle | `writing-cycle/` | 后续独立票交付；当前无正式入口 |

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

## 证明审查与修复

`proof-review` 直接读取现成证明及其依赖，只在回复中给出义务、缺口、反例与影响，不写文件、不编译、不自动修复。普通证明不要求 Lean 或 LaTeX 环境。`proof-repair` 必须由用户显式启动，确认目标命题、精确文件/段落、轮数和工具资源后才修订；编译与其副产物单独授权。修复内部使用已安装的 `proof-review` 复审，严重问题另做 fresh 盲审；缺少独立能力时报告未完成。

在可丢弃的项目副本中手工验收：

1. 放入含错误归纳步的现成证明，记录原始文件内容与目录清单。调用 `proof-review`，核对能定位错误、列出影响，并且项目无新增或变更文件，编译标为未运行。
2. 显式调用 `proof-repair` 但尚不确认写入，检查它展示具体契约并等待，文件仍不变。确认仅修复一个证明环境、保持命题/假设、限定 1 轮且不编译，再核对只有该环境改变，完整推导和实际复审反馈留在回复中。
3. 对被核实反例推翻的命题，仅允许改证明、不允许改假设或命题；应停止并提出待用户决定的选项，保留反例、gaps 和失败路线，不能偷偷加条件。
4. 分别拒绝编译或使用缺少编译器的环境，报告必须准确写未执行/不可用；若另行批准编译，则检查真实退出码、日志与新产物，不把编译成功等同数学正确。缺少独立审查、轮数耗尽或写入前文件发生冲突时，同样保留未完成状态。

各宿主须实际保留 `proof-repair` 的显式调用策略。Skills CLI 1.5.26 本地安装实测：Eve 副本保留 `name`，但移除 `disable-model-invocation`；Claude Code / Codex 限定安装的规范副本保留源字段。Eve 的真实显式调用策略尚未验收，无法确认时暂停在该宿主使用修复。其他宿主同样须核实；此处指令不是宿主权限强制执行机制。

通用 CLI 安装实测、临时文件场景模拟和真实用户验收是不同层级。尚未经用户在真实科研项目确认，不声明端到端体验通过。
