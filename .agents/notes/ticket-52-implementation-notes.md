# Ticket #52 实施记录：迁入 interrogate，交付独立挑战与主审判断

Spec #48 / Ticket #52。worktree `/Users/rolex/.t3/worktrees/Research OS Studio/t3-1f3dfbaa`，分支 `t3/independent-interrogate-reviewers`，基线 `integration/spec-48` @ `98e4333`（本地 tip，无远端引用）。

## 状态

2026-10-24按本记录当时收束阶段补记下一步列；原五列和历史结果不改，不把后继修复/复审倒灌为当时验证。

| 单元 | 交付目标 | 状态 | 产物 | 验收证据 | 当时下一步 / 阻塞 |
|---|---|---|---|---|---|
| U1 interrogate 技能 | 独立挑战、findings 去重、分歧保留、主审有据判断，只读 | done | `skills/general/interrogate/` | 绿：21 passed | 无（本票静态合同范围）；真实派发/科研未验 |
| U2 科研 reviewer 参考 | 覆盖实际材料与证明义务，共识≠数学证据 | done | `references/research-review.md` | 绿 + 红重放 | 无（参考交付范围）；不等于数学正确性 |
| U3 上游保真+来源 | rubric/reviewer/lead 机制保留，来源 revision+许可记录 | done | 同目录 references + PROVENANCE + LICENSE | diff 逐字节核对 | 无（当时采用核对范围）；后续变更另核 |
| U4 登记 | MIGRATED_CONTRACT、README 清单、入口指针、checker 函数 | done | `scripts/check-skills.py`、两 README、research-os 入口、migration-boundary | 绿 + checker 无新错 | 无（本票登记）；整包验收由后票/parent收口 |
| U5 安装实测 | 可丢弃目录 `--list` 发现新技能 | done | 本文「安装证据」 | 实跑 npx skills@latest | 无（安装可达范围）；宿主行为不外推 |

## 决策

1. **落位 `skills/general/interrogate/`**：interrogate 与 arena/swarm 同属 pstack 组织机制，是编排层能力而非 cycle 叶，放 general。
2. **按委托合同迁移**：新能力直接写「委托继承」小节并登记 `MIGRATED_CONTRACT`，无旧门；不占路线表行（无 playbook），入口用指针句指到独立点名，playbook 整合属后续票。
3. **宿主中立**：删 Cursor 规则路径与固定模型默认表（claude-opus-5-5 / grok-4.7），reviewer 模型从项目角色表 `.agents/research-os-models.md` 的 `reviewer:` 行解析；缺子代理标 blocked，不串行代跑。
4. **科研 lens 独立成文**：upstream rubric/code-quality 保留用于变更审查；科研材料审查新增 `references/research-review.md`（证明义务、具体引用、等强未证引理≠进展、数值异常保持候选、模型重合信号不是数学证据）。
5. **只读边界正面写**：独立调用不自动修订；修复由编排者按委托授权组织（proof-repair / research-improvement 等能力）。

## Deviations

1. **恢复实施而非重写**：接管 r2 遗留的已暂存/未暂存产物，逐项核对后补证据，不 reset/clean；notes 状态表原标 U4/U5 未开始，实际 unstaged 已含 checker 与登记改动，按实际内容补齐验收。
2. **安装 CLI 缓存路径失效**：brief 给的 `/Users/rolex/.npm/_npx/5606f1555d02ef53/.../cli.mjs` 已不存在（npx 缓存被清），改用票 49 先例 `npx --yes skills@latest add`，不改产品内容。
3. **红证据用独立损坏副本重放**：历史无红留证；`git archive HEAD` 出可丢弃副本并 `git init`，删除 `只读` 表述与 `references/research-review.md` 后重放本票测试，10 失败/exit 1，如实注明为补证重放而非原始首红。
4. **reviewer-prompt.md 为有据适配**：改自上游同名文件（补只读约束与研究材料占位），rubric / code-quality-review / lead-judgment 三份逐字节原样保留；PROVENANCE.md 逐条记录来源 revision 与差异。

## 红绿证据

环境：uv + uv 缓存 pytest 9.1.1（PYTHONPATH 指向 `~/.cache/uv/archive-v0/…` 五路径，同票 49 离线法）。所有命令在 worktree 根执行。

红（独立损坏副本重放）：

```text
$ git archive HEAD | tar -x -C /tmp/spec48-52-red.bghE0g  # + git init、cp 本票测试/skill/scripts
$ sed -i '' 's/只读//g' skills/general/interrogate/SKILL.md
$ rm skills/general/interrogate/references/research-review.md
$ uv run python -m pytest tests/test_spec48_ticket52.py -q   # PYTHONPATH 离线
10 failed, 11 passed
EXIT=1
```

绿（本票测试，真实工作区）：

```text
$ PYTHONPATH=… uv run python -m pytest tests/test_spec48_ticket52.py -q
21 passed in 0.13s
EXIT=0
```

全套回归（历史基线区分）：

```text
$ PYTHONPATH=… uv run python -m pytest tests scripts/test_check_skills_ticket*.py -q
7 failed, 111 passed, 44 subtests passed
EXIT=1
```

7 个失败与 9 条 checker 断链（evidence tar 包）均为未改动的既有基线，与本票新增断言无关；未屏蔽、未跳过。

静态 checker：

```text
$ uv run python scripts/check-skills.py
FAIL: 9 个问题   # 全部为既有 evidence 断链，无 interrogate 相关新错
```

## 安装证据（可丢弃目录 /tmp/spec48-52-install.Hk4BGJ）

```text
$ npx --yes skills@latest add "<worktree>" --list
◇ Found 40 skills（含 interrogate，描述可见）
EXIT=0

$ npx --yes skills@latest add "<worktree>" -s interrogate -a claude-code -y
✓ interrogate (copied) → ./.claude/skills/interrogate
EXIT=0
```

安装副本 9 项资源逐项 `test -f` 全部 OK：SKILL.md、LICENSE、agents/openai.yaml、references/{rubric,reviewer-prompt,code-quality-review,lead-judgment,research-review,PROVENANCE}.md。

## 上游保真核对

对照 `/tmp/research-os-spec48-upstream/pstack@88d47514b82e7c44f00f2b2a72ff6dd12158038c/pstack/skills/interrogate/`：

- `references/rubric.md`、`code-quality-review.md`、`lead-judgment.md`：与上游 diff 为空（逐字节一致）。
- `references/reviewer-prompt.md`：机制（severity/finding/evidence/suggestion、空审查合法）保留；补只读约束与研究材料占位，差异已在 PROVENANCE 登记为有意适配。
- `SKILL.md`：逐模型独立 reviewer、findings 合并去重与提出者记录、分歧保留、主审四桶（Act on/Consider/Noted/Dismissed）、只读边界全部保留；Cursor 规则路径、固定模型表（claude-opus-5-5 / grok-4.7）、PR open 语境删除，reviewer 模型改从项目角色表 `.agents/research-os-models.md` 解析，缺子代理标 blocked。
- 许可：上游根 LICENSE（MIT, Copyright (c) 2026 Lauren Tan）已亲核，全文共置于 `skills/general/interrogate/LICENSE`。

## AC 逐条证据

| AC | 结论 | 证据 |
|---|---|---|
| 核查并适配上游正文、reviewer 参考、许可及宿主模型配置 | 满足 | 上游保真核对节；SKILL.md 宿主中立测试绿；LICENSE 共置 |
| 保留独立审查、findings 去重、分歧保留及有理由的主审处理判断 | 满足 | FindingsContract/LeadJudgment 测试绿；rubric/lead 逐字节一致 |
| 科研审查参考覆盖实际材料和证明义务，不将模型重合信号当作数学证据 | 满足 | `references/research-review.md`；ResearchLens 4 测试绿 |
| 独立调用保持只读，不自动修订材料；委托内由编排者按适用授权组织后续修复 | 满足 | SKILL.md「始终只读」+ checker 只读合同；红重放验证该断言有效 |
| 检查安装、资源引用和上游职责保真，不强制固定数学人设或实际攻克开放问题 | 满足 | 安装证据节；openai.yaml 显式调用；reviewer-prompt 无固定人设 |

## 限制

1. 本票只验结构合同、静态 checker 与真实安装；「模型会用 interrogate 正确组织真实数学审查」「共识/票数不被模型误当数学证据」属运行行为，未验证，不据此宣称科研质量。
2. 全套 7 失败与 checker 9 断链为既有基线，留给对应历史票；本票未修，也未新增失败。
3. 红证据为损坏副本重放（历史无首红留证），已如实注明。
4. skills CLI 缓存路径已失效，安装实测改走 npx skills@latest（票 49 同源先例），不将安装行为当科研真值。

## 合并验证

提交 `9d58ce0` 后 merge `integration/spec-48`（tip `e84f779`，含 #54）。冲突 2 处，双方登记均保留：

- `scripts/check-skills.py` `MIGRATED_CONTRACT`：interrogate + create/maintain-formal-verification-skill 三条并存。
- `skills/general/research-os/references/migration-boundary.md`：对抗审查 + 形式化检查创建/维护三行并存。

合并后复验（merge commit `33d2e30`）：

```text
$ PYTHONPATH=… uv run python -m pytest tests/test_spec48_ticket52.py tests/test_spec48_ticket54.py -q
46 passed
EXIT=0

$ PYTHONPATH=… uv run python -m pytest tests scripts/test_check_skills_ticket*.py -q
7 failed, 136 passed, 44 subtests passed   # 仍为同 7 条历史基线失败，无新增

$ uv run python scripts/check-skills.py
FAIL: 9 个问题   # 输出中 0 条涉及 interrogate 或形式化，全为既有 evidence 断链
```
