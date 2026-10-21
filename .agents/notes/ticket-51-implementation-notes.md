# #51 arena 迁入实现笔记

## 状态区

| 单元 | 状态 | 产物/证据 | 下一步 |
|---|---|---|---|
| 读取合同材料与上游 arena 原文 | done | 本记录「来源亲核」节 | 无 |
| 测试先红 | done | 红例：14 failed / 1 passed（见「红绿证据」） | 无 |
| arena 能力实现 | done | `skills/organization/arena/{SKILL.md,LICENSE,agents/openai.yaml}` | 无 |
| 入口指针 + 两 README 清单 + checker 登记/迁移边界 | done | `skills/general/research-os/SKILL.md`、`README.md`、`skills/README.md`、`scripts/check-skills.py`、`references/migration-boundary.md` | 无 |
| 离线 pytest + checker diff + 安装实证 | done | `.agents/notes/ticket51-evidence/`（ignored） | 无 |
| 提交 + merge integration tip 复验 | done | commit `b17297d` + merge `81cc259`（基 e84f779） | 交回 parent |

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

- 红（实现前）：`uv run --offline --no-project python -m pytest tests/test_spec48_ticket51.py -q` → **14 failed, 1 passed**（唯一通过项为当时尚无新增回归的 checker 检查）。
- 绿（实现后）：15 passed；ticket49 定向 **31 passed, 2 subtests passed** 不变；合并后定向 **46 passed, 2 subtests passed**。
- 全套：候选/合并后均 **7 failed, 130 passed**（候选时 105 passed），7 个失败与 #49 记录的历史集合逐名一致（evidence tarball 断链所致 checker 非零连带），无新增回归。
- checker：exit 1，输出恰为 9 条历史 `docs/acceptance` 断链；candidate 与 postmerge 输出逐字 diff 为空。

## 安装实证

使用缓存 CLI `/Users/rolex/.npm/_npx/5606f1555d02ef53/node_modules/skills/bin/cli.mjs`（skills 1.7.4），在 `.agents/notes/ticket51-evidence/` 可丢弃目录：

- `add <worktree> -s arena -a claude-code -y` → exit 0；`.claude/skills/arena` 与源目录 `diff -r` 完全一致（SKILL.md/LICENSE/agents/openai.yaml）。
- `add <worktree> -s '*' -a claude-code -y` → exit 0，39 个 skill 含 arena，arena 副本仍逐字一致。
- 证据：`install-arena-selected.txt`、`install-arena-all.txt`。用户全局安装未触碰。

## 过程坑（供下一次尝试）

1. 红绿测试的副本若放在仓库内且 `TMPDIR` 指向仓库内，`copytree` 会自包含递归（路径爆炸、超时）。修复：ignore `ticket51-tmp`，副本用系统临时目录。
2. 副本 `git init` 后 `.git` 对象只读，`shutil.rmtree` 需 onexc chmod 重试。
3. pytest 无 `--timeout` 插件，慢因是上面的递归复制，不是测试本身。
4. merge integration tip 时 `MIGRATED_CONTRACT` 与边界表与 #54（形式化验证两技能）文本冲突，按并集解决，双方登记都保留。

## Deviations

- 测试 `test_orchestrator_synthesizes_not_mechanical` 最初只断言词面（「综合」「逐项」），属弱合同；机制保真由 checker 的六阶段检查 + 人工对照上游原文补足。保留词面断言为最低门，未升级为语义检查（静态合同边界，spec Testing Decisions 2/7 允许）。
- 入口未加路由表行：路由行合同要求 playbook 文件；本票范围不含 playbook，改用匹配节指针，发现性由测试与 checker 链接检查保证。

## 边界

只证明安装结构合同与机制保真对照：不冒称 arena 能产出真实科研/数学正确结果，不宣称全宿主交互验收（仅 claude-code 限定安装实证），未 push / PR / issue / 清理 worktree。
