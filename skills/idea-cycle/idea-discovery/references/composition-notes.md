# 组合说明：阶段映射与缺口降级

本文件是 `idea-discovery` 的共置方法说明，不是中央协议。各内部能力按自身 SKILL.md 执行；本表只规定阶段顺序、它们向 canonical 报告贡献哪个章节，以及能力缺失时如何降级。章节内容原样合入，不改写。

## 阶段映射

只有本次明确给出 canonical 报告路径（默认 `IDEA_DISCOVERY.md`）时，各内部能力才以 composed 模式贡献对应章节；路径存在本身不是 composed 信号。

| 阶段 | 调用的已交付内部能力 | canonical 章节锚点 |
|---|---|---|
| Phase 1 文献 | `research-lit` | `#文献 Landscape` |
| Phase 2 发散 | `idea-generation`（卡住时在生成职责内用已安装的 `creative-thinking-for-research`） | `#候选池与筛选` |
| Phase 3 查新 | `novelty-check`（逐个入围候选） | `#查新结论` |
| Phase 4 评审 | `idea-review` | `#独立评审` |
| Phase 4.5 收敛 | `idea-refinement`（另写入获准的 `RESEARCH_PROPOSAL.md`） | `#收敛与 Proposal` |

## 缺口降级

- **无可用检索能力**：Phase 1 按 supplied-material synthesis 继续，覆盖范围限定为已供材料；不推断“无文献存在”。
- **无可读材料**：Phase 2 索取一组材料并停止；材料可用但有缺口时标明缺口，继续生成条件式候选。
- **无独立评审者或原文不可达**：对应阶段标 **REVIEW UNAVAILABLE / EVIDENCE GAP**，交付已完成部分后停止；生成者自查与作者自评不升级为独立裁决。
- **无参考论文全文**：保留缺口，不凭记忆补写摘要，不影响其余阶段。
- **预算耗尽**：停止该类型新工作，保留未检查项与缺口，用已有材料完成报告，不循环扩大。
