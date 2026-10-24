# Spec48 explicit unknown archive link regression

## 状态
- 未登记显式链接回归：done；`scripts/check-skills.py`、`tests/test_spec48_archive_safe_index.py`；`/tmp/spec48-checker-unknown-link-fix/logs/red.log` rc=1，`green.log` rc=0 / 15 passed / 42 subtests passed；12 格实际 CLI 全覆盖并分别断言登记与目标诊断。
- 定向验证与交接：done；`/tmp/spec48-checker-unknown-link-fix/REPORT.md`；structure=0 / history=1；追加提交以包含本记录的 commit 为准；下一步 parent 复核回归，不重跑全 suite、不接管 R2。

## 决定与边界
- 明确有界 bug-fix worker 直接执行，不派发。已读全局规则、前轮材料与最新 F3 review。
- 问题是目标拒绝被 `rows.keys()` 条件限制，登记检查又依赖链接目标有效；这两项必须独立，不可用未知名字或坏目标绕过另一项。
- 测试矩阵：已知/未知名 × 合法 href/坏 href/坏 fragment × 同行好索引有/无。实际 CLI 使用 tracked-only 副本、存在的文件作为 href，避免被通用断链或历史红代检出。
- 只改 checker、归档测试、本 notes；不变更历史 SHA/索引/限制/原包，不读秘密，不碰 integration/R2、不推送/关票/清理。
- 最小修复移除目标检查的已登记名过滤；登记检查对全部显式名无条件执行，不依赖自身目标有效性。普通正文名仍按既有同行索引关联规则处理，不改变正文 + 索引合法写法。
- RED 完整 CLI 中未知名 + 坏 href/fragment 共 4 格误为 rc=0；GREEN 改为 1 且同时报告缺记录与坏目标；已知名 + 合法目标 2 格始终 0，其余 10 格均按目标缺陷拒绝。旧正文 + 索引、合法 fragment、同名链接屏蔽反例继续实跑通过。
- KISS/YAGNI/DRY：checker 仅修改既有两个拒绝条件，无新依赖、状态或解析机制；复用既有 tracked-only copy 与 CLI 入口。无 TS 变更。

## Deviations
- 无。
