# Ticket #59 独立 review / merge verification

## 状态

- 合同与实际 diff 审查：done；R1–R4 定向修复通过，新增阻断 R5；本文件含逐 AC 裁决。
- 干净 archive 验证：done；证据根 `/tmp/research-os-spec48-ticket59-final-review/`，五 mutant 全拒绝、六个具体输入合同回放、四种真实 CLI 安装、精确基线对照均已落盘。
- 唯一 merger 裁决：done（REJECT，不 merge）；因 R5 未执行 no-ff merge 或合入后复验，仅提交本 review notes，不修改产品。下一步由实现者补齐 R5 后再独立复验，不在本轮派发或代修。

## 范围与约束

- 2026-10-21，Asia/Shanghai。按本轮明确指定 reviewer / 唯一 merger 直接执行，不继续派发、不实现 feature；20% 上下文上限内分段审查/验证/交接。
- 唯一仓库写域为 integration-spec-48，初始 `bc35b36a9b7aee57f003967c67b5bca6485ab891`，初始 clean；待审 tip `af5e3864bf41c02c9bbf034411b4faebf1546a8f`。不动源 checkout/主目录、不用 jj、不 push/PR/issues、不清理 worktree。
- 已读 Multi-Agent、model-availability、pstack-models、CODING_STANDARDS；本轮无模型调用或动态 workflow。review 加载 `/Users/rolex/.pi/agent/skills/writing-for-agents/{SKILL,SKILL-MECHANICS}.md`、`/Users/rolex/.codex/skills/pre-implement/SKILL.md` 与主仓库 `.pi/skills/tdd/SKILL.md`（仅只读）。
- 测试 seam 沿用 spec 的安装后包、静态合同与现有 checker/helper；干净 archive，树外 TMPDIR，Python 一律 uv。本轮不重造 runtime 或补追首红。

## Deviations / 证据边界

- 源实现 notes 披露当时未找到 tdd/pre-implement/writing-for-agents/SKILL-MECHANICS；保留该过程偏离。本轮发现可用指针并加载不能倒推源当时加载成功，也不追认最初 red。
- 静态合同、反例和 CLI 安装不证明真实科研质量、模型遵循、实际长期累计扣账、所有宿主交互或后台服务。

## 最终裁决：REJECT / 新增 R5（P1，安装许可闭合）

**定位**：待审 tip 的 `docs/upstream-sources-and-licenses.md:362–366` 将新增 `research-os/playbooks/continuation.md` 登记为改编自 pstack，并称其位于“自带许可证与来源文档随包”的入口包。实际 `skills/general/research-os/LICENSE:3` 为 `Copyright (c) 2026 Matt Pocock`；该包 28 个文件没有 Lauren Tan 版权文本，也没有固定 pstack revision 的来源说明。不能用这个原有 LICENSE 代替本次采用资产的归属。

**独立最小复现**：Skills CLI 1.7.4 从干净 `af5e386…` archive 单独安装 `research-os`，exit 0；`install-entry_only/.claude/skills/research-os/` 全部 **28/28 文件**逐文件 SHA256 与 archive 相同。对所有已安装文件全文查 `Lauren Tan` 结果为空，唯一含 `MIT License` 的文件是 `LICENSE`（Matt Pocock）；不存在本次 pstack NOTICE 或完整 Lauren Tan MIT。另三个安装中能找到的完整 pstack 文本在 `research-improvement/UPSTREAM-LICENSE.md`，它不是入口单包安装的资源，也未被入口声明为该许可前置。

**影响与要求**：原 brief 明确“MIT 版权文本随独立技能共置”，#59 AC1/AC6 与父 spec 要求采用来源许可和独立安装资源闭合。入口单独安装带出了新 continuation，却没带该采用记录对应的版权/许可；仓库级 docs 不随这个 Skill 安装。此为交付要求与实际包不符，不对改编是否达到版权法的实质性复制门槛作法律判断。当前 checker 和绿测均不能排除此问题，故即使 R1–R4 已修也不能整票接受。

**最小后续方向（未实施）**：在 research-os 包内共置固定 pstack 来源/revision/适配范围与完整 MIT（保留原有 Matt Pocock LICENSE，不覆盖它），并让入口单包真实安装及相应缺失/截断反例覆盖这些资源。不要把 research-improvement 强行变成通用 continuation 的运行前置。本轮不补 feature、不重造 runtime。

证据：`installed-audit.json` 的 `entry_license_finding`、`logs/cli-entry_only.log`、`logs/LICENSE-finding-evidence.log`、`logs/upstream-sources-and-licenses.md-finding-evidence.log`。固定 pstack MIT SHA256 为 `bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e`；入口现有 LICENSE 为 `0e7ac423bf2c6e223b7c5b156f8cf72da49d748e56a1641402c31f22ad07dbb5`。

## R1–R4 原 findings 响应验收

- **R1 通过（合同）**：叶明确直接调用与委托级联不同入口，已授权第二轮仅核原轮数/写域/剩余额度，不需重新点名；pickup 不再索要恢复会话本轮批准清单；composition-map 区分已迁移内部能力与未迁移叶/独立顶层。以三轮授权、已用一轮的具体输入核对第二轮可续、第四轮不得进入；不推导任何新写权限。
- **R2 通过（合同/安装）**：paired 的普通非付费非作业恢复没有 setup、没有两模板，按原委托/暂停记录核实后在原有界首轮继续，不增加新轮。相同安装进入费用/作业批次，只阻断该分支。代表安装两模板真实存在，但项目账本/有效批次授权仍必须另核，不把模板存在当运行许可。pickup 的 5 个反引号必读资源按条件逐个解析，而非仅检查 Markdown 链接。
- **R3 通过（合同）**：叶、loop-methods、dependencies、composition-map 的 reviewer 缺失处理统一 blocked；只读自查不计 fresh review、不记改进轮完成。没有将当前 reviewer 自评当第二个独立审查者。
- **R4 通过（五个已报告损坏的定向守护）**：在完整 head archive 分别实际修改 quota-reset / resume-trust-summary / auto-public-tracker / incomplete-license / broken-branch-map，逐项运行完整 checker 与 #59 测试；五项两入口都 exit 1，checker 均产生超出原 9 条的明确诊断。自动外发损坏锚点使用修复后仍存在的“先展示拟改内容并等用户确认”（原报告带句号的位置已变为逗号），保证真正改动而非零替换。每次 finally 用 apply_patch 恢复，最终全树 SHA256 与损坏前一致。此通过仅覆盖具体反例，不宣称静态分析能理解任意语义或覆盖 R5。

## 逐 AC 裁决

| #59 AC | 裁决 | 实际证据与边界 |
| --- | --- | --- |
| 1 持续/暂停/恢复、决策记录、recall/reflect/correct、许可资源 | **未通过** | continuation 保留检查谓词/最小步进/安全交接/事实恢复，改进日志记录摩擦；已亲读固定上游 autonomous-run/pause-safely/session-pickup、recall/reflect/correct 和 MIT。research-improvement 全文 MIT 正确，但入口包新增 continuation 的共置许可/来源有 R5。 |
| 2 真实经过时间、跨 worker/重试/恢复累计、非固定比例收束 | 通过（合同） | continuation:11–13,29–30；mandate 研究额度；improvement 批次启动核对：实际消耗、运行中最坏预留、本次最坏消耗、attempt/并发/重试/过期。未知保留，不重置，没有固定百分比。没有真实长期计时/费用扣账验证。 |
| 3 停滞换方法、死路交接、不降标准、失败重开 | 通过（合同） | continuation:17–19,28；mandate 完成/停止；失败尝试和重开新变量必须可追溯。未验证真实数学路线或穷尽性。 |
| 4 恢复目标、授权、原始产物、义务与作业，不信成功标签 | 通过（合同/资源） | pickup、continuation 与改进模板；无 setup 正例/批次缺模板反例/有模板无运行许可/继承轮次人工回放，`manual-contract-replay.json`。没有启动真实作业或模拟模型遵循。 |
| 5 项目改进留记录，公共行为确认，不自动外发/扩权 | 通过（合同） | 叶第9节、日志流程/工具改进；外发 mutant 被拒；目标替换与公共行为/外部 tracker 只阻对应动作，权限不随额度变大。无任何 tracker/外部写入。 |
| 6 automate-me 非必需，真实宿主边界，安装资源/行为合同 | **部分通过，整体未通过** | 无 automate-me 运行前置，不将文本当后台，缺真实子代理/reviewer 为 blocked；真实 CLI 与 15 映射/5 pickup 条件路径核验通过；但 R5 阻断单入口包许可闭合。 |

## 独立执行与精确基线

所有脚本/日志在上述证据根；`replay.py`、`finish_checks.py`、`commands.json` 记录 cwd/argv/exit，Python 用 uv offline，`TMPDIR=<证据根>/tmp` 在快照树外，禁 bytecode/pytest cache，复用本机缓存 pytest。`git archive` 分别导出 bc35b36 与 af5e386；只在外部快照 `git init`/`git add -f .` 满足 tracked-files seam，未在源 checkout 写入。

| 执行 | 结果 |
| --- | --- |
| `git diff --check bc35b36 af5e386` | exit 0 |
| head 关键 `tests/test_spec48_ticket{49,50,52,53,54,59}.py` | exit 0，**134 passed, 61 subtests passed**；含原登记 checker、有界一次重派和行为 helper 正反例 |
| baseline 全套 `tests scripts/test_check_skills_ticket*.py` | exit 1，**7 failed, 184 passed, 93 subtests passed** |
| head 同全套 | exit 1，**7 failed, 202 passed, 105 subtests passed** |
| baseline/head 完整 checker | 均 exit 1，原始输出逐字节相同，仅下列 9 条 archive 断链 |
| 五 mutant 各完整 checker / #59 测试 | 均 1 / 1，不接受只比较原有非零退出码；额外诊断见 `mutants.json` |
| 全部 mutant 恢复后重跑 #59 | exit 0，**18 passed, 12 subtests passed**；所有 archive 文件 SHA256 与损坏前一致，`git diff --exit-code` exit 0 |

七个失败 pytest node ID **逐个完全相同**，且 JUnit failure 属性（type/message）也逐项字面一致，见 `baseline-comparison.json`、`exact-failure-attributes.json`。不泛过滤、不 skip/xfail、不改产品掩盖失败。JUnit classname 含不同 archive 绝对目录，最初 harness 直接比较 classname 因此停下；改用原始 pytest node ID 比较，并额外字面核对全部 failure 属性。该修正属于树外证据工具，不是产品修复或忽略新失败。

```text
tests/test_check_skills_policy_gates.py::PolicyAndGates::test_checker_green_and_leaf_baseline
tests/test_config_contract.py::ConfigContractTests::test_gate_baseline_and_counterexamples
tests/test_config_contract.py::ConfigContractTests::test_shipped_templates_and_full_checker
tests/test_config_contract.py::ConfigContractTests::test_valid_policy_and_log_fields
tests/test_config_contract.py::ConfigContractTests::test_valid_role_table
tests/test_final_contract_fixes.py::FinalContracts::test_full_cli_damaged_declarations_refs_and_readme
tests/test_review_fixes.py::ReviewFixes::test_compute_limits_are_per_unit_not_summed
```

九条诊断的精确文件/行号/目标定位（路径均在 docs/acceptance/，逐字节相同的原始完整输出见两份 checker log）：

```text
v2-release-host-regression.md:93 -> evidence/v2-release-host-regression.tar.gz
v2-final-contract-fixes.md:53 -> evidence/v2-final-contract-fixes.tar.gz
v2-release-gate-combinations.md:49 -> evidence/v2-release-gate-combinations.tar.gz
v2-merged-host-smoke.md:54 -> evidence/v2-merged-host-smoke.tar.gz
v2-accept-validation.md:98 -> evidence/v2-accept-validation.tar.gz
v2-accept-hosts.md:9 -> evidence/v2-accept-hosts.tar.gz
v2-final-contract-independent-verify.md:41 -> evidence/v2-final-contract-independent-verify.tar.gz
v2-final-contract-independent-verify.md:53 -> evidence/v2-merged-host-smoke.tar.gz
v2-accept-remediation.md:92 -> evidence/v2-accept-remediation.tar.gz
```

## 最终真实安装

真实 CLI 命令为 `node <缓存skills/bin/cli.mjs> add <干净head快照> -s <各包> -a claude-code -y --copy`，隔离 HOME 和临时 Git 项目；CLI 版本 1.7.4，各次 exit 0。逐包枚举全部文件 SHA256，无缺失/新增/字节差异；不是手工 copytree 或重点文件抽查。

| 组合 | 文件/实际 Markdown 链接 | 精确资源结果 |
| --- | --- | --- |
| research-improvement 单包 | 9 / 22 | 所有本地链接可达，完整 Lauren Tan MIT 与固定上游逐字节一致；缺 research-os 共享合同，按声明 blocked |
| research-improvement + research-os | 37 / 79 | 唯一缺链是 baseline 已有的可选 `research-os/SKILL.md -> ../interrogate/SKILL.md`，原样登记，不泛过滤；pickup 3 个普通分支资源存在，2 个 setup 模板按费用分支缺失，不能称全部链接零断 |
| 代表分支八包 | 78 / 113 | 上述两包 + setup-research-os / proof-review / paper-claim-audit / paper-compile / experiment-audit / interrogate；全部实际链接可达；15 个仓库源/扁平映射逐条一致，选中四个组合分支及 pickup 5 个必读路径实际可读 |
| research-os 单包（R5 最小复现） | 28 / 57 | 与源全部字节一致，1 个上述可选 interrogate 缺链；pstack 来源/版权文本缺失，唯一 MIT 为 Matt Pocock |

setup 的 workspace 模板有四个明示待填的尖括号示例链接，单列在 `template_links`，没有当作现存文件或有效安装链接计入 113。其他未选兄弟分支的缺失按实际清单保留，不冒称安装或执行。完整反引号清单、全部文件哈希/链接/映射在 `installed-audit.json`；不是只凭 Markdown 链接计数证明依赖闭合。

## 交回与未完成项

- 已拒绝合入，integration 产品树仍停在 `bc35b36a9b7aee57f003967c67b5bca6485ab891`；本次提交只增加此 notes。待审源完整 tip 仍为 `af5e3864bf41c02c9bbf034411b4faebf1546a8f`（修复 `a2cc3b451d8d45c8eb34b13521642a0a6565e36a`，源合基线 `08749d4a2bfd983f5569ee0d2b8513d8ebc1ea94`）。没有 no-ff merge，所以没有“合入后复验”可宣称。
- 未完成：R5 产品补齐及缺失/截断入口许可反例、修复后的新一轮独立 review，之后才考虑唯一 merger no-ff merge 和最终六票/全套复验。本轮不继续派发或代修。
- 未验证：真实开放科研、数学真值、付费/远程生产作业、真实跨模型调度、长期后台执行、所有宿主或全部技能组合。过程偏离和原始首红缺证据仍保留，不以本轮验收追认。

---

## R5 修复后新独立 review round（2026-10-21）

### 本轮状态（前述 REJECT 是历史裁决，不改写）

- 范围/规则/历史核对：done；本轮按明确授权直接审查，不继续派发、不新增 feature，不调用受限模型或动态 workflow。仓库唯一写域为本 integration worktree，使用 Git，不碰源 checkout/主目录。
- R5 差异、固定上游与独立反例：done；起点 `8b21f78385d89b5f600ccbef7843278a048be0fa`，待审 `ea1e162979156d1e06b77f179dca06eaba888eae`；产品基线 `bc35b36a9b7aee57f003967c67b5bca6485ab891`。证据根 `/tmp/research-os-spec48-ticket59-r5-review/`（仅测试归档/临时项目，不是其他仓库写域），四个 R5 mutant 均真实 red，恢复后整 #59 20 passed/12 subtests。
- 六票关键、全量与精确基线比较：done；136 passed/61 subtests；head 全套 7 failed/204 passed/105 subtests，baseline 7 failed/184 passed/93 subtests。七个原始 node ID、JUnit failure type/message 属性逐项相等，九条 checker 诊断原始字节完全相同。
- 唯一 merger 裁决/合后复验：done；新 round ACCEPT（仅安装/结构/文本合同），无新增阻断；no-ff merge `d4fd5ed0f8629a1678e9c92e07722ee894ad8ae8`，双亲是起点 8b21f78 与精确源 ea1e162。合后干净 archive 的六票/全量/精确基线对照及入口单装全部复验，见 `postmerge-verification.json`。

本轮复用前轮 R1–R4 的详细通过证据，已核对相关产品/测试未回退；本次完整重跑 #59 与 #49/#50/#52/#53/#54、全套及九诊断。仅追加本文件，不写 orchestrator notes；已加载 pre-implement 与 writing-for-agents/SKILL-MECHANICS，仍不追认实现者原始首红或历史工具加载。

### 亲核结果、逐 finding 与 AC

- **R1：通过，未回退。** 前轮实际三轮授权/第二轮恢复、第四轮不得进入的合同回放仍有效；`af5e386… → ea1e162…` 的叶 SKILL、composition-map、pickup 等产品逐字节未变。本轮重跑整 #59 覆盖已授权轮次/恢复。未重新声称执行了真实模型循环。
- **R2：通过，未回退。** 普通无 setup 与费用批次条件依赖的前轮实际回放复用；本轮真实入口单装仍不含 setup，pickup 五个反引号必读路径中三个普通路径存在、两模板按批次依赖缺失。代表八包真实安装后五路径全在，15 行源路径→扁平路径逐行核对；仅选中分支要求实际存在，未选兄弟缺项保留，不泛过滤。
- **R3：通过，未回退。** 缺 reviewer 的 blocked/只读建议不冒充独立完成，相关叶、loop-methods、依赖文件与前轮完全相同，整 #59 正反合同检查通过。
- **R4：通过已有五个 mutant 的定向守护。** 复用前轮 `mutants.json`、补丁/原始日志和哈希恢复证据，五项真实 red 不重新冒称本轮运行。与前轮比本次 checker 仅新增 R5 资产检查/固定 SHA256/两份 MIT 字节比较，既有守护和相关产品未删改，#59 测试仅增加 fixture 资产与两个新测试；三项 R5 选测包括一项原有测试，不虚称新增三测试。本轮全票/联合/全量均复跑。
- **R5：通过，本轮独立重放。** 入口 `NOTICE-PSTACK.md` 明确 cursor/plugins、固定 revision `88d47514b82e7c44f00f2b2a72ff6dd12158038c`、原正文路径、采用范围、MIT/Lauren Tan 及不含 Cursor/cloud-worker/固定模型/transcript 假设。亲读 autonomous-run/pause-safely/session-pickup/recall/reflect/correct 正文及完整 LICENSE；所读七文件的长度与 git blob SHA1 均与固定归档 manifest 对应。适配保留最小步进/可检查谓词、检查点、安全暂停、原始事实恢复、流程摩擦改进；上游自动外发 backlog 未引入。
- 本轮分别实际删除 notice、删除入口 LICENSE-PSTACK、截断 notice、将 LICENSE-PSTACK 截为标题/版权行；四次完整 checker 均有新增明确诊断且 exit 1，整 #59 也均 exit 1（分别 12 failed/17 passed/3 subtests、12 failed/17 passed/3 subtests、1 failed/19 passed/12 subtests、1 failed/19 passed/12 subtests）。每次均用 apply_patch 恢复，完整快照文件 SHA256 manifest 与原值一致，最终 #59 为 20 passed/12 subtests。此为新独立反例证据，不是倒推最初 TDD red。
- 入口单包真实 Skills CLI 1.7.4：只选 `research-os`，30/30 全文件集合与字节一致，未安装 research-improvement；原 `LICENSE`（Matt Pocock）与 `LICENSE-PSTACK`（Lauren Tan）同在。完整 pstack MIT 1067 bytes，SHA256 `bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e`，与固定上游及 RI 许可逐字节相同；原 LICENSE 与 bc35b36 原值相同（SHA256 `0e7ac423bf2c6e223b7c5b156f8cf72da49d748e56a1641402c31f22ad07dbb5`），没有替换原包许可。56/57 条本地 Markdown 链接可达，唯一缺链仍是前轮精确登记的可选 `research-os/SKILL.md -> ../interrogate/SKILL.md`，不称零断链。代表八包 80/80 文件一致，113/113 实际链接可达，另四个 workspace 模板尖括号占位示例单列。
- **AC1 通过**：持续/暂停/恢复及适用 recall/reflect/correct 机制、固定采用说明与两种独立包完整许可闭合；证据为正文/manifest、真实安装与 R5 四反例。
- **AC2 通过（合同）**：wall-clock 与资源跨 worker/重试/恢复累计、unknown 保留、按状态收束不固定比例；相关产品与前轮未变，额度正反测试复跑。
- **AC3 通过（合同）**：停滞检验前提/换方法、真实死路如实交接、不降完成条件，保存失败路线与重开依据；continuation/日志与前轮未变。
- **AC4 通过（合同/资源）**：恢复目标/授权/原始产物/义务/活跃作业，不信旧成功摘要；R1/R2 合同及实际恢复资源闭合沿用前轮，五条 pickup 路径本轮实装重核。
- **AC5 通过（合同）**：项目改进留记录；公共套件行为、外发 tracker、越权动作保留确认；相关 SKILL/日志与前轮未变，相关反例测试复跑；本轮没有外发。
- **AC6 通过（约定 seam）**：automate-me 非必需、不冒称后台，单包/代表安装、资源和合同测试实际执行；不扩大为真实科研或长期后台证明。

### 命令、回归及范围保护

- 快照来自 `git archive <精确tip> | tar -xf - -C <独立快照>`，再在各快照 git init/add 满足 tracked-files seam。TMPDIR 在快照外 `/tmp/research-os-spec48-ticket59-r5-review/tmp`；uv cache 同证据根；`PYTHONDONTWRITEBYTECODE=1`、pytest 禁 cache，沿用已存在 pytest site-packages；所有 Python 经 uv，未用 copytree 假装安装。
- 原始命令/exit/cwd：`commands.json`、`logs/`；复现脚本 `review.py`（复用前轮通用运行/哈希函数但全新执行和日志）、`provenance_and_resources.py`。测试命令 `uv run --offline python -m pytest -q -p no:cacheprovider --junitxml=<证据文件> tests scripts/test_check_skills_ticket*.py`；关键命令显式列六票。实际 CLI 为 `node <既有skills/bin/cli.mjs> add <干净archive> -s <选中包> -a claude-code -y --copy`，各次独立 HOME/临时 Git 项目。
- 精确对照：`head-baseline-comparison.json` 保留七个 node ID 和 failure 属性；`logs/{baseline,head}-checker.log` 原始字节相同，均为本文件历史章节原样列明九诊断，不新增 skip/xfail、宽泛过滤或改产品掩盖基线问题。
- 许可/采用与未回退：`provenance-and-no-regression.json`；新反例：`r5-mutants.json`、对应 JUnit/原始日志；全部文件恢复：`head-manifest.json`；实装：`installed-entry.json`、`installed-representative.json`、`installed-resources.json`。
- source 已含 8b21f78（旧 REJECT notes），本次整合不是覆盖其他 merger。#50 swarm 的「缺证据有界重派一次」、#52 interrogate 的始终只读、#53 创建/维护行为验证与 helper 及六票相关测试均与 integration 基线未变。入口只增加 continuation 行/说明，迁移登记只追加 #59 一行，已有迁移行未删除；共享旧测试只适配 pickup 原授权和新增 continuation 路由。KISS/YAGNI/DRY 自检：本轮无产品代修/新 runtime/新依赖或功能，完整许可校验是交付守护；`git diff --check` 通过。

### 本轮限制与偏离

- 只验证离线固定上游归档与其 blob manifest，不对未归档上游作在线认证或法律判断。实现者 R5 的先红后绿仅作为其记录；本轮独立反例不能倒推首红。
- 本轮复用前轮 R1–R4 深入回放/五 mutant 证据，未重新做相同人工输入/五 mutant；已用精确 diff 确认其产品未变并重跑全部相关测试。没有代替模型执行或新行为 runtime。
- 未做真实开放科研/数学真值、真实跨家族调度、实际费用或 wall-clock 扣账、付费/远程生产作业、全部技能组合、所有宿主、长期后台。全部 pass 仅限 spec 已确认的安装/结构/文本合同 seam。原过程偏离保留。
- 不 push、不 PR/issues、不清理 worktree，不写其他 checkout 或 orchestrator notes。合后状态与完整 merge tip 见下续记。

### 合入后复验与交回

- 已无冲突地 `git merge --no-ff --no-edit ea1e162979156d1e06b77f179dca06eaba888eae`，得到 **`d4fd5ed0f8629a1678e9c92e07722ee894ad8ae8`**；父提交依次为 `8b21f78385d89b5f600ccbef7843278a048be0fa`、`ea1e162979156d1e06b77f179dca06eaba888eae`。作者/提交者为现有身份 `rolex <torolex@163.com>`，未覆写身份或关闭 hooks。合入结果与待审源完整 tree OID 同为 `b1336ad678b7637616a12cdd546f891da2618a36`，没有语义解冲突或代改产品。
- 对该 merge 重新 `git archive` 至独立 `merged/`，再次运行六票关键 **136 passed/61 subtests**、全套 **7 failed/204 passed/105 subtests**、checker **9 个历史问题**。`merged-baseline-comparison.json` 断言七个原始失败 ID 和 JUnit failure 属性逐项与 bc35b36 一致；checker 输出仍与 baseline 原始字节完全相同。没有把非零全量称作全绿。
- 对该 merge archive 再次真实 CLI **只装 research-os**：30/30 文件逐字节一致，两份 LICENSE 与 notice 保留，不带 research-improvement；完整 MIT 1067 bytes/固定 SHA256 与前验相同；仍是 56 可达链接 + 1 条精确登记的可选 interrogate 缺链。证据 `installed-merged-entry.json`、`logs/cli-merged-entry.log`。完整合后快照文件哈希在执行前后不变；`postmerge.py`、`postmerge-verification.json` 记录命令及断言。
- 亲核旧 `8b21f78` 的 verification notes 是当前文件的**逐字节前缀**，原 REJECT 章节、findings、限制和未完成历史均未删除或倒改；只有本新 round 追加验收并关闭 R5。本次仓库新增写入仅本 verification notes，产品由原源提交及 no-ff merge 引入。最后 notes 提交只含本文件，不改变已验证产品树。
- 交回裁决：**ACCEPT #59（限定 seam），已 no-ff 合入，R1–R5 无剩余阻断**。剩余为原有七项失败/九诊断与上述明确未验证事项；未 push/PR/issues/清 worktree。完整最终记录提交 tip 由提交后 `git rev-parse HEAD` 交回，避免自引用 hash。
