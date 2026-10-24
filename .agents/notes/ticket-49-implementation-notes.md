# Ticket #49 实施记录：研究委托合同 + 最小单入口

Spec #48 / Ticket #49。worktree `/Users/rolex/.t3/worktrees/Research OS Studio/t3-c5be9381`，基线 `integration/spec-48` @ `bce31c1`（本地 tip 未再前进；远端没有 `integration/spec-48` 引用，故「最新 tip」即该提交，merge 报 already up to date）。分支初始由 T3 分配为 `t3/c5be9381`，2026-10-20 22:48 由宿主自动改名为 `t3/implement-ticket-49`（reflog: `Branch: renamed refs/heads/t3/c5be9381 to refs/heads/t3/implement-ticket-49`），提交在该分支上，未推送。

## 状态

2026-10-24按本记录当时收束阶段补记下一步列；前五列和历史正文不变，不以当前产品状态重写当时结果。

| 单元 | 交付目标 | 状态 | 产物 | 验收证据 | 当时下一步 / 阻塞 |
|---|---|---|---|---|---|
| U1 委托合同 | 目标／权限／额度／完成停止语义单一权威 | done | `skills/general/research-os/references/mandate.md` | `tests/test_spec48_ticket49.py::ContractText`（3 passed） | 无（本票合同范围）；词汇/ADR提交决定见下文上位事项 |
| U2 迁移边界 | expand 迁移集与未迁移旧基线并存，不宣称全叶统一 | done | `skills/general/research-os/references/migration-boundary.md` + `MIGRATED_CONTRACT` / `LEGACY_LEAF_GATES` | `MigrationBoundary`（3 passed）、`CounterRelationship::test_*_is_red`（3 个损坏用例） | 后票继续迁移，不外推全叶已统一 |
| U3 完整路径 | 入口 → research-lit → 结果验收 | done | `playbooks/literature-review.md` + 路由行 `literature` + `research-lit` 的「委托继承」 | `CompletePath`（2 passed）、`FlatInstall`（2 passed） | 无（本票路径/安装范围） |
| U4 checker 迁移 | 去固定数量、显式迁移集、保留旧门与引用完整性 | done | `scripts/check-skills.py` | `CounterRelationship`（6 passed，含 2 个新增红用例） | README等数量/终态统一留#60；保留正文历史边界 |
| U5 安装实测 | 可丢弃目录安装入口与代表能力，资源可达 | done | 本文「安装证据」 | 实跑 `npx skills@latest add`（见下） | 无（安装可达范围）；真实研究/宿主行为未验证 |

## 决策

1. **合同单点 + 叶内自包含继承**：完整委托语义只写在 `references/mandate.md`；已迁移叶不再复制全文，只带一段「委托继承」。原因是 `research-lit` 声明可单独调用，扁平单独安装时跨 Skill 文件指针会断（spec Testing #3 要求独立安装可解析）。因此叶的继承条款写成自足的一小段，合同本体由调用者持有。
2. **数量改为关系，不换新常数**：删除 `EXPECTED_COUNT = 39`，改由「实际发现的 `skills/*/*/SKILL.md` == `README.md` 与 `skills/README.md` 清单」+「skill 目录必须有 SKILL.md」保证。新增/迁移 Skill 不再需要改常数，只同步清单与门基线。没有引入 `>=N`、分类计数或新固定数字。
3. **显式迁移集，不全局抹旧门**：`MIGRATED_CONTRACT`（路径 → 必须存在的合同小节）与 `LEGACY_LEAF_GATES`（原 37 条减去 research-lit）互斥。已迁移：`Gates: none` + 合同小节；未迁移：逐条保留 `Gate: … | approval=explicit-user` 基线。未登记的门声明仍报错，避免新 Skill 静默逃检。
4. **门基线解析收敛到一个函数**：`expected_gates()` 统一 setup／入口／已迁移／未迁移四种来源，`check_gates()`（`--gates-dir` 外部合同入口）与仓库扫描共用，避免两份查表逻辑漂移。
5. **迁移边界必须可对照**：`migration_boundary_problems` 检查合同四小节（目标／权限／研究额度／完成与停止）、入口指向合同、每个已迁移技能有合同小节、边界文档含「未迁移」小节并点名 `LEGACY_LEAF_GATES` 为权威且列出每个已迁移技能。删门不能连职责约束一起删。
6. **最小完整链路选 literature**：`literature` 路由 + `playbooks/literature-review.md` 走完「委托核对 → 读叶正文 → 执行 → 按实际产物验收 → 收束交付」，叶侧用已有 `research-lit`（有独立预算、来源核实、模板与报告契约），不牵入数学／远程／写作实现。`REQUIRED_RELEASE_ROUTES` 增加该行，路由成套性检查覆盖新路径。
7. **custom 不再等批准**：委托已含授权时，`playbooks/custom.md` 直接开始其中不需越权/超额/破坏性授权的那部分，只在那一步停。否则「无匹配路线」会成为委托语义的例外洞。
8. **宿主映射不再以串行代跑冒充委托**（初版遗留，已在下一节定向修复解决）：初版 `host_fallback_problems` 要求「无子代理时编排者串行执行」，与 spec ID16 冲突，已改为能力前提 + blocked 语义。

## Deviations

1. **改了别票的旧测试断言（两处，最小编辑）**：`tests/test_check_skills_policy_gates.py` 删掉 `research-lit` 的旧门期望（其门已按本票迁移）；`scripts/test_check_skills_ticket46.py` 的 `REQUIRED_ROUTES` 增加 `literature` 行、方法名去掉「fourteen」。理由：spec Testing #7 要求更新与旧产品冲突的断言；新增路由与迁移必然使这两处旧期望为假。其余测试文件未触碰。
2. **未迁移 `pickup`／`PHASE-BOUNDARIES.md`／`proof.md`／`idea-discovery` 的停点语义**：这些属于后续 #58/#59 的配方与恢复范围。本票只改入口契约、custom、research-lit 与新链路，边界已写进 `migration-boundary.md`，不宣称它们已统一。
3. **未提交 `GLOSSARY.md` / `docs/adr/0006–0008` / `docs/design` / `docs/planning`**：这些是用户工作区未提交背景（领域词汇与 ADR），按派发约束不擅自搬入产品。因此本票的新术语（研究委托／研究额度／目标替换）只存在于 Skill 正文，根 `GLOSSARY.md` 未同步 —— 需用户决定是否随新合同提交这些背景资产（原索引 D1）。
4. **README 里的 `39`（badge / 目录标题 / 「全套包含 39 个独立技能」）未改**：本票不增删 Skill，数字仍为真；checker 已不再依赖它。逐处数字与英文 README、`docs/user-acceptance-guide.md`、`docs/atomic-switch-manifest.md` 的统一属 #60 终态同步。
5. **未改 `STALE_PROMISE_SNIPPETS` / `REQUIRED_RELEASE_ROUTES` 之外的旧承诺词表**：旧承诺 sweep 仍是 #58/#60 的范围；本票新增文本不含旧承诺片段。

## 执行与红绿证据

所有命令在 worktree 根目录执行。

```text
# 基线（改动前，干净 worktree bce31c1）
$ python3 scripts/check-skills.py
FAIL: 9 个问题
  - docs/acceptance/…: 链接目标不存在或未追踪: evidence/*.tar.gz   （9 条，均为 .gitignore:44 造成的历史断链）
EXIT=0（脚本自身未崩，问题而非异常）

$ uv run --with pytest python -m pytest tests scripts/test_check_skills_ticket*.py -q
7 failed, 67 passed, 44 subtests passed

# 红：先写 tests/test_spec48_ticket49.py
$ uv run --with pytest python -m pytest tests/test_spec48_ticket49.py -q
13 failed, 4 passed     （失败均为合同/路径/迁移集尚不存在；4 个通过项是"既有行为必须保留"的守卫）

# 绿：实现后
$ uv run --with pytest python -m pytest tests/test_spec48_ticket49.py -q
17 passed

$ uv run --with pytest python -m pytest tests scripts/test_check_skills_ticket*.py -q
7 failed, 84 passed, 44 subtests passed
```

失败集合与基线**完全一致**（同一 7 个测试，均因上述 9 条历史断链导致 checker 退出码非 0）：

```
tests/test_check_skills_policy_gates.py::PolicyAndGates::test_checker_green_and_leaf_baseline
tests/test_config_contract.py::ConfigContractTests::test_gate_baseline_and_counterexamples
tests/test_config_contract.py::ConfigContractTests::test_shipped_templates_and_full_checker
tests/test_config_contract.py::ConfigContractTests::test_valid_policy_and_log_fields
tests/test_config_contract.py::ConfigContractTests::test_valid_role_table
tests/test_final_contract_fixes.py::FinalContracts::test_full_cli_damaged_declarations_refs_and_readme
tests/test_review_fixes.py::ReviewFixes::test_compute_limits_are_per_unit_not_summed
```

本票未修这 9 条断链（它们指向的 tarball 按设计不入库），也未把 checker 说成全绿；`test_current_tree_has_no_new_breakage` 只允许这一组历史失败继续存在。

## 安装证据（可丢弃目录）

```text
$ cd /tmp/spec48-49-install
$ npx --yes skills@latest add "<worktree>" --list
◇ Found 39 skills          # 发现数量来自仓库实际内容，不再是代码常数
EXIT=0

$ npx --yes skills@latest add "<worktree>" -s research-os -s research-lit -a claude-code -y
Installed 2 skills → ./.claude/skills/research-os, ./.claude/skills/research-lit
EXIT=0
  research-os/references/{mandate.md,migration-boundary.md,PRODUCT-MAP.md,…}   可达
  research-os/playbooks/literature-review.md                                   可达
  research-lit/references/{source-methods.md,source-verification.md}           可达
  research-lit/templates/literature-report.md                                  可达
  两个已安装副本内相对链接断链 = 0（脚本逐条 resolve）

$ cd /tmp/spec48-49-install-all
$ npx --yes skills@latest add "<worktree>" -s '*' -a claude-code -y
39 skills installed → ./.claude/skills/*
  research-os/references/mandate.md 可达；research-lit/references/source-verification.md 可达
  全包扁平安装的跨 Skill 相对链接断链 = 20 条，全部位于未改动的既有 Skill
  （research-improvement 13 条、paper-writing/ml-/systems-paper-writing 的 composition-map 4 条、
   setup-research-os/templates/workspace.md 的 3 条 `<占位符>` 行文）
```

即：本票迁移面（research-os + research-lit）在扁平安装下自足；全包 20 条跨目录链接是既有安装语义问题（README 已记录 Level 1/2/3 差异），非本票回归，留给 #60 的整包安装验收。

## 给后续 9 票的可引用路径

- 合同语义（目标／权限／额度／完成停止／验收）：`skills/general/research-os/references/mandate.md`
- 迁移登记（代码）：`scripts/check-skills.py` 的 `MIGRATED_CONTRACT`（路径 → 必须存在的合同小节）与 `LEGACY_LEAF_GATES`
- 迁移登记（文档，必须同步）：`skills/general/research-os/references/migration-boundary.md` 的「已迁移」表
- 迁移一个能力的动作清单：`migration-boundary.md`「已迁移」段落后一段
- 完整链路模板（新增能力可照抄结构）：`skills/general/research-os/playbooks/literature-review.md`
- 新路由登记点：入口路由表行 + `REQUIRED_RELEASE_ROUTES` + `scripts/test_check_skills_ticket46.py::REQUIRED_ROUTES`

## 未完成 / 需上位决定

1. 根 `GLOSSARY.md` 与 ADR 0006–0008 仍未提交（用户背景资产），新术语暂无领域词汇真源；是否随合同提交由用户定。
2. ~~`host_fallback_problems` 与 spec ID16 的张力未解~~ → 已在「定向修复」一节解决（缺宿主子代理时统一入口与新路径如实 blocked，不伪称委托已执行）。
3. README／英文 README／验收指南／`atomic-switch-manifest.md` 的 `39` 数字与终态措辞待 #60 统一。
4. 本票只做静态合同检查与安装可达性；「模型会用委托语义正确推进真实研究」未验证，也不据此宣称科研质量。

## 定向修复：缺宿主子代理如实 blocked（spec ID16）

复核发现新链路把「无子代理」写成编排者串行代跑同一合同，与本票自己的验收前提冲突：spec ID16 规定 subagent 是支持前提，不引入无子代理的伪独立降级。初版把它记为 #60 待办（原 Deviations 8），实际属于本票「统一入口 + 完整路径」的语义，因此就地修正。

### 决定

1. **能力前提，按能力判定**：是否有子代理工具按当前会话实际可调用的工具判定，不按宿主品牌推定；`host_fallback_problems` 更名为 `host_capability_problems`，不再要求点名三个品牌，改为要求能力前提 + `blocked` + 独立调用边界，并把串行代跑原文列为红。
2. **缺能力即 blocked，不串行代跑**：入口与新 literature 路径在需要分派的那一步标 `blocked` 并写明缺宿主子代理能力；只读建议（当前路线、下一步、可直接点名哪个能力）仍可给，但不得记成委托已执行。
3. **保留底层单能力的真实边界**：用户直接点名 `research-lit` 等叶完成那一件事仍是能力本身的用途，不是入口的降级模式；不在这一点上把独立调用一起禁掉。
4. **完成 ≠ 用户叫停**：`mandate.md` 把「用户叫停」从完成移到停止，并单列一条说明它是停止而非目标达成；literature playbook 的停止行同步加入 blocked。
5. **顺手同步一处活文档**：`docs/user-acceptance-guide.md` 第 13 行原本写着「无子代理时编排者按 playbook 顺序自己做」，是同一旧语义的用户可见清单，按最小编辑改为能力门表述；`docs/acceptance/**` 历史验收记录未改。

### 改动清单

- `skills/general/research-os/SKILL.md`：宿主映射两处委派列去掉串行降级、补能力门段落；模型段去掉「请求串行回退」「串行完成可执行阶段」；级联段无子代理时改标 blocked。
- `skills/general/research-os/playbooks/literature-review.md`：步骤 3 与停止行。
- `skills/general/research-os/references/mandate.md`：权限段新增「子代理前提」；完成与停止段重排 + 新增「用户叫停是停止」。
- `scripts/check-skills.py`：`HOST_PREREQUISITE_MARKERS` / `HOST_SERIAL_SUBSTITUTES` / `host_capability_problems`。
- `tests/test_spec48_ticket49.py`：新增 `NoSubagentCapability`（4 例）与 `test_mandate_counts_user_stop_as_stop_not_completion`；`test_entry_points_at_mandate_and_keeps_readonly_and_host_map` 的保留短语由串行降级换成 `blocked`。
- `scripts/test_check_skills_ticket46.py`：宿主映射两例改名/改期望，新增串行代跑红例。

### 红绿证据

所有命令在 worktree 根目录执行。沙箱无网络，`uv run --with pytest` 拉取失败，改用 uv 解释器 + uv 缓存中的 pytest 9.1.1（`PYTHONPATH` 指向 `~/.cache/uv/archive-v0/…`）离线运行；这只改运行方式，不改测试内容。

```text
# 红：先写/改测试，源码回到修复前（git stash 仅暂存 5 个源码文件）
$ /tmp/spec48-49-pytest.sh tests/test_spec48_ticket49.py scripts/test_check_skills_ticket46.py -q
8 failed, 23 passed, 2 subtests passed
  failures: test_mandate_counts_user_stop_as_stop_not_completion,
            NoSubagentCapability::{test_entry_blocks_delegation_without_subagent_capability,
              test_entry_drops_serial_stage_execution_promises,
              test_host_check_is_capability_based_not_brand_pinned,
              test_literature_playbook_blocks_instead_of_serial_stepping},
            ReleaseGate::{test_host_map_serial_substitute_is_red,
              test_host_map_states_blocked_without_subagents,
              test_host_map_without_fallback_is_red}

# 绿：实现后
$ /tmp/spec48-49-pytest.sh tests/test_spec48_ticket49.py scripts/test_check_skills_ticket46.py -q
31 passed, 2 subtests passed

$ /tmp/spec48-49-pytest.sh tests scripts/test_check_skills_ticket*.py -q
7 failed, 90 passed, 44 subtests passed     # 失败仍是基线同一 7 个历史断链测试

$ uv run python scripts/check-skills.py
FAIL: 9 个问题（全部为 .gitignore 造成的历史 evidence tarball 断链，与基线逐条相同）
```

### 偏离与剩余

- 未迁移叶的既有串行表述未动（如 `playbooks/proof.md` 的「串行自查明示非独立」）：那是一张如实标签，属于后续迁移范围，不在本次定向修复内。
- `docs/acceptance/**` 历史验收记录保留旧的串行说法，它们是历史证据，不改写。
- 仍未验证：模型在真实宿主缺子代理时是否照新语义停下（本票只做静态合同与测试检查）。
