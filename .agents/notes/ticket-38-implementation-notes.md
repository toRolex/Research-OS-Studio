# Ticket #38 implementation notes

## 共享合同（维护者已确认，可被后续票引用）

来源：`/tmp/research-os-v2-notes/shared-contract-approved.md`。维护者于本次 implement-spec 会话回复「确认」。integration branch：`integration/research-os-v2`。原工作区未提交 ADR/planning/CONTEXT 只读，不带入本分支。

### 路由

12 逻辑路线：idea-discovery、experiment-plan、experiment-bridge、paper-writing、proof、rebuttal、resubmit、paper-talk、improvement、pickup、route-only、custom（无匹配先设计有界流程，仅真歧义才问）。paper-writing 三变体 general/ml/systems，共 14 个具体 playbook 文件（含 custom）。

固定列：`route | variant | triggers | applicability | read-only | playbook`。唯一键 `(route, variant)`。用户只读意图优先，材料限定，规模决定编排，任意大任务不直接等于 improvement。说 new task 重匹配。路线文件与路由行随各票原子新增；checker 不要求尚未交付的路线。触发词按 #37/#38 与各票自然语言意图。

### 模型

研究项目 `.agents/research-os-models.md`。单角色单行 `reviewer: provider/model-id | high`。角色：orchestrator、literature、ideator、implementer、analyst、prover、writer、reviewer。thinking：off/minimal/low/medium/high/xhigh/max，且必须是该模型支持的值。正文引用 `Role: reviewer`。缺配置则回退当前 session 可用模型及 thinking，并明示，不虚构 slug。同上下文自审不能冒充 fresh 独立审查。显式指定的模型不可用时停下确认替代，不静默修改。全局 `~/.agents/pstack-models.md` 不动。

### 政策与日志

工作区 `compute-policy.md`，setup 模板共置。默认政策不等于本批授权。未配置时授权数值默认 0，有效期 0 小时，范围未指定，绝非运行许可。

字段：scope（计划/允许写域/环境）；cost_limit/currency（有限非负数/币种）；compute_limit/compute_unit（有限非负数，cpu-core-hour 或 gpu-device-hour，异构分行）；run_limit/run_count_basis（非负整数，planned-run 或 attempt）；per_attempt_cost_limit、per_attempt_compute_limit（同单位且 ≤ 累计上限）；concurrency_limit（非负整数，可执行时 ≥ 1）；retry_limit（每 planned run 额外 attempt 次数）；valid_for_hours（政策有限非负小时）；valid_until（批次 ISO8601 带时区）。禁止 unlimited、负数、NaN、无单位。not-applicable 必须解释；未知必须停。

experiment-bridge 使用 planned-run 名额，research-improvement 使用 attempt 名额，保留原合同差异。每个 attempt 都扣费用和算力。重试额度不替代修复轮数。

日志复用政策字段，并增加 batch_id、计划、模式、用户确认内容/时刻/依据、valid_until、授权状态；每个 attempt 记 run_id/attempt_id、最坏预估、起止时间、实际消耗、结果状态、产物路径。

启动前：已消耗 + 运行中预留最坏消耗 + 本次最坏消耗 ≤ 额度，同时核对单次、名额、并发、重试、范围、过期。恰好上限允许。失败、超时、无效仍记账；未知不按 0 释放。pickup 重读真实授权和作业状态，不续命。单编排者写账和启动；无法核实并发状态则停。不造 runtime。setup 不改既有 research-log。

### 门声明

既有审批正文旁固定：

`Gate: strategy-confirm | before=reply-drafting | approval=explicit-user | source=SKILL.md#回应策略`

无自带审批点写 `Gates: none`。ID 稳定。source 限定当前 skill 共置正文或 references，且锚点有效。#39 完整人工盘点存活叶 skill 及 references。#38/#40 各负责入口/setup。唯一 `scripts/check-skills.py` 内维护经审阅的 skill → 预期 gate 集合基线。校验缺失、多余、重复、格式、来源，以及 none 与基线一致。反例：删一条、全部改成 none、改 ID、重复、坏 source、整节删除。静态检查不证明自然语言新增门完整，也不证明真实执行停点。

### 验收纪律

全部 Python 操作用 UV。先红后绿。静态检查只有 `scripts/check-skills.py` 一个入口，不另拆 checker 文件。Seam B 必须是真实工具轨迹，不用模拟、静态或字段保留冒充行为证明。三个宿主命令存在不等于登录或能力可用。证据不足不关票。实现完成与行为待验分开记录。

## 本票范围

#38 拥有新 `research-os` 入口、route-only 与 custom 两个 playbook、删除旧 router、迁移 PRODUCT-MAP、路由/引用 checker、README breaking 与宿主映射。其余执行 playbook 由后续票新增，本票不实现。

## Decisions

- 路由表用中文列名，与合同英文字段一一对应：路线、变体、触发词、适用条件、只读约束、playbook。唯一键是（路线, 变体）。本票表内只放 route-only 与 custom；其余 12 逻辑路线写在「已命名、文件未交付」清单，checker 不要求它们的文件。
- 反引号级联只强制 `skills/general/research-os/`。全仓强制会把既有上游来源段里的历史 `references/*.md` 报成缺文件。
- 级联路径先相对所在 Markdown，再相对含 `SKILL.md` 的 skill 根，也接受从仓库根开始的 `skills/...`。
- 旧名 `ask-research-os` 在产品入口、清单、验收指南中清除。许可证溯源、原子切换快照、CHANGELOG、写作审计和 README breaking 迁移句允许保留旧名。
- 门基线目前只有 `research-os → {}`，正文必须是 `Gates: none`。叶 skill 的预期集合留给 #39。
- 调用策略在原「yaml 存在」之外，再要求 user-invoked 的 `allow_implicit_invocation: false`。不把 `setup-research-os` 改成 model-invoked；那是 #40，且当前文件已是显式调用。
- 角色表与算力政策只写入口必须遵守的回退规则，不生成项目文件，不实现 setup。

## Deviations

- 链接解析从 `Path.resolve` 改为按路径段拼接。含空格的 worktree 路径会让 `Path` 少算一层 `..`，旧 checker 因此放过 `paper-compile-repair` 的两处 `../../paper-compile/references/diagnostics.md`。该路径从 `skills/writing-cycle/paper-compile-repair/` 会落到不存在的 `skills/paper-compile/`。已改为 `../paper-compile/references/diagnostics.md`，目标仍是原来的 diagnostics 文件，只修正相对路径。
- `.agents/` 被 gitignore。本 notes 用 `git add -f` 纳入提交，否则集成后无法引用共享合同。
