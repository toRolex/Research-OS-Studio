# v2 最终组合验收（#37 / #46）

## 执行基线与结论口径

- 本地 `integration/research-os-v2` 起点 `af43cc8`，对 `v2/accept-remediation` 精确 tip `fa9065226cc955d74e88f6c972da5e7da13c8edf` 执行 `merge --no-ff`；合并执行 tip **`5efd2daffc68612def5e4660defb68db5a7780e3`**。无冲突，原始验收失败保留。
- 当前tip独立组合回归已结束：host包45 CLI记录中43完整真实模型终态、1部分timeout、1误slash空调用；gate包8完整场＋1同session澄清。旧失败、纠正与空调用不冒充通过。#41–45原AC均达标且已关闭。最终UV在 `eaa76f07f9488e26a11af58894c65c80e4e88041` 又实际跑68通过；后续仅验收文档/归档/notes变更，不改变产品skills或checker。
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
2. [当前tip三宿主完整组合回归](acceptance/v2-release-host-regression.md)：三宿主各39×270文件与执行源及当前skills同SHA；38 explicit字段＋setup唯一allow true。14具体playbook各独立真实输入→对应叶/门；三宿主直接/自然串行/只读冲突、原session sticky/newtask、custom/mismatch/ambiguity、setup既有材料与不可用模型代表。route首失败经唯一原合同重跑恢复；pickup timeout由208.51s真实stop重试补齐。最新ML51工具亲核canonical4716行、原批准/反馈/CSV/current构建绑定/7PNG，UV Decimal独算50.625/90/39.375，不只转述。810安装、612fixture、全局hash/mtime末核相同。host包928文件/15,807,902bytes，SHA `d80e120694d7623533e253798550a43d8b61b6eea78592a5df388a2063a4cadc`。
3. [当前tip跨票门组合](acceptance/v2-release-gate-combinations.md)：8场＋1同session ML澄清全部exit0/stop/agent_end，默认四工具实开；missing、failed累计超额、unknown保留预留、pickup过期/原五件消费、ML停止后拒第4build与外发、talk严重claim停，以及获准可逆候选write→亲自read均有完整raw。安装39/270文件同字节。ML首route-only安全诊断不称执行级联，唯一澄清后实际读ML playbook/叶/终止授权；talk禁写诊断也不称生产talk，获准可逆候选才是真paper-talk审查分支正向编排。门包577文件/12,544,022bytes，SHA `2291c39cbe506db6fa90c11e684e5047d9300ebd813d35496d5942e6cbb3efc1`。共享并发snapshot看见获准新文件的事实保留，以case域/固定物补核，不宣称全项目所有snapshot零差。
4. [安全与静态独立报告](acceptance/v2-release-security-static.md)：新45MiB包899常规文件、70,273,550字节及11PDF文本已扫描；898/898 payload SHA全同，无缺失/额外/mismatch，真凭据0，不需清洗。四包合计5753常规文件/545,918,107原字节；148候选均科学授权文案/模板/regex/已REDACTED publisher签名或CLI help，转义JSON字符串补scan也无真敏感。validation唯一软链接包内目标AGENTS，核边界但不创建。
5. UV实跑 `uv run python scripts/check-skills.py`（39/U38/M1）、`uv run python -m unittest discover -s tests -v`（23）、`uv run python -m unittest discover -s scripts -p 'test*.py' -v`（45）：**68通过**，不是仅默认discover可能漏suite。
6. doc sweep TDD小fix `ecdddab`：两真实旧句副本RED两subtest，保留合法叶停止正例；既有checker literal补两条、README中英各一行GREEN8/8，两Python主动LSP0、diff --check通过，无新validator。该commit不改变产品skills，回归执行5efd2da仍核当前同字节skills。

## #46 逐AC与精确剩余

| 原票AC | 本轮判定 |
|---|---|
| 1 前票验收证据齐备并汇总本票评论 | 达标。#38–40此前已关闭；#41–45本轮独立逐AC关闭；四固定报告＋三新独立报告/原始归档汇总，最终context评论附本地commit未push说明。 |
| 2 Seam B场景全部跑过且输入/预期/允许禁止副作用/tool留证 | 有限代表覆盖达标。14具体playbook、四路由边界、sticky/newtask、可逆与叶门、授权完整旧矩阵＋当前受影响组合、外发/删覆、setup、串行/亲核均有真实证据。不是每宿主×每叶全笛卡尔积重演，也不是全部过程纪律零偏差。 |
| 3 三宿主限定安装字段＋直接点名/级联 | 有限代表达标。810文件/39各份字段，三宿主原生直接proof-review、叶级联plan/自然串行、只读冲突/重匹配工具轨迹。 |
| 4 单命令静态/链接/清单零豁免 | 达标。checker39/U38M1，tests23＋scripts45＝68全绿；损坏引用/路由/角色/额度/门/旧承诺反例均在实际suite。 |
| 5 breaking公告/迁移最终核对 | 达标。中英顶部公告、旧ask删除/route-only迁移；pi原生 `/skill:name` 映射真实；两旧无条件stop句TDD清理。 |
| 6 v2.0.0 tag | **未满足：未打tag，用户本轮明确禁止。** 不伪标完成。 |

按原票范围，**未满足的发布AC是#46-6 tag**；#37/#46继续OPEN留最终review决定。不是继续缺泛泛科研raw、学术PASS、真实会议/投影、人类终验或再重演全部长产物。

### 必须披露但不无限追加为关票条件

- Codex直接proof-review首轮裸Python probe/fallback违反UV；唯一重跑无Python，但 `review-rules.md` shell聚合输出截断未续读，不能声明该次“全部审查资源完整覆盖”。其真实入口/固定反例/不写不修可核；三宿主有限直接/级联AC不扩大为任意叶全覆盖保证。若最终review要求**该单场完整资源纪律**作为额外release条件，精确补项仅为同fixture完整读取review-rules且UV/no-write终态，不是从零全部科研。
- Claude末newtask将已确认x=0反例描述成gap，推荐解释质量局限；补读全文/原生重匹配/只读及清单通过，不把有限安全通过说成全部科研判断准确。
- 初route虚报/压缩清单、pickup timeout、误slash空调用、并发整snapshot污染、旧ML/talk/Idea越界全部保留。原报告不追认；最新有效复验单列。
- #42空Python probe、#44被测fresh生成digest及门组合一条无可见账本仍为过程偏差，不谎称全纪律通过。

## 可发布判断与动作边界

**可交最终release review的候选：是。无条件已发布/所有宿主永远安全：否。** 票面1–5有限代表证据充分；科研REVISE/WARN及审计FAIL按门闭环/有界停属于正确交付。额外纪律局限明示供最终review采纳，不用不相关未来人验无限阻塞。

已按独立原AC评论并关闭 **#41/#42/#43/#44/#45**；GraphQL回查全部CLOSED。#37/#46仍OPEN；已有context评论 `5968914862` / `5968915099`，最终再补归档/commit指针。

本轮不tag、不push、不PR、不关闭#37/#46，不改main/全局。所有commit/归档仍本地，不能把相对路径当在线原始证据。

实施因果见 `.agents/notes/v2-merge-remediation-release-implementation-notes.md`。
