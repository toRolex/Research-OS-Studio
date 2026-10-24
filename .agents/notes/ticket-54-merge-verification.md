# #54 独立验收与整合记录

## 范围、输入与结论

入口判定：用户指定本 worker 为唯一 merger/独立验收，禁止继续派发与实现 feature；这是已有实现的有界审查、复验、整合 work unit，故直接执行。采用用户明确批准的 Git worktree 例外，不用 jj。已读 Multi-Agent、CODING_STANDARDS、model-availability 与 writing-for-agents（含机制参考）；未调用额外模型或子代理。

唯一写域 `/Users/rolex/.t3/worktrees/Research OS Studio/integration-spec-48`。所有 bash 显式 cd，读写文件用绝对路径；源 worktree 只读。未改产品或测试，未写 orchestrator notes，未 push/PR/issues/清理 worktree。临时测试、安装、缓存输出均定向到本写域内 ignored 证据目录。

输入：`/tmp/research-os-spec48-context/spec/#48.md`、`tickets/#54.md`；固定上游归档 README、两份 `pstack/skills/{create,maintain}-formal-verification-skill/SKILL.md` 与 `pstack/LICENSE`；源实现 notes、全部实际 diff 与共置资源。上游 revision `88d47514b82e7c44f00f2b2a72ff6dd12158038c`。

- integration 起点：`98e4333b5e740558a59cf376d48de227cc4b2ff1`，clean。
- 源 tip：`6de82c75098e78c79549b5ef93c7138e927a7ffc`（产品 `a83da0c`）；branch `t3/b33ec12f`。
- **结论：无本票阻断，5 项 AC 接受；已无冲突 no-ff 合并为 `6aaad916dca838e08527573d73f055d56d6e2566`。**
- 合并 parents 为 `98e4333` 与 `6de82c7`；合并树与源 tip 逐字一致（`git diff --exit-code 6de82c7 HEAD`）。源两提交作者 `pi-worker <pi-worker@local>` 保持原样，没有改写；本 worker 的合并和本记录提交使用仓库有效身份 `rolex <torolex@163.com>`。

2026-10-24依据本记录原`6aaad91`合并验收阶段补记下一步列；原结论、历史失败和证据不改，本次未重跑历史。

| 单元 | 状态 | 验收产物 | 当时下一步 / 阻塞 |
|---|---|---|---|
| 来源、实际 diff、两技能与资源逐 AC 审查 | done | 下表及原文件 | 无（当时本票AC范围）；未来变更另核 |
| 候选/基线/独立损坏副本复验 | done | `targeted-premerge`、`suite-{candidate,baseline}`、`checker-{candidate,baseline}`、`independent-red` | 无（该次复验）；历史7失败/9诊断保留，不称全包通过 |
| 真实缓存 CLI 分别独立安装两能力 | done | `install-*`、`list-*`、`install-inspection` | 无（安装可达范围）；真实形式化任务/宿主行为未验 |
| no-ff 整合与合并后复验 | done | merge 6aaad91；`targeted-postmerge`、`suite-postmerge`、`checker-postmerge` | 无（该次合并/复验）；后续整体验收交parent |

证据统一位于 `.agents/notes/ticket-54-verification-evidence/`，文中日志名均补 `.txt`。该目录 ignored、保留本地；仅强制追踪本记录，未把大体积快照/日志或 orchestrator notes 纳入提交。

## 逐项 AC（静态/人工合同与实际执行分开）

| #54 AC | 判定 | 亲核依据与执行证据 |
|---|---|---|
| 适配创建/维护，核查来源许可、工具参考、资源自包含 | ACCEPT | 创建保留从代码选目标、问题决定工具、好检查判据、生成本地 skill、划痕自证与交接；维护保留四结果、验证-only 编辑范围、逐提交读覆盖变化、按代码而非通过更新、反例回放、故障暴露、blocked 不推进 sync。两目录各携完整 MIT/Lauren Tan 许可与 NOTICE；两 LICENSE 与固定上游字节相同，SHA256 `bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e`。明确为 pstack 插件级许可，不称仓库根 MIT；MIT 保留通知后适配分发，未引入其他依赖或额外许可资产。create 的 3 references 与 1 template 全部共置；maintain 正文自足，不依赖 create 已安装。分别实际独立安装各一能力，8/4 文件逐字相同，LICENSE/NOTICE/agents 及全部资源可读，8 条内部 Markdown 文件链接全部可达。工具参考给工具类别及选择判据，不假装已经安装真实验证器。 |
| 区分代码性质/形式模型/数学定理/普通测试，按问题选工具，非全链强制 | ACCEPT | create §1 四类表、§2 与 tool-selection 的实现/顺序/每规模/具体用例分支；普通测试够用就停，语言无验证器时生成输入测真实代码，替代手段如实命名。没有固定证明工具、宿主命令、个人目录或模型；独立复核缺子代理则 blocked、不伪装串行独立复核。未改 proof 族，保留只读/委托边界。`QuestionChoosesTool`、`HostNeutrality` 与独立 kind/model 损坏副本为补证。 |
| 记录假设、材料/依赖版本、实际覆盖、同步及变化重验 | ACCEPT | create §4、assumption-ledger 字段/规则、record 的覆盖/外部假设与材料/同步/重验；maintain §1/3–5/7 覆盖移动/新增状态写路径、材料/工具/库/定义更新，标 stale，blocked 不前移 sync。旧通过只代表旧对象，未知版本/未读材料维持未核实。`AssumptionVersionSync` 通过。 |
| 审计原问题↔编码定义/定理声明及外部输入，不把占位符/编译/有限数值当原定理 | ACCEPT | create §5、correspondence-audit 的原文来源→定义→完整声明、对象/量词/假设/定义域边界/结论强度/外部依赖核对；账本与模板记录外部规范、数据、生成器、公理及版本/条件。maintain §5 要求变化后重做审计。无占位符/编译成功只是必要非充分条件，模型/有限数值只覆盖实际界；换题/缺口不得宣称原问题已证。`CorrespondenceAudit` 通过；这些是合同审查，不是实际证明。 |
| 故障暴露、未运行即草稿，验收安装与合同而非真实全形式化 | ACCEPT | create §3/6/7：每条性质坏变体需失败、撤销后回到原结果、生成资产未执行标草稿；maintain §6 复核失败能力并区分漂移/bug，禁止削弱性质或暗改产品。record 含变体输出、恢复结果、状态。独立损坏许可/草稿/四类/固定模型四副本均在9条基线之外精确新增预期诊断。真实 CLI 安装与静态正反例实跑；未新增项目级形式化 helper，因此没有将真实定理或 Lean/SMT/模型检查工具执行作为本票验收或完成宣称。 |

## 复验方式与结果

从固定提交 `git archive` 生成候选/基线快照，在证据目录内初始化局部 Git 追踪；合并后再次 archive 得 postmerge。未在源 worktree 跑测试；避免缓存写入源目录。沿用 #49 的离线 pytest 依赖方式：

```sh
cd '/Users/rolex/.t3/worktrees/Research OS Studio/integration-spec-48'
# 完整环境与退出码记录逻辑见证据目录 run-checks.sh
# uv --offline --no-project python；PYTHONDONTWRITEBYTECODE=1
# PYTHONPATH 来自五个已有 uv archive，不下载安装依赖
bash .agents/notes/ticket-54-verification-evidence/run-checks.sh targeted-premerge \
  "$PWD/.agents/notes/ticket-54-verification-evidence/candidate" \
  -m pytest tests/test_spec48_ticket54.py -q
# 全套：-m pytest tests scripts/test_check_skills_ticket*.py -q
# checker：scripts/check-skills.py
```

| 对象 | 定向 | 全套 | checker |
|---|---|---|---|
| 98e4333 基线 | 不适用 | 7 failed, 90 passed, 44 subtests passed | exit1，9条历史断链 |
| 6de82c7 候选 | 25 passed | 7 failed, 115 passed, 44 subtests passed | exit1，与基线逐字相同 |
| 6aaad91 合并后 | 25 passed | 7 failed, 115 passed, 44 subtests passed | exit1，与基线逐字相同 |

全套三组失败集合逐行相同，未跳过、屏蔽或修改历史测试：

1. `PolicyAndGates::test_checker_green_and_leaf_baseline`
2. `ConfigContractTests::test_gate_baseline_and_counterexamples`
3. `ConfigContractTests::test_shipped_templates_and_full_checker`
4. `ConfigContractTests::test_valid_policy_and_log_fields`
5. `ConfigContractTests::test_valid_role_table`
6. `FinalContracts::test_full_cli_damaged_declarations_refs_and_readme`
7. `ReviewFixes::test_compute_limits_are_per_unit_not_summed`

checker 9条均为 `docs/acceptance/` 引用缺失/未追踪的 `evidence/*.tar.gz`：release-host-regression、final-contract-fixes、release-gate-combinations、merged-host-smoke、accept-validation、accept-hosts、final-contract-independent-verify 两条、accept-remediation。原样保留非零状态，未冒称全绿。

源 notes 的前期「9 failed,16 passed」红测试仅作为历史记录，本 worker 不声称独立复现了当时中间树。独立红例另用 `inspect-evidence.py mutate` 从最终候选复制四个损坏副本：删维护 LICENSE、删创建草稿标记、删工具参考四类之一、加入固定模型；各 checker exit1 且新增诊断分别命中缺资产、缺草稿、缺形式模型、固定模型。日志 `red-{missing-license,draft-removed,kind-removed,model-pinned}.txt`。候选25测试本身也执行5个 checker counterexample。

真实安装使用现有缓存 **skills 1.7.4**：

```text
node /Users/rolex/.npm/_npx/5606f1555d02ef53/node_modules/skills/bin/cli.mjs \
  add <candidate-snapshot> -s <one-formal-skill-name> -a claude-code -y
node <same-cli> list
```

分别在 `install-create-formal-verification-skill` 与 `install-maintain-formal-verification-skill` 中执行，只装各自一能力；add/list 均 exit0。实际目录为 `.claude/skills/<name>`（CLI copied 模式），没有依赖另一 Skill。独立检查初稿错误假设 `.agents/skills`，导致一次验收脚本失败；完整保留 `install-inspection-initial-harness-error.txt`，按实际 CLI 输出修正的仅为本地验收脚本路径，未改产品/安装内容，随后 inspection exit0。

两安装 SKILL.md SHA256：create `e7ca068e9ed38481a78b650dda6eeeefc0a9f189479f4748d4daa1dfd98fc4ea`；maintain `07cd4c1ef0bb8db905be3a3530c0c1a8f7585794979e892411179fc968888905`。

`git diff --check 98e4333..6de82c7`、合并后 diff 检查与源树一致性通过。orchestrator notes 在验收前、合并后及最终检查的 SHA256 均为 `2a6f46e02ef848fc96666049f12e52ba0aaf5d2f253ef6c1f93fcc08634f31aa`；本 worker 未写或暂存它。

## 遗留与声明限制

- 无本票阻断或新增失败。既有7测试失败/9历史断链未修，需后续终态验收处理。
- README 固定39计数、英文说明及验收指南未随新增两能力终态同步；源已列为 #60 边界，本次不扩大写域/产品范围。未重新验收全包全部其他能力引用，不以本票两能力安装通过为整包背书。
- 检查器大量依赖语义标记，能发现本次覆盖的结构损坏，不等于语义理解或运行时行为证明。人工逐 AC 审查与静态测试互补。
- 未运行 Lean、SMT、TLA+ 或真实数学项目；未验证模型在实际科研中选工具/审计/维护的质量，未验所有宿主、服务器或长期无人值守。本票只接受安装后的两能力结构、合同与资产可达性；数学正确性和真实形式工具执行均未声称。
- 本记录提交后交回父任务；未擅自修改作者、推送、开 PR/issue 或清理任何 worktree。
