# Ticket #60 C01 实施记录

| Work unit | 状态 | 产物与验收证据 | 下一步 |
|---|---|---|---|
| C01：paper-compile-repair 委托授权合同修复 | done | 产品 commit `5ddae2e8ad1fbe61ec0ae583c9bc6e23c05083ec`、red-test strengthening `056cbbf859b7993e1808f8a9c4478a5f52b18b61`；安装后候选红→工作绿、#57 13 tests、checker 原 9 条 archive diagnostics；报告 `/tmp/spec48-contract-fix-A/REPORT.md` | 交由 parent 另派 merger 与新独立复审；不外推为 #60 通过 |

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

- 实际变更严格限于 `paper-compile-repair/SKILL.md`、`references/bounded-repair.md` 与 `tests/test_spec48_ticket60_c01.py`。候选到最终文件集的 patch artifact `/tmp/spec48-contract-fix-A/actual.diff`，SHA-256 `0555cd3659469ce2cb6fbc17cb0902b231ad9099d724c776c654628f1cea2db2`。
- 安装后 public seam：用 `SPEC48_C01_BASELINE=f7b03400a4b77bc77265e9076199977815163a87` 安装候选旧正文，先因旧普遍 gate `原稿仅应用本轮用户明确认可的具体 diff` red，returncode 1；日志 `/tmp/spec48-contract-fix-A/logs/c01-installed-red-baseline.log`，SHA-256 `7011c7c4ffe1ebbbfa902f7397ed7c572d410b72adf3e5f4426db1639f679e84`。当前合同安装后 green 1 pass、returncode 0；日志 `/tmp/spec48-contract-fix-A/logs/c01-installed-green-final.log`，SHA-256 `fd28992562d6e4f1ee1de9109933954dba9edaf4138105529701952d1a885186`。Skills CLI 1.7.4 通过 tracked helper fixture 实际安装；测试还扫描全文旧 gate、授权内分支与安全边界。
- integration tip 合并后最终 C01 安装测试 1 pass、returncode 0；日志 `/tmp/spec48-contract-fix-A/logs/c01-post-integration.log`，SHA-256 `3a3e8e8e80e042d805d4b009cb10cbcb2cfeec5b04382e4dd59631be3ad72684`。#57 回归 13 pass、returncode 0；日志 `/tmp/spec48-contract-fix-A/logs/ticket57-post-integration.log`，SHA-256 `553fc5f8ab95b0e7e4cf7c61a53f404ec11f3e85c0e8eb9569d32e9b078db53c`。
- 合并后 checker returncode 1，仍只有已知 9 条 `docs/acceptance/**/evidence/*.tar.gz` 诊断，日志 SHA-256 `acbd51e6f5e308fc570dced0eb6f46d3c9df9eb5de0323fc74271c38a0ff1cbf`，与历史记录一致；未改归档、allowlist 或 6 项历史全套失败，且未运行全套。
- 命令均串行、树外 `TMPDIR=/tmp/spec48-contract-fix-A/tmp`、单命令上限 180 秒。TDD skill 缺失，因此按用户要求的最小安装后 red→green seam 实施，不声称已加载该 skill。
- 交付报告：`/tmp/spec48-contract-fix-A/REPORT.md`，包含 finding 响应、实际 diff 指针/哈希、命令与日志 hashes、分支和 worktree、历史失败限制及 parent handoff。
- 既有 9 条 archive 与 6 项历史失败只记录、不修复、不隐藏。fresh 独立审查由 parent 后续另派，本 worker 不自判 #60 通过。
- 本 unit 不代替 merger 或独立 reviewer 判定 #60 最终通过。交付前只在本分支 merge 明确的当前 integration tip 并复验；父 agent 另行派发 merger 和独立复审。

## Deviations

- 初次查找 TDD skill 时只检查了 `~/.agents/skills` 与 `~/.codex/skills`，后续在 app-managed skill 目录找到并完整读取。未因此改变用户指定的安装后 seam、测试实现或验证范围；无需更改产品代码。
