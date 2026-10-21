# Ticket #56 implementation notes

## Status

| Work unit | Status | Deliverable / evidence | Next |
| --- | --- | --- | --- |
| #56 experiment execution & remote contract | done | `tests/test_spec48_ticket56.py` (14 passed); 九个实验 Skill、run-experiment 授权/执行/远程参考，checker 与迁移登记；单装及联装资源检查通过 | 无；全套保留基线 7 个失败 / checker 9 条历史断链 |

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

## Revalidation discoveries and decisions

- 独立验收新增用例发现：原 `run-experiment` 只把执行许可委托给通用“批次授权”引用，却没有在可单装正文中明确从 `research-log.md` 读取，并且存在“每个 milestone 仍需用户确认”的旧语义；这会让实际执行控制无法证明已继承同一批授权。现已将批次账本、到期/scope/额度/运行名额/并发/重试检查、预留与补账、批次内不重复索权明确放在统一控制器，并将跨能力细节指向共享合同。
- 原研究 OS `experiment-bridge` playbook 仍保留第二套授权检查和 attempt 记账，与叶兼容入口已取消控制权冲突；现改为把执行交给 `run-experiment`，并在委托明确要求时组合只读分析/审计。实验桥接叶入口也补上此兼容委托说明。
- 原始红已在先前记录。新增回归测试先实测 `2 failed`，指出 run-experiment 未包含批次授权合同及 playbook 未路由分析/审计；补齐后新增 checker 回归用例又实测 `2 failed`（checker 未检测授权字段缺失与 playbook 重复控制），本票测试最终 `14 passed`。
- 安装复核发现 run-experiment 曾跨出其 Skill 根引用 Research OS 的 `batch-authorization.md`，单独安装时断链。现将完整授权核验规则共置为 `references/batch-authorization.md`，并让 checker 验证必需文件及合同标记；单装安装实测所有资源均在位。

## Original execution evidence

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

## Final revalidation evidence

```text
$ uv run --offline --with pytest python -m pytest tests/test_spec48_ticket56.py -q
14 passed
EXIT=0

$ uv run --offline python scripts/check-skills.py
FAIL: 9 个问题；全部为 integration/spec-48 基线已有、被 .gitignore 排除的历史 evidence tarball 链接。
EXIT=1

$ uv run --offline --with pytest python -m pytest tests scripts/test_check_skills_ticket*.py -q
7 failed, 129 passed, 44 subtests passed
EXIT=1
  失败集合与 integration/spec-48 基线 7 failed / 115 passed 完全一致；均关联同一组 9 个历史 evidence tarball 断链。

$ git diff --check
EXIT=0
```

## Installation evidence

```text
$ node /Users/rolex/.npm/_npx/5606f1555d02ef53/node_modules/skills/bin/cli.mjs add <worktree> --list
EXIT=0   # CLI 1.7.4，发现 41 个 Skill

$ node <skills-cli> add <worktree> -s run-experiment -a claude-code -y
EXIT=0   # 单装成功；SKILL.md、LICENSE、agents/openai.yaml 及 4 个必要参考/模板均可达。

$ node <skills-cli> add <worktree> \
      -s experiment-plan -s experiment-bridge -s run-experiment \
      -s experiment-queue -s monitor-experiment -s training-health-check \
      -s analyze-results -s experiment-audit -s result-to-claim \
      -a claude-code -y
EXIT=0   # Installed 9 skills → /tmp/spec48-56-final.JrGqis/.claude/skills/
  九个 SKILL.md、LICENSE 与 agents/openai.yaml 均存在；run-experiment 的 execution-contract.md、remote-execution.md 与 batch-authorization.md 可达。
  安装副本 Markdown 链接检查：29 条，断链 0；run-experiment 单装七项必需资源全部存在，Skill 正文中的 Markdown 链接也均可达。
```

限制：九个相关 Skill 联装的 Markdown 链接检查通过，run-experiment 独立安装资源及链接检查通过；未逐个单装其余八个技能。静态/安装验证不代表全宿主行为或科研结论已验证。

## Delivery & merge

```text
Branch/worktree: `t3/spec-56-experiment-workflows` @ `/Users/rolex/.t3/worktrees/Research OS Studio/t3-d1a67b73`
Original implementation commit: `2d27daf92aedd75d8473a4e58b4345d11c4633ce`
Initial merge base: `integration/spec-48` @ `e84f779d78755937a59d46364e14cc6496aa2b03`
Initial integration check: `integration/spec-48` had not advanced beyond the base. Final pre-merge check: still `e84f779d78755937a59d46364e14cc6496aa2b03`; `git merge --no-edit integration/spec-48` returned “已经是最新的”。
Final integration check: `git merge --no-edit integration/spec-48` returned “已经是最新的”；`git merge-base --is-ancestor integration/spec-48 HEAD` exited 0. Final commit: `8650ee4be7efeff008c9a54768bcf2398de4f163` (`fix(validation-cycle): complete experiment authorization inheritance`).
```
