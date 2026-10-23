# #60 收缩切片 W — implementation notes

入口判定：本任务跨资源迁移、入口路由、许可与公开安装 seam，分为可独立验收的 writing 与 experiment 两个顺序 work unit；当前先处理 writing。依据用户明确禁止继续派发且给出“先完成 writing 二包并提交、bridge 明确剩余”的预算回退。基线 `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e`；仅此隔离 worktree，不碰 integration/main、不 push、不操作 tracker，也不拉入独立活文档提交 `a11775f58190d09aa6a2371272e61c5e05402386`。

| Work unit | 状态 | 产物与验收 | 下一步 |
|---|---|---|---|
| W1：统一 paper-writing 迁移 ML/Systems 专业资源，移除旧平行控制器 | done | 产品 commit `8a00c4bb51654c6c1e83c0cf477e7366a4458de0`；迁移映射及安装后合同完成；证据见下方日志 | `/tmp/spec48-ticket60-contract-W/REPORT.md` 汇总并交 parent |
| W2：experiment-bridge 兼容壳收缩至 run-experiment | 本轮明确剩余 | `experiment-bridge/{SKILL.md,LICENSE,agents/openai.yaml,references/{composition-map,mandate}.md,templates/bridge-report.md}` 与 `/research-os` 路由/README/验证地图/Checker 活调用者，以及 `run-experiment` CLI 独立安装均未改/未测 | Parent 后续单独收缩；不得把本轮 W1 证据外推至实验安装 |

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

## Deviations

- （无）
