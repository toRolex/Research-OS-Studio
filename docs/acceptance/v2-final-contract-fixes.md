# v2 最终两轴 review：六项修复与补分支复验

## 基线、范围、判定

- 基线 `76af6a360de4a6ce035a540f01cb8dc66c9ae91c`；修复 commit **`bf0855ab2e3cad842723785840a8e6939f5a6709`**，分支 `v2/final-contract-fixes`。报告前再次 `git merge integration/research-os-v2`，其 tip 仍为76af6a3，already-up-to-date；随后在bf0855a重测全部suite。
- 完整读 approved、CONTEXT、原spec/ADR0006/0007、四份原验收与release报告。最终 Spec/Standards 原消息从父session恢复并全文读取，原文收入证据 `evidence/original-review-{spec,standards}.md`。六项均复现，不以“checker绿”驳回有效review。
- 单implementer；只改既有 `scripts/check-skills.py`、入口、14条playbook和共享批次reference，新增回归测试。**未重写任何叶科研流程，未新增产品runtime/router/checker文件。** 临时fixture/meter只用于明确TOY行为与验收核对，不是产品协议。
- **六项实现缺口已修；补实验门与记账有新的真实执行证据。** 不把科研ready等同发表、真值或全部未来宿主安全；历史UV/存储偏差保留，见下。

## 六项逐项闭合

| 轴/原定位 | 最小修复 | 实际验证 |
|---|---|---|
| Spec P1 improvement:21 | 补实验强制读共享batch-authorization与真实本批log；scope/expiry/perattempt/累计＋running预留/attempt名额/concurrency/retries全核，未知预留不释放、单写账者。reference明确planned-run与attempt分别计数 | 新expired-retest零job/零写；新valid-retest真实失败+成功，失败占额，第三attempt拒绝；非旧零实验review |
| Spec P2 入口:46–60 | 入口实际`Role: orchestrator`；每条playbook具体阶段声明literature/ideator/implementer/analyst/prover/writer/reviewer，按已确认project行fresh传model+thinking，当前宿主不切模型；缺行明示fallback，显式不可用/不支持/重复行停；无fresh标独立未执行 | 默认CLI正例＋Role ghostwriter损坏副本红；真实project reviewer gpt medium两fresh、implementer glm high，session身份/档位核；父宿主不改 |
| Spec P2 policy:837–876 | 全字段非空，非compute三字段唯一；有限非负数/整数、单位与单次累计配对、scope文字、currency、ISO日历与时区合法（拒+01:99）、执行并发≥1。not-applicable解释语义保留 | 空currency/scope/expiry、非法币种/单位/日期/offset、重复cost/scope/expiry、NaN及小数count反例；零默认与CPU/GPU异构正例继续绿 |
| Standards P2 checker:426 | `./`、`../`真实相对路径解析；`.agents/...`项目配置示例不 blanket 当产品级联 | 不存在`./references/MISSING.md`默认CLI红；合法`../references/batch-authorization.md`与.hidden配置示例绿 |
| Standards P2 checker:543 | 逐引用所在句判断迁移语境，非全文一次breaking即豁免；现行use/invoke/请使用声明即报错 | 真实README副本追加“请使用 /ask-research-os”红；合法删除迁移句绿 |
| Standards P2 checker:164 | 整行解析disable值，禁止子串；frontmatter/YAML同层同父键重复及关键声明重复拒绝，allow值唯一 | true/false两种顺序、重复name/description/allow、他键值藏disable全部默认CLI红 |

政策格式检查不声称现场有效：合法但过去的ISO仍能静态通过，运行时必须读真实时钟拒绝expired。未指定保留于 `run_limit=0` 且 `valid_for_hours=0` 的不可执行默认政策（包括已有异构额度建议正例）；不升级为本批许可。币种为三大写字母形式，不维护新汇率/ISO目录；scope内部真实计划/写域/环境覆盖由运行门核实，静态不能证明自然语言scope充分。

## TDD与静态

- 新 `tests/test_final_contract_fixes.py`：先 **RED 18失败** → **GREEN 6测试**（大量subtests）。补+01:99 offset和纯数字scope再 **RED 2** → GREEN。raw日志保留 `tdd-{red,green}.txt`、`tdd-extra-{red,green}.txt`。
- 修复commit bf0855a与最新integration重合后：`uv run python scripts/check-skills.py` **39/U38/M1**；`uv run python -m unittest discover -s tests -v` **29**；`uv run python -m unittest discover -s scripts -p 'test*.py' -v` **45**，总 **74通过**。
- 两改动Python文件主动LSP **0 diagnostics**，`git diff --check`及cached检查通过。全部实现/验收侧Python经UV。静态不替代行为。

## 新真实补实验：不是旧零实验场景

环境 pi1.0.0、UV0.12.22；`/tmp/ros-v2-final-contract/` 独立toy项目。当前skills/source-layout副本39技能/272文件与修复正文一致，逐文件manifest入包；本次不冒充重新跑三宿主安装矩阵。父默认 **read/bash/edit/write全部开放**，未以工具阉割制造门；关闭扩展/context发现避免全局干扰。只有fresh reviewer按只读职责配置read；implementer四工具开放。

### expired-retest

- 授权真实log `valid_until=2020-01-01T00:00:00Z`，父亲核真实UTC时钟2026-10-03T12:56:38Z。
- 入口→playbook→叶/reference/template及所有primary完整读；**22工具、0job、0文件变化**，research-log字节不变、results空。未派child；独立review未执行明示；不假造ready，不延长有效期。

### valid-retest + 唯一明确续批

- project已确认模型表：父/orchestrator及reviewer `cliproxy/gpt-6.1-sol | medium`；implementer `cliproxy/glm-5.3-flash | high`。真实三个新session、无fork/resume/continue；父保持原模型。Reviewer两次只primary路径、当前diff、原findings、固定问题/标准，没有执行者修复总结或旧评语。父在implementer运行时暂停写账；返回后亲读raw result/meter/log、复算MAE。
- 本批scope冻结代码、plan、evaluator、meter、CSV、policy、角色表；run_count_basis=attempt、run_limit2、retry3、concurrency1、CPU累计0.004/单次0.001、0USD。每次先核实scope/时钟/名额/累计预留/并发/retry、追加最坏预留再运行；meter用原系统时钟与RUSAGE_CHILDREN，明确覆盖inner UV及evaluator后代，排除宿主和wrapper。
- 两条真job：`uv run python meter.py fail results/a1.json` **exit7**；随后获准retry `... success results/a2.json` **exit0**，五行平方MAE0。实耗分别 **9.640555555555557e-06**、**6.657777777777776e-06** cpu-core-hour，累计 **1.6298333333333333e-05**，0USD，原始时间/CPU/exit与账直接核。冻结物字节不变；CSV仍空表头，未伪造历史。
- **失败a1同占attempt，2/2耗尽；明确拒第三**，即使retry3、累计余量仍够。原始启动trace只有两条meter job；没有第三产物。两fresh score **5/not ready → 9/ready**；canonical两轮回应与CLI最终文本直接字符串核相同。
- **历史存储失败保留**：原3MB被raw session/stream占用超过，父诚实停，不再派review2。操作者唯一明确追加20MB/15min，不增attempt/dialog/轮数、不改expiry、不删旧证据，才消费剩余review2、落完整日志并停止。新最后存储7,864,799文件bytes（du9552KiB）在20MB内。**不追认原3MB超限为PASS**；wall消息接收精确起点不可见如实记unknown，不猜时刻。
- 独立末审明确“当前五行TOY产物PASS；历史流程FAIL”，源码执行时身份与历史门控独立见证有限。父补证不冒充第二次独立审计，不无限开第三review。

### 首轮失败不能删除

首 `expired`/`valid` GLM父已真实0job/7+0/第三拒绝，但多次裸python3解析违反UV；原完整session保留，**不采全纪律PASS**。新expired/valid-retest父子Python全UV、冻结/原回应核；后者原存储越界另列，续批不追認。科研ready只对应固定TOY标准，不是publication-ready。

## 轻归档与安全

[evidence/v2-final-contract-fixes.tar.gz](evidence/v2-final-contract-fixes.tar.gz)：**2,489,643 bytes**，SHA-256 **`f2657476febf3689258397dc35d924b0e32ba5b4ca505d946374438d056b2df1`**。

根 `ros-v2-final-contract/`；455 payload SHA+bytes逐项验证匹配、manifest本身不自列，常规文件456。含两原review、红绿/全suite/LSP、所有四case完整父child session/prompt/raw stdout/stderr、真实result/meter、canonical日志、前后快照、工具索引、source副本和scratch fixture/核验脚本。gzip压缩小，不过滤失败原轨迹，不另复制旧大包。

新包所有payload及JSON解码字符串扫描：私钥、provider key、Bearer、URL userinfo、signed token query候选 **0**，无值输出、无需清洗。无外部论文/私人数据，不包含凭据环境值。SHA是验收侧机械核对，不是产品科研协议。

## 交付边界

仅本地commit，未动main/全局模型表，未push/tag/PR/关票；#37/#46原release评论与tag剩项仍由原报告记录，不在此伪关。本次补受影响分支，不将14playbook全部角色声明静态闭合冒充每个角色全宿主新行为矩阵。

因果notes独立 `.agents/notes/v2-final-contract-fixes-implementation-notes.md`（force-add）。
