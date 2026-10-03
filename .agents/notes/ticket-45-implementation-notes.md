# Ticket #45 implementation notes

## 共享合同

沿用 `.agents/notes/ticket-38-implementation-notes.md` 与 `/tmp/research-os-v2-notes/shared-contract-approved.md`。本票只新增 proof、improvement、pickup。

## Decisions

- 基线：`v2/ticket-45` 已含 `integration/research-os-v2` tip `f94fc10` 的祖先；开工时 HEAD `50ae6aa` 不落后，无需先 merge。
- 不新造状态机。证明续接消费 `proof-orchestrator` 已有轮次文件（`task.md`、`local-proof.md`、`audit.md`、`next.md`、`handoff.md` 等）。改进循环消费 `research-improvement` 的改进日志与 findings。pickup 只重读工作区真实 `compute-policy.md` 与 `research-log.md`。
- 阶段边界采用上游 PHASE-BOUNDARIES 五选项与先问顺序，共置于 `skills/general/research-os/PHASE-BOUNDARIES.md`，并指向 pickup。route-only 的「不在本发行」改为读这份已发行文件。
- 级联用反引号仓库路径，checker 已支持从仓库根解析 `skills/...`。既有 composition-map 只被 reference，不内联、不改写。
- 叶 skill 自带门保留：proof-orchestrator 的 round-scope / external-action，research-improvement 的 loop-authorization / experiment-topup。playbook 要求读到这些门后才进入对应动作。
- 测试先写 `scripts/test_check_skills_ticket45.py`，红于缺 playbook、缺路由行、旧「不在本发行」。
- notes 在 `.agents/`（gitignore），提交时 `git add -f`。

## Deviations

- 反引号级联若只写 `templates/improvement-log.md` 或 `playbooks/pickup.md`，checker 从所在文件和 skill 根都解析不到。改为仓库根路径 `skills/...`。Markdown 链接仍用相对路径。
- PHASE-BOUNDARIES 采用上游五选项与判断顺序，并增加「科研续接 → pickup」一段。没有把上游英文全文内联进 route-only。
- 行为证据：`/tmp/ros-pickup-cw7n/session.jsonl`。pi `cliproxy/glm-5.3-flash`，`--offline --approve`，未传 `--tools` / `--no-tools`。13 次工具调用全是 `read`：7 个级联文件 + 6 个交接文件。回复认定 `valid_until: 2020-01-01T00:00:00Z` 已过期、消耗 `unknown` 不按 0、零写入。交接 md 的 mtime 仍是生成时。
- 第一次无 session 的运行把 skill 根误当成 `/tmp` 交接目录，没有读到 playbook。不作为通过证据。通过证据是带 `--session` 的第二次轨迹。
- 未跑真实证明器、独立 reviewer 或补实验。proof 命题固定与 improvement 循环的执行行为仍是 AC 待验；本次只证明交接被读取且过期授权停住。
- 叶 skill 正文与 composition-map 未改。
