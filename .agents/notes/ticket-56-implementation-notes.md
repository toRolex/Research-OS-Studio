# Ticket #56 implementation notes

## Status

| Work unit | Status | Deliverable / evidence | Next |
| --- | --- | --- | --- |
| #56 experiment execution & remote contract | 待验收 | `tests/test_spec48_ticket56.py`; 九个实验 Skill、run-experiment 执行/远程参考、checker 与迁移登记 | merger 验收 |

## Red evidence

```text
$ PYTHONPATH=<cached pytest wheels> uv run python -m pytest tests/test_spec48_ticket56.py -q
8 failed, 2 passed
EXIT=1
```

失败覆盖：桥接控制仍独立、九个实验能力未统一委托继承、运行/队列合同缺输入版本／工具链／独立目录／作业身份／退出码／原始日志／产物、断线恢复缺原作业查询、远程执行参考缺失，以及 checker 未登记本票合同。

## Decisions

- 将旧 `experiment-bridge` 保留为兼容入口，不再拥有授权门、里程碑、报告或 tracker 更新；统一执行控制在 `run-experiment`，批次细节仍在 `experiment-queue`。
- 九个实验能力统一登记到 `MIGRATED_CONTRACT`，以「委托继承」替代旧叶门；付费、远程、上传、下载和破坏性动作仍按批次授权，只读请求不启动。
- 运行/队列合同新增共置 `execution-contract.md` 与 `remote-execution.md`；断线恢复要求查原作业并分开作业退出、产物有效和科学结论。旧文件不能证明来自本次作业身份时标 `stale`/`unknown`。
- 实验计划把对照口径改为按问题选：机器学习保留训练 baseline，数学计算使用计划声明的对照、已知值、证书重放或独立检查，不硬套训练 baseline。
- 独立安装的委托引用不用跨 Skill Markdown 链接；正文写明 research-os mandate，避免单装副本断链。

## Green evidence

```text
$ PYTHONPATH=<cached pytest wheels> uv run python -m pytest tests/test_spec48_ticket56.py -q
10 passed
EXIT=0

$ uv run python scripts/check-skills.py
FAIL: 9 个问题（全部为 .gitignore 造成的历史 evidence tarball 断链，与基线逐条相同）
EXIT=1

$ PYTHONPATH=<cached pytest wheels> uv run python -m pytest tests scripts/test_check_skills_ticket*.py -q
7 failed, 125 passed, 44 subtests passed
EXIT=1
  失败集合与基线完全一致（同一 7 个测试，均由 9 条历史 evidence tarball 断链造成；
  #54 记录为 7 failed, 115 passed，本次多出的 10 passed 即本票测试）
```

## Installation evidence

```text
$ node /Users/rolex/.npm/_npx/5606f1555d02ef53/node_modules/skills/bin/cli.mjs add <worktree> --list
EXIT=0   # CLI 1.7.4，发现 41 个 Skill

$ node <skills-cli> add <worktree> \
      -s experiment-plan -s experiment-bridge -s run-experiment \
      -s experiment-queue -s monitor-experiment -s training-health-check \
      -s analyze-results -s experiment-audit -s result-to-claim \
      -a claude-code -y
EXIT=0   # Installed 9 skills → /tmp/spec48-56-final.JrGqis/.claude/skills/
  9 个 SKILL.md 均存在；run-experiment 的 execution-contract.md 和 remote-execution.md 可达。
  最终安装副本 Markdown 链接检查：43 条，断链 0。
```

限制：一起安装 nine 个副本的链接检查通过；未逐个单装全部组合并检查旧有跨 Skill 链接。新增的 mandate 引用已改为正文名称，不依赖 general/research-os 的安装路径。

## Delivery & merge

```text
Branch/worktree: t3/spec-56-experiment-workflows @ /Users/rolex/.t3/worktrees/Research OS Studio/t3-d1a67b73
Commit: 当前分支 tip `feat(validation-cycle): unify experiment execution contracts (#56)`（以最终 git log 为准）
Merge base: integration/spec-48 @ e84f779d78755937a59d46364e14cc6496aa2b03
Merge result: Already up to date；合并后 T56=0 / checker 仅 9 条历史断链 / FULL=7 failed 125 passed / diff --check=0
```
