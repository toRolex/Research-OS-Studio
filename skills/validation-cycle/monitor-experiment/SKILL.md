---
name: monitor-experiment
description: 只读观测已有实验或训练作业的运行事实（running/completed/crashed/unknown、进度、输出与退出证据）。用户问“跑完了吗/还在跑吗”，或父 Workflow 在授权范围内需要运行状态时使用。
disable-model-invocation: true
---
<!-- argument-hint: "[运行标识或日志/状态路径；可指定报告位置]" -->

# Monitor Experiment

从现有作业与观测报告**运行事实**：作业是 running、completed、crashed 还是 unknown，以及可核对的进度与输出证据。它回答“现在发生了什么”，不回答“结果好不好”。

## Scope and authorization
Gate: write-path | before=report-write | approval=explicit-user | source=SKILL.md#scope-and-authorization

- **Role:** explicitly invoked or path-cascaded internal capability within the caller's authorized research scope; users may also explicitly invoke it standalone. This skill is read-only: it observes existing processes, logs and artifacts. It never stops, kills, restarts, retries, pauses or reconfigures a job, and never starts a new one. A parent Workflow is a caller, not permission to control jobs.
- **Inputs:** a run identifier or the locations of existing observation surfaces (log files, scheduler/status output, stdout/stderr, exit-code records, heartbeat/progress files, artifact directories). Read existing project instructions and workspace navigation if present. Setup, a particular directory layout, a specific provider, a GPU scheduler or any research runtime is not a prerequisite.
- **Resolve before work:** identify exactly which run is observed and which surfaces actually exist. If the target is ambiguous, ask one focused question and stop; do not guess from a directory listing. If a named surface is unreadable, record it as an observation gap instead of substituting an unrelated one.
- **Resources:** use already available, authorized read tools, following host-specific tool routing. Issue only non-mutating operations (list, tail, read, status/query). Do not install tools, open new credentials, pay for services, or write to remote systems. If access is denied, report the exact gap and stop; do not escalate.
- **Writes:** standalone returns the report in chat unless the user authorizes a destination for the run-status record. Composed contributes only the run-status section of the caller's named canonical report (or returns the section for the caller to insert). Any written record holds observed facts and evidence locators only, never research results, conclusions or claims. Reuse existing material without overwriting it; ask on file conflicts.
- **Cadence:** observe once per invocation, then stop. Do not create schedules, loops, cron jobs or background pollers, and do not decide to be re-invoked. The user or an authorized parent Workflow decides whether and when to observe again. A non-terminal run is reported as it stands.
- **Budget:** one bounded observation pass per invocation. Read only what establishes status and progress; prefer a log tail over loading a whole file. Stop once the status is determined or available surfaces are exhausted, recording what remains unknown.

## Observation vocabulary

Use exactly one primary run status, with the evidence that establishes it:

- **running** — an active process/session/job exists and has produced output or a heartbeat within its expected interval. Evidence: a live process or scheduler entry plus a recent log timestamp or progress counter.
- **completed** — a terminal success fact exists: a recorded exit code 0, or a completion marker emitted by the job itself. The process is no longer active. This is a run fact only; it does not mean the experiment succeeded scientifically, that a metric is good, or that a Claim holds.
- **crashed** — a terminal failure fact exists: a recorded non-zero exit, an OOM/kill signal, or a fatal error in the job's own output. The process is no longer active.
- **unknown** — no usable surface, conflicting evidence, or unreadable observations (including not started). Say `unknown` rather than infer a status from file presence alone.

Record only what is actually observed: observation time, run identity, elapsed, last output timestamp, progress counters (step/epoch/total if the log emits them), output/artifact paths present or absent, recorded exit code, and any resource or cost figure the run itself logged. Quote raw recorded values as evidence; do not compare, rank or interpret them.

## Phase 1: Locate the run and its surfaces

Read [observation sources](references/observation-sources.md) when the surfaces are not obvious. Determine which available surface types describe this run and whether each is current. Confirm run identity (job name/id, working directory, start time) so a status is not attributed to a different run.

**Complete when:** the target run and each available or unavailable surface has a concrete locator, or the target is ambiguous and one focused question has been asked.

## Phase 2: Determine the run fact

For each available surface, read only what establishes status and recent activity. Cross-check surfaces; reconcile conflicts toward the most direct terminal evidence. A process entry with no recent output is not automatically running; a missing process with no exit evidence is not automatically completed. When nothing is decisive, the status is `unknown`.

**Complete when:** the primary status is supported by named evidence, or is explicitly `unknown` with the conflicting or missing observations stated.

## Phase 3: Capture progress and output facts

Capture only machine-checkable progress and output facts: the latest progress counters, the log tail showing the most recent activity, and whether expected output paths exist together with their modification times. Do not open result files to judge their contents, and do not assemble metrics into a comparison.

**Complete when:** each progress and output fact has a locator, and every unavailable one is marked as not observed.

## Phase 4: Report facts and stop

Output a readable Markdown run-status record using [the report template](templates/run-status-report.md). The template organizes observations; it is not a machine schema.

- State the primary status, its evidence, and the observation time for each surface.
- List what could not be observed and how that limits the record.
- Keep interpretation out: no baseline comparison, no “promising/failed” judgment, no advice about the research direction. If the caller needs training-quality diagnosis, that is the separate `training-health-check` capability and it is not started here.
- Preserve observed failed, invalid and superseded attempts; do not report only the latest pleasant-looking line.

**Complete when:** the record contains status, evidence locators, progress/output facts, explicit unknowns and the observation time. Then stop. The user or parent Workflow decides whether to diagnose health, analyze results or change the job; this skill controls nothing.

## Interpretation rules

- A run fact is not a research fact: `completed` describes the job, not the result.
- 无退出记录即 `unknown`：空 tail、缺日志或进程消失，在作业自己记下终态之前保持 `unknown`。
- Prefer the most direct evidence: the job's own exit record or completion marker over elapsed time or file presence.
- Report raw observed numbers; comparison and quality judgment belong to analysis and audit capabilities the user invokes separately.
- Reading is not controlling: report a broken-looking run as a fact and leave stop/restart/retry to the user.
