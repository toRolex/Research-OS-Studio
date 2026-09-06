# Adapter capability 与支持矩阵

状态针对当前实现和已有证据，不是对整个平台能力的永久判断。PASS 表示列明边界通过；BLOCKED 表示前置能力不足；NOT_EVALUATED 表示没有声明环境中的真实验收；FAIL 表示缺少产品要求或校验失败。

| 边界 | 当前支持 | 不可推导的能力 |
|---|---|---|
| Direct CLI | 显式 outer／CPU／math workflow、typed validators、独立 freeze 命令 | 不自动调用模型、无 planner、无自动接受 |
| Claude Code projection | 15 workflow 加 `disable-model-invocation: true`；固定 canonical／Adapter／profile digest；共享 validator | frontmatter 不是进程／工具隔离 |
| Codex projection | canonical bytes 保留；每 workflow `agents/openai.yaml` 禁隐式调用 | YAML policy 不等于真实执行隔离 |
| Claude Code 真实 Charter | BLOCKED：`adapter.isolation_unavailable`；离线 `adapter.offline` | 不启动宿主、不写 candidate、不 fallback 到 direct CLI |
| Codex 真实 Charter | BLOCKED：`codex.isolation_unverified`；离线 `codex.offline` | 不启动宿主；显式 RUN 确认也不解除隔离门 |
| Adapter validate | 同一 Core、同一 fixture 可比 verdict／exit code，漂移阻塞 | 不证明真实模型 Artifact／stop parity |
| Disciplines | canonical 8 项；Claude 完整 model-only projection；Codex workflow-only manifest 固定 excluded/BLOCKED | Codex 不支持私有 discipline；候选不等于最终 port acceptance |
| 本地 CPU | 两 reference 产物 E2E：真实命令、PDF／freeze／恢复 | 无费用/GPU/token 非零预算的普遍计量承诺 |
| Lean 固定 reference | 官方临时隔离 elan 的 Lean 4.19/Lake；真实 build、axiom audit、comparator、kernel replay PASS | 只覆盖无外部依赖的 P0 isolated-rebuild |
| SSH | 缺配置返回结构化 BLOCKED；真实环境 NOT_EVALUATED | probe available／fake executable 测试不等于远程生命周期成功 |
| SLURM | 缺配置返回结构化 BLOCKED；真实环境 NOT_EVALUATED | 本地 scheduler fixture 不等于集群支持验收 |
| Publication | 真实 deterministic PDF、staged preflight、digest freeze、不可覆盖／恢复 | API fixture 不等于通用 CLI manuscript 支持或真实学术接受 |
| Repository／ports | `validate-repository` 与 `validate-ports` PASS；8 ports accepted，release_authorized=true | 来源/许可/评价/接纳只覆盖固定 digests，不外推上游 runtime |

## Capability / unsupported policy

Adapter 只生成投影、探测能力、映射调用、记录 provenance 与触发阻止。不复制 contract／validator／研究语义／预算／gate。manifest 固定 canonical skill、Adapter 与 capability profile 的版本和摘要；任何漂移必须阻止，不能静默生成更宽权限版本。删除 Adapter 后 Core 仍可阅读、手工执行和验证。

实际验证入口：

```text
research-os generate-projection claude-code --output NEW_DIRECTORY
research-os generate-projection codex --output NEW_DIRECTORY
research-os adapter claude-code validate --project PROJECT artifact.json
research-os adapter codex validate --project PROJECT artifact.json
```

真实模型对照验收待安全 host isolation profile 和用户真实外发授权；测试内受信 host receipt 仅协议证据。不能通过配置 flag 把内部 test host 当作已支持宿主。

## SSH／SLURM 条件验收

未配置时可运行现有公共入口探测，必须得到 exit 3／blocked。此命令不配置凭据、不提交任务：

```bash
uv run --frozen python -m research_os.remote --project /absolute/project probe
```

真实环境需用户另行提供配置并确认有成本的执行。参照 installed `adapters/ssh/capability.json`／`adapters/slurm/capability.json` 与 `python -m research_os.remote --help`，使用单个稳定 ledger：显式 probe → submit → status → logs/artifact；另一个用户授权作业验证 cancel。记录每个动作的实际命令、时间、exit code、RemoteReceipt、attempt/job identity、提交 ACK、terminal status、检索 bytes/hash/size、配置与 pinned Git revision，输出结论才可从 NOT_EVALUATED 改为 PASS/FAIL/BLOCKED。

当前条件 profile：可信、非 daemonizing、CPU、无 cost/tokens/GPU；SSH worker 需 Linux `/proc`，SLURM 为单作业、非 array/federation/heterogeneous/requeue，accounting 可见且工作目录共享；时钟偏差过大阻止。unknown、提交 ACK 丢失、身份漂移、状态冲突均 hard stop，不盲目重提；cancel_requested 不等于 cancelled/succeeded。不得删除 ledger 解锁重试。

不支持 hostile executable／setsid 逃逸／cgroup 安全隔离；进程组清理不是容器。真实条件 E2E 没有在本次运行，两个 Adapter 保持 **NOT_EVALUATED**；新增 CI 不读取 secrets、不触发远端提交。
