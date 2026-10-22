# Ticket #58 实施记录：研究发现、检索与绘图随包闭环

Spec #48 / Ticket #58。worktree `/Users/rolex/.t3/worktrees/Research OS Studio/t3-da263918`，分支 `t3/da263918`。开始时 HEAD `98e4333` 且工作区干净；随后安全 fast-forward 合入本地 `integration/spec-48` @ `e84f779`。

续接记录（2026-10-22）：入口判定为直接执行，不继续派发：这是用户明确限定的单票实现与既有 worktree 验收，交付边界清楚；同时服从“禁止继续派发”。续接开始时 HEAD 为 `55398b3`，已有 16 个跟踪文件改动及未跟踪 `skills-lock.json`，无冲突、无 `MERGE_HEAD`；全部既有成果保留，锁文件留在工作区但不纳入交付。本次不操作主目录或 `integration/spec-48`，仅用 Git。全局 TDD skill 不可用（技能目录未找到），故按现有回归测试先红后绿。所有命令均显式进入本票 worktree。

## 状态

| 单元 | 交付目标 | 状态 | 产物 | 验收证据 |
|---|---|---|---|---|
| U1 委托迁移 | idea-cycle 全叶与 academic-plotting 遵循委托合同，去掉阶段门但保留职责约束 | done | 8 个 SKILL.md、迁移边界与 checker 登记 | `tests/test_spec48_ticket58.py::MigratedSet` |
| U2 发现配方 | Discovery 按目标缺口组合子集、重排与回访，保留叶职责 | done | `idea-discovery/SKILL.md`、composition notes、playbook、能力图 | `tests/test_spec48_ticket58.py`、checker 组合反例及安装根资源合同 |
| U3 授权与路径 | 既有委托内自主选图与新文件路径，越权/冲突门保留 | done | `academic-plotting/SKILL.md`、`idea-discovery/SKILL.md` | Ticket58ReviewRegressions 自主选图/路径合同 |
| U4 依赖闭合 | 发现独立安装必需兄弟依赖可成组安装，未安装明确 blocked | done | Discovery 正文、组合说明、技能安装说明、测试 | CLI 单装/成组实装日志及 `install-single-revised/`、`install-group-revised/` 树 |
| U5 文件能力缺口审计 | 记录文本/PDF/扫描OCR/连接器/绘图导出覆盖、宿主前提与不引资产理由 | done | `research-lit/references/file-capability-audit.md`、来源方法链接、绘图合同 | 覆盖矩阵回归通过；无目标宿主/具体转换需求，不虚称找尽兼容资产 |
| U6 本票验收与提交 | 汇总 F1–F4 证据，在唯一授权 worktree 提交 | done | 当前票提交（Git-only） | 69 passed/54 subtests；26 passed/52 subtests；diff 检查；全仓 checker 历史断链明确列出 |

## 决策

1. 不新增检索或绘图 Skill：`research-lit`、`novelty-check` 已覆盖文献检索/来源处理/查新，`academic-plotting` 已覆盖数据图与示意图。本票只迁移语义、整理配方和登记资源；不凭数量补重复能力。
2. Discovery 按目标缺口和已有材料选择所需能力子集，允许重排/回访；五项 sibling 是完整方向到 Proposal 配方的 Required skills，但非每个局部任务都要执行全部。CLI 单装不闭合依赖，因此显式给多选成组安装命令，单装缺依赖则标 blocked。
3. `creative-thinking-for-research` 暂留：继续作为可选生成职责内的认知转换方法，不合并、不删除；没有比较独立收益的新证据。
4. 共享资源继续由各能力共置，保证独立安装时能从自身目录解析；不在发布资源中引用 `/tmp` 或个人目录。

## 逐 AC 证据

1. **保留成熟能力且不添重复**：未新增 Skill；`research-lit`、`novelty-check` 和 `academic-plotting` 继续作为共享检索/来源处理/绘图能力。`tests/test_spec48_ticket58.py::SharedAssets::test_existing_retrieval_and_plotting_assets_are_reused`。
2. **阶段控制转组合配方**：Discovery 按目标缺口与现有成果选择需要的能力，可局部开始、重排或回访；完整方向到 Proposal 只是可选方案。`tests/test_spec48_ticket58.py::Ticket58ReviewRegressions::test_discovery_recipe_is_gap_driven_not_a_locked_route` 与 checker 反例覆盖。
3. **creative-thinking 暂留**：目录、SKILL 与 references 均存在，仍被 Phase 2 作为生成职责内的认知转换方法；未做合并或删除。
4. **许可/资源/外部服务**：各能力保留 MIT LICENSE，`SharedAssets::test_bundled_sources_licenses_and_resources_resolve` 覆盖；`test_external_services_and_writes_stay_authorized` 覆盖付费、凭据、远程写入、上传和本地环境边界。
5. **独立安装不依赖开发路径**：旧整包 CLI 1.7.4 实装 41 个 Skill 与代表资源有记录于 `/tmp/research-os-spec48-ticket58-review/evidence/install-all.log`、`install-check.log`。本次再次以 CLI 1.7.4 实装单独 Discovery（仅入口），并以一条 CLI 命令成组安装入口与五个 Required skills，确认五个依赖正文均可达；证据为该目录的 `evidence/install-idea-discovery-revised.log` 和 `install-idea-discovery-group-revised.log`。
6. **分工**：未改 `citation-audit` 或 `apply-citation-fixes`；只迁移 academic-plotting 并把它登记为共享绘图能力。

## 红绿证据

所有 Python 命令均在工作区内经 uv 的离线缓存 Python/pytest 执行，`UV_OFFLINE=1`，不访问网络。原提交红绿计数与独立审查重跑记录保留在 `/tmp/research-os-spec48-ticket58-review/REPORT.md`；本次 F1–F4 红例和绿灯：

```text
# RED：更改修复前新增组合/授权/依赖/审计回归
$ uv run --no-project --python /Users/rolex/.cache/uv/archive-v0/ZHSqs5vxcDKWb5QD/bin/python python -m pytest tests/test_spec48_ticket58.py::Ticket58ReviewRegressions -q
1 failed + 14 subtest failures（发现 F1/F2/F3/F4 原有正文/文件缺陷）

# GREEN：所有新增与既有本票测试
$ uv run --no-project --python /Users/rolex/.cache/uv/archive-v0/ZHSqs5vxcDKWb5QD/bin/python python -m pytest tests/test_spec48_ticket58.py -q
21 passed, 46 subtests passed

# GREEN：本票加受其产品合同影响的既有 checker ticket suites
$ uv run --no-project --python /Users/rolex/.cache/uv/archive-v0/ZHSqs5vxcDKWb5QD/bin/python python -m pytest tests/test_spec48_ticket58.py scripts/test_check_skills_ticket*.py -q
67 passed, 48 subtests passed

# GREEN：Discovery 相关旧的逐字原评审内联合同
$ uv run --no-project --python /Users/rolex/.cache/uv/archive-v0/ZHSqs5vxcDKWb5QD/bin/python python -m pytest tests/test_accept_remediation_contract.py::AcceptRemediationContract::test_idea_dispatch_and_canonical_keep_original_feedback scripts/test_check_skills_ticket38.py::IdeaDiscoveryRoute tests/test_spec48_ticket58.py -q
24 passed, 46 subtests passed

# CHECKER：仅报告原有断链证据，不含本票新增问题
$ uv run --no-project --python /Users/rolex/.cache/uv/archive-v0/ZHSqs5vxcDKWb5QD/bin/python scripts/check-skills.py
exit 1；9 条 docs/acceptance evidence tarball 断链，与独立审查 base/head 相同

$ git diff --check
exit 0
```

另外运行更广 `tests/test_spec48_ticket58.py tests scripts/test_check_skills_ticket*.py` 曾得 9 failed / 134 passed / 90 subtests：其中 8 项是 checker 固定要求历史九条断链为零导致的基线失败；另 1 项既有全项目角色表断言要求 idea-discovery 保留 `ideator`。新增 playbook 为避免固定分工改为 orchestrator only，独立职责按缺口按需委派；已用有差异的 ticket/checker 范围 67 pass 与 Discovery legacy tests 24 pass 验证。非本票多个旧 contract 测试同样调用全仓 checker 并与历史断链冲突。本次未改这些无关测试或断链材料。

## F1–F4 定向修复记录（2026-10-21）

1. **F1 路线锁定**：删除 Discovery/入口中的固定 Phase 0→4.5 连续主链、固定跨 turn route 语义和强制 Proposal 终点。正文、playbook、能力图与中英文使用说明均改为按目标缺口及已完成成果选择子集、重排和回访；仍保留各叶来源、预算、独立 reviewer 原文与 Problem Anchor 义务。checker 新增组合语义检查；红例把正文改成固定顺序后应报错。
2. **F2 普通审批重复**：composed plotting 在既有委托图数/材料范围内自主选有依据的图并记录理由；在授权目录内可选新文件路径。standalone 仅缺目标/材料范围时澄清；同名冲突、越权目录、覆盖、上传、付费及超额仍留决定门。Discovery 同样允许授权目录内选择不冲突新文件名。checker 红例恢复普通选图需确认后应失败。
3. **F3 单装依赖缺口**：composition 明列五个 Required skills 与真实 `skills add --skill` 多选命令，解释 CLI 单选仅安装入口本身；入口缺 sibling 时明确 `DEPENDENCY MISSING / BLOCKED`，不冒充独立评审。用户 README、Idea Cycle 能力图和安装指引同步。CLI 1.7.4 在 `/tmp/research-os-spec48-ticket58-review/install-single-revised/` 实装单独 Discovery，确认只有入口；在 `install-group-revised/` 成组实装六项，五个依赖 `SKILL.md` 均可达。证据：`evidence/install-idea-discovery-revised.log`、`evidence/install-idea-discovery-group-revised.log`。CLI 还生成了源码目录未跟踪 `skills-lock.json`，不属于交付；保留现场、不清理、不提交。
4. **F4 文件能力审计**：新增 `skills/idea-cycle/research-lit/references/file-capability-audit.md`，涵盖文本/Markdown、数字 PDF、扫描文档/OCR、连接器、绘图/示意及 PDF/SVG/PNG 导出/目检，区分随包方法与宿主 reader/OCR/connector/runtime 前提。基于本票缺少指定目标宿主与具体转换/OCR需求的限制，不引入新运行依赖；明确不是声称不存在兼容许可资产。后续只有确定目标和缺口才评估候选，并审许可证、资源可达性与依赖。source-methods 提供指针、checker 检查文件及边界。

## 当前验证（2026-10-22）

- **RED → GREEN（资源路径合同）**：续接后首跑 `uv run --no-project --python /Users/rolex/.cache/uv/archive-v0/ZHSqs5vxcDKWb5QD/bin/python python -m pytest tests/test_spec48_ticket58.py -q` 中 `test_discovery_playbook_resolves_required_reads_from_installed_skill_roots` 失败，3 个 Skill 子项显示资源路径未列明：playbook 对生成/创意/细化资源只写“本次所需”，未列出相对于独立安装 Skill 根的真实路径。补齐明确相对路径并将测试改成按安装树精确核验后，通过 **23 passed, 52 subtests passed**。
- **RED → GREEN（旧合同测试迁移）**：受影响的全套 ticket/checker 测试首跑暴露 `test_check_skills_ticket38.py::IdeaDiscoveryRoute` 仍要求源码 checkout 路径；这和独立安装解析合同冲突。将断言改为 Skill 名称解析并禁止源码路径后，`... pytest tests/test_spec48_ticket58.py scripts/test_check_skills_ticket*.py -q` **69 passed, 54 subtests passed**。Discovery 历史联测命令 `... pytest tests/test_accept_remediation_contract.py::AcceptRemediationContract::test_idea_dispatch_and_canonical_keep_original_feedback scripts/test_check_skills_ticket38.py::IdeaDiscoveryRoute tests/test_spec48_ticket58.py -q` **26 passed, 52 subtests passed**。
- **全仓 checker（非绿）**：`... python scripts/check-skills.py` exit 1，仅列出 9 个既有 `docs/acceptance/evidence/*.tar.gz` 断链；与原只读 review 记录的 base/head 相同，未改无关历史证据包/断链。
- **CLI 实装证据**：真实通用 Skills CLI 1.7.4 单选安装只得到 Discovery 的日志：`/tmp/research-os-spec48-ticket58-review/evidence/install-idea-discovery-revised.log`，目标目录 `/tmp/research-os-spec48-ticket58-review/install-single-revised/.agents/skills/idea-discovery/`。同 CLI 多选安装日志：`.../evidence/install-idea-discovery-group-revised.log`，目标目录 `.../install-group-revised/.agents/skills/`；六项 `SKILL.md`（入口及五项 Required skills）实存。不是 copytree 仿真。`skills-lock.json` 是 CLI 现场产物，仍不提交。
- `git diff --check` exit 0；工作区验收时 HEAD=`55398b3`、分支=`t3/da263918`，无冲突/merge state。全量 tests 未声称通过；不会处理 integration/主目录。

## 未完成 / 限制

1. 静态合同、结构可达性和扁平安装已验证；未验证真实宿主会在每次委托中完美执行 Discovery 配方或检索/绘图质量。
2. 未新增付费检索 provider 清单；外部账号、订阅与付费服务仍按各能力授权门处理，缺授权时如实阻塞。
