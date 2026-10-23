# Discovery

本 recipe 是 `/research-os` 内部的发现路线，不是第二个入口或独立 Skill。用户可以直接说明研究方向、已有成果与目标；“从方向到 Proposal”是完整且独立可交付的用户目标，完整需求不要求先指定技能名称、单独 setup 或批准阶段转换。用户也可只要求一个已有方向下的局部发现结果。

本 playbook 将一次委托接入可组合的发现能力，不固化路线或阶段顺序。先按目标缺口和已有证据选择能力；匹配后持续的是用户目标、授权与额度，新证据可改变能力选择，局部工作完成不要求切换用户目标。用户明确说 new task 时，返回入口重匹配，不把旧目标带入新委托。

## 委托继承与边界

沿用 `/research-os` 的当前目标、权限、额度、完成与停止条件；内部能力继承该授权，不重复索要已授予的决定。目标、可用材料、权限、总预算与交付物由用户决定；未给出的约束保持未知，不以假设补齐。

只有主要目标替换、越权、超额、未授权破坏性或对外动作、以及既有文件冲突需要用户决定。将缺工具或缺依赖标为受影响职责的阻塞，只暂停该职责；其他不依赖分支继续。保留原始材料，只在授权目录写入不冲突的新产物；公开检索不授权上传私有材料、付费服务、新凭据、远程写入或安装科研环境。

## 按需角色

Role: orchestrator

负责盘点目标、已有材料、已完成成果及未解缺口；按需选择职责并协调交付。下列角色映射供缺口委派使用，不要求每次都调用，也不构成阶段顺序。

Role: literature

按需承担文献范围、来源证据或 prior-work 核对，对应 `research-lit` 与 `novelty-check`。

Role: ideator

按需承担候选生成、视角扩展或方法收敛，对应 `idea-generation` 与 `idea-refinement`。

Role: reviewer

仅在需要独立挑战时委派给 fresh 独立评审者，对应 `idea-review`；生成者自查不替代该角色。

按安装后的 Skill 名称定位其目录；读取其完整 `SKILL.md`，并从该 Skill 目录解析共置 `references/`、`templates/` 和许可文件。下表的资源文件名相对于所选 Skill 的对应目录，不依赖仓库源码目录布局。

按用户目标和已有材料选择能力。用户需要完整方向到 Proposal 时，按缺口组合五项 Required 能力；已有成果可满足个别职责时省略并记录边界，不把五项变成固定流水线。需要组合规则时读[Discovery 组合参考](../references/discovery-composition.md)。需要综合报告时，先用[Research Brief 模板](../templates/research-brief.md)整理用户提供的 brief（可选输入），并按[Discovery Report 模板](../templates/discovery-report.md)汇总被选职责；最终 Proposal 仅在用户目标包含 Proposal 且 refinement 实际完成时交付。

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
4. 按用户要求交付局部结果或综合报告。只有目标包括 Proposal 时才运行 refinement 并交付 Proposal；不默认制造完整流水线产物。若目标是完整方向到 Proposal，按未解决缺口组合所需职责并交付完整报告与实际完成的 Proposal。

**完成条件**：用户本次目标达到，或未达成部分均有可核对的缺口/阻塞；实际读取的文件、完成/省略/blocked 的职责和写入路径可核对。目标替换、越权、超额、既有冲突保留决定门，仅阻塞对应工作。

完成后停止，不自动启动 pilot、实验计划、Validation 或 Writing。
