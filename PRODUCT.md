# Product

## 产品边界

Research OS P0 是安装到独立科研项目的 provider-neutral Agent Skills、共享契约、确定性 validators、templates 与薄 Adapter 集合。不是网页产品、具体科研项目、中央 planner、scheduler 或自动科研 runtime。`research-architecture.html` 是历史架构展示，不是生产运行界面。

服务独立计算研究者与数学研究者。Project 定义边界，Workstream 可并行或暂停，Artifact 是唯一规范交接，Publication 是经用户确认的封闭发布投影。用户拥有研究语义、评价标准、预算、statement 修订、workflow 间推进及接受／冻结权。

## 交付目标与现状

| 范围 | 当前证据 | 发布结论 |
|---|---|---|
| 15 个显式 workflow | canonical inventory 与确定性 CLI 已存在 | 不等于完整科研能力 |
| 8 个 model-invoked disciplines | canonical catalog 与 Claude projection 实测 8；Codex workflow-only 明示 8 项 BLOCKED | 已实现；8 个对应 ports 已获用户最终 digest 接纳 |
| 计算 reference | wheel/setup、六外循环、五实验 workflow、CPU MSE 1.25、失败与预算硬停、PDF/freeze、历史恢复 | 产物验收通过；不证明 novelty 或研究贡献 |
| 数学 reference | 普通 proof、固定 review、独立 discipline、PDF/freeze、历史恢复 | 产物验收通过；不代表学术接受 |
| Lean reference | 官方临时隔离 elan，固定 Lean 4.19/Lake，真实 build/audit/comparator/replay | 固定 P0 reference PASS；不外推到依赖型项目 |
| 统一 validators | foundation／semantics／Publication 与数学 typed projections 接入单一 registry；直接 CLI 与两 Adapter 共享验证路由 | 行为验收通过；不代替真实 host 隔离与 port 发布门 |
| 社区 ports／license | 八项固定来源、许可、ledger、评价、product binding 与用户最终 digest 接纳；许可证随发行资源 | validate-ports PASS，release_authorized=true |
| Claude Code／Codex | 可重建 projection、共享 validator、隔离不足时拒绝 | 真实模型执行 BLOCKED |
| SSH／SLURM | 本地协议与缺配置检查 | 真实环境 NOT_EVALUATED |

完整发行必须满足 Issue #24 与 GATES.md；上述局部通过不能关闭缺失 gate。

## 非承诺

不承诺 A100／多卡 GPU、远端费用/GPU/token 可靠计量、hostile executable 安全沙箱、自动文献搜索、自动修订研究目标、自动发表、rebuttal/submission、全学科 ontology 或全部云平台。普通证明不要求 Lean；首发固定 Lean 案例仍须真实 build/audit/comparator/kernel replay。

## 技术与原则

- Markdown／JSON／Git 为项目材料；薄 Python CLI 用 UV 管理，冻结 lockfile 验收。
- workflow 不调用另一个 workflow；discipline 无接受、预算追加或冻结权限。
- 六轴 Assurance 不汇总为分数；结构 pass、运行完成、数学审查、形式通过、人类接受彼此独立。
- 固定 Artifact、失败 run、旧安装环境和 Publication 不被更新覆盖；迁移只显式执行。
- port 来源、完整 revision、许可证／NOTICE、baseline hash、adaptation ledger、评价与人工决定缺一不可。当前八项均已绑定用户确认的最终 acceptance request。

审计材料位于 `docs/research/sources/`，来源索引见该目录 README。旧 `analysis/**` 与 `/tmp` handoff 不作为当前可达产品证据。使用与验收见 [README](README.md) 及 [支持矩阵](docs/guides/support-matrix.md)。
