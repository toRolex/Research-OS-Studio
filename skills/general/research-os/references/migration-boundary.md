# 迁移边界

本发行按批迁移到[研究委托合同](mandate.md)。**已迁移**能力遵循该合同；**未迁移**能力保留旧门声明并照旧可用。两批并存是设计，不是遗漏：不把整包说成已统一。

## 已迁移

| 能力 | 正文 | 委托落点 |
| --- | --- | --- |
| 委托入口 | `skills/general/research-os/SKILL.md` | 「研究委托」小节 + 本目录合同与 `playbooks/literature-review.md` |
| 文献综合 | `skills/idea-cycle/research-lit/SKILL.md` | 「委托继承」小节；无旧门，写入与预算由委托给 |
| 并行覆盖（swarm） | `skills/general/swarm/SKILL.md` | 「委托继承」小节；新增能力，非旧门迁移，改编自 pstack swarm（MIT，LICENSE 随目录共置） |
| 对抗审查 | `skills/general/interrogate/SKILL.md` | 「委托继承」小节；无旧门，始终只读，修复由委托按授权另行组织 |
| 形式化检查创建 | `skills/validation-cycle/create-formal-verification-skill/SKILL.md` | 「委托继承」小节；项目内验证资产与依赖准备在授权内，缺子代理时独立复核标 blocked |
| 形式化检查维护 | `skills/validation-cycle/maintain-formal-verification-skill/SKILL.md` | 「委托继承」小节；只改验证不改产品代码，同步 commit 与假设版本随检查推进 |
| 行为验证创建 | `skills/validation-cycle/create-verification-skill/SKILL.md` | 「委托继承」小节；项目内启动、驱动与验证资产在授权内，缺子代理时源读/复核标 blocked |
| 行为验证维护 | `skills/validation-cycle/maintain-verification-skill/SKILL.md` | 「委托继承」小节；只改验证 skill 自身目录，现场驱动与证据清理随轮次推进 |

迁移一个能力的完整动作：把正文改成继承委托（去掉旧 `Gate:`，写出该能力的边界与完成条件），在 `scripts/check-skills.py` 的 `MIGRATED_CONTRACT` 登记路径与小节名，把同一行加入本表，并从 `LEGACY_LEAF_GATES` 删除。

## 未迁移

其余叶 Skill 仍以 `Gate: <id> | before=… | approval=explicit-user | source=…` 声明自己的批准点；权威清单是 `scripts/check-skills.py` 的 `LEGACY_LEAF_GATES`，本文件不复制整表以免两份漂移。

由委托级联进入未迁移能力时，仍按该能力自己的门停下确认；这不撤销委托，处理完该点后同一委托继续。等该能力迁移，这个中途停点才消失。

## 迁移期间仍生效的完整性检查

迁移只改授权与停点语义，不放宽结构约束：门声明格式、来源锚点与追踪状态、frontmatter 与调用策略、共置资源与相对链接、README 清单与实际目录的一致性都继续检查。已迁移能力额外检查合同小节是否存在，因此删门不会连职责约束一起丢。

## 参考

- 合同正文：[mandate.md](mandate.md)
- 委托额度与运行批次：[batch-authorization.md](batch-authorization.md)
- 完整链路示例：[literature-review](../playbooks/literature-review.md)
