# #60 收缩切片 W — implementation notes

入口判定：本任务跨资源迁移、入口路由、许可与公开安装 seam，分为可独立验收的 writing 与 experiment 两个顺序 work unit；当前先处理 writing。依据用户明确禁止继续派发且给出“先完成 writing 二包并提交、bridge 明确剩余”的预算回退。基线 `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e`；仅此隔离 worktree，不碰 integration/main、不 push、不操作 tracker，也不拉入独立活文档提交 `a11775f58190d09aa6a2371272e61c5e05402386`。

| Work unit | 状态 | 产物与验收 | 下一步 |
|---|---|---|---|
| W1：统一 paper-writing 迁移 ML/Systems 专业资源，移除旧平行控制器 | done | 产品 commit `8a00c4bb51654c6c1e83c0cf477e7366a4458de0`；迁移映射及安装后合同完成；证据见下方日志 | `/tmp/spec48-ticket60-contract-W/REPORT.md` 汇总并交 parent |
| W2：experiment-bridge 兼容壳收缩至 run-experiment | 待验收 | run-experiment 单包资源、研究配方/文档、checker 与 #56/#60 测试已同步；测试证据见下方“W2 续接” | 明确 integration tip 复验后提交产品；notes 再记录最终 commit 与报告位置 |

## W1 资源迁移映射（实施前）

| 旧资源 | 新权威资源 | 保留原则 |
|---|---|---|
| `ml-paper-writing/references/experiment-reporting.md` | `paper-writing/references/ml-experiment-reporting.md` | 保留报告、复现性与限制方法，不并入短 standards 摘要 |
| `ml-paper-writing/references/reviewer-expectations.md` | `paper-writing/references/ml-reviewer-expectations.md` | 保留审稿人关注维度与来源归属 |
| `ml-paper-writing/references/venue-checklists.md` | `paper-writing/references/ml-venue-checklists.md` | 保留 venue 检查项、来源与当前规则核验边界 |
| `ml-paper-writing/templates/ml-writing-report.md` | `paper-writing/templates/ml-writing-report.md` | 独立模板随统一包安装 |
| `ml-paper-writing/references/sources.md` + `LICENSE` | `paper-writing/references/sources.md` + `LICENSE-ML.txt` | 归并来源说明；核对已有许可证字节相同后只保留一份真实许可证 |
| `systems-paper-writing/references/checklist.md` | `paper-writing/references/systems-checklist.md` | 保留阶段自检资源，不与 ML/general checklist 混同 |
| `systems-paper-writing/references/evaluation-methods.md` | `paper-writing/references/systems-evaluation-methods.md` | 保留评价面、公平性与可复现方法 |
| `systems-paper-writing/references/systems-writing-methods.md` | `paper-writing/references/systems-writing-methods.md` | 保留系统贡献、实验与写作方法 |
| `systems-paper-writing/references/venue-and-reviewer.md` | `paper-writing/references/systems-venue-and-reviewer.md` | 保留 venue/reviewer 专项资源 |
| `systems-paper-writing/templates/systems-paper-writing-report.md` | `paper-writing/templates/systems-paper-writing-report.md` | 独立模板随统一包安装 |
| 两个旧 `references/composition-map.md` | `paper-writing/references/composition-map.md` + 各专业 playbook | 通用能力组合保留在统一 map；ML/Systems 特有资源顺序、条件与缺口语义落到对应路由 |
| 两个旧 `SKILL.md` 控制器 | `paper-writing/SKILL.md` + `paper-writing-ml/systems.md` playbook | 统一停止/委托合同，保留领域请求表达与专业编排差异 |
| 两个旧 `agents/openai.yaml` | 删除 | 用户通过唯一统一入口调用，不保留第二可发现控制器 |
| Systems 两份 LICENSE | `paper-writing/LICENSE-ARIS.txt`、`LICENSE-Orchestra.txt` | 已有同名许可逐字相同；中央来源记录改指向统一包的实际资源 |

## 决策记录

- 两个旧写作包合计约 1,109 行参考/模板且各有不可替代专业内容；优先逐文件迁移并保留专业分层，而不是扩大 `standards.md` 或删成控制器摘要。
- 真实许可文件的字节核对：ML 与统一包 `LICENSE-ML.txt` 相同；Systems ARIS、Orchestra 许可也分别与统一包现有文件相同。将验证结果落入报告与合同测试，不重复散布许可副本。
- 安装后 public seam 先 red（3 项合同失败），再 green（3/3）；Skills CLI 1.7.4 从 npm cache 在独立 `/tmp` HOME/cwd 单装 `paper-writing`，安装 21 文件，manifest SHA256 `0c1171d271c825311694aa184edef161776d7f4ee691bcb443f8715c99fe5eb9`。实际 CLI 输出与哈希见报告。
- 最终通过日志：`final-ticket60-writing-2.log`（3 tests）、`final-ticket57-2.log`（13）、`final-ticket43.log`（8）、`ticket38.log`（21）、`accept-remediation-contract-final.log`（4）、`policy-gates-corrected.log`（4）、`tracked-scan.log`（1）；各命令串行、树外 `TMPDIR=/tmp`、真实 return code，单条 subprocess timeout 180s。
- Checker 最终仍返回 1，但仅余 9 条历史 `docs/acceptance/**/evidence/*.tar.gz` 诊断；原始输出与 `/tmp/spec48-closed-baseline/logs/head-checker.log` 完全一致。未运行全套；沿用 #55 merger 报告记载的 6 个历史失败，不把它们写成当前全套实测。
- W2 尚未改动。剩余包括 `skills/validation-cycle/experiment-bridge/{SKILL.md,LICENSE,agents/openai.yaml,references/{composition-map,mandate}.md,templates/bridge-report.md}`；活调用者包括 `skills/general/research-os/SKILL.md`、`playbooks/experiment-bridge.md`、`README.md`、`skills/README.md`、`references/{PRODUCT-MAP,validation}.md`、`docs/upstream-sources-and-licenses.md` 与 `scripts/check-skills.py`/`tests/test_spec48_ticket56.py` 合同；另需在独立 HOME/cwd 执行 `run-experiment` CLI 单装验证。保留 bridge 配方名可以，但须移除兼容 Skill 控制器并把报告、组合资源及许可归属移到 `run-experiment`。

## W2 收缩实施记录

- **入口判定**：直接在当前隔离 worktree 执行一个有界 W2 单元。用户明确“独立 T3 worktree、不写 integration/main、不 push/tracker、不继续派发”；因此不派发。材料已提供 W2 精确剩余、#48/#60 缓存与 W1 真实单装报告，前置输入齐备。当前分支 `t3/shrink-experiment-bridge` 起于 `integration/spec-48=14d9c6e`，已先快进合入 W1 来源 `3bf2fa3a6a4e10b78a455d302474607ea1013038`；不拉入未完成 Discovery 或独立活文档来源。
- **规则**：已读全局 Multi-Agent、model-availability、CODING_STANDARDS、仓库 `AGENTS.md`、pre-implement、writing-for-agents 与 `SKILL-MECHANICS.md`，以及 #56 ticket56 合同测试/实施记录。当前安装未找到单独的 TDD Skill（`tdd/SKILL.md`、`tests.md`、`mocking.md` 均不存在）；按用户指定的安装后 public seam 先 red→green，不宣称该 Skill 已加载。不得削弱作业身份、退出码、日志、产物有效性、断线先查原任务、数学/非训练分支与额度合同。
- **映射完成**：旧 `LICENSE` 与 `run-experiment/LICENSE` 字节相同（SHA-256 `e30cf5dd5f49b4f9b656590e23d782b4756c924a9f0ff0162b3e7b5d87006bf5`）；旧 `references/mandate.md` 与 run-experiment 同路径副本相同（SHA-256 `88aa76af938dfbcf4baf680c51389c17ed6639bd39328fc3b36ef99e692e04e1`），重复副本已删除。旧组合图的“只选择所需分支、缺能力只阻塞该分支”并入新 `run-experiment/references/composition-map.md`。旧 82 行 bridge report 的实现审查、监控/健康、分析、审计、tracker、消融建议与 next-options 章节并入统一 `templates/run-report.md`；原 attempts/milestones 合并到已有更强作业身份/输入版本/工具链/退出码/日志/产物有效性合同，不重复建模板。旧 Skill/controller metadata 删除；用户需求名只留在 Research OS 配方并直接委托 run-experiment。

### W2 初始检查点与续接

### W2 暂停检查点

- 初始 public-seam 红灯命令 `uv run --offline --with pytest python -m pytest -q -p no:cacheprovider tests/test_spec48_ticket60_bridge.py`，真实退出码 1，4 tests failed。具体：旧目录仍存在；配方合同测试要求 route 文本提及 monitor（此项需保留监控职责但断言应核对适当地图/路由，不应把 monitor 强制并入执行器）；run-experiment 无组合图；真实 Skills CLI 安装副本缺 `references/composition-map.md`。
- 红灯中的真实 Skills CLI `skills@1.7.4` version 命令与 `add ... --skill run-experiment --agent claude-code --copy --yes` 均返回 0；单装目录仅含 `run-experiment` 的断言已通过，随后按合同在缺组合图处失败。没有把 shell copy 当 CLI 安装。原始 CLI stdout/stderr 尚未落盘，不能声称已有 CLI 日志文件或 hash 清单。
- parent 随后重新授权同一 W2，未换 worktree、未重置/清理 patch、未追加派发。

### W2 续接

- **public seam red→green**：原始 red 见上。修正 monitor 检查为职责组合（recipe 只在用户要求时委托；组合图验证观察事实、不控制作业且能力缺失仅阻塞该分支）；最终 `tests/test_spec48_ticket60_bridge.py`：4 passed，13 subtests passed，exit 0。该测试使用真实缓存 Skills CLI 1.7.4 在独立 `/tmp` HOME/cwd 单装，并核对包文件集、逐字节内容、链接、许可证及未安装的 queue 分支行为。
- **#56/入口合同**：`tests/test_spec48_ticket56.py`：27 passed，13 subtests passed；`scripts/test_check_skills_ticket42.py`：4 passed；`scripts/test_check_skills_ticket46.py`：9 passed，2 subtests passed；`scripts/test_check_skills_ticket43.py`：8 passed，3 subtests passed。均为串行、树外 `TMPDIR=/tmp`。
- **checker 基线**：`uv run --offline python scripts/check-skills.py` exit 1，诊断精确为原有 9 条 `docs/acceptance/**/evidence/*.tar.gz` 断链；无 bridge 或其他新诊断。未运行完整测试套件，保留 #55 merger/W1 报告中的原 6 个全套失败（本轮未重跑、未改历史资料或 allowlist）。
- **真实最终 CLI 安装**：`skills@1.7.4 add <worktree> --skill run-experiment --agent claude-code --copy --yes --json` exit 0，选中 1 个、状态 installed、mode copy；独立 HOME/cwd 在 `/tmp/spec48-ticket60-bridge/final-cli-json/`。九个包文件的集合与字节哈希与源码一致；7 个 Markdown 内链全部闭合，无跨包依赖。包清单聚合 SHA-256 `a7bf613a69a3a603cf7186f518570325bb0d22da109058e9850c8e8d9373528d`；逐文件散列与 CLI 日志在 `/tmp/spec48-ticket60-bridge/logs/`，实际安装输出、许可与 mandate 哈希详见 `/tmp/spec48-ticket60-bridge/REPORT.md`。
- **安全合同保留**：#56 测试继续核查作业身份、退出码/日志/产物有效性、断线查原任务后不盲重跑、数学/非训练对照与本批额度。研究配方没有第二授权账本或作业状态机；计划、队列、监控、健康、分析、审计与 Claim 判断仍由独立职责承担。
- **integration-tip 复验**：最终核对 `integration/spec-48=14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e`，在任务分支执行 `git merge --no-edit integration/spec-48` 得 `Already up to date`；合并后按上述顺序串行复跑 bridge 4/13、ticket56 27/13、ticket42 4、ticket46 9/2、ticket43 8/3，均 exit 0。checker 仍仅有原 9 条归档断链。diff check exit 0。
- 当前测试和同步已完成；仅待产品 commit、最终 notes 状态/notes commit 与 `/tmp/spec48-ticket60-bridge/REPORT.md` 落盘。状态区暂列待验收，不提前标 done。

## Deviations

- （无）
