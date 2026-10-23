# Ticket #60 C01 实施记录

| Work unit | 状态 | 产物与验收证据 | 下一步 |
|---|---|---|---|
| C01：paper-compile-repair 委托授权合同修复 | done | 产品 commit `5ddae2e8ad1fbe61ec0ae583c9bc6e23c05083ec`；安装后 red→green、#57 13 tests、checker 原 9 条 archive diagnostics；报告 `/tmp/spec48-contract-fix-A/REPORT.md` | 交由 parent 另派 merger 与新独立复审；不外推为 #60 通过 |

## 入口与范围

- 入口判定：这是用户明确指派的 C01 单元实现；依据 worktree、spec/findings 和验收切片均已限定，适合在本 work unit 内直接执行。用户禁止改 integration/主目录、push、tracker 和继续派发，均遵守。
- 任务边界：只处理 `paper-compile-repair/SKILL.md`、其 `references/bounded-repair.md` 与对应测试；不得改其他 Skill、归档 evidence、静态 checker 或既有失败基线。
- 上游：先在隔离分支 fast-forward merge 候选 `f7b03400a4b77bc77265e9076199977815163a87`，merge 成功，当前 HEAD 即该候选。
- 预算：遵守单 work unit 不超过上下文预算 20%；若接近预算，先将精确剩余切片与证据写入本文件及 `/tmp/spec48-contract-fix-A/REPORT.md`。

## 已读规则与输入

- 已读 `~/.agents/Multi-Agent.md`、`~/.agents/model-availability.md`、`~/.agents/CODING_STANDARDS.md`，仓库 `AGENTS.md`，`writing-for-agents`、`SKILL-MECHANICS.md`、`pre-implement`。
- 已完整读取实际安装路径 `/Users/rolex/Library/Application Support/com.ai-toolbox/skills/tdd/SKILL.md` 及其 `tests.md`、`mocking.md`；用户明确指定了“安装后合同 seam”，因此直接在 Skills CLI 安装后的公共接口做集成风格 red→green，不 mock 内部实现。
- 已完整读取 `/tmp/spec48-ticket60-final-contracts/FINDINGS.md`、`COVERAGE-41.md` 和 `/tmp/spec48-goal-preflight/spec.json`。C01 是自然语言合同矛盾，不推断真实 agent 曾如何行动。spec ID3/4/17、TD5 及 #60 AC3 要求授权继承，同时保留安全边界。
- 已检查 `paper-writing/SKILL.md` 的委托内修复条款、TeX 构建安全参考、共享研究委托额度/授权合同与目标替换门。TDD 操作按 tracked `tests/spec48_workcopy.py` 建 fixture；Python 运行使用 `uv`。

## C01 findings 响应

- 原 finding 指出：基线构建、步骤 3、尚未形成的后续 diff、缺项零应用与步骤 4 的“仅应用已批准 diff”等正文都要求逐轮用户精确批准，导致已授权父委托进入该叶后仍不能执行普通有限修复；末尾继承段无法覆盖这些正文旧语义。
- 修复方向：独立请求只有在本次明确授权足以覆盖目标、文件、工具/命令、构建目录与副产物、时间/资源额度、执行分级和修复轮数时才可写；既有父委托有效覆盖同一边界时，在步骤正文映射并记录授权依据、完整 diff、基线与构建/副产物信息，不再逐 diff 请求用户确认。仅新增副作用、目标/假设替换、写域或外部变化才对受影响动作重新索权。
- 保留：只读请求不写源；完整 diff/基线/范围/命令与工具/构建目录/副产物/预算的展示与记录；TeX 输入闭合审阅及现有可验证 sandbox；并发源检查；目标/假设替换确认；外发、收费、资源批次与预算的既有授权；最多三轮且重试/恢复不重置额度；原 PDF、用户改动和失败日志不被覆盖/清理。
- 红测会通过 Skills CLI 安装单独的 `paper-compile-repair`，并同时核验安装后的正文和 `bounded-repair.md`，既要求两种授权分支又扫描正文旧的普遍逐轮批准/零应用条款，避免只测试尾部新增句子。

## 决策与验证记录

- 实际变更严格限于 `paper-compile-repair/SKILL.md`、`references/bounded-repair.md` 与 `tests/test_spec48_ticket60_c01.py`。完整 patch artifact `/tmp/spec48-contract-fix-A/actual.diff`，SHA-256 `66ca16c6e59ed83b7becd4d20ebeaad0c057b14daf2da6a19f2a847b70152b90`。
- 安装后 public seam：red 1 failure、returncode 1，日志 `/tmp/spec48-contract-fix-A/logs/c01-installed-red.log`，SHA-256 `e8d52d2dcf7678851d39a1ecb91b06febdcbca9c35ed79ed64d0b807681afd99`；green 1 pass、returncode 0，日志 `/tmp/spec48-contract-fix-A/logs/c01-installed-green-final.log`，SHA-256 `4760046a9dd9a97421342075f5baf54c83add1fc29d7896ca6f3aa5b5f4358f3`。Skills CLI 1.7.4 在使用 tracked copy helper 的 fixture 中实际安装；测试同时扫旧普遍逐轮审批语义与父委托/独立分支。
- 合并 integration tip 后，C01 安装测试 1 pass、returncode 0；日志 `/tmp/spec48-contract-fix-A/logs/c01-post-integration.log`，SHA-256 `25639752834c6e9f8119ac995307dcb6c9b02b892793c384818cbe44a628c975`。#57 回归 13 pass、returncode 0；日志 `/tmp/spec48-contract-fix-A/logs/ticket57-post-integration.log`，SHA-256 `88a69e116a594c7289cbb107f88420d639b393c0e9807fd539ada754df0646d9`。
- 合并后 checker returncode 1，仍只有已知 9 条 `docs/acceptance/**/evidence/*.tar.gz` 诊断，日志 SHA-256 `acbd51e6f5e308fc570dced0eb6f46d3c9df9eb5de0323fc74271c38a0ff1cbf`，与历史记录一致；未改归档、allowlist 或 6 项历史全套失败，且未运行全套。
- 命令均串行、树外 `TMPDIR=/tmp/spec48-contract-fix-A/tmp`、单命令上限 180 秒。TDD skill 缺失，因此按用户要求的最小安装后 red→green seam 实施，不声称已加载该 skill。
- 交付报告：`/tmp/spec48-contract-fix-A/REPORT.md`，包含 finding 响应、实际 diff 指针/哈希、命令与日志 hashes、分支和 worktree、历史失败限制及 parent handoff。
- 既有 9 条 archive 与 6 项历史失败只记录、不修复、不隐藏。fresh 独立审查由 parent 后续另派，本 worker 不自判 #60 通过。
- 本 unit 不代替 merger 或独立 reviewer 判定 #60 最终通过。交付前只在本分支 merge 明确的当前 integration tip 并复验；父 agent 另行派发 merger 和独立复审。

## Deviations

- 初次查找 TDD skill 时只检查了 `~/.agents/skills` 与 `~/.codex/skills`，后续在 app-managed skill 目录找到并完整读取。未因此改变用户指定的安装后 seam、测试实现或验证范围；无需更改产品代码。
