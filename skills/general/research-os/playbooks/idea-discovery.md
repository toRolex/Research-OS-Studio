# idea-discovery

本 playbook 将一次委托接入可组合的发现能力，不固化路线或阶段顺序。匹配后持续的是用户目标、授权与额度；新证据可改变能力选择，局部工作完成不要求切换用户目标。用户明确说 new task 时，返回入口重匹配，不把旧目标带入新委托。

## 按需角色

Role: orchestrator

负责盘点目标、已有材料、已完成成果及未解缺口；按需选择职责并协调交付。下列角色映射供缺口委派使用，不要求每次都调用，也不构成阶段顺序。

Role: literature

按需承担文献范围、来源证据或 prior-work 核对，对应 `research-lit` 与 `novelty-check`。

Role: ideator

按需承担候选生成、视角扩展或方法收敛，对应 `idea-generation` 与 `idea-refinement`。

Role: reviewer

仅在需要独立挑战时委派给真实独立评审者，对应 `idea-review`；生成者自查不替代该角色。

按安装后的 Skill 名称定位其目录；读取其完整 `SKILL.md`，并从该 Skill 目录解析共置 `references/`、`templates/` 和许可文件。下表的资源文件名相对于所选 Skill 的对应目录，不依赖仓库源码目录布局。

| 缺口 | 可选职责 | 读取材料 |
|---|---|---|
| 文献覆盖/来源证据不足 | `research-lit` | 读取其 `SKILL.md`；检索时按需读 references/source-methods.md、references/source-verification.md，文件处理时读 references/file-capability-audit.md |
| 候选不足/视角单一 | `idea-generation`；卡在单一表述时可选 `creative-thinking-for-research` | 读取 `idea-generation` 的 `SKILL.md`，按需读 references/generation-methods.md、references/ideation-frameworks.md；创意能力只在已安装时调用，需用时读 references/creative-frameworks.md |
| prior work 未核对 | `novelty-check` | 读取其 `SKILL.md` 与本次实际使用的 references/source-verification.md |
| 需要独立挑战 | `idea-review` | 读取其 `SKILL.md` 与其点名的 references/review-task.md |
| 需要方法收敛/Proposal | `idea-refinement` | 读取其 `SKILL.md`，按需读 references/method-development.md、references/method-review.md，需要 Proposal 时读模板 templates/proposal.md |

## 执行与交付

1. 将用户目标拆成可检查缺口，并标出已有材料已经覆盖的职责。
2. 选择与缺口对应的能力子集；进入每项能力前读取其完整 SKILL.md 与当次所需 reference。叶能力保留自身的来源、独立评审、预算和写入要求。
3. 可依现有证据重排、跳过已满足职责，或在新增证据后回访前项；记录选择理由、未覆盖范围和每项真实结果。缺少依赖或真实独立 reviewer 时如实 blocked/unavailable。
4. 按用户要求交付局部结果或综合报告。只有目标包括 Proposal 时才运行 refinement 并交付 Proposal；不默认制造完整流水线产物。

**完成条件**：用户本次目标达到，或未达成部分均有可核对的缺口/阻塞；实际读取的文件、完成/省略/blocked 的职责和写入路径可核对。目标替换、越权、超额、既有冲突保留决定门，仅阻塞对应工作。

完成后停止，不自动启动 pilot、实验计划、Validation 或 Writing。
