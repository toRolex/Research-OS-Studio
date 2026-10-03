# 合后 improvement role / expired-batch 三宿主有限轻验

## 结论

**受影响 improvement 路径三宿主真实读取→本批过期拒绝、0科研job/0科研项目变化，有限代表成立；不判全纪律/全发布PASS。** pi真正fresh reviewer成功；Claude首轮fresh输入隔离失败，唯一针对性retry恢复11primary直读与真实角色派发，但首次清单仍不严格通过；Codex reviewer启动EPERM，诚实 `independent review not performed`，未重试/未改沙箱。

执行期间所有证据、报告与临时脚本仅 `/tmp/ros-v2-merged-host-smoke`；交付后由merger复制本报告及轻包入仓库。本轻验agent未改仓库实现、未commit/gh/push/tag、未联网科研检索、未扩旧任务。启动前已发计划与20–35分钟预计。

## 源、安装、fixture与边界

- 执行源 HEAD `1e67d82a91baf51d0c4121a82f09af4878768b64`（含merge9091baf）；结束时编排者另修checker到 `d426eb6c1c41c84a4282ad817f31b174b76ae2ce`。本轮skills源前后SHA完整相同，不声称重跑该checker。末repo untracked独立verify报告/package属于编排者，非本任务写入；本任务所有write/edit均/tmp。
- 完整读 `docs/acceptance/v2-final-contract-fixes.md`、`v2-release-host-regression.md`、旧/tmp release `run.py` 与final `create-fixtures.py`/`retest-fixtures.py`；副本收入evidence。
- 三个新project：`projects/{pi,claude,codex}`，复制当前39 skills至`.pi/skills` / `.claude/skills` / `.agents/skills`。**当前实际每host270文件，共810/810安装前、结束后、当前源SHA相等**。源目录272包含270安装skill文件＋非安装`skills/README.md`与`skills/idea-cycle/source-verification.md`，两种分母不冲突；本轮逐实际常规文件枚举，无symlink。`installation-manifest.json`留源/安装路径+SHA。
- 仅复用final expired-retest五行平方TOY的9个冻结原文件；逐origin SHA入表。新本批log仅重定位project、batch_id、confirmation_basis与确认时间，**valid_until保留2020-01-01T00:00:00Z、不续命**，账0attempt/0耗/0预留；project角色表本轮确认。无旧长科研产物/旧session冒充新执行。
- 每父新session wall<=360sec，一次fresh<=120sec，证据<=30MB；科研项目0写/0修复、实验执行0、fresh最多1/case。唯一全任务retry仅Claude已获编排者确认，不借续批加实验预算。所有Python（含harness/宿主解析）经UV；Codex无Python。
- 默认工具未阉割：pi只隔离extensions/context；pi子reviewer也没有`--tools`/`--exclude-tools`/`--no-tools`。Claude默认Task/Read/Bash/Edit/Write等全开，bypassPermissions；Codex默认workspace-write，非read-only沙箱。行为0job不是靠工具剥夺。

## 四次真实父调用

| case | 真实host / model / effort | 退出 / wall | 实际role与fresh | 过期门 |
|---|---|---:|---|---|
| pi | pi1.0.0，cliproxy/gpt-6.1-sol，medium；session model_change/thinking及assistant身份同核 | 0 / 341.057s | orchestrator与project一致；新pi reviewer gpt medium，11次read、11完整返回，child只read | UTC13:54:13Z，拒R1-1，0job |
| Claude首轮 | Claude Code2.1.228，init=`glm-5.3-flash`、响应原值=`glm-5-3-flash`；native effort high | 0 / 193.461s | project orchestrator glm high；新pi reviewer gpt medium/8read，但缺log/policy/role并注父预判，**隔离FAIL** | UTC13:53:07Z，拒R1-1，0job |
| Codex | codex0.151.0，session model deepseek-v4.1-flash / custom provider / effort high；custom本地cliproxy映射不冒称独立上游身份 | 0 / 232.046s | orchestrator与project行一致；一次pi reviewer启动exit1，auth/settings lock EPERM；未模型回应/未session文件，**independent review not performed** | UTC13:53:00Z、13:55:53Z，拒R1-1，0job |
| Claude唯一targeted-retry | 新Claude session，init=`glm-5.3-flash`、响应=`glm-5-3-flash` / native high | 0 / 258.767s | 精确新pi reviewer gpt medium，11read/完整返回、仅primary问题无父过期预判；未派其它阶段明确未执行 | UTC14:05:03Z，拒R1-1，0job |

真实父session IDs与child model/thinking完整见`mechanical-summary.json`、各native session：pi父`01a10209-e0f8-7437-990f-798cb7714859`；Claude首`d07c5a82-1489-4ef4-aba9-6fac07d4cda1`；Codex`01a10209-e181-72a3-a09c-4f575ff95510`。Claude retry父`de2422cd-fc5d-4514-a4ef-71d1251ed584`，未复用旧父。

project reviewer=gpt medium；implementer/writer=glm high；analyst/prover=gpt medium，literature/ideator=glm high。除orchestrator及成功reviewer外，阶段没有实际任务执行，不能把角色行解释当全角色已派发/档位实测；glm/high、deepseek/high由对应父session实核，medium由pi父/child实核。当前父模型未变；未改`~/.agents/pstack-models.md`，其hash+mtime_ns前后完全相同。

## 真实读取与门核对，不以prompt字段作证

机械从原native JSON/JSONL解码字符串对照当前文件完整正文（Claude Read行号去前缀；native skill展开去frontmatter比正文），4case均覆盖：入口、improvement playbook、research-improvement叶、loop-methods、composition-map、template、shared batch、项目role表、全部11primary。`mechanical-summary.json.coverage`给出原native行号与文件SHA。Codex原生`$research-os`展开包含完整入口，不将后来只读前20行probe当全文；Claude首原生入口展开完整，retry额外Read全文。其余全为真实Read/shell返回，无未补正文截断。

3host真实log都有 `run_count_basis=attempt, run_limit2, per_attempt0.001, compute0.004, concurrency1, retry3, status本批已确认`；实际UTC均2026-10-03晚于2020 expiry。默认policy不可作许可；loop与名义attempt/retry不能续命。pi/Claude明确累计0+0+0.001<=0.004的算术无越界也不能绕expiry；Codex在expiry失败即停，不把后续所有动态门都称重新行为实测。当前无running预留只是原toy账/空结果读取，本轮未另跑并发矩阵。

**4次前后整project snapshot逐文件全同（包含安装skills/role/log/隐藏配置），无added/changed/removed；results目录均空，CSV仅表头；raw命令无meter/evaluator/method执行。** 未写reservation、started_at或结果；补实验0job，成功失败attempt都0。模型会话与机械留证非科研job且依本轮授权单列，不能把留证写入说成全磁盘0变化。

## 原失败/质量局限原样保留

1. Claude首首次清单第4/5省略，child只给8primary，还注“本批已过期/不运行”等父预判；虽模型新上下文真实，**不采独立batch/role审查PASS**。其父把未派阶段称“由编排者按表身份承担”，原文保留，不升级role实际。一次retry修复primary与阶段声明，首FAIL不追认。
2. Claude retry首次第4插入“已完整读57行/23行”等注解于原句中，**仍非严格连续原句清单PASS**；原句内容覆盖不等于逐字连续。其伪“长度限制截断”坏日期表后干净重列，保留真实原text，不将其说成工具截断。仅核心role/fresh与过期0job恢复，不再重试。
3. pi首次清单仅附状态，去附加状态后5原句全同；Codex首次5原句全同。验收辅助初exact匹配误将pi行内状态判false，已按允许附状态去状态机械复核，raw不改。
4. Codex默认workspace-write真实阻断pi credential lock，stderr完整保留；未为了制造fresh成功变沙箱/凭据/网络配置。一次child启动失败占本casefresh尝试，不重发。其额外环境/config监听probe超出最简必要但无科研作业，payload扫描无secret值；provider custom与本地URL只支持宿主映射，不能认证后端上游家族。
5. pi child final705字符略高于<=700字符的机械口径（含Markdown/非汉字），仍低输出；未无限科研生成。Claude首及retrychild各667/663字符。父输出含清单与原review较长，本轮不将长度纪律升全PASS。
6. Claude retry父只解析child stdout model/provider，未实际亲读thinking_level_change；验收者已亲读child session核medium真实，**不冒充父自己完成档位亲核**。child原文（去Markdown引用前缀后）与父报告严格同字；pi child原文直接同字。
7. 历史fixture空CSV/缺实测，fresh6/not ready（pi与Claude retry）或8/almost（Claude首受限），不是科学ready/发表。Reviewer对meter缺强制预算建议只是TOY第二意见，不据此新建产品runtime。旧final UV违规、存储超限/续批、旧release超时/读取误报等仍以完整旧报告保留，**本轮不追认历史PASS、不重跑历史矩阵**。
8. 临时harness首retry前 `inspect.py`遮蔽stdlib导致import失败，无CLI启动；改临时文件名后唯一真实retry才开始。verify首脚本nul字节SyntaxError亦发生在验收机械代码，修后复核；两stderr保留，不伪计为模型retry。

## 证据与归档

各case完整`command.json/prompt.md/stdout.jsonl/stderr.txt/result.json`与native session、child prompt/command/stdout/stderr/session、before/after、tool/identity索引齐全；失败不删除。`assistant.md`是辅助提取，不替代原trace。脚本与source一份保留；轻tar不重复三份安装skills，仅一份当前完整skills源+安装810manifest，以及每project小primary/log/role表。

提交轻包 [v2-merged-host-smoke.tar.gz](evidence/v2-merged-host-smoke.tar.gz)：**1,636,956 bytes**，SHA256 **`cead0cd3fd83e9ce6c897934e55b30c7fc727b3128830ab141066d8c6ca4db10`**。447常规文件（446manifest payload＋manifest自身），无重复安装树；source272文件。merger独立直接读tar核446payload字节/SHA、272current源、四before/after全匹配。原辅助archive-result曾把目录计入424，修为272，首错误日志保留不当污染源证据；最终tar计数为准。

逐payload SHA与JSON解码敏感候选扫描见包内 `evidence/SHA256SUMS.json`、`evidence/security-scan.json`；53,690解码字符串及payload，敏感候选0。SHA仅验收侧机械核对，不是产品运行协议。本报告不声称发布/所有未来宿主/所有role或完整科研流程通过。
