# #60 R2 逐 AC 终验实现记录

## 状态

- R2 证据筛选与必需边界核对：done；原七项 AC 及证据/限制已写入 `docs/acceptance/spec48-ticket60-final-acceptance.md`，根据 parent 接受的 F3 回归将 AC2/AC6 更新为已完成证据。
- migration-boundary 最小修订与受影响资源安装补验：done；已将 `proof-review` 与委托继承能力分开描述、保留 checker 所需 `未迁移` anchor/`LEGACY_LEAF_GATES` pointer；精确当前 Research OS 包 35 文件安装对比通过，69 必需链接无缺失。
- 复验、独立提交与报告：done；默认 checker rc=0，安装与有界链接验证 evidence 已记录；独立 R2 commit 和外部报告 `/tmp/spec48-ticket60-final-ac/REPORT.md` 由本轮交付，不操作 integration、issue 或其他 worktree。

## 入口与边界

- 入口判定：直接执行这个有界 R2 文档/验收 work unit，因为上游材料与精确交付物已指定、R1 代码工作已有独立 owner，且用户明确禁止我重修 checker/tests 或自派。
- 依赖：先将 `3bff4a3faeca2b8976adec7a9da10b560b249afd` 安全 `--ff-only` 合入，再将最终 R1 候选 `da7e703bb4b4c7cbedb66fdf1f4441aad69f9d01` 安全 `--ff-only` 合入本 worktree；F1/F2 独立复审关闭，F3 12 格完整 CLI 与最终结构/history 检查已由 parent 接受。
- 验收依据：原始 #60 的七项 AC 与父 spec 中对应 ID/TD；仅复用 R2 指定证据，不重做 41 叶审查、不读取本机原包、不把 `/tmp` 材料描述为随包自包含证明。

## 决策与因果

- 历史身份缺口和当前结构/安装/行为验收分轴记录：原始历史包未获批准入库；历史门可如实未验证，但不能替代当前硬门或改称通过。
- 已有全装证据仅在源产品树精确一致时继承；若更新 `migration-boundary.md`，该随包资源必须追加定向安装与内容哈希比对，不因此重跑全套宿主矩阵。
- `paper-compile-repair` 单装只证明包可安装，不证明七条必需 `paper-compile` sibling 边可用；需保留组合安装的可解析证据与单包装配限制。
- 说明修订依据：当前 `MIGRATED_CONTRACT` 登记委托继承能力，`proof-review` 正文是独立只读 `Gates: none`；因此只重写迁移边界说明，不改 Skill 行为、checker 或测试。
- 首次结构 checker 因说明缺少精确 `未迁移` heading anchor 与 `LEGACY_LEAF_GATES` 权威指针而返回 rc=1；此为文档合同，不是 checker regression。恢复兼容必需的 section/pointer，但说明其当前空门集合，避免重引入“两批并行”的错误事实。
- R1 最终候选 `da7e703` 到达后只读 `--ff-only` 合并并更新 AC2/AC6：F3 已修复并被 parent 定向复验接受，history rc=1 的 8 个 `UNAVAILABLE` 缺口继续如实保留。

## Deviations

- 初始改稿移除了 checker 必需的 `未迁移` heading/`LEGACY_LEAF_GATES` pointer；因为报告指出了确切缺口，最小补回两者并明确当前为空门集，而非改 checker 或保留过时“其余叶都带旧门”的断言。
- 原计划等待 F3 复验；parent 提供最终 R1 commit 和接受证据后，按授权在本分支 fast-forward 合并，不再把 F3 列为待办，也未重复全 suite。最终 R1 与本 worktree 的 `skills` tree 相同，安装证据只需对本轮变更的 migration 资源定向补验。
