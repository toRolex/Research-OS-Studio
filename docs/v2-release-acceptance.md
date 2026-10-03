# v2 最终组合验收（#37 / #46）

## 执行基线与结论口径

- 本地 `integration/research-os-v2` 起点 `af43cc8`，对 `v2/accept-remediation` 精确 tip `fa9065226cc955d74e88f6c972da5e7da13c8edf` 执行 `merge --no-ff`；合并执行 tip **`5efd2daffc68612def5e4660defb68db5a7780e3`**。无冲突，原始验收失败保留。
- 本轮当前tip组合真实回归仍在进行。独立按票AC核原始证据已完成，#41–45均达标；静态 `ecdddab828ef027590d1b49eb3870435bf995a71` 已实跑68通过。最终安全与组合tool trace以下独立报告为准；不把安装、正文增强或旧宿主结果冒充本轮执行。
- 完整读四份报告、#37/#41–46原票（含评论）、维护者approved共享合同。批次计量与低消耗fixture按票面验收，不把TOY证明成真实学术贡献。
- 科研 **REVISE / WARN**、审计 **FAIL** 经按门纠错或预算到顶停止，不自动成为流程AC失败；也不冒充科研正确性PASS。真人投影、真实发表与学术结论不属于这些票明确AC的，不追加为无限关票阻碍。
- 最新diff只影响入口逐字清单、Idea中性handoff/原反馈内联、ML累计build、talk严重修订及版本绑定。未受影响的完整科研流程采用固定证据，受影响边界在当前tip重跑。后续若仅doc/checker/验收归档变更，不以此从零重复全部科研长输出。

## 固定证据（旧失败仍可复核）

| 报告 | 范围 | 归档 SHA-256 |
|---|---|---|
| [原交付](acceptance/v2-accept-deliverables.md) | #41公开论文链、#43三TOY写作、#44三交付及原预算/门失败 | `4dde9d353a92057b29a7dd5f2ee10f63e356234cabb553b929cac9a0e95f6ef0` |
| [验证](acceptance/v2-accept-validation.md) | #42十四授权场景+实际计量三阶段闭环；#45 fixed-proof / 两轮improvement / 原状态pickup | `dc4ae3ef5f4d012cfefe908abe69f0c4818a8dbc6ad8634c7bd4268a1e065f91` |
| [宿主](acceptance/v2-accept-hosts.md) | 79轮；三宿主安装/入口/叶门/setup多轮与失败重试 | `cab141490a54d13564d27723a6f8cfcff726d555698da26668111d0eb3cefa9e` |
| [整改](acceptance/v2-accept-remediation.md) | 新干净Idea、中性三fresh；最新ML图/两build/跨家族审查；talk严重门及最终12页版本绑定 | `ffc305f4c1a94bd9ae6ea31f344de3736f47800b5f8593beb6091077b45e329a` |

> 所有归档均在 `docs/acceptance/evidence/`。这些文件和merge commit仍仅本地，未push；GitHub评论只提供本地context指针，不声称远程已能访问。

## 本轮独立检查

1. [#41–45独立AC复核](acceptance/v2-release-ac-review.md)：每票原AC全部通过，剩余AC无。直接核原session/授权/tool/冻结物；不是科研认证。#42空裸Python probe、#44被测fresh像素探针生成digest的历史过程偏差单列，不谎称全UV/零digest。
2. 当前tip三宿主限定安装/字段与完整路由组合：安装各39×270文件hash全同；真实默认工具回归在执行，待独立原始tool trace结束；不是重演全部科研长输出。
3. 当前tip跨票预算/外发/重大修订门组合：八场真实pi默认工具执行中，待原始tool trace结束。
4. 新45MiB包899常规文件、70,273,550字节及11PDF文本已扫描；898/898 payload SHA全同，无缺失/额外/mismatch，真凭据0，不需清洗。旧三包扫描也无新增真敏感值（publisher签名已REDACTED）；完整安全报告待落盘。
5. UV实跑 `uv run python scripts/check-skills.py`（39/U38/M1）、`uv run python -m unittest discover -s tests -v`（23）、`uv run python -m unittest discover -s scripts -p 'test*.py' -v`（45）：**68通过**，不是仅默认discover可能漏suite。
6. doc sweep TDD小fix `ecdddab`：两真实旧句副本RED两subtest，保留合法叶停止正例；既有checker literal补两条、README中英各一行GREEN8/8，两Python主动LSP0、diff --check通过，无新validator。该commit不改变产品skills，回归执行5efd2da仍核当前同字节skills。

## 发布边界

本轮不tag、不push、不PR；不关闭#37/#46。待最终review决定发布动作。将明确列出最终commit、已关闭前票、精确未满足AC及测试，绝不沿用历史SSL或笼统raw缺口作为永久阻碍。

实施因果见 `.agents/notes/v2-merge-remediation-release-implementation-notes.md`。
