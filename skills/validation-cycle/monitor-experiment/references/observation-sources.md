# Observation Sources

Where run facts come from, and how to read them without taking control. Use only the
surface types this project actually has; do not install a tool or assume a provider
just to create one. Every action here is a read.

## Surface types

只用项目里实际存在的表面类型：live process、terminal multiplexer、redirected stream、scheduler / queue、status / heartbeat file、exit record、artifact directory。无退出记录时的判读留在 [Monitor Experiment](../SKILL.md) 的判读规则。

Read the job's own format before matching text: frameworks name steps, epochs and errors
differently. The same surface can be stale — a log stops advancing when the job dies — so
pair a liveness surface with a recency check.

## Reading rules

- **Read-only.** List, tail, read, and query. Do not send stop, kill, restart, retry,
  pause, delete, submit or reconfigure operations, even when the run looks broken.
- **Remote access uses what the project already set up.** If the project has no working
  access, that is an observation gap; do not create credentials, tunnels or install tools.
- **Tail, do not flood.** A log tail plus the last timestamp usually settles status.
  Loading an entire large log risks hiding the terminal lines that matter.
- **One run at a time.** Confirm identity (name/id, working directory, start time) before
  attributing a process, exit code or artifact to the target run.
- **Unreadable is `unknown`.** A permission error, missing path, truncated file or
  unreachable host is reported as a gap, not silently skipped and not replaced with a
  different surface.

## Reconciling surfaces

- Direct terminal evidence (job exit record, completion marker, fatal error) outranks
  indirect signals (elapsed time, file presence, an empty tail).
- If a process is gone and no exit record exists, status is `unknown`, not `completed`
  and not `crashed`.
- If surfaces disagree, report the disagreement and each locator; do not average them
  into a guess.
- A completed job whose output artifacts are missing is still `completed` as a run fact;
  note the missing outputs separately.

## Cost and resource figures

Only report a cost, elapsed or utilization figure the run or its scheduler actually
logged. Do not estimate a price from a provider you assumed, and do not recommend a
cleanup action; cleanup is an authorization the user owns.
