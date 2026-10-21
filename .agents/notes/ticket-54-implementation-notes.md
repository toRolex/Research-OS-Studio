# Ticket #54 实施记录：形式化验证资产及对应审计

Spec #48 / Ticket #54（12 个 slice 中的第 6 个）。worktree `/Users/rolex/.t3/worktrees/Research OS Studio/t3-b33ec12f`，T3 binding `attached=true`，分支 `t3/b33ec12f`，基线 `integration/spec-48` @ `98e4333b5e740558a59cf376d48de227cc4b2ff1`（clean，本地 tip 未再前进）。实现期不 push、不写 issue、不清理 worktree。只实现本票，不改 proof 族（#55）。

## 状态

| 单元 | 交付目标 | 状态 | 产物 | 验收证据 |
|---|---|---|---|---|
| U1 创建能力 | 建立可重跑形式化检查并留下项目本地 verify skill；许可/来源/资源自包含 | done | `skills/validation-cycle/create-formal-verification-skill/`（SKILL.md、LICENSE、NOTICE.md、3 references、1 template、openai.yaml） | `FormalSkillContract`、`QuestionChoosesTool`、`FlatInstall`（见下） |
| U2 维护能力 | 代码变化后重新对齐、重跑并区分漂移与 bug；同步假设/版本/对应审计 | done | `skills/validation-cycle/maintain-formal-verification-skill/`（SKILL.md、LICENSE、NOTICE.md、openai.yaml） | `AssumptionVersionSync`、`CorrespondenceAudit`、`FaultExposureAndDraft` |
| U3 四类区分与工具选择 | 代码性质/形式模型/数学定理/普通测试；按问题选工具、不强制全链 | done | `references/tool-selection.md` + SKILL 正文「1. 从代码和问题选目标」「2. 按问题选工具」 | `QuestionChoosesTool::*`（3 例） |
| U4 假设与同步 | 外部假设、材料、依赖版本、实际覆盖、同步状态、变化失效 | done | `references/assumption-ledger.md` + `templates/formal-verification-record.md` + 两份 SKILL 第 4/5 节 | `AssumptionVersionSync::*`（2 例） |
| U5 对应审计 | 原问题↔编码定义↔定理声明；占位符/编译/有限数值不冒充定理 | done | `references/correspondence-audit.md` + 两份 SKILL 审计段 | `CorrespondenceAudit::*`（3 例） |
| U6 故障暴露与草稿 | 破坏变体必须被抓住；未执行资产标草稿 | done | create 第 3/7 节、maintain 第 6 步 | `FaultExposureAndDraft::*`（2 例） |
| U7 宿主中立 | 移除 Cursor/个人目录/固定模型；子代理前提与 blocked | done | 两份 SKILL 的「委托继承」与结尾段 | `HostNeutrality::*`（2 例），checker 同规则 |
| U8 登记与检查器 | 迁移登记、README 清单、入口指针、独立 checker 函数、来源文档 | done | `scripts/check-skills.py`（`formal_verification_problems`）、`migration-boundary.md`、两份 README、入口、`docs/upstream-sources-and-licenses.md` | `Registration::*`、`CheckerCounterexamples::*`（5 例） |
| U9 安装与来源核对 | 可丢弃目录实际安装、资源可达；离线资料亲核正文与许可 | done | 本文「安装证据」「来源核对」 | CLI 实跑；LICENSE blob/SHA256 复核 |

## 入口判定

本 agent 是 Spec#48 单票实现 worker，按派发约束不继续派发；任务分流记录为「直接执行」：范围为一张票的 Skill 资产、checker 登记与测试，主 agent 已给出权威 spec/票面、固定上游资料与边界，无需再拆分。

## 决策

1. **按票面新增两个独立能力，不复制 pstack 目录结构**：落在 `skills/validation-cycle/`，与既有 proof 族同级但互不调用；proof 族（proof-writer/review/repair/orchestrator）未改动，留给 #55 的数学配方组合。
2. **四类区分放在能力入口而不是 checker 常数**：`代码性质 / 形式模型 / 数学定理 / 普通测试` 是判断结构，写进 SKILL 与 `tool-selection.md`；checker 只校验这些语义标记存在，不校验具体工具名，避免把某个厂商工具变成发布门。
3. **假设账本与对应审计各自共置**：创建侧携带 `assumption-ledger.md` 与 `correspondence-audit.md`，维护侧在流程第 5 步强制同步二者。没有把这份语义放进共享 `research-os/references/`，因为票面 Testing #3 要求单独安装可解析，跨 Skill 指针在扁平安装下会断。
4. **模板只保留记录结构**：`formal-verification-record.md` 是随项目本地 verify skill 发行的字段骨架，不含工具命令或占位符实现；生成者必须替换为本仓库真实命令。
5. **checker 独立函数 + 独立登记**：`formal_verification_problems(root, tracked)` 与 `MIGRATED_CONTRACT` 两行、`migration-boundary.md` 两行、两份 README 清单同步；不删改他人断言。若与他票在 README/checker 相邻行冲突，由 merger 处理。
6. **迁移而非新增旧门**：两个新 Skill 直接按 #49 的委托合同登记（`委托继承` 小节 + `Gates: none`），不引入新的叶级审批门；这样 `MIGRATED_CONTRACT` 与 `LEGACY_LEAF_GATES` 的划分测试继续成立。
7. **宿主中立按能力判定**：子代理缺失时独立复核/并行核对标 blocked；不写固定模型、个人目录或厂商命令。CHECKER 用禁用词与模型名正则守住该边界，`NOTICE.md` 例外（来源归属必须点名上游）。
8. **不强制全链**：create 的目标选择段允许「普通测试够用就停」，`tool-selection.md` 单列「不强制全链」；这与 spec ID25、ID7 一致。

## Deviations

1. **README 的 39 数字未改**：新增 2 个 Skill 后实际为 41，但 #49 已把 badge／TOC／标题／「全套包含 39 个」的统一留给 #60；本次按「只追加自己的能力行」执行，未改其他段落。风险：发布文档暂时少 2 个计数，已在「未完成」标注。
2. **未改 `docs/user-acceptance-guide.md` 与英文 README**：票面要求同步迁移登记与 README 清单；这两处属终态同步范围（#60），且 checker 不以其为发布门。未新增用户手工验收步骤，改为在本文记录安装与静态证据。
3. **未做真实数学项目形式化**：票面验收范围明确只验安装与合同；本票没有安装 Lean/TLA+/SMT 工具链，也没有对真实定理编码。`create-formal-verification-skill` 的「已执行」判定仅由结构测试与模板字段证明，不声称运行时行为已验证。
4. **维护侧不带 references**：上游维护正文本身已完整覆盖 Outcomes/Pass/Report 与假设同步，拆出 reference 只会重复；按 DRY/YAGNI 保持单文件 + 共置许可。
5. **`NOTICE.md` 出现上游品牌名**：来源归属必须点名 `cursor/plugins`，故宿主中立检查只作用于 `SKILL.md` 与 `agents/openai.yaml`；这是有意豁免，已在测试注释与 checker 里固定。

## 来源核对（离线资料亲核）

- 归档：`/tmp/research-os-spec48-upstream/`，`pstack@88d47514b82e7c44f00f2b2a72ff6dd12158038c/pstack/`，37 文件。
- 逐字阅读：`skills/create-formal-verification-skill/SKILL.md`（5141B）、`skills/maintain-formal-verification-skill/SKILL.md`（7012B）、`LICENSE`（1067B）、`plugin.json`（license MIT、author Lauren Tan）。
- 许可复核：`LICENSE` SHA256 `bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e`，git blob `6b5400237fdf6545be0b8fae370d6f2fcff8fb25`，与 `_meta/manifest-fetched.json` 一致；两个 Skill 的 `LICENSE` 为上游字节副本。
- 归属口径：`cursor/plugins` 的 `pstack/` 子树 @ 该 revision，MIT，`Copyright (c) 2026 Lauren Tan`；不写「仓库根 MIT」（该 commit 根目录无 LICENSE）。
- 采用边界：只采用上述两份正文机制；未复制归档外 pstack 文件、未采用 `third_party/`、未采用宿主绑定（模型表、`/loop`、`agent-transcripts`）。适配范围写入两份 `NOTICE.md` 与 `docs/upstream-sources-and-licenses.md` 新章节。

## 执行与红绿证据

所有命令在 worktree 根目录执行。沙箱无网络，沿用 #49 的离线 pytest 方式（uv 解释器 + uv 缓存 wheel 的 `PYTHONPATH`，脚本 `/tmp/spec48-54-pytest.sh`），只改运行方式，不改测试内容。

```text
# 红：先写 tests/test_spec48_ticket54.py，源码尚未登记/未加 checker 函数
$ /tmp/spec48-54-pytest.sh tests/test_spec48_ticket54.py -q
9 failed, 16 passed
  failures: QuestionChoosesTool::test_question_not_toolchain_chooses_and_no_forced_full_chain,
            HostNeutrality::test_no_cursor_personal_directory_or_fixed_model_binding,
            Registration::{test_checker_has_independent_formal_contract_function,
                          test_current_tree_has_no_new_breakage,
                          test_migrated_and_readme_and_entry_pointer},
            CheckerCounterexamples::{test_dropped_draft_marking_is_red,
                                     test_dropped_kind_distinction_is_red,
                                     test_dropped_license_is_red,
                                     test_fixed_model_binding_is_red}
EXIT=1

# 绿：实现后
$ /tmp/spec48-54-pytest.sh tests/test_spec48_ticket54.py -q
25 passed
EXIT=0

# 全套对照基线
$ /tmp/spec48-54-pytest.sh tests scripts/test_check_skills_ticket*.py -q
7 failed, 115 passed, 44 subtests passed
EXIT=1
  失败集合与基线完全一致（同一 7 个测试，均由 9 条历史 evidence tarball 断链造成；
  #49 记录为 7 failed, 90 passed, 44 subtests passed，本次多出的 25 passed 即本票测试）

$ python3 scripts/check-skills.py
FAIL: 9 个问题（全部为 .gitignore 造成的历史 evidence tarball 断链，与基线逐条相同）
EXIT=1

$ git diff --cached --check
EXIT=0
```

说明：checker 与全套测试的退出码仍为非 0，因为历史断链未修（按 #49 约定不属于本票）；本票新增检查、测试与资产均无新失败，未屏蔽或跳过任何新失败。

## 安装证据（可丢弃目录）

```text
$ cd /tmp/spec48-54-install
$ node <skills-cli> add "<worktree>" --list
EXIT=0   # 发现 41 个 Skill（本票新增 2 个，清单同步）

$ node <skills-cli> add "<worktree>" -s create-formal-verification-skill \
      -s maintain-formal-verification-skill -a claude-code -y
Installed 2 skills → ./.claude/skills/{create,maintain}-formal-verification-skill
EXIT=0
  两个已安装副本均含 LICENSE / NOTICE.md / agents/openai.yaml；
  create 的 3 个 references 与 1 个 template 全部可达；
  副本内相对链接 8 条，断链 0（脚本逐条 resolve）。
  `skills list` 显示两个 skill 来源指向本 worktree。
```

CLI 版本来自 #49 记录的本地 npx 缓存（`/Users/rolex/.npm/_npx/5606f1555d02ef53/node_modules/skills/bin/cli.mjs`），未改用户全局安装。

## 逐 AC 证据

| 票面 AC | 证据 |
|---|---|
| 适配创建与维护机制，核查来源许可、工具参考与资源自包含 | 两个 Skill 目录 + `LICENSE`（MIT/Lauren Tan）+ `NOTICE.md`（upstream/revision/范围）；`FormalSkillContract`、`FlatInstall`；checker `formal_verification_problems` 校验许可与必带资源 |
| 区分代码性质、形式模型、数学定理和普通测试；按问题选工具，不强制全链 | `tool-selection.md` 四类表 + 判据；create 正文「按问题选工具」「不强制全链」；`QuestionChoosesTool` 3 例 + checker 四类标记 |
| 记录外部假设、材料及依赖版本、实际覆盖、同步状态和变化后的重验判断 | `assumption-ledger.md` 字段表与规则、`formal-verification-record.md`、create 第 4 节、maintain 第 5 步；`AssumptionVersionSync` 2 例 |
| 检查原问题与编码定义和定理声明的对应；占位符/编译成功/有限数值不得冒充原定理 | `correspondence-audit.md` 审计链 + 逐项表 + 「不得冒充」清单；create 第 5 节、maintain 第 5 步；`CorrespondenceAudit` 3 例 |
| 适用检查具备故障暴露证据；未执行生成资产标为草稿；验收安装和合同 | create 第 3/7 节「能够失败」「草稿」、maintain 第 6 步破坏变体；`FaultExposureAndDraft` 2 例；安装证据与 checker 合同 |

## 未完成 / 限制

1. **README／英文 README／验收指南的 41 计数与终态措辞**：留 #60 统一（#49 已建立先例）。
2. **真实宿主行为未验证**：未验证模型在真实项目中会按该能力正确选择工具、正确判定漂移与 bug，也未跑真实模型检查器或证明助手；本票只证明结构合同、静态检查与安装可达性。
3. **全链形式化未验收**：票面明确不要求真实数学项目全形式化；`create` 中的工具类别是判据而非已安装清单。
4. **`docs/acceptance/**` 9 条历史断链仍在**：按基线保留，不属本票。
5. **与他票的合并冲突预期**：两份 README 的 Validation 行、`MIGRATED_CONTRACT`、`scripts/check-skills.py` 末尾、入口「匹配」段可能与 #50–#53/#55 相邻；已尽量按「只追加」编辑，冲突由 merger 处理，我不删他人断言。

## 交付与合并复验

```text
分支：t3/b33ec12f（worktree /Users/rolex/.t3/worktrees/Research OS Studio/t3-b33ec12f）
提交：a83da0c feat(validation-cycle): add formal verification create/maintain skills (#54)
基线：integration/spec-48 @ 98e4333b5e740558a59cf376d48de227cc4b2ff1
合并：git fetch origin integration/spec-48 → 无法找到远程引用（与 #49 记录一致，远端无该 ref）；
      git merge --no-edit integration/spec-48 → 已经是最新的（本地 tip 未前进）
```

合并后复验（工作树未变化，证据仍有效）：

```text
$ python3 scripts/check-skills.py
FAIL: 9 个问题（与基线逐条相同）
EXIT=1
$ /tmp/spec48-54-pytest.sh tests/test_spec48_ticket54.py -q
25 passed
EXIT=0
$ /tmp/spec48-54-pytest.sh tests scripts/test_check_skills_ticket*.py -q
7 failed, 115 passed, 44 subtests passed
EXIT=1   # 同一 7 个历史失败，无新增
$ git diff --check
EXIT=0
```

未 push、未开 PR、未写 issue、未清理 worktree；主目录用户改动未触碰。
