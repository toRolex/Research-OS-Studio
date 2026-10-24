# Spec48 F3 — archive link binding

## 状态
- F3 同行链接关联：done；`scripts/check-skills.py` 与 `tests/test_spec48_archive_safe_index.py`；`/tmp/spec48-checker-f3-fix/logs/red.log` rc=1，`green.log` rc=0 / 14 passed / 30 subtests passed；逐链接错误未被同行合法链接遮蔽。
- 定向验证与交接：done；`/tmp/spec48-checker-f3-fix/REPORT.md`；structure=0 / history=1，7 UNVERIFIED + 1 MISMATCH，全 UNAVAILABLE。完整 CLI 8 场景及 diff 在 green.log；独立追加提交以包含本记录的 commit 为准。下一步 parent 复审 F3，R2 继续独立收尾；本轮未重跑全 suite。

## 边界与决定
- 唯一 bug-fix worker 直接执行，不派发、不接管 R2；先读全局规则与前轮 R1/修复响应/最新复审。
- F1/F2 已关闭，本轮只修 F3（P2）。同行 `any(index-link)` 只能支持非链接正文归档名，不能支持明确归档链接的错误自身 href。
- 继续使用现有 Markdown inline-link 解析边界，不引入依赖或另造通用 Markdown parser；先补 fixture 与真实完整 CLI 正反例，再实现。
- 只改 checker、归档测试、本 notes；保留历史 SHA/限制，不读取原包/秘密，不推送/关票/清理/直接合 integration。
- 实现将每个 inline link match 内的归档名绑定其独有 target，逐链接检查路径/fragment；仅链接之外的正文名可以沿用同行索引入口。即使同名归档另有合法链接，错误链接仍产生独立诊断。
- 完整 CLI RED 实测 wrong-alone=1，masked-href/fragment/same-archive=0；GREEN 四项均为 1，baseline/body-name/index/valid-fragment 四项均为 0。诊断命中归档目标校验，不由通用断链或历史 scope 代检出。
- KISS/YAGNI/DRY：仅复用既有 link match 并提取路径/fragment 判定为局部 helper；不改解析器边界、历史状态、R2 文档或许可/安装资源。未涉及 TS。

## Deviations
- 无。
