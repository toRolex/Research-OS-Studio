# Spec48 / #60 最终验收聚合（R2）

日期：2026-10-24。范围按原 #60 七项 AC 与父 spec 决策聚合；本记录用于 parent 最终裁决，不代替关闭 issue。

## 最终集成状态（2026-10-24）

- 最终 review candidate `242a9fb7c1a3c693ac3f93d5953f4c7d884cc5d3` 已从原干净 integration HEAD `4816745b3f18db76adf64524a4eef080196339b6` 以 fast-forward-only 合入；本轮验收补记见 [`spec48-final-verification.md`](spec48-final-verification.md)。issue 状态仍由 parent 处理。
- 精确 doc-only 测试 HEAD `edca41919141515361b40d51438de7c9959f1003` 全 38 个 tracked 测试文件逐个串行运行：398 passed、760 subtests passed、无失败/跳过；最终细节与结果提交链见补充验收记录。
- 21 个确认 Spec finding 有独立关闭或精确对象继承证据；Standards 13 个原 ID 中 8 个关闭，5 个抽象建议（S1/S2/SL3-1/S4-1/W6-S2）明确延期且未修。
- #60 AC4 最终按 TD3 所声明的 sibling 依赖边可解析接受；这**不表示** `paper-compile-repair` 单装即可提供完整修复功能，也不表示多宿主或真实端到端执行已通过。下文保留 R2 当时记录及其证据边界。
- 历史轴仍有 8 项 unavailable（7 `UNVERIFIED`、1 `MISMATCH`），不记 history PASS；科研真值、生产 SSH、远程作业和多宿主 E2E 未验证。

## 身份与证据边界

- 权威输入：`/tmp/spec48-goal-preflight/spec.json`（SHA-256 `851d04a6b4b05552f5d5676fa024314c04b66981cfbc5d2959712b84b3726161`）及 `tickets.json`（SHA-256 `62dc2d7861936b15002ff34060405f5dc67c0f9577f097f794200721164b6921`）。AC 顺序和措辞以 #60 body 为准。
- R1 最终依赖已安全 `--ff-only` 合入本分支：`da7e703bb4b4c7cbedb66fdf1f4441aad69f9d01`（含 `3bff4a3`、`9503496` 与未知名漏检修复）。独立复审 `/tmp/spec48-checker-scope-review/REPORT.md` 关闭 F1/F2；F3 的精确回归由 `/tmp/spec48-checker-unknown-link-fix/REPORT.md` 和 parent 在精确 HEAD 上的复验接受：15 passed/42 subtests（含 12 格完整 CLI）、默认结构 rc=0、严格 history rc=1 保留 8 个不可用历史缺口。本记录不重改 checker/tests，也不重复全 suite；当前 history scope 非零不是结构通过或历史通过的混淆。
- 不读取、复制或恢复用户本机历史原包。`/tmp` 报告、安装快照和摘要只作为可追溯证据，不是随包自包含内容或历史原包身份证明。

## 七项 AC 结论

| 原 AC | 本轮结论 | 证据与限制 |
|---|---|---|
| 1. 无调用者且替代能力齐备后删除旧控制器/迁移兼容形式，保留必要数学方法、历史和资源。 | **通过（保留历史限制）** | `/tmp/spec48-ticket60-final-contracts/PSTACK-MATRIX.md` 记录 5 个旧 Skill 目录已移除及 50 项 retired-resource 映射；`skills/general/research-os/references/migration-boundary.md` 将原数学审查、交接方法、NOTICE 等资源指向随包 `proof-review`。历史验收记录保留于 [`evidence/README.md`](evidence/README.md)，未把旧原包全部恢复当门槛。独立历史检查仍为 rc=1（7 `UNVERIFIED` + 1 `MISMATCH`，均 `UNAVAILABLE`）；这不是历史通过，也不否定当前保留资源。依据父 spec ID9/10/17 与 R2 报告第 1、4、5 节。 |
| 2. 统一能力地图、使用说明、许可来源与校验合同，不按旧 39/14 数量限制产品。 | **通过（历史 scope 继续未验证）** | 41 叶能力覆盖与许可证/来源材料见 `/tmp/spec48-ticket60-final-contracts/COVERAGE-41.md`、`docs/upstream-sources-and-licenses.md`；本轮已最小修正迁移边界中“旧门两批并行”的过时描述。R1 unknown-link 修复使显式归档名登记与每条 href/fragment 目标逐一校验；parent 在精确 HEAD 实跑 15 passed/42 subtests（含 12 格完整 CLI），默认结构 rc=0。严格 history 仍 rc=1，8 个历史材料均 `UNAVAILABLE`；这是保留的历史身份限制，不认证为通过。父 spec TD7。 |
| 3. 检查保留能力的授权、停止及引用规则不与主入口反向冲突；独立调用仍可用。 | **通过（限既有合同审查与本轮必需边）** | `/tmp/spec48-ticket60-review-r3/REPORT.md` 对 C01–C07、K01、K02 逐项复判为 CLOSED；`COVERAGE-41-DELTA.md` 记录差分，没有据此宣称 41 叶方法全文重审。对 Research OS 入口、proof/paper-writing 路由、proof-review 只读审查及 repair sibling 声明共 11 个必需文档定向检查 69 条本地链接：0 missing；这些必需边没有 Markdown fragment，因此未遗留必需 anchor 的语义核验。安装总图仍有 23 个其他同文件 fragment 未作语义核验，不据此扩大本 AC 或宣称全量 anchor 审计。父 spec TD3/TD5。 |
| 4. 实际整包与代表性独立安装，检查发现、读取、自包含及无开发目录依赖。 | **通过（按 TD3：已声明的 sibling 依赖边可解析；不等于单装功能完整）** | `/tmp/spec48-final-test-hygiene/install-audit.json` 记录单一 Claude Code 宿主真实全装：41/41 slug、333/333 文件 SHA 一致、57 个许可/NOTICE 类文件一致、无 symlink/差异，项目仅 `.claude/skills`、HOME 为空；`/tmp/spec48-ticket60-verify-r3/REPORT.md` 另记 395 条相对路径全解析。该 full-install 源产品树 `skills` Git tree 为 `6a8a3556aafb54338cfdde40fe056fa5cce38407`，与本轮修改前的 `fd3d5e1`、R1 `3bff4a3` 相同。迁移说明是本轮唯一产品资源改动，故对当前 `research-os` 重新单装：CLI rc=0，35 个文件与源树逐项相同，`migration-boundary.md` source/install SHA-256 均为 `534f6a0559f551ce0fe8795538d5fbdf65cdadb83ec31c59b1c78d1088d3457a`。最终证据目录 `/tmp/spec48-ticket60-final-ac/tmp/research-os-final-install.QNxB6x`（首轮目录在补回 checker 必需 section 前，不作为最终安装证据）。TD3 下接受已声明并可解析的 `paper-compile` sibling 关系；边界仍是 `paper-compile-repair` 单装 10/10 文件成功**不等于**完整修复功能独立可用，组合安装 18/18 且 7/7 sibling 边可解析。该限制及其 hash 证据见 R3/hygiene 报告，不称单装全功能通过。没有跨宿主实测。父 spec TD1/TD3。 |
| 5. 对固定 pstack 版本完成结构职责与 verify 原则对照，记录适配、排除、实证和未验证范围。 | **通过（按明确范围）** | `/tmp/spec48-ticket60-final-contracts/PSTACK-MATRIX.md` 固定源为 `88d47514b82e7c44f00f2b2a72ff6dd12158038c`，保留适配、排除项、引用的既有执行证据及未验证边界；原表 C01–C06 权限语义未收敛、C07 旧兼容入口等失败记载未删除，当前关闭依据追加见 R3 C01–C07/K01/K02 逐项复审。上游缓存 37/37 blob 一致仅证明缓存与记录一致，不是远端来源认证；未验证原则叶、helper 实跑、全宿主、真实科研及 reviewer/runtime 均保留为未验证。父 spec TD4/TD6/TD9。 |
| 6. 本票是最终聚合而非首次测试；前序各票已各自完成检查。 | **通过（前序检查证据齐备；整体裁决交 parent）** | R1 完整串行 suite 在 `3bff4a3` 基线上实跑 35 个文件、356 passed/625 subtests；默认结构 checker rc=0，严格历史 checker rc=1（7 `UNVERIFIED`、1 `MISMATCH`）。随后 F1/F2 独立复审实跑 33 passed/71 subtests 与 37 mutants；F3 的 12 格完整 CLI 在最终 `da7e703` 定向复验 15 passed/42 subtests，parent 接受。没有在 `9503496`/`da7e703` 重跑 full suite，不作该声明。既有逐票记录和 R3 合同复审用于说明前序检查，不以旧 issue snapshot 中 OPEN/CLOSED 状态代替证据。最终 #60 接受与整体集成仍由 parent 裁决。 |
| 7. 不要求真实开放问题求解、生产 SSH、付费 GPU、长期无人值守或全部宿主端到端实测。 | **通过** | 本记录将单宿主真实安装与静态/人工对照分开报告；没有把跨宿主运行、真实科研、生产远程作业或长期运行列为通过条件。父 spec Out of Scope 与 AC7 一致。 |

## 聚合裁决与限制

- **历史 R2 结论保留，最终 AC4 解释已补齐。** `da7e703` 上 F3 12 格回归及两轴 checker 已由 parent 接受；严格 history 的 8 个不可用缺口仍是未验证，不是新硬门。R2 原先将 AC4 列为部分通过；本次按 TD3 对已声明 sibling 可解析的合同作接受解释，仍不把 repair 单装说成完整功能通过。
- **没有“恢复全部旧历史包”硬门。** 结构与历史两轴不可混为一谈；历史仍未验证，尤其 validation 候选 SHA mismatch 和范围外 deliverables 继续披露。若某项必要方法/许可资源唯一证据只存在于缺失原包，才阻塞该具体项；现有 R2 证据未指出此类必然依赖。
- `paper-compile-repair` 的完整修复分支要求可解析、已声明的 `paper-compile` sibling；单装不能称完整独立功能通过。23 个非必需 fragment、全宿主实测、真实 reviewer/数学正确性和长期运行均未认证。

## 本轮修改与验证

- 修改仅为本文件、`.agents/notes/spec48-ticket60-final-ac-implementation-notes.md` 和 `skills/general/research-os/references/migration-boundary.md`；未修改 checker/tests、其他产品 Skill/许可证、原包、integration 或 issue 状态。
- 当前 `research-os` 真实定向安装命令：`npx --offline --yes skills@1.7.4 add <worktree> --skill research-os --agent claude-code --copy --yes`，运行于树外 `/tmp/spec48-ticket60-final-ac/tmp/`；rc=0。整个 Skill 子树 `diff -qr` rc=0，迁移说明 `cmp` rc=0；最终 installed/source SHA 同为 `534f6a0559f551ce0fe8795538d5fbdf65cdadb83ec31c59b1c78d1088d3457a`。R1 的 final targeted/history/structure/diff 证据见 `/tmp/spec48-checker-unknown-link-fix/REPORT.md`；没有重跑其 suite。
- 必需引用筛查用 `uv run --offline --no-project python`，仅覆盖上述 11 个文档：69 本地链接、0 missing、0 fragment；这是范围筛查而非全仓 Markdown anchor validator。
