---
name: training-health-check
description: "只读诊断已有训练观测（loss/梯度记录、训练日志、资源记录）中的 NaN/Inf、发散、OOM、停滞与日志完整性问题，并给出继续、停止调查或补充观测的建议；用户问“训练是否健康/是否异常”，或父 Workflow 在授权范围内需要训练健康诊断时使用。只诊断，不写研究结果、不停止或重启作业、不判断 Claim。"
argument-hint: "[训练运行标识或日志/指标路径；可指定报告位置与观察窗口]"
---

# Training Health Check

从固定观测诊断训练是否出现 NaN/Inf、发散、OOM、停滞和日志完整性问题，并给出**建议**。它回答“训练过程是否健康”，不回答“实验是否支持 Claim”。作业控制权始终在用户手中。

## Scope and authorization

- **Role:** model-invoked internal capability within the caller's authorized research scope; users may also explicitly invoke it standalone. This skill reads observations and diagnoses. It never stops, kills, restarts, retries, requeues, pauses or reconfigures a job, and never edits training code, configuration, data or checkpoints.
- **Inputs:** existing training observations — loss/gradient/metric records, training logs (stdout/stderr), resource or scheduler records, and the user's stated window and expected schedule when given. Observations may be a file, a directory of logs, or text the user pasted. A specific tracking service, GPU scheduler, framework or live session is not a prerequisite.
- **Resolve before work:** identify the run, the signal(s) to check, and the observation window. If the target or the log location is ambiguous, ask one focused question and stop. If only a run-status fact is available, that is a monitor fact, not a health diagnosis: without training observations the result is `insufficient observation`.
- **Resources:** use already available, authorized read tools, following host-specific tool routing. Only non-mutating reads and queries. Do not install tools, open credentials, pay for services, or write to remote systems. If a required observation is unavailable, record the gap; do not fabricate a value or substitute an unrelated run.
- **Writes:** standalone returns the report in chat unless the user authorizes a destination for the health record. Composed contributes only the health section of the caller's named canonical report (or returns the section for the caller to insert). Any written record holds observations, the diagnosis and recommendations only, never research results, Claims or paper content. Reuse existing material without overwriting it; ask on file conflicts.
- **Cadence:** diagnose once per invocation, then stop. Do not create schedules, loops, cron jobs or background pollers, and do not decide to be re-invoked. An early or under-observed run is reported as `insufficient observation`; the user or an authorized parent Workflow decides whether to observe again later with more data.
- **Budget:** one bounded diagnostic pass per invocation, bounded by the named or available window. Read the relevant window or tail rather than entire large logs. Stop at the window boundary or when the observed signals suffice to classify; retain the unexamined range as a stated limit.

## Phase 1: Establish observations and their completeness

Read [health signals](references/health-signals.md) now. List every observation surface actually available for this run, with its locator and the range it covers. Then check whether the observations are usable at all:

- The surface exists, is non-empty, and is readable in its stated encoding.
- Step/epoch or timestamp numbering is contiguous, or the gaps are identified.
- Records are not truncated mid-entry; the tail is a real last record, not a partial write.
- Expected evaluation or checkpoint entries appear where the run's own format says they should.
- Timestamps advance and their recency is meaningful for the run's expected cadence.

Classify observation adequacy: **sufficient** (enough contiguous history to judge the checked signals), **partial** (usable but with named gaps), or **missing** (no usable training observation). Missing or partial observations can never certify the run healthy.

**Complete when:** every surface has a locator, coverage and adequacy label, and every gap is stated.

## Phase 2: Check each signal

For each signal in the catalog — NaN/Inf, divergence, OOM, stagnation, log completeness — record the evidence locator, the observed values or window, and a classification. Use trends over multiple checkpoints, not one point:

- Compare against the run's **own** earlier values, not against a paper baseline or an expected final number.
- Respect the run's expected schedule (warmup, LR decay, curriculum, evaluation cadence) before calling a shape anomalous.
- Treat a single spike, a short plateau or one noisy point as inconclusive rather than a failure.
- Prefer the most direct evidence: a recorded NaN/OOM/error line outranks an inferred trend.

Optional secondary signals (loss spikes, exploding/vanishing gradient, LR-schedule deviation) may be reported when the observations actually carry them. Process liveness and idle resources belong to `monitor-experiment`, not here.

**Complete when:** each catalog signal is classified with its evidence and window, or explicitly marked as not observable in the available data.

## Phase 3: Diagnose

Give one diagnosis, bounded by the observed window:

- **no anomaly detected** — within the observed window, the checked signals show no anomaly. This is a statement about the observations, not a scientific verdict and not proof the run will succeed.
- **anomaly detected** — name each anomalous signal, its evidence, its severity, and whether it is terminal.
- **insufficient observation** — the observations are missing or too short/gappy to judge; list exactly what is needed.
- **indeterminate** — surfaces conflict or the data is too ambiguous to classify.

**Complete when:** the diagnosis names the signals checked, the window, the evidence and the residual uncertainty.

## Phase 4: Recommend — advice only

Pair the diagnosis with a recommendation the user can act on:

- `continue` — no anomaly in the observed window; the user may keep training and observe again later.
- `stop and investigate` — a clear anomaly (NaN/Inf, divergence, OOM, terminal failure) is present; recommend that the user inspect and decide whether to stop.
- `collect more observations` or `extend the window` — partial or inconclusive data; say which signal needs which additional observation.
- `fix the observation` — the log itself is incomplete or unreadable; the immediate problem is observability, not necessarily training.

State plainly that stopping, killing, restarting or requeueing the job is the user's action; this skill performs none. Record the evidence the user should preserve (log window, run identifier, observed values) so the decision is not lost when the job ends.

**Complete when:** every recommendation maps to a diagnosis and says what evidence would change it.

## Phase 5: Report and stop

Output a readable Markdown report using [the health report template](templates/health-report.md). The template organizes the diagnosis; it is not a machine schema. Keep raw observations separate from the diagnosis so the user can re-judge.

**Complete when:** the report contains the observation surfaces and adequacy, per-signal findings with locators and windows, the diagnosis, the recommendation and its limits. Then stop. The user or parent Workflow decides whether to stop, restart, analyze results or write them up; this skill neither controls the job nor produces research results.

## Interpretation rules

- Diagnose training dynamics, not scientific validity: a healthy run does not validate a hypothesis, and a crashed run does not falsify a Claim.
- Trend over multiple checkpoints, never one noisy point.
- Missing observations are an observability result, not a healthy result.
- A plateau or a spike is labeled with its window and uncertainty; when the window is too short, say `insufficient observation` rather than guessing.
- Default thresholds in the catalog are starting points the user may override for the run; state any threshold used.
- This skill reads and recommends only: no stop, restart, retry, requeue, or training-code edit.

## 来源

改编自 wanshuiyin / ARIS `skills/training-check/SKILL.md`，revision `0472e530251cdbd3364c33b110063c58f819edd7`（MIT）。保留 NaN/Inf、发散、停滞的可检查信号、多 checkpoint 趋势优先于单点噪声以及观察间隔自适应思想；从同 revision 的 `skills/experiment-bridge/SKILL.md` W&B 调用点与训练检查的进程／质量分层补充 OOM 与日志完整性。按父 spec 重写为只诊断：删除 CronCreate 自调度、Codex MCP 裁决、`tools/watchdog.py` 分层、固定 model/W&B 依赖和“kill training”动作，输出改为建议，停止／重启由用户执行。MIT 全文见 [LICENSE](LICENSE)。来源与采用细节记录于仓库集中来源文档，该文档是维护信息，不是执行依赖。
