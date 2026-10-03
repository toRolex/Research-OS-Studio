---
name: research-os
description: "科研任务的唯一编排入口：按意图、材料和规模选路线；只读请求只给推荐。"
disable-model-invocation: true
---

# Research OS

用户显式调用 `/research-os` 后，本入口负责匹配路线并照 playbook 执行。除 `setup-research-os` 外，各 skill 仍由用户点名或由本入口按路径级联读取；模型不自动发现它们。

Gates: none

## 匹配

用户意图和只读约束优先，材料状态限定适用路线，规模决定编排方式。任意大任务不等于 improvement。匹配后跨 turn 保持该路线；用户说 new task 时重新匹配。

无已交付路线时打开 [custom](playbooks/custom.md)，先设计有界流程，只有真歧义才问。不要把未交付路线的文件写成已经存在。

## 路由表

| 路线 | 变体 | 触发词 | 适用条件 | 只读约束 | playbook |
|---|---|---|---|---|---|
| route-only | — | 我该从哪开始、该用哪个、只看推荐、推荐入口、不要执行 | 用户只要入口或下一步建议 | yes | [route-only](playbooks/route-only.md) |
| rebuttal | — | 回复审稿、逐条回应审稿意见、写 rebuttal | 已有论文与审稿意见，要逐 concern 候选回复 | no | [rebuttal](playbooks/rebuttal.md) |
| resubmit | — | 转投、换 venue 重投、保留旧稿改投 | 已有投稿目录，要在新目录适配另一 venue 并保留旧稿 | no | [resubmit](playbooks/resubmit.md) |
| paper-talk | — | 做会议演讲、生成 slides notes script、准备 paper talk | 已有论文，要 slides、notes 与逐字 script | no | [paper-talk](playbooks/paper-talk.md) |
| custom | — | 没有对应流程、设计一个流程 | 已交付路线都不匹配 | no | [custom](playbooks/custom.md) |

已命名、文件未交付，不建路由行：idea-discovery、experiment-plan、experiment-bridge、paper-writing（general / ml / systems）、proof、improvement、pickup。对应 playbook 由后续票与路由行一起加入。

## 只读优先

只要用户是在问该从哪开始、该用哪个、或明确不要执行，就打开 [route-only](playbooks/route-only.md)。即使句子里同时出现「写论文」「跑实验」等执行词，只读意图仍优先。route-only 不创建任务、不联网、不写文件、不派子代理。

## 模型

项目角色表是研究项目里的 `.agents/research-os-models.md`，一行一个角色：`reviewer: provider/model-id | high`。角色只有 orchestrator、literature、ideator、implementer、analyst、prover、writer、reviewer。thinking 只能是 off、minimal、low、medium、high、xhigh、max，而且必须是该模型支持的值。正文引用写成 `Role: reviewer`。

文件缺失时使用当前 session 实际可用的模型与 thinking，并明示回退，不编造 slug。同上下文里的自审不是 fresh 独立审查。用户指定的模型不可用时停下，请用户确认替代。不修改 `~/.agents/pstack-models.md`。

## 算力

工作区 `compute-policy.md` 是默认政策，不是本批运行许可。未配置时范围未指定，费用、算力和运行数都是 0，有效期 0 小时。启动执行前由持有该路线的 playbook 核对授权；route-only 与未批准的 custom 不消耗额度。

## 宿主映射

三宿主都用显式 `/research-os`。安装目录和派发方式不同：

| 宿主 | Skills 位置 | 委派 | 会话 |
|---|---|---|---|
| pi | 项目 `.agents/skills/`，也发现用户目录下的 agents skills | `herdr_spawn_agent`；子代理按项目 `.agents/research-os-models.md` 的 `Role:` 选模型 | pi 默认 sessions 目录中的 `--session` 文件 |
| Claude Code | 项目 `.claude/skills/` | Agent tool 派 subagent；无该工具时由编排者串行执行 | 当前 Claude Code 会话 |
| Codex | 项目 `.agents/skills/` 或 Codex 实际报告的 skills 目录 | spawn_agent；无该工具时由编排者串行执行 | Codex 当前 thread / session |

命令存在不等于已经登录或具备委派能力。并行 fan-out 只在该宿主当前会话确实有子代理工具时使用；没有时，编排者按 playbook 顺序自己执行。本文件不发明第四种宿主映射。

## 级联

命中已交付 playbook 后，逐字采用其步骤。步骤里的反引号路径和 Markdown 链接都要读全文，例如 `references/PRODUCT-MAP.md`。不把未读文件说成已执行。
