# Observation Sources

Where run facts come from, and how to read them without taking control. Use only the
surface types this project actually has; do not install a tool or assume a provider
just to create one. Every action here is a read.

## Match the surface to the fact

| Surface | Typical read | Establishes |
|---|---|---|
| Live process | `ps -o pid,etime,cmd -p <pid>`, process table query, container/pod list | `running` |
| Terminal multiplexer | `screen -ls`, `tmux ls`, capture-pane / hardcopy (read the copy) | `running`, log tail |
| Redirected stream | `nohup.out`, `*.stdout`, `*.stderr`, framework log file | progress, fatal errors |
| Scheduler / queue | Slurm `squeue`/`sacct`, PBS/SGE `qstat`, LSF `bjobs`, Kubernetes pod status/logs, cloud job status | `running`/terminal state, exit code |
| Status / heartbeat file | state or progress file written by the job | `running`, progress counters |
| Exit record | launcher-captured `$?`, `*.exit`, scheduler exit state, job completion marker | `completed` / `crashed` |
| Artifact directory | `ls -l` of expected output paths and their modification times | output present or absent |

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
