# Spec48 最终集成验收

日期：2026-10-24。此记录补充最终集成与独立复核，不替代 issue 操作，也不把结构验证、历史证据或静态审查扩大成真实科研/多宿主通过。

## 集成身份与范围

- 固定原审查范围：`bce31c1618c98b5ca4ed12bf3eb2ed091cdd5e02` → 原 integration HEAD `4816745b3f18db76adf64524a4eef080196339b6`。覆盖账本和原始证据见 `/tmp/spec48-spec-aggregate/REPORT.md`、`/tmp/spec48-standards-aggregate/REPORT.md`。
- 基线 `4816745...` 工作树干净。候选 `242a9fb7c1a3c693ac3f93d5953f4c7d884cc5d3` 的 parent 是 `431eed494b28b19dde84b3630485acf8226ca049`；候选只比 parent 多改 `tests/test_spec48_ticket60_contract_M.py`。已用 `git merge --ff-only 242a9fb7c1a3c693ac3f93d5953f4c7d884cc5d3` 前进；无 reset、stash、jj、push 或 issue 操作。
- 候选完整 tree：`37dda12c77fe2cca61a4df6fc39907bb90340e89`；parent tree：`fd12ab22657b01182c47504b644ec1e1fac77871`。`skills/` tree 在 `6d492e27af28593cebacb4066be4833e22f3f287`、`431eed4`、`242a9fb` 三个对象均为 `dc15a1d2d96299281e636507ad26f3111de16f26`；`git diff 431eed4 242a9fb -- skills/ LICENSE package.json README.md` 为空。此次末修是测试 oracle 收紧，不是产品资源改动。
- Spec 21 IDs 与 Standards 13 原 IDs 的精确复审目标对象为 `6d492e27af28593cebacb4066be4833e22f3f287`（tree `2d184492db2cd17cb961e30234287525e10446a9`），见三份 final review 报告；不能把这些报告说成在 `242a9fb` 上重跑。`6d492e2 → 431eed4 → 242a9fb` 的后继差异限定在 `tests/test_spec48_ticket60_contract_M.py`；review 对象比较、配置/checker 复审与继承报告分别绑定其实际审过的文件/边界，空白 oracle 修正单独由 R1 证据和最终 suite 收尾。
- `.agents/notes/spec48-goal-implementation-notes.md` 是被保护的 ignored 文件：合并前后 SHA-256 均为 `5c235e7dd73fd8686459d8c345549bfdcca1b10cb491cb3c2349b880d4f7f4a9`。本轮未编辑该文件；最终代码提交共 66 文件、1069 insertions/243 deletions（继承提交）；末修候选只增加/调整一个测试文件；本轮自身只提交本目录下的验收文档。

## Spec

### 21 个确认 finding：逐项闭合

原 Spec 聚合的 19 个 ID，加上已裁定的 `S1-Q01-F1`、`S1-Q03-F1`；`Q-S1-02` 已判非缺陷，不计入。以下结论绑定独立复审明确的精确对象及后继对象继承证据，不表示整个项目或超出各报告边界的能力通过。

| finding IDs | 结论与闭合证据 |
|---|---|
| `F-S1-01`, `A-F2` | **独立关闭。** `/tmp/spec48-final-config-review/REPORT.md`：标准八角色配置可表达多个隔离 reviewer；真实 CLI 的互读坏例拒绝、合法改写通过，fresh/readonly/peer 输入隔离与 lead 后置均有正反例。A-F2 未被夸大为真实模型或宿主 E2E。 |
| `A-F1`, `A-F3`, `S6A-F1` | **独立关闭（有限静态/人工边界）。** `/tmp/spec48-final-checker-review/REPORT.md`：三项逐 ID 结论、47 项定向测试及完整 CLI 变体证据；checker 不替代任意自然语言语义、真实调度或恢复验证。 |
| `S2-F1`, `S2-F2`, `S3-F1`, `S3-F2`, `S3-R1`, `F57-01`, `F57-02`, `F57-WR-01`, `F57-WR-02`, `F57-TALK-01`, `S6-F1`, `S6-F2`, `S6-DOC-F1`, `S6-REM-F1`, `S1-Q01-F1`, `S1-Q03-F1` | **指定对象关闭继承。** `/tmp/spec48-final-inheritance-review/REPORT.md` 的逐 ID 表、对象 tree/blob/mode 比较与定向补验绑定原关闭锚点；其中 Q01/Q03 继承 parent 对 B10 的定向关闭。此继承仅覆盖列明对象及边界，不认证真实 PPT/TeX 渲染、demo 的真实扫描行为或任意后继。 |
| `S3-F1`, `S3-F2`（资源保全交叉证据） | `/tmp/spec48-resource-test-review/REPORT.md` 审查 17 项迁移资源（8 项严格字节、9 项批准适配），并确认方法/许可边界；其 R1 是测试 oracle 的列表空白漏检，已由候选 `242a9fb` 删除空白规范化、对批准控制行做严格逐行比较并增加拒绝回归。修复 diff 已由 parent 完整读取；最终全 suite 的精确对象结果见下方测试记录。R1 不是产品越权 finding。 |

**计数核对：**2 项配置复审 + 3 项 checker 复审 + 16 项继承复审 = 21 个 Spec IDs。资源保全行是交叉证据，不重复计数。

### 产品/安装证据继承

- 原实现对象 `/tmp/spec48-final-candidate-validation/REPORT.md`：单一 Claude Code 宿主 41/41 skill 包、333/333 文件 SHA-256 与 mode 一致；58/58 LICENSE/NOTICE/COPYING 类资源 SHA-256 与 mode 一致；另有 `interrogate`、verify 创建/维护、`proof-review`、`paper-talk`、Research OS Discovery 声明组合的代表性实装证据。
- 继承链由 `/tmp/spec48-final-candidate-validation-r2/REPORT.md` 核对：`6d492e2`、`431eed4` 的 `skills/` tree 同为 `dc15a1d2d96299281e636507ad26f3111de16f26`，新候选相对 parent 仅变测试文件，故最终安装输入不变。此次未重装。单一宿主的副本一致不等于真实 agent 功能、多宿主 E2E 或全部 sibling 单装功能通过。
- `paper-compile-repair` 仍要求同根安装且可解析已声明的 `paper-compile` sibling。按 TD3 对声明边可解析的接受解释计入 AC4；不把 `paper-compile-repair` 单装说成完整修复功能通过。具体接受说明同时保留在 [`spec48-ticket60-final-acceptance.md`](spec48-ticket60-final-acceptance.md)。

## Standards

Standards 共保留 **13 个原 ID**，按来源 finding 逐项结案，不合并 ID：

| 状态 | 原 ID | 证据/结论 |
|---|---|---|
| **关闭（8）** | `S4-2`, `W6-S1`, `S7-1`, `N1`, `NA1`, `B2`, `B1`, `NA2` | `/tmp/spec48-final-inheritance-review/REPORT.md` 的 Standards 逐 ID 终态与 12 份 notes 保真核对；`W6-S1` 继承指定 12 对象复审，`S7-1` 有独立 talk/docs 证据，其余文档约定逐实例确认。原历史状态、阶段边界与因果保留；不据此重新认证旧测试/安装。 |
| **明确延期、未修（5）** | `S1`, `S2`, `SL3-1`, `S4-1`, `W6-S2` | 抽象/去重建议作为非阻塞维护风险延期；无修复提交，不称“已修”或“关闭”。风险与边界见 `/tmp/spec48-standards-aggregate/FINDINGS.md`、`/tmp/spec48-final-review-fixer-batch13/FINAL-LEDGER.md` 与 final inheritance 报告。 |

Standards 审查补件：原 `tests/test_ticket60_flat_install_links.py:1–76` coverage gap 已由 `/tmp/spec48-final-inheritance-review/REPORT.md` §“原coverage gap”补审，新增 finding 为 0；没有把它伪装成第 14 个 ID。

## 结构、历史与明确限制

- 结构与历史分轴。默认结构命令：`uv run --offline --no-project python scripts/check-skills.py --archive-scope structure`；严格历史命令独立运行：`uv run --offline --no-project python scripts/check-skills.py --archive-scope history`。本轮精确 HEAD 上结构 rc=0、历史 rc=1：7 项 `UNVERIFIED` + 1 项 `MISMATCH`，全部 `UNAVAILABLE`；不是 history PASS，也不等同结构检查失败，实际结果见下文。
- 科研质量/定理真值、真实模型派发、生产 SSH、远程作业/恢复、多宿主宿主 E2E、完整 PPT/TeX 导出均未在本次验收中实测；不声称通过。
- 测试基准边界：`/tmp/spec48-final-candidate-validation-r2/REPORT.md` 的全 38 文件、397 passed、757 subtests 是旧精确对象 `431eed4` 的结果，**不得作为新候选 `242a9fb` 的全绿证据**。此前旧失败日志保持原位，不覆盖。

## 最终提交验证结果

**测试执行 HEAD：**`edca41919141515361b40d51438de7c9959f1003`（先提交两份验收文档的 doc-only commit；测试前该 HEAD 工作树干净）。用 tracked 文件清单重新 collect，实际 **38 个文件、398 个 pytest 节点**；逐文件串行执行 **38/38 rc=0，398 passed、760 subtests passed、0 failed、0 skipped**。包含 `scripts/test_*.py`；没有 `-k`、`--ignore`、skip 或并行。环境为 uv 0.13.5、Python 3.14.4、pytest 9.1.1；每文件 180 秒 timeout，临时目录在 `/tmp/spec48-final-merger-closeout-record/tmp/`。

修复目标 `tests/test_spec48_ticket60_contract_M.py` 在该精确 HEAD 为 **12 passed、286 subtests passed**；`test_unapproved_control_whitespace_changes_are_rejected` 实际执行并通过。逐文件日志、实际 rc、完整收集节点与文件清单见 `/tmp/spec48-final-merger-closeout-record/logs/{collect.log,tracked-test-files.txt,suite/results.tsv,suite/file-01.log…file-38.log}`。此前 `431eed4` 的 397/757 旧结果没有代替本次执行。

```text
timeout 180 env TMPDIR=/tmp/spec48-final-merger-closeout-record/tmp UV_CACHE_DIR=/tmp/spec48-final-candidate-validation-r2/logs/uv-cache uv run --offline --no-project --with pytest==9.1.1 python -m pytest --collect-only -q <logs/tracked-test-files.txt 中的全部路径>
timeout 180 env TMPDIR=/tmp/spec48-final-merger-closeout-record/tmp UV_CACHE_DIR=/tmp/spec48-final-candidate-validation-r2/logs/uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --offline --no-project --with pytest==9.1.1 python -m pytest -vv --tb=short <逐个传入一个 tracked test_*.py>
```

**结构 / 历史独立结果（均在测试执行 HEAD）：**

| 命令 | rc 与结果 |
|---|---|
| `uv run --offline --no-project python scripts/check-skills.py --archive-scope structure` | **rc=0**；`OK: 41 个 Skill（U 40 / M 1）`。 |
| `uv run --offline --no-project python scripts/check-skills.py --archive-scope history` | **rc=1**；8 项均 `UNAVAILABLE`：7 `UNVERIFIED`、`v2-accept-validation.tar.gz` 为 `MISMATCH`。不是 history PASS。 |

命令原始输出与 rc 见 `/tmp/spec48-final-merger-closeout-record/logs/check-{structure,history}.{log,rc}`。测试前 `git diff --check`、候选范围 diff check 均 rc=0，status 干净；受保护 notes SHA 仍相同。

这次结果提交仅更新验收文档，是 `edca419` 的 doc-only 后继；**测试执行 SHA 仍是 `edca41919141515361b40d51438de7c9959f1003`**。最终 HEAD 的精确 SHA、其与测试 HEAD 的 ancestry、非文档 tree 不变校验及最终 structure 重跑结果记录于 `/tmp/spec48-final-merger-closeout-record/REPORT.md`。结果提交后另行复跑 structure checker；不重跑 suite，不改产品或测试。

**本地限制：**不 push、不关闭 issue、不清理 worktree/历史材料。issue tracker 后续由 parent 处理。
