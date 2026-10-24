# Spec48 checker scope fix

## 状态
- R1 checker 两轴：done；`scripts/check-skills.py`；`/tmp/spec48-checker-scope-fix/logs/final-suite/checker-{structure,history}.{cmd,log,rc}`，结构 0 / 历史 1；7 UNVERIFIED、1 MISMATCH，全部 UNAVAILABLE。
- 原六失败与 mutation seam：done；同目录 `file-*.log`、`suite.tsv`；原六 node 通过，37 个目标 mutants 全部 rc=1（policy 6 / gates 6 / config 9 / full-cli 10 / compute 6）；无历史失败允许集。
- 串行验收与交接：done；`/tmp/spec48-checker-scope-fix/REPORT.md`；35 文件 / 356 passed / 625 subtests passed，无失败、跳过或超时；提交包含本记录，commit ID 以外部 REPORT 最终记录为准。下一步由 parent 做 R2，不关闭 #60。

## 边界与决定
- 唯一 implementer 直接执行，不再自派；仅 R1，不承担 R2 最终全量 review。
- 已读 Multi-Agent、模型可用性与 CODING_STANDARDS；本机未发现 tdd skill，按测试先红再实现再绿执行。
- 输入为 acceptance-review 第 3 节、safe-closeout、preflight spec/tickets 与原 probe。
- 将索引结构错误与历史字节状态分开；仅新增显式 history scope，默认结构不假报历史 PASS。
- 不读原包，不改历史 SHA/限制，不恢复、上传或推送；fixture 只使用明确标记的人工字节。
- 保留索引原文不动；生产历史事实单一来源，测试以原始 Git blob 防止历史 SHA 被悄改，不再重复整张生产表；不冻结候选/状态的合法演进，限制另作证据合同正反例。
- 状态有限集合：仅本地保留、未入库／已入库、待核验／已入库、已核验；后者仍须实际 tracked 字节与两份 SHA/size 一致。
- 定向运行揭露完整 CLI 副本把无后缀 LICENSE touch 成空文件，先于 mutants 被 13 条许可错误阻塞；改用现有 tracked-only 字节副本 helper，不豁免许可检查。
- 首轮 29 个 tests 文件串行跑完，两个 archive seam 失败：#53 固定单行输出与 #56 固定九条失败。按 R1 移除 #49/51/53/54/56/57/58 的归档允许集（其余功能断言不减）；#53 只识别严格 HISTORY 状态语法，保留 crash 检查并新增伪 HISTORY PASS 反例。
- 补充 RED：同一包另一有效入口不可遮蔽真实错误 href；逐行验证索引 href，支持真实 fragment，不仅检查集合中是否出现过。
- 最终从 Git tracked 文件清单收集 35 个测试文件（含 scripts 下 6 个），串行、每文件 175s、树外 TMPDIR；无 ignored 树遍历或复制。全部实际 rc/命令/node 均保留。
- KISS/YAGNI/DRY 核对：仅给已有 checker 增加 scope 与有限状态，不引入运行时或归档恢复协议；复用既有 tracked-only copy 与 heading anchor helper。无 TS 变更。

## Deviations
- 所需归档测试适配散布在上述 ticket 测试，不仅独立 archive/policy 两文件；仅删除历史失败允许集及适配新状态输出，未改变这些票的产品合同。
