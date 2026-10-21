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
