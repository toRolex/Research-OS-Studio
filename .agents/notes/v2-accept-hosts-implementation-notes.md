# v2-accept-hosts implementation notes

## Scope / discipline

- 开工 HEAD/integration 均 `67a04ff5b3714f7d6883cb9a33b1b4259348fabf`，祖先检查成功。仅本 worktree、临时项目，不 push/tag/PR/关票。
- 已读 approved shared contract、release acceptance、user acceptance guide、#38/#39/#40/#46 issue REST 原文、相关历史 notes；历史不足不视为永久阻碍。
- 已调用 pre-implement；tdd 未注册，完整读取 `/Users/rolex/.agents/skills/tdd/SKILL.md`。沿用批准 seam：checker CLI 与真实宿主 CLI/tools。Python 一律 UV。若正文 bug，先失败回归后小修。
- 证据根 `/tmp/research-os-v2-hosts`，保留 prompt、commands、stdout/jsonl/session、快照、安装文件哈希。禁止凭据内容进入证据；全局角色表仅 stat/hash。默认工具代表场景与真实多轮 setup，不能手填输出代替执行。

## Progress

- GitHub 先 rate-limit skill；4 次 REST issue 读取，初始 core/graphql remaining 5000。不写 GitHub。
- 版本：pi 1.0.0，Claude Code 2.1.228，Codex 0.151.0，UV 0.12.22。模型清单 `models.txt` 已由真正 `pi --list-models` 产生。

## Decisions

- 行为执行由安装项目中的真实 CLI 产生；所有对话 turn/prompt 单独保存，同宿主多轮按 session resume。工具许可不是用户叶门批准。

## Red / green / behavior

- pi首次普通`/research-os`误选唯一自动可见setup。读pi官方skills.md确认原生`/skill:name`；新增公开文档合同回归1红，最小修README/宿主映射，8绿，54f2ada。限定重装后原生命令真实默认工具重跑读推荐叶且零副作用。
- Claude new task进入route-only却TaskUpdate旧计划。先回归1红，补任务状态也只读的具体pointer，a15c586；限定重装、原session真实重跑仅Read无TaskUpdate。没有新增审批科研门。
- 三宿主setup真正逐角色8轮确认、完整全文批准后实际7文件写入。pi不可用slug停+冲突保留旧日志；三宿主幂等重跑均零变动。Claude无CLI清单时宿主自己合理替代GET /v1/models HTTP200，仅输出id、不泄密。Codex目录无provider，安全读单字段model_provider=custom；workspace-write拒.agents后仅toy进程放开重试7/7。
- 79轮真实调用：全局表hash+mtime全相同；项目变化只有4获准写轮，精确7/7/7/2路径。原prompt/command/tool/session/快照/artifacts归档docs/acceptance/evidence/v2-accept-hosts.tar.gz，报告独立docs/acceptance/v2-accept-hosts.md。
- 完成前merge最新integration（仍67a04ff）重测checker39/U38/M1、tests18+scripts41=59绿。

## Deviations / remaining

- 真实宿主会违反UV：Codex初轮/重跑先裸python3后UV重跑；fresh主审也裸python3并创建删除额外自产临时报告。证据完整保留，只证明fresh子context隔离，不判纪律全过。
- Claude多轮timeout并出现破损重复计划，续接后压缩BLOCKED交付；不把叶全文读取当完整科研计划通过。逐字todolist没有所有宿主都照合同执行，仍列缺口。
- Codex mismatch重跑安全只读完成，但首选proof与用户写作意图一致性有局限；未据一次sample扩大改科研匹配逻辑。
- 模型token成本由真实宿主记录；无额外付费计算资源、外部投稿上传或用户数据删除。未派herdr子agent；fresh验收由宿主自己启动独立pi CLI子session。

