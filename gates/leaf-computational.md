# Gates: Computational slice

Scope: 五个 computational workflow、真实 CPU、shared foundation/semantics handoff、预算与失败保留。2026-09-06 L10 对齐复验。

- [x] G1: computational 回归
  CHECK: `uv run --frozen python -m unittest discover -s tests/workflows/computational -v`
  EVIDENCE: 38 tests / 21.992s / OK。含真实临时 Git 仓库、CPU 命令；不是 mock 发布门。
- [x] G2: shared foundation + semantics，不改共享 facade 或 validators
  CHECK: `uv run --frozen python -m unittest discover -s tests/contracts/semantics -v`；`uv run --frozen python -m unittest discover -s tests/contracts/foundation -v`
  EVIDENCE: semantics 34 tests / 0.081s / OK；foundation 29 tests / 0.008s / OK。computational 的七份 E2E Artifact（design/preparation/run/analysis/Claim/Evidence/result-to-claim analysis）逐份过 shared foundation/type；Claim/Evidence 另过 executable semantics schemas，provenance 过共享规范及真实 Git contextual digest 验证。
- [x] G3: canonical supports 与真实上下文
  EVIDENCE: Evidence spec 仅 `project/workstream/description`；唯一 relation 为 `{relation: supports, claim: fixed ref, scope, method, conditions}`。设计显式接收真实 Project/Workstream pins，逐阶段传播并核对绑定。拒绝非法 Claim、版本、重复/冗余 scope、伪造 provenance digest、不同合法 Workstream、替换 run 或 result。共享 scope 支持根指针及显式空 conditions。
- [x] G4: 不把研究结论或活输出伪装成 Assurance/fixed handoff
  EVIDENCE: 三种 verdict 均保留 `experiment-analysis@1.0.0` / `role=result-to-claim-assessment`；仅 supports 创建 Evidence。does_not_support/inconclusive 无 Evidence 文件或 relation。无虚构 Project、commit 或 sibling live Evidence 引用；下游须由用户真实提交后固定 commit+digest。workflow report、attempt ledger 为诊断记录，不宣称它们是通过 Artifact validator 的 Artifact。
- [x] G5: 预算、失败、CPU、分析与用户停止边界
  EVIDENCE: 原六维预算、preparation/run 累计、ordinary 首败停止、BLOCKED、失败快照、append-only 重调用、symlink/TOCTOU/provider 环境隔离回归保留。真实 CPU 输出 MSE=1.25；分析无 executor、只读 run commit bytes。显式用户撤销在尝试间返回 user_stopped，保留旧失败。失败留下 partial result 时保留原字节及快照，下一次尝试前停止 partial_result_requires_user_action，避免“失败残留＋成功空操作”冒充结果。
- [x] G6: TDD 与独立复核
  EVIDENCE: design context / canonical relation / forged provenance / status-only analysis / user stop / unrelated fixed run / stale partial noop 均记录实际 RED，再最小修复 GREEN。独立顾问发现 run/result 语义链替换与跨尝试残留两项，均新增公开 seam 回归并修复；结果链核对 run 类型/成功/边界、result 的路径/digest/run commit 与 design/preparation 绑定。
- [x] G7: owned 质量
  CHECK: `uv run --frozen ruff check src/research_os/workflows/computational tests/workflows/computational reference-projects/computational/experiment.py`；对应 `ruff format --check`；`git diff --check`
  EVIDENCE: All checks passed；7 files already formatted；diff check 通过。仅修改授权 computational 目录、五个 skill、模板/reference 与本 gate；无 commit/push。

- [x] G8: L10 集成与 partial 精确停止回归
  CHECK: `uv run --frozen python -m unittest discover -s tests/integration -v`
  EVIDENCE: 15 tests / 4.510s / OK，含 CPU workflow 的显式调用、typed 输出与共享 validator/Publication CLI。partial 负例明确断言 `stop_reason == partial_result_requires_user_action`、`calls == [1]`、原始 result bytes 为 `b'partial'`、所有 `attempt-0002.*` 不存在，并保留第一轮失败快照。补强后 computational 38、semantics 34 同轮复跑均 OK。

- [x] G9: Critical 本地 timeout 后代清理（2026-09-06）
  CHECK: `uv run --frozen python -m unittest discover -s tests/workflows/computational -v`；同命令 `-s tests/remote`、`-s tests/integration`；`uv run --frozen python -m unittest tests.e2e.test_e2e_computational -v`
  EVIDENCE: 最终 Darwin 实跑 computational 62 tests / 53.170s / OK（原38＋执行专项24）；remote 44 / 5.438s / OK；integration 21 / 58.855s / OK；安装 wheel CPU→Publication E2E 1 / 35.885s / OK。仅可信 fixture 与固定系统探测命令，无真实 SSH/SLURM 或不可信外部代码。
  TDD: 实际 RED→GREEN 覆盖关闭 stdio 子进程超时后延迟写 marker、父提前退出遗留子进程、提前 reap 造成组身份丢失、TERM 宽限中断、communicate 内部 `_wait` 中断、SIGKILL 阶段中断；最终延迟 marker 均不存在，直接子进程 waitpid 确认已回收，测试结束进程表未发现 fixture 残留。
  IMPLEMENTATION: `start_new_session=True` + Popen communicate；WNOWAIT 保留 leader PID 至最后一次组信号；整组 TERM、150ms 宽限、整组 KILL、共享1s清理截止时间、drain/close/wait。即使父正常退出也不遗留后台子进程；正常0/非零退出语义保持。拒绝调用者组/危险组号；平台或 waitid 能力不足、SIGCHLD 自动回收时启动前 blocked。
  RECEIPTS: timeout 始终 `timed_out` / 无 return code；spawn 错误 blocked；普通完成清理异常 blocked，timeout 清理异常保留 timeout 并明确 cleanup unconfirmed。保留 binary stdout/stderr、累计 partial output 和 TERM handler 输出；实际 elapsed 包含 spawn 与清理，不截断为预算。中断收尾后传播原异常。
  DARWIN: zombie-only 组可能返回 EPERM；仅确认 leader 仍 waitable 且固定 `/bin/ps -g <pid> -o stat=` 全为 Z 时视为无活进程；固定 PATH/LC_ALL、200ms探测超时，探测失败或非全Z保持 fail-closed。
  QUALITY: 授权 execution/test 范围 ruff check、format --check（4 files）、git diff --check 均通过。本次只改 execution.py、新执行专项测试、本 gate；不改 shared facade，不 commit/push。

边界：本次真实验收环境为 Darwin；Linux 分支实现未在真实 Linux 内核实跑，不记 Linux PASS。进程组清理不是恶意代码沙箱；主动 setsid/setpgid 脱组后代不在保证范围，其他线程/自定义 SIGCHLD handler 不得抢先 reap 本 executor 子进程。系统拒绝 kill 或清理超限会准确记录 unconfirmed，不宣称绝无残留；重复中断/不可中断内核任务无法保证有界回收。SSH/SLURM/GPU 未实跑，不记 PASS；跨仓库/URI 的 computational fixed 输入明确不支持。用户停止仍在启动前/尝试之间检查；timeout 与 KeyboardInterrupt 清理不等于新增中途用户取消 API。
