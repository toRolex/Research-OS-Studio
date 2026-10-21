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
| F1 数量门修正、F2 授权偏离记录、Ruff 新告警清理与最终合并复验 | 进行中 | `tests/test_spec48_ticket51.py` 18 passed / 2 subtests passed；Ruff 0.17.1 从 12 项降至与基线相同的 8 项；checker 仍精确 9 项且与基线输出无 diff | 合并 `integration/spec-48` 最新 tip 后复验全套失败名、checker 9 项及逐 AC 证据，再提交

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
- 当前全套重验：**7 failed, 132 passed, 44 subtests passed**。7 项均是既存 `docs/acceptance` evidence tarball 断链导致 checker 非零引发；与 merge 前 `suite-postmerge.txt` 的失败测试逐名一致，新增两项本票测试通过。未屏蔽历史失败，也未将完整测试称为全绿。
- checker 当前 exit 1，输出仍恰为 9 条历史 `docs/acceptance` 断链；与 merge 前 `checker-postmerge.txt` 逐字 diff 为空。arena 阶段、README 计数与迁移登记检查均无新增问题。
- 静态：`uv run --no-project ruff check tests/test_spec48_ticket51.py scripts/check-skills.py` 与 `git diff --check` 均通过；提交 `d3ca46d` 后复跑定向测试 17 passed、ruff 通过、checker 仍只有 9 条历史断链、`git diff --check HEAD^ HEAD` 通过，worktree 干净。证据 `ruff-final.txt`、`diff-check-final.txt` 与 `checker-delivered.txt`。

## 安装实证

使用缓存 CLI `/Users/rolex/.npm/_npx/5606f1555d02ef53/node_modules/skills/bin/cli.mjs`（skills 1.7.4），在 `.agents/notes/ticket51-evidence/` 可丢弃目录：

- `add <worktree> -s arena -a claude-code -y` → exit 0；`.claude/skills/arena` 与源目录 `diff -r` 完全一致（SKILL.md/LICENSE/agents/openai.yaml）。
- 原实现实证：缓存 CLI `skills@1.7.4` 对 arena 单项及当时 40 项全集安装均 exit 0；修改前的历史日志 `install-arena-selected.txt`、`install-arena-all.txt` 保留在 ignored evidence 目录。用户全局安装未触碰。
- 当前最终修订后复验：arena 单项安装 exit 0，隔离临时项目中的安装副本与源目录 `diff -r` 为空；42 项完整套件安装 exit 0，输出确认 `Found 42 / Installing all 42 / Installed 42`，实际 42 个安装 Skill，安装后的 arena 与源目录精确一致。证据：`install-arena-delivery.txt`、`install-arena-delivery-diff.txt`、`install-suite-delivery.txt`、`install-suite-delivery-diff.txt`；旧套件日志只证明发现/安装清单，未用于声称逐字匹配。

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

## 独立审查与修正

本节只记载先前发生的事实；上方 F2 已校正其授权状态，不能把两轮派发视为获准或将其结果计作授权证明。第二轮因 luna provider `auth_unavailable / empty_stream` 503 失败，保持 failed，不计作通过。

只读审查代理（luna6 xhigh）指出三项具体缺口：独立调用引用了不存在的「范围」小节；README 徽章/标题仍标 39，当前目录含 42 Skill；关键机制回归合同主要靠宽泛词面断言。主 agent 复核后已修正：独立调用现直接定义授权范围、默认两候选以及何时增加数量，工作区输出不覆盖既有材料；README 徽章/标题、目录锚点同步为 42；checker 与 pytest 增加实际数量一致检查、rubric 必须在 fan-out 前、候选完整阅读/隔离、逐项比较/非机械 graft、数学整合重查、授权范围和 stale badge 负例。新增测试初次执行时意外捕获断言放错段落；按真实 phase 调整断言后测试通过。第 2 轮因 luna 上游 empty_stream 返回 503 未完成；此失败是 review 通道故障，不记作通过审查，也不是产品失败。原始独立审查未发现正文机制缺失，发现的是文档边界与回归覆盖不足。

## 边界

只证明安装结构合同与机制保真对照：不冒称 arena 能产出真实科研/数学正确结果，不宣称全宿主交互验收（仅 Claude Code 安装实证），未 push / PR / issue / 清理 worktree。原始红绿历史只引用已有笔记，不声称本轮重放或恢复了原实现前红态。
