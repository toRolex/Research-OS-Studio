# #60 候选 merger 第三小片 implementation notes

## Status

| Work unit | 状态 | 产物 / 验收证据 | 下一步 |
|---|---|---|---|
| 按指定顺序合候选、A、B | done | 候选 `653ca524fd480a1db1e92a6d92a02314e1fb226a` 从起点快进；A no-ff merge `07f4d0dea38358c07697c97d4a1ffd03a4a39340`（双亲：候选、`9a4f36658e70daa5b628cc6b801f69137eafa5a1`）；B no-ff merge `800602b696b332883b9add026ba0e6ca564b032e`（双亲：A merge、`b378cece18589aa8dc878decd9de137108b622e8`）。自动合并均无文本冲突。 | 审资源与原合同剩余语句。 |
| 审查合并后的资源树与旧冲突正文 | done | A `paper-compile-repair` tree 与 A 产品源相同（`25c8bbee…`）；B `proof-repair`/`proof-review` 分别与 B 产品源相同（`393d0ce7…` / `6829ac71…`）；C 七包逐一与源 `e7fcb080…` 相同；D `research-os` 等于已测 tree `7578ab8b…`。无 Git 冲突标记。M 测试仅对 `independent-review.md` 做授权/额度/可信元数据语义断言并跳过该资源 SHA，其余 14 项原样 hash 比较。 | 运行变化后的 A/B 安装态测试及要求的串行回归。 |
| 串行回归 | done | 全部串行、`timeout 180s`、临时目录外置；A1、B2、C7、D discovery2、D W3-3、#45/#55/M/policy-29、#57-13 均 rc=0；checker rc=1 且 stdout/stderr log 与 D 基线及 merger-2 checker log 两次 `cmp` 均 rc=0；`git diff --check 14d9..HEAD` rc=0。逐项日志及 SHA 见最终报告。 | 无；全仓完整测试套件未运行，也不作其通过声明。 |
| 报告、notes commit 与交付核验 | done | 完整报告 `/tmp/spec48-contract-fix-merger-3/REPORT.md`；A/B/C/D、#45/#55/M/policy、#57 回归和 checker 精确比较日志在 `/tmp/spec48-contract-fix-merger-3/logs/`；产品候选 B merge `800602b696b332883b9add026ba0e6ca564b032e`；本状态与 notes 将作为单独小提交记录，最终 SHA/clean 状态在报告补录。 | 无；仅候选、不 promotion，交 parent 后续处理安装引用 fix 与独立复审。 |

## 入口、边界与因果

- 入口判定：直接执行；这是明确指定的 merger implementation work unit，且用户明确禁止继续派发，合并与验收范围可在本 worktree 内界定。
- 只在本独立 T3 worktree 操作；不写 integration/主目录、不 push、不碰 tracker、不发起其他分支任务。
- 只合指定已完成的候选、A、B；不合在途安装引用修复。后续与 `paper-compile-repair`/其他 Skill 的局部冲突交给下一 merger。
- A 终态摘要中的猜测 SHA 不作为依据；以本地 Git 对象、实际 tree 和 diff 为准。B 将 `independent-review.md` 的迁移测试从字节比较改为语义比较是该资源有意更新所需，其余迁移资源哈希约束必须保留。
- 本工单交付候选，不据此声称 #60 总体验收或 promotion；所有安全门和只读/真实职责边界保留。
- 安装态 CLI 证据仅在完整 Skill 包 tree 与已测来源一致时继承；本轮 A/B/C/D 所涉包均逐项等树，因此只需重跑 A/B/C/D 指定安装态测试与相关跨票回归。未来在途安装引用修复 `3df3c63de4f6c06f096d178d2187094e2191ca25` 不在本候选祖先链中。

## Deviations

- 两次 no-ff merge 都由 Git `ort` 自动完成、未出现内容冲突；定向语义审阅和安装态验证通过，无需手工修补。没有重跑全仓 suite，且 checker 的已知 9 条 archive 诊断仍存在、未改写。
