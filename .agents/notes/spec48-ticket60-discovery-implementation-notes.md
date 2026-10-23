# #60 idea-discovery slice — implementation notes

## Status

- Discovery controller: **done**；资源映射、方向→Proposal 需求、活调用清理、控制器删除、最小 public-seam red→green、CLI 双安装、checker 基线比较、integration tip 复验和提交均完成。证据及交接报告：`/tmp/spec48-ticket60-discovery/REPORT.md` 与其 `logs/`。
- 其他 #60 slices / 全票验收：**不在本单元范围**；由 parent/merger 处理。

## 入口、边界与基线

- 入口判定：直接执行这个用户明确限定的单控制器 work unit；不再派发，独立 worktree 内实现。探索范围只覆盖 idea-discovery；proof 迁移不重做，W 的 writing/bridge 目录不触碰，活文档源 `a11775f...` 不提前合入，不写 integration/main、不 push、不操作 tracker、不做整票验收或历史 archive。
- 本次预先约定的 TDD public seam（来自任务 brief）：安装后的 `research-os` 发现配方及同包资源；验证完整 direction→Proposal 需求/模板/许可可达、旧控制器无活调用、五项能力按缺口子集组合/重排/回访且不变成固定流水线、缺依赖只阻塞关联分支、fresh 独立审查仍保留。
- 起始 worktree `/Users/rolex/.t3/worktrees/Research OS Studio/t3-845d3885`，branch `t3/rework-discovery-controller`，基于 integration `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e`；按要求已 fast-forward merge 精确 proof 交付 `ff53d4689684099c34b8a6e026fe56b3be10ed93`，当前工作树 clean。
- 已读全局 Multi-Agent/model-availability/CODING_STANDARDS、仓库 AGENTS/CLAUDE/GLOSSARY/ADR-0005、pre-implement、writing-for-agents 与 SKILL-MECHANICS、`~/.claude/skills/tdd/{SKILL,tests,mocking}.md`，以及 `/tmp/spec48-ticket60-contract-M/REPORT.md`、`/tmp/spec48-ticket60-prep/REPORT.md`、`/tmp/spec48-goal-preflight/{spec.json,tickets.json}`。

## 决策记录

- proof 收缩源是当前 HEAD 的祖先；merge 为 fast-forward，无冲突。其 15 份 proof-review 资源及既有独立 CLI 验证属于已完成输入，不复做、不改写其证据。
- 先完成逐文件旧→新归属映射与活调用者核查，再写最小 seam 测试；以逐字节迁移保留来源资产，语义仅在新配方/参考表达必要差异；source/license 仅随包迁移既有授权，不扩大许可或改验证标准。

### 旧资源 → 新能力映射（实施前）

| 旧路径 | 新归属／保留方式 | 预期保真 |
|---|---|---|
| `skills/idea-cycle/idea-discovery/SKILL.md` | `skills/general/research-os/playbooks/discovery.md`；保留方向→Proposal 独立目标、委托继承、目标/额度/文件决定门、按需组合与报告交付，不保留独立 Skill 控制器/阶段总控 | 语义保全并适配唯一入口 |
| `skills/general/research-os/playbooks/idea-discovery.md` | 同包 `playbooks/discovery.md` | 迁入现有可组合配方，修正引用与入口名 |
| `skills/idea-cycle/idea-discovery/references/composition-notes.md` | `skills/general/research-os/references/discovery-composition.md` | Required 五能力、optional creative、依缺口子集/重排/回访、分支阻塞、真实独立 review、canonical 报告和来源/额度/写入边界保全；安装示例改为新入口 |
| `skills/idea-cycle/idea-discovery/templates/research-brief.md` | `skills/general/research-os/templates/research-brief.md` | 保全 brief 的问题、背景、约束、产物、假设与已有结果字段；把入口称呼改为新 recipe |
| `skills/idea-cycle/idea-discovery/templates/discovery-report.md` | `skills/general/research-os/templates/discovery-report.md` | 保全所有能力章节与证据/交付字段；移除过时的逐阶段批准记录，改为缺口选择/重排/回访记录 |
| `skills/idea-cycle/idea-discovery/LICENSE` | `skills/general/research-os/licenses/idea-cycle/LICENSE` | 逐字节搬迁，随新包复制发行 |
| `skills/idea-cycle/idea-discovery/agents/openai.yaml` | 删除 | 宿主专用 controller 元数据不是发现能力资源；新入口按通用 `research-os` Skill 分发 |

活调用清理范围：`research-os` 路由/新 playbook/安装示例、README 中英/skills README、PRODUCT-MAP 与 Idea Cycle 能力图、demo 与 workflow 图、checker 的 required/legacy/static path、58 与 gate 测试。来源记录和 acceptance/历史 notes 中关于上游采用的历史叙述保持原样；新包携带既有 MIT LICENSE。
- Red：先新增 `tests/test_spec48_ticket60_discovery.py` 作为安装后 `research-os` 包可见能力的 public seam（完整入口与报告/brief、五个 Required 与 optional creative、动态组合/局部分支阻塞/fresh review、许可与旧调用退休）。迁移前实际运行 `uv run python tests/test_spec48_ticket60_discovery.py`，exit 1，首个可观察失败为入口无 `discovery` 路由；这是实际 pre-implementation red。
- Green：`uv run python -q tests/test_spec48_ticket60_discovery.py` 最终 exit 0。重定向 #58 原测试职责到 research-os 包后，`tests/test_spec48_ticket58.py` 23/23、`scripts/test_check_skills_ticket38.py` 21/21、`scripts/test_check_skills_ticket46.py` 9/9、`tests/test_check_skills_policy_gates.py` 4/4、`tests/test_accept_remediation_contract.py` 4/4 均实跑通过；保留并验证了 dropped composition、固定顺序、缺 Required 依赖、源树路径等负例。CLI manifest 见 `/tmp/spec48-ticket60-discovery/logs/cli-manifest-and-links.txt`。
- Skills CLI：缓存 `skills@1.7.4`，version、树外 `research-os` 单包安装与树外 `research-os`+五 Required 组合安装分别 returncode 0；两次均独立 HOME/CWD，组合安装 6 个 slug。逐文件比较 65/65 文件 hash 全等（research-os 34、research-lit 7、idea-generation 7、novelty-check 5、idea-review 5、idea-refinement 7）；包内 Markdown links 无断链。Required slug 与 CLI 命令一致，creative-thinking-for-research 明确 optional 且未混入组合安装。
- checker：`uv run python scripts/check-skills.py` 返回 1，仅保留 proof Slice M 基线的 9 条 `docs/acceptance/**/evidence/*.tar.gz` 缺失诊断，逐行一致；无本 slice 新诊断，未弱化 checker。
- 合并复验：明确读取并执行 `git merge --no-edit refs/heads/integration/spec-48`；integration tip `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e` 已是祖先，结果 `Already up to date`。另确认活文档源 `a11775f58190d09aa6a2371272e61c5e05402386` 仍不是当前 HEAD 祖先，遵守不提前合并。
- License 全文仍为源 SHA256 `e30cf5dd5f49b4f9b656590e23d782b4756c924a9f0ff0162b3e7b5d87006bf5`；brief/report 模板分别从原 SHA `5f4b2705ca6cac7753fa893631b001a50c74ff109e9c1ea0828fe56061c5e56c` / `d21023a5be365c37d9b8644a68bbf2809b229f8b073b26cdbd9c236509e1f29a` 适配为新 SHA `8bbcff5a9e333a05516172fc8e91f400825f8db0212abe70834f2e4183aac6d0` / `653eac9e96b3144e44f0cfa9f335f14d379d67f5d1976a2af719c0d6722f669a`。报告仅去除阶段批准字段并更新新入口路径，保留原报告章节与 brief 要素。

## Deviations

- 首次 CLI 执行忘记将命令 CWD 切到树外临时项目，CLI 在当前 worktree 产生 65 个被忽略的安装副本及 `skills-lock.json`。发现后用 `apply_patch` 全部删除；再把两个安装命令分别重跑于独立 `/tmp` CWD 与 HOME，只有后两次结果作为验收证据。跟踪树安装副本计数为 0、lock 不在版本差异中；没有调用外部检索、账户、联网内容源或真实科研工作流。
