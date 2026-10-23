# #51 arena 迁入实现笔记

## 状态区

| 单元 | 状态 | 产物/证据 | 下一步 |
|---|---|---|---|
| 读取合同材料与上游 arena 原文 | done | 本记录「来源亲核」节 | 无 |
| 测试先红 | done | 红例：14 failed / 1 passed（见「红绿证据」） | 无 |
| arena 能力实现 | done | `skills/organization/arena/{SKILL.md,LICENSE,agents/openai.yaml}`；授权范围补足见当前提交 | 无 |
| 入口指针 + README 清单/徽章 + checker 登记/迁移边界 | done | `skills/general/research-os/SKILL.md`、`README.md`、`skills/README.md`、`scripts/check-skills.py`、`references/migration-boundary.md` | 无 |
| 定向/全套 pytest、静态合同与安装实证 | done | `.agents/notes/ticket51-evidence/{targeted-final,suite-final,checker-final,ruff-final,diff-check-final,install-arena-delivery,install-suite-delivery}.txt` 与各安装 diff（ignored）；独立首轮审查有 findings，第二轮因上游 503 失败 | 无 |
| 提交 + merge integration tip 复验（原阶段） | done | 原实现 `b17297d`、双方登记 merge `81cc259`、范围/README/回归修复 `d3ca46d`；当时合入 `e84f779` 后定向测试/lint/checker/diff/status 复验 | 本轮继续验收最新本地 tip `b0d8ead`
| F1 数量门修正、F2 授权偏离记录、Ruff 新告警清理与最终合并复验 | done | 2026-10-22 最终复验见文末；merge commit `1006d9e4` 合入 `b0d8ead` | 无

## 来源亲核（许可与资源）

- 上游 arena 原文：`/tmp/research-os-spec48-upstream/pstack@88d47514b82e7c44f00f2b2a72ff6dd12158038c/pstack/skills/arena/SKILL.md`（4511B 单文件）已全文读过。机制：todolist 六阶段 Frame / Fan-out / Cross-judge / Pick / Graft / Verify + Outputs；候选同 prompt、先定 rubric、输出隔离、dropout 记录、只读交叉评判、主编排者完整阅读逐项对比、手工 graft、验证兜底。
- 许可：`pstack/LICENSE` = MIT，Copyright (c) 2026 Lauren Tan。arena 目录仅 `.md`，无独立子资产许可。`skills/organization/arena/LICENSE` 为字节级拷贝（SHA256 `bc957ca6…` 与上游一致）。SKILL.md 末「来源与许可」节写明 `cursor/plugins` 的 `pstack/` @ `88d47514b82e7c44f00f2b2a72ff6dd12158038c`，不写「仓库 MIT」（上游 README 第 2 条）。
- 上游宿主绑定项已适配移除：`~/.cursor/rules/pstack-models.mdc`、固定 slug（claude-opus-5-5-xhigh / grok-4.7-xhigh-fast）、家族前缀映射、poteto-mode / principle skills 引用、`/tmp/arena-<slug>` 个人示例路径。

## 适配决策

- 落位 `skills/organization/arena/`（新分类 organization；#50 swarm 未实现，arena 不引用它，checker 禁 swarm 字样）。
- 迁移状态：`MIGRATED_CONTRACT` 登记 + SKILL.md「委托继承」小节 + `migration-boundary.md` 表加行；arena 编排强依赖子代理前提，mandate「权限·子代理前提」正是该语义；缺子代理标 blocked，不串行代跑。
- 模型选择按项目角色表（`.agents/research-os-models.md` Role 行）或当前会话实际能力解析，明示回退，不固定品牌。
- 数学整合：Graft 后整体重查假设/记号/依赖闭合；「候选胜出不等于命题成立」独立小节；Verify 区分已验证/未验证。
- 入口发现：匹配节加 arena markdown 指针（`../../organization/arena/SKILL.md`），不加路由行（无 playbook 文件，不改 REQUIRED_RELEASE_ROUTES / RELEASE 路由合同）。
- checker 新增仅本票的独立检查：`arena_contract_problems`（六阶段保真 + 无上游宿主绑定残留 + 不引用 swarm）；另有 MIGRATED_CONTRACT/边界表登记（复用既有机制）。

## 红绿证据

- 红（实现前）：原笔记记录 `uv run --offline --no-project python -m pytest tests/test_spec48_ticket51.py -q` 为 **14 failed, 1 passed**；当前 worktree 的 uv cache 已不含 pytest，显式 `uv run --no-project --with pytest python -m pytest ...` 已实测可用。
- 初始交付实证（历史记录）：15 passed；合并后定向 **46 passed, 2 subtests passed**。现状定向重验 **17 passed**，增加了独立调用范围、关键 phase 合同及 README 计数反例。
- 上一轮全套重验（旧树，非本次最终 merge tip）：**7 failed, 132 passed, 44 subtests passed**。当时 7 项均由既存 `docs/acceptance` evidence tarball 断链导致 checker 非零引发；本轮未在整合 tip 重跑全套，不把旧树结果冒称为当前通过。
- checker 在上一轮及本次最终树均 exit 1，输出 9 条既存 `docs/acceptance` evidence tarball 断链；本轮定向合同测试将这些历史问题排除后通过。尚未证明全仓库 checker 全绿。
- 上一轮静态记录：Ruff 新增告警已从 12 项降到 8 项；本次最终树复验见文末，`tests/test_spec48_ticket51.py` 单独 Ruff 通过，checker 文件的 8 项为已有基线告警。历史记录路径 `ruff-final.txt`、`diff-check-final.txt` 与 `checker-delivered.txt`。

## 安装实证

使用缓存 CLI `/Users/rolex/.npm/_npx/5606f1555d02ef53/node_modules/skills/bin/cli.mjs`（skills 1.7.4），在 `.agents/notes/ticket51-evidence/` 可丢弃目录：

- `add <worktree> -s arena -a claude-code -y` → exit 0；`.claude/skills/arena` 与源目录 `diff -r` 完全一致（SKILL.md/LICENSE/agents/openai.yaml）。
- 原实现实证：缓存 CLI `skills@1.7.4` 对 arena 单项及当时 40 项全集安装均 exit 0；修改前的历史日志 `install-arena-selected.txt`、`install-arena-all.txt` 保留在 ignored evidence 目录。用户全局安装未触碰。
- 上一轮最终修订后复验：arena 单项安装 exit 0，42 项完整套件安装 exit 0；这是旧树历史证据，不表示最新整合树仍有 42 项。

## 过程坑（供下一次尝试）

1. 红绿测试的副本若放在仓库内且 `TMPDIR` 指向仓库内，`copytree` 会自包含递归（路径爆炸、超时）。修复：ignore `ticket51-tmp`，副本用系统临时目录。
2. 副本 `git init` 后 `.git` 对象只读，`shutil.rmtree` 需 onexc chmod 重试。
3. pytest 无 `--timeout` 插件，慢因是上面的递归复制，不是测试本身。
4. merge integration tip 时 `MIGRATED_CONTRACT` 与边界表与 #54（形式化验证两技能）文本冲突，按并集解决，双方登记都保留。

## Deviations

- 测试 `test_orchestrator_synthesizes_not_mechanical` 最初只断言词面（「综合」「逐项」），属弱合同；机制保真由 checker 的六阶段检查 + 人工对照上游原文补足。保留词面断言为最低门，未升级为语义检查（静态合同边界，spec Testing Decisions 2/7 允许）。
- 入口未加路由表行：路由行合同要求 playbook 文件；本票范围不含 playbook，改用匹配节指针，发现性由测试与 checker 链接检查保证。

### F2：授权偏离（未追认）

- 原实现 brief 明确写明“你是Spec#48单票实现worker，不继续派发”。恢复用的 r3-luna prompt 声称重述完整原范围，却遗漏了这一禁令；遗漏不是撤销，也没有明确授权继续派发。
- 尽管如此，r3-luna 实现 thread 实际创建了两轮子审查：`review-luna-r1` 已完成，`review-luna-r2` 失败。依据原始禁令，两轮派发均属未授权偏离；本记录和后续修正均不追认授权。第二轮保持 failed，不计作通过；第一轮的意见仅作为历史线索，当前修正以规格及可复验测试为依据。
- 原 brief、恢复 prompt、父子 thread ID、时间和核查限制见 `/tmp/research-os-spec48-ticket51-review/orchestration-evidence.md`。该证据说明发生了什么，不把未读取的旧审查正文补写为已验收。

### F1：移除数量硬门，保留清单集合校验

- Spec #48 Implementation Decision 17 要求删除固定数量断言；Testing Decision 2 禁止以文件数量/特定措辞作为行为正确性证明。checker 继续逐项比较 README 中链接的 Skill 集合与实际 `SKILL.md` 路径集合，只删除数字徽章/标题必须存在且匹配库存的门。
- 先以 count-free README 反例复现拒绝（原始数量门产生两条诊断），再移除数量门；`test_count_free_readme_manifest_is_accepted` 与清单缺项负例现各自通过。删除 42→39 的徽章损坏测试，改为删除 arena 清单行，避免固定库存数并确保集合检查仍能发现漏项。
- Ruff 0.17.1 原报告 12 项中，本票新增的 checker `FURB167`、测试 `FURB167`、`I001` 与 `PLW1510` 均已消除；当前余下 8 项与基线相同，未扩大 lint 范围去改写既有 checker 代码。

## 独立审查与修正（历史记录）

本节只记载先前发生的事实；上方 F2 已校正其授权状态，不能把两轮派发视为获准或将其结果计作授权证明。第二轮因 luna provider `auth_unavailable / empty_stream` 503 失败，保持 failed，不计作通过。

只读审查代理（luna6 xhigh）当时指出三项缺口：独立调用引用了不存在的「范围」小节；README 徽章/标题数量过期；关键机制回归合同主要靠宽泛词面断言。早期曾临时同步 README 数量，后续 F1 复核确认不应把数量化表达立为门槛，最终移除 README 数字表达。独立调用范围与 arena 关键机制合同另有修正。第 2 轮因 luna 上游 empty_stream 返回 503 未完成；此失败是 review 通道故障，不记作通过审查，也不是产品失败。原审查发现的是文档边界与回归覆盖不足，不证明数学科研质量。

## 2026-10-22 收尾验收

- 入口判定：这是单票 agent 指令、脚本与合同测试实现；用户明确禁止继续派发，因此当前 worker 直接执行 F1/F2/lint 收尾，不拆分、不创建子任务。`writing-for-agents`、`pre-implement` 与 TDD 的 `SKILL.md` 在本机已配置 skill 根目录中均不存在，无法加载；不将未加载技能描述为已遵循。
- Git-only 整合：进入时工作区 index 有 67 个 staged 路径、无 unmerged path，但实际 `.git/MERGE_HEAD` 不存在。逐项核对 index 与 `integration/spec-48`：除 #51 的 10 个文件外，staged tree 与 integration tip 一致；四个自动合并冲突的人工并集保留 arena 登记/入口/README/ checker 机制且不覆盖其它票内容。用已核对 tree `c3bb2f3e` 形成双父 merge commit `1006d9e4`（parents：`5e8b255`、`b0d8ead`）；未 reset/clean、未改主目录或 integration。
- F1 最终行为：README badge、目录锚点/标题及介绍已去掉 Skill 数量；checker 不再要求数字表达或固定库存数，只校验清单中 Skill 路径集合与实际 `SKILL.md` 路径集合相等。正例 `test_count_free_readme_manifest_is_accepted` 在不删清单项的 count-free README 上要求 checker 无新增问题；反例 `test_missing_skill_from_readme_manifest_is_red` 删除 arena 清单行并要求 checker 报清单缺项，未使用 `42→39` 数值反例。
- F2：本次不追认旧实现两轮子派发。原禁止派发、恢复 brief 漏项、两轮 ID/状态与第二轮 503 failed 已如实记于上方 F2；第二轮不计通过，详见 `/tmp/research-os-spec48-ticket51-review/orchestration-evidence.md`。
- 测试：`uv run --no-project --with pytest --with pytest-subtests python -m pytest -q tests/test_spec48_ticket51.py` → **18 passed, 2 subtests passed**（最终 README 修改后重跑）。`uv run --no-project python scripts/check-skills.py` → exit 1，仍为 9 条缺失的历史 `docs/acceptance/*.tar.gz` 链接，不属于 #51 新增问题；全仓库 pytest 未在此 merge tip 重跑。
- Ruff：`ruff==0.17.1` 对 `tests/test_spec48_ticket51.py` → clean；对 `scripts/check-skills.py` → 8 个已有基线告警（EXE001、5×FURB167、SIM102、FURB162），与既有基线同数。本票此前新引入的 FURB167 / I001 / PLW1510 已清除；不为清除无关旧告警扩大 checker 重构范围。
- 通用 CLI 实证：实际调用缓存 `skills@1.7.4` 对本 worktree 执行 `add <source> -s arena -a claude-code -y`，Found 46 skills、Installed 1 arena；安装副本有 3 个文件，`diff -r` exit 0。隔离项目路径：`/tmp/research-os-spec48-ticket51-cli-BJLEbu/project/.claude/skills/arena`。未触碰用户全局安装。
- 限制：安装只证明 arena 单项可由通用 CLI 安装且文件精确；未在最新整合 tip 重跑全套安装、全仓库 pytest，亦不证明真实数学研究正确性或所有宿主交互。

## 边界

只证明安装结构合同与机制保真对照：不冒称 arena 能产出真实科研/数学正确结果，不宣称全宿主交互验收（仅 Claude Code 安装实证），未 push / PR / issue / 清理 worktree。原始红绿历史只引用已有笔记，不声称本轮重放或恢复了原实现前红态。
