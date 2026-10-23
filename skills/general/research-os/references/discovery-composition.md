# Discovery 组合参考

本参考供 `/research-os` 的 Discovery recipe 按需读取。它说明五项 Required 能力如何组合，不是中央协议或第二总控；职责表不构成固定顺序。先识别本次目标缺口、已有结果与未解事项，再选能力子集、排序或回访。叶 Skill 的来源、预算、原文评审、写入和完成要求始终有效。

## Required skills

完整支持“从研究方向到 Proposal”需要五项独立能力：`research-lit`、`idea-generation`、`novelty-check`、`idea-review`、`idea-refinement`。这是能力依赖集合，不是每次必须全部执行的阶段清单。按本次目标和证据选择缺口子集；已有成果已覆盖的职责可省略，新增文献或评审意见可触发重排、回访。独立使用某项叶能力仍可完成局部目标。

`creative-thinking-for-research` 是可选能力，只在生成受阻、该 Skill 已安装且本次目标需要时调用；缺少它不构成阻塞。

通过通用 Skills CLI 单独安装 `research-os` 并要求发现能力时，同时安装五项 Required skills；CLI 不会解析逻辑依赖：

```bash
npx skills@latest add toRolex/Research-OS-Studio \
  --skill research-os research-lit idea-generation novelty-check idea-review idea-refinement \
  --agent codex --copy -y
```

使用其他 CLI 版本时先查 `skills add --help`。若不支持多个 `--skill` 值，对同一项目逐个安装或安装整包。安装后从宿主实际报告的位置读取 `research-os` 与各叶 Skill，再从每个 Skill 自身目录解析其共置资源和许可；不依赖源码 checkout、开发路径或配方文件的位置推导其他包。

本配方采用的上游 Idea Cycle 资源按原有 MIT 条款发行；完整许可副本随本包保存在 [licenses/idea-cycle/LICENSE](../licenses/idea-cycle/LICENSE)。

缺少依赖只阻塞受影响职责：任一 Required Skill、其本次所需资源或宿主需要的独立 reviewer 不可用时，只将依赖它的职责标为 **DEPENDENCY MISSING / BLOCKED** 或 **REVIEW UNAVAILABLE / EVIDENCE GAP**，写明受影响目标与可行补救；完成其他已授权且不依赖它的分支。不得假报已运行，也不得以顺序代跑或生成者自查冒充 fresh 独立评审。

## 能力矩阵

| 能力 | 适用缺口 | 典型贡献 | 综合报告章节 |
|---|---|---|---|
| `research-lit` | 文献范围或来源证据不足 | 有出处的 literature landscape | `# 文献 Landscape` |
| `idea-generation` | 缺少候选或探索视角不足 | 候选池与筛选理由 | `# 候选池与筛选` |
| `novelty-check` | 候选主张尚未对照 prior work | closest-work 比较或具名证据缺口 | `# 查新结论` |
| `idea-review` | 需要独立挑战与裁决（fresh 外部 reviewer） | 独立 findings、来源定位与未决意见 | `# 独立评审` |
| `idea-refinement` | 方法选择/收敛或 Proposal 未完成 | 固定 Problem Anchor 下的路线取舍 | `# 收敛与 Proposal` |
| `creative-thinking-for-research`（optional） | 生成受阻于单一表述、表面类比或二选一 | 可检验的认知转换 | `# 候选池与筛选` 单列 |

完整方向到 Proposal 通常需要五项职责；现有文献可让工作从生成或查新开始，现成候选可先做查新、评审或细化，已有证据可覆盖其他职责。生成、查新和独立评审的相对顺序依赖目标与材料。每项只按自身完成条件执行并记录跳过理由和覆盖边界；不为凑齐模板而制造未运行的章节。

若交付综合报告，采用 [templates/discovery-report.md](../templates/discovery-report.md) 的 canonical 章节，保留叶能力的原始实质结论；模板是自然语言检查单，不是 schema、审批表或阶段 gate。各叶贡献只写入用户明确授权的目标文件或新路径。单项目标可直接交付局部结果，不强制生成 Discovery 报告或 Proposal。

## 证据与分支边界

- 调用 `idea-review` 时，fresh reviewer 直接读取获准的原始候选与文献；将实际评审请求和原始回复逐字完整内联到获准报告的 `# 独立评审`，保留轮次、来源定位及未解决意见；链接或摘要不替代原文。没有执行评审时不制造空章节。
- 无可用检索时，`research-lit` 可按其 Skill 规则综合用户提供的材料，并限定覆盖范围；不得推断“无文献存在”。
- 缺少可读研究材料时，报告受影响的生成/评审职责与所需输入；仍可完成不依赖材料的范围澄清。
- 参考论文全文不可读时保留具体证据缺口，不凭记忆补写；不因此阻塞其他适用职责。
- 额度耗尽时停止该类新工作；用现有证据完成其余授权职责，报告未检查项，不扩大额度或循环尝试。
- 主要目标替换须由用户确认；独立候选分支的越权、超额或文件冲突仅阻塞对应分支。
- 完成用户目标或报告未决缺口后停止；不自动启动 pilot、experiment-plan、Validation 或 Writing。
