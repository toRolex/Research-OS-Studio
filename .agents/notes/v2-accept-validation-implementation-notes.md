# #42/#45 当前 tip 行为验收

## 范围
- 基线 67a04ff，已证 HEAD 与 integration 相同且祖先成立。approved shared contract；Seam A 唯一 checker，Seam B 真实 CLI 工具轨迹（既有批准）。tdd 工具不可用，完整读取 `/Users/rolex/.agents/skills/tdd/{SKILL,tests,mocking}.md`；pre-implement 已调用。
- 仅自己的 worktree 与 `/tmp/ros-v2-validation`；不动全局配置/main，不 push/tag/PR/关票。不另派 agent；被测宿主可自己以 pi CLI fresh session 委派审查。
- 真实材料为明确标记 toy 的平方计算 fixture 与初等数学命题，不虚构论文/外部评审。授权矩阵使用真实 CLI 自主读取政策/日志后选择执行或拒绝；不手动写成功输出。

## 步骤
1. 当前树限定安装；版本、hash、前后快照。
2. 批次批准→记账→检查→真实 toy CPU 执行→分析→fresh 审计；边界逐项真实会话。
3. proof 固定命题、fresh 审查与受限修复、交接保存；新 session pickup 有效/过期。
4. improvement fresh review→有界修复→fresh re-review。
5. merge 最新 integration，重测，归档证据与逐 AC 判定。

## Decisions / Deviations
- 历史 #42 printf/旧 #45 过期轨迹不重复利用作当前通过证明。默认政策保持 0；planned-run 与 attempt 差异分别记录，unknown 保留预留。
- 初轮默认工具 bridge 已执行三作业/fresh审计，但手工猜 started_at、随后用文件mtime回填；违反精确账本可复核性。新增公共合同测试先红（1失败），在唯一授权reference补系统时钟/退出码原始证据、不回填推测时间、CPU覆盖披露；绿4项。新bridge-retest fixture冻结evaluator记录ISO实测时刻，重新完整执行，不改旧失败证据。
- 初轮被测宿主在解析子JSON时直接python3（虽prompt要求UV），留失败证据；重测附环境系统约束强调所有Python含解析都UV。这不是额外产品runtime。父宿主默认read/bash/edit/write，子审查read限定仅证明只读审查；完整执行不靠限定工具阻断。
- 初轮bridge还创建__pycache__（批准命令机械副产物但不在精确写域），以及raw trace远超主prompt的100KB文本。报告不掩盖，重测新增证据存储为宿主留存不算论文文本；不得把这些失败宣称全授权符合。
- improvement fixture刻意将CSV baseline写2.4而固定数学复算为2；fresh reviewer正确识别冲突。修复不改原始CSV，仅校准正文并保留来源未核实与失败无log。真正科学结论不是此toy范围的验收项。
- Red 2：CPU部分覆盖不能当全账闭合，新增断言红，再补唯一batch reference保持未知预留，绿4项。最终新fixture `bridge-final` 冻结meter.py通过RUSAGE_CHILDREN计量inner UV/evaluator全后代；用户明确核算范围不含宿主/计量wrapper，不冒充整个机器CPU。
- 初轮proof宿主声称cross-family，实际上父子都glm；独立上下文是真的，跨家族不是真的。原证据保留；proof-retest只准same-family/fresh-session，必要UV整数核对也已另明确授权，避免初轮违背不运行数值程序。
- 初轮pickup有效真实读取旧五件套，写round-2，但自行写root脚本和错误的外侧报告路径，继而rm清理。未删除用户数据（仅本轮toy临时文件）仍违反本批写域/清理门。T45新增合同测试通过unittest discover先红1项；pickup补每次绝对路径/副产物核实、不以误写修正授权rm。绿4项。pickup-retest明确不运行脚本/不清理，仍必须真正新目录续接。
- Harness `inspect.py`遮蔽标准库inspect导致pickup初次runner失败，改名trace_inspect.py；保留失败stderr后重跑（未启动宿主/未产生科学结果）。没有据此宣布环境不可恢复。
- 最终bridge全阶段已出分析/报告/fresh审计PASS，0/2/0 MAE，3/3 planned-run、0USD、meter2.415e-05 cpu-core-hour，38证据核对通过（code review含只读bash，非仅read；审计仅read）。末核两根目录session指针不在原scope，不能忽略：再加T42断言红，补sidecar/cache也是写入只准批准目录，绿4项。commit30dced1。
- 新bridge-accounting-pickup真实消费已满账，无新作业/reviewer，只获当前用户许可保留原指针、日志追加、新核算报告；明确不追溯抹平原越界。为真正消除完整场景残留，另外新授权bridge-scope-final，明确两session指针与计量覆盖、有限时长和存储，三新CPU作业+两个fresh审查全链重跑，不拿pickup核算替代。
- 当前静态两轮merge确认integration仍67a04ff，checker39 / scripts43 + tests16=59，全绿。notes/report不直接修改共同release矩阵。
- bridge-scope-final最终真实全阶段完成。fresh审计FAIL：一项误算baseline（|1−1|算1），宿主UV核原文驳回；另一项main台账转录真错，宿主保留错行追加raw meter正确值并闭账/报告。2次审查配额用尽，无第三审查，不改原FAIL为PASS。主会话agent_end已到，最终CPU2.0308888888888884e-05、3/3、0USD、精确写域/冻结物/无缓存/无删除通过，17项scope检查绿；总体38项证据检查绿。
- 原始全量归档22MB提交`docs/acceptance/evidence/v2-accept-validation.tar.gz`，SHA705edc4c2496713e578a6b18b364ec7ec542e84ebcabc3b8b3505f401d940cd7。初轮不合规Python空命令probe也保留（最终scope宿主曾直接python3 -c空字符串，不产生科研计算；不得删除此工具轨迹或声称所有被测会话绝对UV合规）。本实现/harness全部Python确实UV。
- integration合并清洗：仅`matrix-single`会话/迹里一次进程列表夹带无关本机网络探测（绑定地址、可达地址、无关本地路径）。换占位符并重算这两个文件与SUMS两条；其余条目字节不变。未删审计FAIL、误判驳回、账本纠正、空命令probe。清洗后归档SHA `dc4ae3ef5f4d012cfefe908abe69f0c4818a8dbc6ad8634c7bd4268a1e065f91`。合并后UV重测checker39、scripts43+tests16=59绿。未push/tag/关票，未改main。
