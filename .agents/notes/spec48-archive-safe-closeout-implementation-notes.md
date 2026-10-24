# Spec-48 #60 历史归档安全收尾

| Work unit | 状态 | 产物 / 验收证据 | 下一步 |
|---|---|---|---|
| 归档索引与引用语义 | done | `docs/acceptance/evidence/README.md`；8 个归档、9 个验收入口；3 条新回归通过 | 不含原包或敏感原值 |
| checker 真实性保留 | done | `scripts/check-skills.py`；原九条归档缺口诊断保持，SHA差异在索引/回归中明确 | 无 checker allowlist 或绿化 |
| 串行验证、提交与交接 | done | `/tmp/spec48-archive-safe-closeout/REPORT.md`、`logs/`；351 collected、345 passed、6 个原历史失败；checker 精确匹配原基线 | 独立提交后向 parent 交接 |

## 入口与范围

- 直接执行：主任务已经把余项限定为一项小型归档收尾，证据和测试边界已提供；用户明确禁止本轮继续派发。
- work unit：在当前隔离 worktree 中维护 8 个归档的脱敏索引、替换 9 处失效归档链接语义、维持 checker 可见的历史未验证状态并做相关验收。无依赖；基线 `1e509ef2e3b28a5423b06afed48ecc830bd535e0` 已核为当前 `HEAD` 的祖先。
- 前置材料：`/tmp/spec48-archive-preflight/REPORT.md`、`/tmp/spec48-archive-safety/REPORT.md`、`/tmp/spec48-final-test-hygiene/REPORT.md` 和 #48/#60 tracker snapshot。原始包只作本地材料，不读取、不复制、不上传。
- 测试 seam：用户指定的 #60 历史证据引用与 `scripts/check-skills.py`；新增回归测试先红后绿。Python 仅通过 `uv`；串行、树外 `TMPDIR`、命令有界 timeout。

## 决策

- `historical SHA` 是接受文档中的历史声明；`candidate SHA` 是 2026-10-24 只读本地预检记录的候选字节摘要。两者含义分开，不因同值就宣称当前 worktree 可重验来源。
- 不将原始包、成员、敏感原值或本地绝对路径放入仓库；summary 不是 archive replacement。扫描仅启发式，未证明无秘密。
- 缺失原包仍应被 checker 显示为未入库/不可重验；`v2-accept-validation` 的候选/历史 SHA 差异保留在索引与字面量回归断言中。绝不加 checker allowlist 或删原始真实性约束。
- 用户正文中的九个原包引用改为可用的索引入口；checker 继续用既有九条逐文档/逐原包诊断报告原包未跟踪，保持历史检查结果集合与 rc=1，不把可访问索引说成可下载归档。
- RED：`logs/red.log` / `logs/red.rc`；GREEN：完整 suite 中 `logs/file-13.log` / `.rc`（新归档测试）与 `logs/file-07.log` / `.rc`（index-link 负例）；各文件实际 argv、log、rc 均在同目录 `file-*.{cmd,log,rc}`。

## Deviations

- 原 `test_checker_historical_allowlist_rejects_replaced_diagnostic` 负例依赖已经移除的 tarball href，改为破坏新索引 href；断言仍要求九条原归档失败完整存在，且新增无效索引目标与缺少索引入口两条错误，未降低真实性或诊断断言。
