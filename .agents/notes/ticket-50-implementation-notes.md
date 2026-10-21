# Ticket #50 实施记录：迁入 swarm，宿主中立并行覆盖能力

worktree `/Users/rolex/.t3/worktrees/Research OS Studio/t3-b26667a5`，branch `t3/add-swarm-capability`，基线 `integration/spec-48` @ `98e4333`。接续中止的原任务，全部写入留在本 worktree；本次复验期间未触碰主目录与 integration。已合并 `integration/spec-48` @ `e84f779`，并在 `34a374e` 保留 #50 与 #54 两侧成果。

## 状态

| 单元 | 交付目标 | 状态 | 产物 | 验收证据 |
|---|---|---|---|---|
| U1 swarm 能力 | 分片/竞赛/混合、独立 brief、预声明规则、输出隔离、有界重派与缺口 | done | `skills/general/swarm/SKILL.md`（Frame / Fan out / Aggregate / Report） | `tests/test_spec48_ticket50.py::SwarmMechanism`（7 passed） |
| U2 许可与归属 | 上游正文核查、MIT 版权文本随技能共置 | done | `skills/general/swarm/LICENSE`（字节复制自 pstack@88d4751 的 `pstack/LICENSE`，Copyright (c) 2026 Lauren Tan） + SKILL.md「来源与许可」 | `UpstreamAttribution`（2 passed）；LICENSE 为 `cp` 原样复制 |
| U3 宿主中立 | 去 Cursor cloud／固定模型／个人目录绑定；角色表解析；缺子代理 blocked | done | SKILL.md「委托继承」「Phase A/B」 | `HostNeutrality`（3 passed）+ checker 禁词清单（`swarm_contract_problems`） |
| U4 入口发现 | 路由行 + playbook + checker/README/迁移登记 | done | `playbooks/swarm.md`、入口路由表 `swarm` 行、`REQUIRED_RELEASE_ROUTES`、`MIGRATED_CONTRACT`、migration-boundary 表、两份 README 清单 | `EntryDiscovery`（7 passed） |
| U5 安装实测 | 独立安装可读、资源可达 | done | 本文「安装证据」 | 实跑 skills CLI 1.7.4：独立 swarm 安装与 research-os+swarm 组合安装均成功（见下） |

## 逐 AC 证据

1. **上游核查与归属**：逐字读取 `/tmp/research-os-spec48-upstream/.../pstack/skills/swarm/SKILL.md`（2734B 原文）与 `pstack/LICENSE`；LICENSE 原样复制进 `skills/general/swarm/LICENSE`。SKILL.md「来源与许可」记录 repo、revision `88d47514b82e7c44f00f2b2a72ff6dd12158038c`、MIT、作者与改写范围。采用上游归档自述的边界：归属写 `cursor/plugins` 的 `pstack/` @ revision，不写「仓库 MIT」。
2. **机制保留**：四阶段（Frame/Fan out/Aggregate/Report）、分片/竞赛/混合、`first pass`/`rank all`/`best-of` 派发前声明、完成条件先行、每 worker 独立可写输出（输出隔离）、独立 brief；Aggregate：缺 brief 点名证据的结果不算通过 → 有界重派一次 → 二次缺失记缺口；缺口不算通过；掉线记 N-1 继续。测试 `SwarmMechanism` 逐项断言。
3. **宿主中立**：worker 模型按项目角色表 `.agents/research-os-models.md` 的 `implementer` 行解析，缺行沿用当前会话模型并写明；没有固定模型名、`~/.cursor`、`pstack-models`、`environment: "cloud"`、`cloud_base_branch`；无子代理工具时标 blocked，不用编排者串行代跑冒充已执行（沿用 mandate 的子代理前提）。checker 新增 `swarm_contract_problems` 强制这些标记与禁词。
4. **缺证据重派/缺口**：见上；测试断言「重派」「缺口不算通过」与「一次」有界语义。
5. **安装与入口引用**：checker 登记（`MIGRATED_CONTRACT` + 独立检查函数，不动他人断言）、入口 `swarm` 路由行 + `playbooks/swarm.md`、两份 README 清单各加一行、migration-boundary「已迁移」表加一行；安装实测见下。验收范围是结构与可达性，不宣称真实数学求解或全宿主行为。

## 红绿证据

```text
# 原实现记录中的红（本次未独立复现原始中间树，不追认）
# 原 notes 记录：9 failed, 10 errors, 19 items
# 本次独立红：从 34a374e git archive 生成损坏副本，将 swarm 正文的“重派”改为“转交”
$ cd /tmp/spec48-50-verification.uJW75f/damaged
$ uv run --with pytest python -m pytest tests/test_spec48_ticket50.py::SwarmMechanism::test_evidence_absent_result_not_pass_and_bounded_respawn -q
1 failed（预期：缺少重派合同标记） EXIT=1

# 绿（合并后的现工作树）
$ cd '<worktree>'
$ uv run --with pytest python -m pytest tests/test_spec48_ticket50.py -q
19 passed

# 全套（含既有测试）
$ uv run --with pytest python -m pytest tests scripts/test_check_skills_ticket*.py -q
7 failed, 134 passed, 44 subtests passed
```

失败集合与 #49 notes 记录的历史基线**完全一致**（同 7 个测试，均为 9 条 `evidence/*.tar.gz` 历史断链）。唯一中途出现的非历史失败是 `test_check_skills_ticket46.py::test_release_routes_are_complete`，其 `REQUIRED_ROUTES` 固定元组不含新路由，属 spec Testing #7 允许的预期漂移，已按 #49 同款最小编辑加 `("swarm", "—", "no")` 行；未删除他人断言。

```text
$ python3 scripts/check-skills.py
FAIL: 9 个问题   # 与改动前基线相同：9 条历史 tar.gz 断链；本票无新增
```

## 安装证据（可丢弃目录）

```text
$ node /Users/rolex/.npm/_npx/5606f1555d02ef53/node_modules/skills/bin/cli.mjs --version
1.7.4

$ node <CLI> add "<worktree>" -s swarm -a claude-code -y
Found 42 skills → Installed 1 skill → ./.claude/skills/swarm   EXIT=0
  SKILL.md、LICENSE、agents/openai.yaml 均在

$ cd /tmp/spec48-50-verification.uJW75f/combined
$ node <same CLI> add "<worktree>" -s research-os -s swarm -a claude-code -y
EXIT=0；research-os/playbooks/swarm.md、references/mandate.md、swarm/SKILL.md 均可达
```

上述目录为临时可丢弃验收目录；CLI 实际将两技能复制到各自 `.claude/skills/` 下。独立 swarm 安装只验证正文及同目录资源；组合安装验证入口引用的 playbook、mandate 与 swarm 资源可达。本次没有重跑全包 `-s '*'` 安装，也没有声称对所有安装后相对链接逐条解析；旧记录里的 40 技能/链接扫描不作为本次独立证据。

## 合并后复验

本次临时验收目录：`/tmp/spec48-50-verification.uJW75f`。

- 基线现为 `98e4333`；源实现提交 `6c47ecf`，上游 integration 提交 `e84f779`。合并提交 `34a374e` 两父分别为 swarm 提交与最新 integration tip；`git merge-base --is-ancestor integration/spec-48 HEAD` 退出码 0。工作树无未提交改动。
- `git diff --check 98e4333..HEAD` 通过；未改动 #54 整合带入的文件。
- 合并后定向测试 19 passed。全套 7 failed / 134 passed / 44 subtests passed，失败集合逐条对应 #49 notes 的七个 checker 受历史 tar.gz 断链影响的既存失败；checker 仍报同 9 条，不屏蔽。
```

## 决策

1. **目录落位 `skills/general/swarm`**：swarm 是编排能力，与入口同属 general；不建占位分类。
2. **worker 角色复用既有 `implementer` 行**：项目角色表是 checker `ROLES` 固定集合，新增角色会牵动共享合同测试；swarm 是执行类并行，`implementer` 语义吻合。角色行缺失时回退当前会话模型并写明（YAGNI：不引入新角色或默认模型常量）。
3. **合同用「委托继承」单小节，不跨 skill 链接 mandate.md**：与 research-lit 同款，保证扁平/独立安装时正文自足（归档 README 的引用闭合检查也确认上游同类文件无跨文件硬依赖）。
4. **checker 为本票新增独立 `swarm_contract_problems`**：只追加函数与一处调用，不改既有检查；禁词清单是具体绑定形态（`~/.cursor`、`pstack-models`、`grok-4.7`、`environment: "cloud"`、`cloud_base_branch`），不含裸 "cursor"，因为归属段合法出现 `cursor/plugins`。
5. **无上游原样复制正文**：SKILL.md 是改写（宿主中立化、委托合同衔接、重派/缺口合同），骨架与上游一致；机制要点逐条对照过原文。
6. **恢复对正文检查器的“重派”标记**：复验发现本地 Skill 编辑器曾自动将正文中的“重派”规范化成“转交”，导致本票定向测试中 1 项失败；把本票两处标记恢复为 “重派” 后单测复绿，符合已有 checker/test 合同，无需扩展测试或改变实际语义。

## 限制 / 未完成

- 静态合同与安装可达性已验；「模型会按 swarm 正文正确派发真实子代理」「竞赛规则在真实会话中被遵守」未验证，属宿主交互与真实科研验收，不在本票宣称。
- `HostNeutrality` 禁词是结构检查；不证明任何宿主运行时行为。
- 历史 9 条 evidence 断链未修（按设计不入库），未屏蔽。
- 无 push / PR / issue 写入；worktree 保留。
