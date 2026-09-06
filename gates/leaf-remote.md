# Gates: Remote adapters

Scope: SSH/SLURM capability adapter；仅本 leaf 文件。2026-09-06。

- [x] G1: remote tests pass，非零 discovery
  CHECK: `uv run --frozen python -m unittest discover -s tests/remote -v`
  EXPECT: OK
  EVIDENCE: 44 tests，5.080s，OK；可信本地 transport/fake SSH executable/fake sbatch+squeue+sacct+scancel，未访问真实远端。
  ROOT CHECK: `uv run --frozen python -m unittest discover -s tests -p 'test_remote_*.py' -v`
  ROOT EVIDENCE: 同 44 tests，5.268s，OK；不是空测试 pass。
- [x] G2: 无配置/工具缺失返回结构化 BLOCKED，退出码 3；配置错误 2；未知/不一致状态 hard stop
  EVIDENCE: 缺配置六个入口、缺 SSH、缺 scheduler tools、CLI JSON exit 3/2；丢失提交 ACK、并发提交、receipt 写盘失败、配置/作业身份漂移、损坏账本、unknown 后迟到成功均阻止重提。
- [x] G3: submit/status/cancel/log/artifact lifecycle，固定 attempt/job，校验 retrieved bytes
  EVIDENCE: 提交前 intent+fsync+目录 fsync，flock+独占写+hash chain；SSH boot ID/PID/start ticks；SLURM job ID+完整 token job name；request 配置/command/cwd/environment/revision/inputs/remaining/deadline 固定。
  EVIDENCE: scancel ACK 仅 cancel_requested；cancelled/timed_out 绝不冒充 succeeded；unknown 仍允许按原身份取消，但不解除 unknown 锁。队列/会计无记录、重复、矛盾、未知状态及 PID 消失/复用全部 fail closed。
  EVIDENCE: Git committed blobs 独立快照，不执行脏工作树；expected SHA-256 + transmitted SHA-256 + size 三重一致后发布；no-follow dir_fd、独占原子链接、禁止覆盖/穿越/符号链接/FIFO/超限文件；写入故障不发布半成品。
- [x] G4: run-attempt protocol 兼容
  CHECK: `uv run --frozen python -m unittest discover -s tests/workflows/computational -v`
  EVIDENCE: 27 tests，3.084s，OK。RemoteExecutor 返回现有 ExecutionReceipt/BudgetUsage；原 workflow 负责 attempt/round 计数，不重复计费；非终态、未知、取消映射 blocked，避免自主模式重提。
- [ ] G5: 配置正向真实远端条件验收
  RESULT: **NOT_EVALUATED**（SSH 与 SLURM 均未提供/访问真实环境）。fake 测试通过不代表真实平台支持验收通过。
  EVIDENCE: 两个 capability.json 和所有 RemoteReceipt 明确 real_environment=NOT_EVALUATED。probe=available 只表明工具探测，不是生命周期 pass。

## 实施决策 / 集成 seam

- 已读 PLAN.md、GitHub Issue #24 原文、computational AttemptContext/Executor/ExecutionReceipt/AttemptLedger。未修改共享 facade。
- 公共 API：`research_os.remote.RemoteConfig`、`RemoteAdapter`、`RemoteExecutor`、`RemoteReceipt`。
- leaf CLI：`uv run --frozen python -m research_os.remote --project <path> [--config <json>] [--ledger <safe-relative-directory>] probe|submit|status|cancel|log|artifact`。无配置 probe 返回 JSON + exit 3。submit 使用 `--request` JSON，顶层仅 context（attempt/round/command/cwd/environment）和 remaining（六项 BudgetUsage）；status/cancel 使用 `--attempt`；log/artifact 使用 `--path --destination`，artifact 另必需 `--sha256`。
- `RemoteAdapter(project, config, ledger_directory=..., transport=None)`：默认真实 OpenSSH transport，测试显式注入可信 transport；submit 是唯一远端启动入口。每个显式 run 使用稳定 ledger；现有 ledger 不允许换 config、重用 attempt 或绕过未决作业。
- `RemoteExecutor(adapter, artifacts={remote_path: (local_destination, expected_sha256)})`：可直接注入 computational Executor seam；lifecycle receipt 序列在 remote ledger，最终结构化 receipt 放 ExecutionReceipt.detail，并保留 stdout/stderr。它不调用其他 workflow。
- SSH login shell 会二次解析命令，因此只传 shlex.join 引用后的固定 Python worker；研究 command/env 只经 JSON stdin，worker Popen(argv, shell=False)。SSH 禁用读取用户 SSH config、交互、host key 自动接纳和 forwarding；不自动安装/配置/提交付费资源。
- 使用远端 clock probe 固定保守绝对截止时间，supervisor 启动前及运行中检查；SLURM no-requeue+time，客户端等待耗尽按原身份请求取消，不宣称完成。supervisor 异常 finally 清理进程组并 wait；测试故障注入断言 child PID 已消失。
- 三轮独立只读顾问：前次三项 high 已修并回归；最终发现 accounting 故障仍阻止 cancel、retrieval 可污染自身 ledger，两项均已修。cancel 只要求队列唯一匹配原 ID/name，不依赖健康 accounting；默认/自定义 ledger 及父子路径在传输前拒绝作为输出。新增测试断言 scancel 真被 fake executable 接收、unknown 不解锁、账本字节和 transport 调用数不变。修复后本地回归通过；未声称顾问对修复后代码再次批准。
- 最终静态检查：已安装 Ruff format/check，8 个 Python 文件，All checks passed。
- 官方文档核对：Context7 `/websites/slurm_schedmd_documentation`（sacct/scancel），`/openssh/openssh-portable`（exec shell -c、非交互 argv）。

## 条件支持边界 / Deviations

- 当前实现条件 profile：可信、非 daemonizing、CPU、无费用/tokens/GPU；非零 cost/token/GPU allowance 或 GPU 请求因缺可靠计量返回 BLOCKED，不虚报零消耗。
- SSH worker 要求远端 Linux /proc；SLURM 为单作业、非 federation/array/heterogeneous/requeue，需可见的 accounting 与共享工作目录。客户端/远端时钟探测差异超过一秒即 BLOCKED；不承诺抵御运行中恶意改时钟。
- 不支持 hostile research executable、setsid 逃逸、cgroup 安全隔离；进程组清理不是容器/沙箱承诺。既有 checkout 快照最多 64 MiB，只含 committed regular files，不支持未提交输入、submodule、symlink。环境/认证必须由用户预先配置。
- unknown 无自动解除/认领/重提接口；必须保留现场，人工核对。不得删除 ledger 后假装一次新 attempt。状态查询可以继续留证，不能把后来状态当作自动重提授权。
- 按用户文件所有权约束，实施 notes 仅记本 gate，未新建共享 notes。`uvx ruff` 外部下载被权限拒绝后未下载，改用已安装 `/Users/rolex/.local/bin/ruff`；不改权限或配置。
- 未 commit/push；测试仅在 TemporaryDirectory 内建立 fixture Git commit，不提交产品仓库。
