# 两条 reference 的复现与证据边界

所有命令从仓库根执行；Python 操作均通过 UV。测试驱动不是产品 orchestrator：它模拟用户逐条调用命令，固定模型／研究者提供的 candidate 和人工角色决定。没有真实模型请求、外部文献检索、社区 port 接纳或真实论文发布。

## 一次性或持久产物复现

```bash
uv lock --check
uv sync --frozen
# 必须是不存在的新绝对目录；需要长期保留证据时选择持久位置。
EVIDENCE_ROOT=/replace/with/new/absolute/research-os-reference-evidence
TEST_OUTPUT=/replace/with/new/absolute/research-os-test-evidence
RESEARCH_OS_E2E_OUTPUT="$EVIDENCE_ROOT" \
  uv run --frozen python tests/e2e/run_suite.py --e2e --output "$TEST_OUTPUT"
```

`/tmp` 只适合一次性本地复验；不能作为持久证据位置。每次运行使用唯一新目录，避免覆盖旧证据。

输出 `collection.json` 含完整 test ID 清单，`results.json` 明确 collected／selected／executed／passed／failures／errors／skipped；默认仅执行 tests/e2e，但先完整收集全树，禁止漏文件。全部测试运行用去掉 `--e2e` 的同一命令；本次只运行用户允许的 E2E，不借用其他叶子旧的“全量通过”计数。

产物目录：

```text
$EVIDENCE_ROOT/
  empirical-computational/
    requests/             # 每条显式用户请求，带真实 input digest/commit
    runs/                 # 成功、失败、预算耗尽的不可覆盖日志
    reports/              # workflow 结构化报告
    manuscript.json
    paper.txt             # 本地查看辅助，非第二 primary text
    paper.pdf             # 真实确定性 PDF
    stage.json
    confirmation.txt      # 本次 fixture 用户最终确认串，不是通用授权
    publications/reference/manifest.json
    .research-os/         # wheel setup 及 side-by-side update 证据
  mathematical-theoretical/
    statement.json
    proof.json
    review-statement.json # 显式 record projection，保留原 typed envelope
    review-proof.json
    review.json
    manuscript.json
    paper.pdf
    publications/reference/manifest.json
```

上述科研目录为临时 Git 仓库的完整副本；其中 commit／SHA-256 可核验，不使用产品仓库脏工作树冒充固定输入。命令 request 中 Python 路径属于临时 wheel 环境，**复制输出后不能直接盲目重跑旧绝对路径**。用相同 E2E 命令创建新 fixture/environment，或用户显式选择自己的 interpreter、写新 request 并重新 pin；旧 request 与失败现场不修改。

## 计算 reference

来自 wheel 内的 `_reference_projects/computational/experiment.py` 与 `data.json`，实际 CPU 计算四个固定值的常数均值 baseline，独立期望 MSE=1.25。

验收顺序：

1. 真 build wheel → UV 独立 venv 安装 → 清除 PYTHONPATH，wheel Python `-I` 证明 import 不来自 checkout → setup。
2. 用户逐项 research-charter／literature／gap／idea／novelty／reflect；每次验证输出、commit/digest pin、断言下一产物不存在。
3. 不伪造文献：queries=[]，gap unsupported，novelty inconclusive。它们是外循环停止与输入契约证据，不构成论文创新 claim。
4. 用户 design → prepare → run。先显式 ordinary 失败 exit 7，保留 failed-run；后以**新调用**运行真实 experiment。先固定结果，再 pin 包含 result 的 run commit。
5. analyze 只读 fixed run；assess-result-to-claim 将 `/statement` scope 的结果与同 scope Claim 连接 canonical Evidence。
6. 另一次用户授权的 design 只准一次 attempt；bounded_autonomy 首次失败后预算硬停，下一条写 marker 命令不得执行。
7. 所有运行、失败、请求、输出以原 bytes material 进入 Publication closure；稿件仅声称固定 fixture MSE。
8. 验证稿件／Assessment，渲染 PDF，stage preflight，错误确认拒绝，最终 digest 确认后 freeze，重复 freeze 拒绝、包不变。
9. 显式 side-by-side update、旧 commit export，逐文件比较真实失败 run、安装投影、Artifact 与 Publication。

## 普通数学 reference

命题为每个自然数 n，n+0=n。用户经公共 API 创建／确认 statement，再**单条 math-proof CLI**提交定义方程的普通论证，无 Lean 自动调用。证明保留 lemma map、attempt budget 和 stop reason。

当前独立 review API 只接受原始 record，不接受 CLI typed envelope；测试明确生成、pin record projection，在新 wheel subprocess 检查 reviewer!=author/user、真实 input bytes 与 isolation receipt。review verdict 和 human acceptance 是显式 fixture 输入，不是假装真实独立模型思考。review 不自动升级为六轴数学／human Assessment。

用户材料形成有限 Claim/Evidence、Manuscript；formal_verification 明确 not_applicable。之后与计算路径相同地 PDF → preflight → final digest freeze → immutable verify → 显式 update／历史恢复。普通证明产物可通过，不等于 Issue #24 的 accepted discipline 或统一 CLI 覆盖完成。

## Lean 4.19 历史结论与可移植复验

固定 mathematical reference 曾在隔离的官方 Lean 4.19 环境真实通过 build、axiom audit、statement comparator 与 kernel replay；历史命令和输出保留在 [`gates/leaf-lean419-reference.md`](../../gates/leaf-lean419-reference.md)。该 gate 是当时的 CHECK 账本，含临时 elan 路径、旧 checkout 绝对路径和用户 shell 摘要，**不是可移植安装脚本，也不要求把临时验收环境改成持久全局安装**。

在另一台机器复验前，由用户自行准备一个持久、隔离且固定 Lean 4.19.0 的环境；本仓库不自动安装 Lean。先确认真实测试只需要 `lean`、`lake`、`ELAN_TOOLCHAIN=leanprover/lean4:v4.19.0` 和可选隔离的 `ELAN_HOME`／`CARGO_HOME`，再从当前仓库根运行：

```bash
REPO="$(git rev-parse --show-toplevel)"
cd "$REPO"
lean --version
lake --version
RESEARCH_OS_REQUIRE_LEAN=1 uv run --frozen python -m unittest \
  tests.mathematical.test_reference_fixture -v
```

若用户的持久 Lean 可执行文件不在 PATH，应显式设置该环境的 PATH；不要复制 gate 中的旧 `/tmp` 或用户目录。工具不可用时普通回归可准确报告 BLOCKED/skip；严格发布复验不能把 BLOCKED 当 PASS。

## 独立发布检查

```bash
uv run --frozen python tests/e2e/check_release.py --output /tmp/research-os-strict-gates
```

`/tmp` 在此仅用于一次性结果；需留存时换成唯一的新持久绝对目录。当前仓库记录的 Core、ports 和固定 Lean reference 已 PASS；live Claude/Codex host 仍 BLOCKED，SSH／SLURM 真实环境仍 NOT_EVALUATED，因此综合检查可准确返回非零。以本次输出为准，不沿用早期构建阶段的 FAIL/BLOCKED 结论。

冻结 UV CI 保存独立结果，不用 continue-on-error／mock／expectedFailure 把发布门改绿。CI 定义已交付，但本机运行不等于 GitHub Linux CI 已运行。
