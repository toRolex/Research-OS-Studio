# 安装依赖与解析

`research-improvement` 的正文、方法、组合映射、日志模板及第三方来源/许可证均与本 `SKILL.md` 共置。用通用 Skills 安装器单独安装时，这些本地资源随该 Skill 一起复制；安装后从 `research-improvement/` 目录解析 `references/`、`templates/`、`NOTICE.md` 与 `UPSTREAM-LICENSE.md`。

## 必需的共享合同

运行本 Skill 前必须安装同一 Research OS 套件的 `research-os` Skill。它提供唯一权威的委托与批次合同，不在本 Skill 内复制：

| 依赖 | 仓库内路径 | 扁平 Skills 安装路径 |
|---|---|---|
| 委托合同 | `skills/general/research-os/references/mandate.md` | `<skills-root>/research-os/references/mandate.md` |
| 批次授权 | `skills/general/research-os/references/batch-authorization.md` | `<skills-root>/research-os/references/batch-authorization.md` |

`<skills-root>` 是安装器放置各 Skill 目录的共同父目录（例如 `.claude/skills/`）。先按当前 Skill 的安装目录找到该根，再检查所进入分支的目标文件实际存在且可读；缺少当前分支必需依赖时只将该分支标为 `blocked`，不以摘要、缓存或本文件替代。

## 作业/费用批次的条件依赖

普通研究恢复不需要 `setup-research-os`。该 Skill 是仅作业/费用批次分支依赖：只有进入作业、费用/资源或远程批次分支时，才需要它的策略与账本模板；缺模板只阻断该批次分支，不阻断按委托/暂停记录进行的普通恢复。

| 依赖 | 仓库内路径 | 扁平 Skills 安装路径 |
|---|---|---|
| 计算策略模板 | `skills/general/setup-research-os/templates/compute-policy.md` | `<skills-root>/setup-research-os/templates/compute-policy.md` |
| 作业与费用账本模板 | `skills/general/setup-research-os/templates/research-log.md` | `<skills-root>/setup-research-os/templates/research-log.md` |

## 按需的组合能力

`composition-map.md` 中列出的能力是分支依赖，不是全套硬前置，也不是自动调用链。进入相应分支前，按同一 `<skills-root>/<skill-name>/SKILL.md` 规则核实对应 Skill 已安装且可读；未安装或宿主不支持所需独立执行者时，只将该审查/实验分支标为 `blocked`，如实报告，不伪造输出。能力名与仓库路径对应如下：

| 能力 | 仓库内路径 | 扁平 Skills 安装目录 |
|---|---|---|
| `paper-claim-audit` | `skills/writing-cycle/paper-claim-audit/SKILL.md` | `<skills-root>/paper-claim-audit/SKILL.md` |
| `citation-audit` | `skills/writing-cycle/citation-audit/SKILL.md` | `<skills-root>/citation-audit/SKILL.md` |
| `claim-stress-test` | `skills/writing-cycle/claim-stress-test/SKILL.md` | `<skills-root>/claim-stress-test/SKILL.md` |
| `proof-review` | `skills/validation-cycle/proof-review/SKILL.md` | `<skills-root>/proof-review/SKILL.md` |
| `experiment-audit` | `skills/validation-cycle/experiment-audit/SKILL.md` | `<skills-root>/experiment-audit/SKILL.md` |
| `analyze-results` | `skills/validation-cycle/analyze-results/SKILL.md` | `<skills-root>/analyze-results/SKILL.md` |
| `run-experiment` | `skills/validation-cycle/run-experiment/SKILL.md` | `<skills-root>/run-experiment/SKILL.md` |
| `experiment-queue` | `skills/validation-cycle/experiment-queue/SKILL.md` | `<skills-root>/experiment-queue/SKILL.md` |
| `monitor-experiment` | `skills/validation-cycle/monitor-experiment/SKILL.md` | `<skills-root>/monitor-experiment/SKILL.md` |
| `training-health-check` | `skills/validation-cycle/training-health-check/SKILL.md` | `<skills-root>/training-health-check/SKILL.md` |
| `paper-compile` | `skills/writing-cycle/paper-compile/SKILL.md` | `<skills-root>/paper-compile/SKILL.md` |

独立 reviewer 是 review/repair/re-review 的必要条件。reviewer 不可用时将对应审查/改进轮标为 `blocked`；允许提供只读自查建议，但不计为 fresh 独立审查，也不算完成 review/repair/re-review。不能以编排者串行自评替代该轮。

仓库 checker 核对仓库路径存在；离线安装验收则核对实际安装目录。若安装器改变布局，先从它的实际输出确认安装根并更新此映射及测试，不能假设路径或用复制目录代替安装。
