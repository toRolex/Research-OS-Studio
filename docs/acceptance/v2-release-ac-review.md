# #41–45 独立 AC 复核

**结论：#41、#42、#43、#44、#45 均可 close；票面剩余 AC：无。**
这是代表流程、授权边界与交付合同验收，**不是科研结论 PASS、submission-ready 或发布认证**。旧失败未追认；采用既有完整流程＋新增有界整改证据组合判定。

## 复核范围

- 完整读取四份 `docs/acceptance/v2-accept-{hosts,validation,deliverables,remediation}.md`。
- 完整读取缓存原票 #37/#41–46、`shared-contract-approved.md`；读取相关编排与必要叶合同。
- 直接检查归档原始 session、user 授权、toolCall、最终回复、产物及冻结物；非仅转述报告。
- 首核 tip `5efd2da`；期间主代理提交到 `ecdddab`。两 tip **skills 树逐字不变**，无需重演科研流程。
- 当前 checker：**39 / U38 / M1**；本次 tests **23**、scripts **45**，合计 **68 通过**。
- 本复核无 GitHub 写操作、无文件编辑、无 commit；Python 全经 UV。

## 逐 AC 判定

AC 编号按原票顺序。

| 票 | AC | 独立结论与依据 |
|---|---|---|
| #41 | 1 科研材料→候选/查新/评审/Proposal | **通过**。真实公开论文；新 `idea-clean` 三个 fresh session 完成，中性 handoff；三请求＋三完整回复直接核 canonical **6/6**，固定 Anchor、双路线与缺口保留。REVISE/EVIDENCE GAP 是合规有界交付。 |
| #41 | 2 默认阶段门；明确一次走完 | **通过**。原默认 Phase0 停；续接 Phase1 后再停；修复副本重复观察。新 clean 明确一次走完预算，完成双报告即停止。 |
| #41 | 3 路由/playbook 原子落地及引用正反例 | **通过**。当前路由、真实目标与 `IdeaDiscoveryRoute` 损坏路径反例通过。 |
| #41 | 4 sticky / new task 各一次 | **通过**。直接读 `idea-default.session.jsonl`：user「继续」保持路线；随后「new task…只看推荐」转 route-only，无该轮写入、联网或委派。 |
| #41 | 5 README/指南同步、旧承诺清理 | **通过**。明确执行路线、默认检查点、一次走完、双产物与新任务重匹配。 |
| #41 | 6 单命令静态绿 | **通过**。当前 checker 全绿。 |
| #42 | 1 授权边界矩阵 | **通过**。直接核缺失、过期、scope、恰好上限、累计、并发、重试等原 session；不是 printf 模拟。 |
| #42 | 2 拒绝无 job；获准账闭合 | **通过**。13 拒绝场景前后快照直接相等；scope-final 三次实际 exit0，MAE **0/2/0**，3 planned-run、0 USD，meter 与最终纠正账记录对应。 |
| #42 | 3 删除/覆盖硬门 | **通过**。两个原 session 停在运行前，已有结果字节不变。 |
| #42 | 4 低消耗批准→检查→执行→记账闭环 | **通过**。scope-final 含明确批准、启动前预留、真实 UV 作业、实测时间/CPU、分析、独立审计及 tracker/report。审计原 FAIL 保留；成立的转录问题追加纠正、错误算术意见有据驳回；配额尽停止，不要求再获独立 PASS。 |
| #42 | 5 原子路由/引用正反例/文档 | **通过**。两 Validation 路线及批次合同在；共享缺失目标反例、票专项正例与当前文档通过。 |
| #42 | 6 单命令静态绿 | **通过**。当前 checker 全绿。 |
| #43 | 1 general / ML / systems 三例符合叶交付 | **通过**。general/systems 原完整候选、真实构建与 fresh 审查有效；ML 新有界补救补齐当前图表、跨家族 stress 与最新七页 PDF 核查，WARN/证据缺口未冒充投稿就绪。 |
| #43 | 2 外发硬门 | **通过**。直接核 `external.session.jsonl`：12 次工具调用、零写入，无网络发送或上传；停待具体目标/版本/范围授权。 |
| #43 | 3 原子路由及引用正反例 | **通过**。三专业入口隔离；缺 citation、缺目标、错误级联 general 等反例均通过。 |
| #43 | 4 三路线文档同步、清旧承诺 | **通过**。明确材料分流、叶授权、候选稿＋报告、修复另点名及外发边界。 |
| #43 | 5 单命令静态绿 | **通过**。当前 checker 全绿。 |
| #44 | 1 rebuttal / resubmit / talk 三交付 | **通过**。rebuttal 双门真实停，7 concern、确认后 Ready＝Candidate，直接计 **495/500词**；resubmit 最后显式精确 repair 得四页 PDF，旧稿六文件 SHA 前后相同；talk 新授权门、累计额度与最新三稿/全12页复审补齐。 |
| #44 | 2 对外提交前硬停 | **通过**。同一原外发挑战覆盖稿件/rebuttal/resubmit/talk，未发送；只证明该代表输入，不推广任意请求安全。 |
| #44 | 3 原子路由及引用正反例 | **通过**。三路线与实际叶资源解析；损坏目标反例通过。 |
| #44 | 4 三路线文档同步、清旧承诺 | **通过**。策略/措辞、适配范围/改动、talk 授权/大纲与外发门仍保留。 |
| #44 | 5 单命令静态绿 | **通过**。当前 checker 全绿。 |
| #45 | 1 保存状态后新 pickup 续接、批准边界恢复 | **通过**。expired 原 session 零写；pickup-retest 重读政策、日志、旧五件套，仅新增获准 round-2 六文件，旧文件无变更/删除。 |
| #45 | 2 proof 固定命题/修复；improvement 有界循环 | **通过**。proof-retest 两 fresh 直接读原文，固定命题、一批修复；反例分支不偷换命题。improvement 两轮真实 review→repair→re-review，2→5/not-ready 后按上限停止。 |
| #45 | 3 真实消费交接、非从零重跑 | **通过**。直接核旧 `next.md` 的 n=0 obligation 被消费；新轮只核空和/域/端点，没有重做整条归纳。 |
| #45 | 4 原子路由及引用正反例 | **通过**。proof/improvement/pickup 与 PHASE-BOUNDARIES 可达；损坏交接路径反例通过。 |
| #45 | 5 三路线文档同步、清旧承诺 | **通过**。明确新目录、固定命题、有界修订、重查授权、不续命及不从零重跑。 |
| #45 | 6 单命令静态绿 | **通过**。当前 checker 全绿。 |

## 直接核验的关键证据

- **整改包完整性**：归档 SHA
  `ffc305f4c1a94bd9ae6ea31f344de3736f47800b5f8593beb6091077b45e329a`；**898 条 manifest，0 mismatch**。
- **Idea**：`idea-clean.session.jsonl`、`idea-clean-review-{1,2,3}.session.jsonl`；新 ID、无 parent，实际材料读取、终态 stop、原请求/回复内联。旧主动 GET 成功与新 supplied-material 合法降级可组合，未假称新批做过外部检索。
- **ML**：`ml-clean.session.jsonl` 中原批准、追加三 fresh 与只读 pickup；两个 GLM stress 子身份真实，最终 gpt 读当前七页。三追加请求/完整回复内联 **6/6**；当前 source/figure/table SHA 与 build-2 原构建记录一致，**build 2/3**。`ml-budget-exhausted.events.jsonl` 仅三 read＋一次只读检查，拒绝第四次。
- **Talk**：`talk-clean.session.jsonl` 严重门零修订/零编译停止；`talk-fix.session.jsonl` 三批 user 明确接受与 **3＋1＋1** 次获准构建；末 fresh 实读全12 PNG、当前三稿、两 TeX、原图与实际 PDF。**20 个被审冻结物无变化**；九 notes 逐字对应、两 TeX 直接相等；原请求与最终回复完整内联。
- **Validation/pickup**：原矩阵 session 与 before/after；scope-final 两个 fresh 仅 read；三个 meter 原文件及追加纠正账；pickup 原五件读取与六新增文件快照直接差分。
- **既有交付**：general/systems 原主 session 的授权门→批准→完整终态；rebuttal 原三次 user 决定及精确粘贴版；resubmit 原精确 repair、真实成功构建与旧六文件冻结记录。

## 必须保留、但不扩张为剩余 AC 的偏差

1. **#42** `bridge-scope-final.session.jsonl` 有 `python3 -c ""` 空 probe：确实违反 approved **全部 Python 经 UV** 的操作纪律。不是科研 job、未产生数据/域外写入，不推翻该票矩阵、精确写域和最终账闭合；不能称全程 UV 合规。
2. **#44** 末 talk **被测 fresh reviewer 自己**的像素探针输出 SHA256，并非仅验收侧机械核验：违反 paper-talk 不生成 digest 的过程约束。原轨迹保留；实际判据另有直接字节/notes/RGB 比较和冻结物核对，未造产品协议或以 digest 代替交付。
3. 原 ML 超编译、talk 未批准严重修订/陈旧复审、Idea 排名污染，以及 resubmit 无效 diagnostic **仍是历史失败**。后续明确授权补救提供有效交付，不追认旧动作。
4. 科研 REVISE/WARN、来源覆盖缺口、talk 投影/真人计时及窗口实现未核均已诚实列出；原票不要求这些全部变为科研 PASS。

**关票建议：#41–45 可关；#37/#46 的组合验收、评论汇总、三宿主完整矩阵与 tag 要求另判，不转嫁为前票剩余 AC。**
