# Ticket #53 实现记录：交付可创建、维护的项目行为验证能力

## 历史逐单元状态（补记）

2026-10-24依据本记录2026-10-21最终分支`06b9257`收束阶段补记；下方原长聚合段、各时点integration、失败及日志全部保留，本次没有重跑或把历史结果改成当前PASS。

| 单元 / 交付目标 | 当时状态 | 原有产物与验收证据 | 当时下一步 / 阻塞 |
| --- | --- | --- | --- |
| 创建/维护行为验证能力与共置资源 | done（本票资产范围） | 下文交付物、逐AC证据；create/maintain两个Skill及各自资源 | 无（该阶段交付范围）；真实应用E2E未验 |
| R1 实际证据归属与变化失效 | done | 两份SKILL内联revision/dirty diff/输入依赖/验证资产/范围假设，stale与受影响覆盖重跑，见原聚合段 | 无（R1合同范围）；不外推真实应用行为 |
| R2 Markdown destination检查 | done | helper按scheme/path/fragment分开核对；安装副本anchor/外链/标题正例与错链反例日志 | 无（本票局部helper范围）；不查锚点内容 |
| R3 checker结果协议 | done | 原聚合段记exit/stderr/OK-FAIL/诊断数及崩溃反例 | 无（该阶段R3范围），不追认早期断言覆盖 |
| 合并与fixture污染修正 | done | merge `528eddb`、登记保留#50/#53；README fixture改`.fixture`，首轮4/11新失败与纠正日志保留 | 后续候选整合/独立复审交parent，不改原失败 |
| 定向/联合/全套与安装验收 | done（限定验收工作） | 27 passed/49 subtests、联合89 passed；全套7 failed/163 passed、checker9历史断链；CLI create8/maintain4及helper安装正反例 | 历史失败与完整#54限制保留，不称全包/宿主通过 |
| notes与证据交接 | done | 原最终HEAD `06b9257`、原基线/后继指针、本文各日志路径 | 后续integration同步和总验收归parent；本次只索引历史事实 |

日期：2026-10-21。分支 `t3/spec-53-verification-skills`，worktree `/Users/rolex/.t3/worktrees/Research OS Studio/t3-a3b0d13a`，原审查 tip `ea8b8464b4d133a70787465dfc88d96e8103cf2a`，修复提交 `ae720e9b4614cb46bcfeb24ff9dbeb16197241ed`，合并提交 `528eddb`。状态：R1/R2/R3 定向修复完成，已合并 `integration/spec-48` @ `60ecb1bbb4b10308ea6b20a498654c12f30fdcef`（#50）。最终 branch HEAD `06b9257cf93308daa329f15895322f4a31272cc7`，当前 integration 指针另前进至 `dd70401cd46dbc6adb6eeaec2eead0b20d07a83f`（包含后续 #52；源 branch 已合并 integration tip 为 `60ecb1bbb4b10308ea6b20a498654c12f30fdcef`。网络 `ls-remote` 无输出，未继续追加更新）。HEAD 直接父为 notes 更新 `5d10a85`，其父为 merge commit `528eddb`；merge parents 为修复提交 `ae720e9` 与 #50 integration tip `60ecb1b`。合并冲突仅在共享 `MIGRATED_CONTRACT` 登记中；解决后同时保留 #53 两个验证技能登记及 #50 swarm 登记。合并后首轮四票联合失败 4 项、全套 11 项：新失败均由 #53 反例 fixture 以 README.md 存在源树触发全仓 Markdown 链接检查。改为 `.fixture` 源文件，并在定向 helper 测试中只复制到隔离临时目录构建真正 Markdown fixtures；checker 回到基线9项。红/绿：合并后失败日志 `/tmp/ticket53-merge-verification-joint.log` 与 `...joint-final.log`（含第一次重构误处理临时 README 的失败）；定向票测 `uv run --with pytest python -m pytest tests/test_spec48_ticket53.py -q` exit 0，27 passed/49 subtests；合并后的 #49/#50/#53 加 #54 核心合同/登记类回归 `uv run --with pytest python -m pytest tests/test_spec48_ticket49.py tests/test_spec48_ticket50.py tests/test_spec48_ticket53.py tests/test_spec48_ticket54.py::FormalSkillContract tests/test_spec48_ticket54.py::QuestionChoosesTool tests/test_spec48_ticket54.py::AssumptionVersionSync tests/test_spec48_ticket54.py::CorrespondenceAudit tests/test_spec48_ticket54.py::FaultExposureAndDraft tests/test_spec48_ticket54.py::HostNeutrality tests/test_spec48_ticket54.py::Registration -q` exit 0，89 passed/49 subtests（最终日志 `/tmp/ticket53-merge-verification-selected-final.log`）。合并后全套 `uv run --with pytest python -m pytest -q` exit 1：163 passed/7 failed/93 subtests（`/tmp/ticket53-merge-verification-full-final2.log`）；仍是 checker 历史9断链引起原7失败，失败组与之前已知相同。完整 #54 原文件含独立安装/自我复制 WorkCopy 合同测试，单独三票/全套无法通过其自我 tree no-new-breakage（会把历史 baseline也当 fail），此项已由本轮安装副本及静态 checker 另核；未声称完整 #54 模块全通过。checker `uv run --no-project python scripts/check-skills.py` exit 1，9条且全属历史 evidence 断链（最终 checker log `/tmp/ticket53-merge-verification-checker-final.log`）。真实 CLI 1.7.4 对 create/maintain 分别安装到空项目，均 exit 0；create副本8文件、helper executable 755，maintain副本4文件且无 create 同级依赖（`/tmp/ticket53-fix-retest.UCwwcp/`）。已安装副本 helper 实跑正 anchor、外链、标题链接 exit0；缺失带fragment路径与root-relative错链 exit1，临时安装测试数据在 `/tmp/ticket53-installed-fixtures-final/`，逐条输出 `/tmp/t53-verified-installed-*.err`。R1：两个独立 SKILL 共置证据归属/失效合同，要求 revision、dirty diff、关键输入/依赖工具链、验证资产版本、范围假设，变化标 stale，旧证据只留历史，重跑受影响覆盖恢复。R2：轻量 Markdown destination 解析，按 scheme/path/fragment 分开检查本地相对 Markdown 存在及索引成员，不查锚点。R3：checker wrapper 核 exit、stderr、严格 `OK`/`FAIL` 摘要及诊断数量，注入退出码2、带stderr伪合法FAIL、无诊断异常退出均 fail。静态 checker 最终仍仅 9 条基线 acceptance/evidence 断链；全套剩下7失败与此前报告的失败组相同。worktree 最终干净，HEAD `06b9257cf93308daa329f15895322f4a31272cc7`，merge-base 为已合并 integration `60ecb1bbb4b10308ea6b20a498654c12f30fdcef`，`git diff --check` exit 0。真实应用端到端不在本修复范围。

## 交付物

- `skills/validation-cycle/create-verification-skill/`：SKILL.md（采访仓库→生成→播种覆盖映射→自证→交接；启动/doctor/驱动/证据/清理/隔离机制全保留）、LICENSE（上游 pstack/LICENSE 字节一致，SHA256 `bc957ca6…77b200e`）、NOTICE.md（revision `88d47514…`、采用与适配范围）、agents/openai.yaml（allow_implicit_invocation: false）、`references/feature-map-example/`（README+search+create-record 三文件，改写上游示例）、`helpers/feature-map-lint.py`（本仓新写，可执行）。
- `skills/validation-cycle/maintain-verification-skill/`：SKILL.md（clean/changed/blocked 三态、只改验证、源读波子代理、现场驱动三条不变量、verified-unreachable 前置条件、triage 三分）、LICENSE、NOTICE.md、agents/openai.yaml。
- `scripts/check-skills.py`：新增 `verification_skill_problems`（含 `VERIFICATION_SKILLS`/`VERIFICATION_REQUIRED_FILES` 常量与登记）；两新 skill 加入 `MIGRATED_CONTRACT`（「委托继承」）。未改动 #54 的 `formal_verification_problems` 及其登记。
- `skills/general/research-os/references/migration-boundary.md`：追加两行已迁移条目。
- `skills/general/research-os/SKILL.md`：仅追加一段入口指针（行为验证点名路由，含与形式化分工），未重写其他段。
- `README.md` / `skills/README.md`：仅追加本票两行能力清单。
- `tests/test_spec48_ticket53.py`：23 用例 + 28 子测试。

## 逐 AC 证据

1. **适配与许可共置**：LICENSE 与上游字节一致（SHA256 比对通过）；NOTICE 记 revision 与适配范围。测试 `LicenseAndProvenance`。
2. **机制保留、覆盖要求分别明确**：create 侧六机制关键词检查通过；create 要求「驱动一个已映射特征（一个就够）」，maintain 要求「每个特征文件都要有源覆盖」「每个特征都要被真实驱动一次」，测试 `MaintainSkillContract::test_coverage_requirements_distinct_from_create` 断言两侧差异。
3. **草稿与失败如实**：create「只能标为草稿」「执行失败或项目不可达时如实说明，清理后保留证据」；maintain「未执行的覆盖如实标为待执行，不冒称已验证」。测试断言这些短语存在。
4. **helper 正反例**：`feature-map-lint.py` 对随附示例目录退出 0（正例）；孤儿文件与死链两个反例各退出 1 并点名问题文件。`FeatureMapLintHelper` 三用例。
5. **安装/引用/verify 原则**：checker 仅余 9 条历史 `docs/acceptance/**`→`evidence/*.tar.gz` 断链（基线既有），非历史问题 0 条；入口指针与迁移登记测试通过；两 SKILL 均写明行为验证不冒称定理/形式化。

## 红绿记录（uv，pytest 经 `uv run --with pytest`）

- 原实现记录红：`git stash` 移除本票实现后运行票测，报告 **24 failed, 5 passed**；shell 记录 `RED_EXIT` 管道值为 0，失败数为准。本次没有重做该破坏性 stash 操作。另以 integration 基线临时 archive 副本重放，仅本票测试结果为 25 failed、4 passed（退出 1）；该副本缺失基线未追踪的新技能，不等于完整原始红态。
- 绿：恢复后同命令 → **23 passed, 28 subtests passed**（0.38s）。
- 原实现记录称全仓回归前后失败集一致，为 7 条既有失败（policy_gates、config_contract×4、final_contract_fixes、review_fixes），并记录 ticket54 `test_current_tree_has_no_new_breakage` 的 stash 态变化。本次独立复验当前树得到 92 passed、7 failed、70 subtests passed，失败名与上述既有组一致；因本次没有在修订前另建同版本对照，保留为既有记录但不将“前后完全一致”视作本次已独立证明。
- checker 全量：`python3 scripts/check-skills.py` 输出 9 条问题，全部匹配历史断链模式，`FAIL: 9 个问题` 与基线相同。

## 限制与边界

- 本票只做静态/结构合同与 helper 局部正反例；未在任何真实应用上执行生成的 verify skill，不宣称软件行为验证能力已被端到端运行验证。
- 未执行上游 feature-map-example 原文件逐字复用：示例为本仓改写（NOTICE 已注明），机制保留；上游原文正文与许可已亲核（LICENSE 字节一致，SKILL.md 全文阅读后改写）。
- `check-skills.py` L965 nested-if 为 #54 既有代码风格告警，不属于本票范围，未改动。
- worktree 共享主仓 .git；本票所有 git 写操作仅限本分支，未动 integration/主目录文件。

## 后续核验与修订（2026-10-21）

原提交的维护 Skill 在独立安装时指向创建 Skill 的 helper，违反独立资源可达。改为要求维护 Skill 自己按目录 glob 与 README 相对链接规则轻量检查；NOTICE 一并更新。README 路径测试原来把根 README 的 `skills/validation-cycle/` 前缀错误地改写到 skills README 场景，按两个 README 的各自相对链接修正。

- 修订前本地 helper 不存在测试红：`uv run --with pytest python -m pytest tests/test_spec48_ticket53.py::MaintainSkillContract::test_independent_install_has_its_feature_map_helper -q`，1 failed（目标资源未共置）。该临时测试因最终方案选择无依赖而撤回，不作为持续回归断言。
- 原提交缺乏未实现票测基线，不能 stash 移除已提交实现。改在 integration 基线临时 archive 副本放入票测重放：25 failed、4 passed，退出 1；此为损坏副本回放，不追认为当时原始红证据。
- 绿：`uv run --with pytest python -m pytest tests/test_spec48_ticket53.py -q` → 23 passed、28 subtests passed（退出 0）。
- `python3 scripts/check-skills.py` → 9 条历史 evidence 断链（退出 1），未增加本票问题。全仓 pytest → 92 passed、7 failed、70 subtests passed；7 个失败与既有票面所述历史组一致，但无修订前同版本全仓运行记录，故不声称严格证明前后无差异。
- Skills CLI 缓存版本对两个新 Skill 在可丢弃 `/tmp` 项目 `--skill create-verification-skill maintain-verification-skill --agent codex --copy --yes` 安装成功；最终副本共 12 个文件，创建 Skill 的 helper 在安装副本内正例 exit 0。只证明文件安装与资源可达，不代表目标宿主已加载或真实应用行为已验收。
- 最新 integration 验收：`git -C <worktree> rev-parse integration/spec-48` 为 `e84f779d78755937a59d46364e14cc6496aa2b03`；`merge-base HEAD integration/spec-48` 为同一完整 SHA，确认 #49/#54 已在当前分支基线。对照 `tests/test_spec48_ticket49.py` 为 22 passed；`tests/test_spec48_ticket54.py` 为 25 passed；本票 23 passed、28 subtests passed。checker 输出与已记录基线相同 9 条历史 evidence 断链。分支最初 HEAD `19f01db`，含自包含修订 `2e6ff56` 与验收记录 `e61a33f`；本 notes 更新后另有文档提交。没有另造 merge commit，因为 `integration/spec-48` 已是该分支祖先。

## 简化自检（KISS/YAGNI/DRY）

- helper 单文件、无依赖、无配置面；示例仅 3 文件；checker 常量复用 #54 的 HOST_BINDINGS/MODEL_PIN 而非复制正则；未引入专用测试 runtime。
