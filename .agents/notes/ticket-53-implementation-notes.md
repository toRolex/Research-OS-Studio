# Ticket #53 实现记录：交付可创建、维护的项目行为验证能力

日期：2026-10-21。分支 `t3/spec-53-verification-skills`，worktree `/Users/rolex/.t3/worktrees/Research OS Studio/t3-a3b0d13a`，基线 integration/spec-48 @ `e84f779`（含 #54 形式化资产，已安全合并、未覆盖其登记）。状态：#53 实现/独立安装复验 done；逐 AC 静态与票测通过；真实应用端到端未执行；待提交并合并最新 integration tip。

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
- Skills CLI 缓存版本对两个新 Skill 在可丢弃 `/tmp` 项目 `--skill create-verification-skill maintain-verification-skill --agent codex --copy --yes` 安装成功；只测试安装文件与 helper 正例，不代表目标宿主已加载或真实应用行为已验收。

## 简化自检（KISS/YAGNI/DRY）

- helper 单文件、无依赖、无配置面；示例仅 3 文件；checker 常量复用 #54 的 HOST_BINDINGS/MODEL_PIN 而非复制正则；未引入专用测试 runtime。
