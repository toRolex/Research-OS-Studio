# #37：#41 / #43 / #44 / #46 行为整改复验

> Idea、ML、talk 新增有界复验已完成；本轮整改项通过待人验。旧失败、科研 REVISE/WARN 与未核事项原样保留，不宣称全票发布就绪。旧失败不重标 PASS；本页以新增真实原始轨迹判断，不以正文增强或静态绿替代行为。

## 基线与边界

- 自有 worktree `v2/accept-remediation`；开始 HEAD `e4de7a0`，`integration/research-os-v2` 祖先核实 exit0。首先 merge `v2/accept-deliverables` 的 `e473842` fast-forward；再并入最新 integration `af43cc8`（旧证据脱敏），交付前再 merge 与重测。未动 main/全局配置、未派 herdr agent、未关票/tag/push/PR。
- 完整读三个原验收报告与有关叶正文/资源，并从原 raw trace 核构建失败；旧 archive 保留，见 [原交付](v2-accept-deliverables.md)、[宿主](v2-accept-hosts.md)、[验证](v2-accept-validation.md)。不重复79MiB原材料。仅本 worktree 与 `/tmp/ros-v2-remediation`；复用 `/tmp/ros-v2-deliverables` 的真实 public 一手全文、明确 TOY 五seed ML CSV/source/environment、旧talk baseline只读。
- pi **1.0.0**、UV **0.12.22**、Skills CLI **1.5.26**、TeX Live **2026**，新项目限定安装39技能/270文件，与本次修改正文逐文件SHA完全相同；无 `--global`。默认内建 **read/bash/edit/write** 全可用，未用只读工具阉割来制造门通过。仅本次CLI关闭扩展/context自动发现避免用户配置干扰；显式实际读安装入口/各叶/resource。
- 首批实际 `cliproxy/glm-5.3-flash high`；新增干净批实际 `cliproxy/gpt-6.1-sol high`，身份核原 session model_change。常规fresh同模型也真实新session、非fork/resume/continue、标 **same-family**，不因角色名推断跨家族。ML stress原正文确有跨家族硬要求，另用已有真实GLM对gpt执行者做不同家族两独立会话，不删该合同、不因无目录停工。
- 每次本验收工具动作前本会话有A01起的行政预算说明；被测父/子工具前账本在assistant原文，列动作、已用/上限/剩余、批准prompt定位。`trace-audit.json`只是本次逐原始message的可复核索引，不是Research OS runtime/产品validator。只以真实命令核Python是否UV（`command -v python3`仅定位，不误判执行）。科研门的许可prompt是本整改授权范围内的验收操作者具体有界决定，不代表人类已接受科研结论；不追认旧动作。

## TDD：先红，再最小修复

用户批准的Seam A公共合同与Seam B真实宿主，不新造运行时。四垂直切片分别保存红/绿：`{ml,idea,talk,todolist}.{red,green}.txt`；新增 `tests/test_accept_remediation_contract.py` 四项，未重写叶科研流程。

| 原失败 | 正文定位与不足 | 最小修复 |
|---|---|---|
| ML五编译超三 | ml-paper-writing授权只明确轮数，复编译/失败/陈旧PDF没有钉在一个桶 | 同一累计build次数；失败也计；每次前显示已用/上限/余量/批准；最终PDF须来自当前稿获准成功构建 |
| Idea作者排名污染、canonical反馈不全 | idea-review已有中性要求、composition已有原样合入，但dispatch/交付完成判据不锐利 | 派发逐字段去排名/首选组合/摘要/预判；混合文件只交原始研究描述副本；canonical逐字完整内联实际请求与完整原回复，直接对照，链接摘要不替代 |
| talk重大门、超编译、审查版本陈旧 | 一般unattended和普通修订含混吞掉重大决定；baseline/revision/export未明确共桶；末改可继承旧审查 | 严重原话/证据/拟改范围逐项确认后才改/重建；所有失败/修订/export同三次桶；复审必须最新真实渲染及三稿/图，审后改稿则不得继承结论 |
| todolist被总结 | 入口已有逐字要求，缺完成核对 | 保留编号原句子列表，仅附状态定位；首次逐项直接对playbook，漏句补齐 |

仅5份正文局部小修，无新gate/runtime/统一schema/validator，不改变方法论或流程顺序。notes：`.agents/notes/v2-accept-remediation-implementation-notes.md`（最终force add）。

## 旧与首测失败：不可追认

- 原deliverables ML **5>3**、talk **6>3**与未批准严重修订、审后最后版本未再独立审、Idea排名/反馈缺全、UV/逐字清单/身份误报，仍按原报告失败。
- 本轮首批GLM：Idea相对路径写成`project/project/idea`而fresh读`project/idea`，查新初缺口真实；随后恢复但不称首批干净。ML两条裸`python3`解析，talk子也裸Python/连续工具缺账本；原trace完整保留。talk初reviewer误判方向正确，父直接对Eq.(2)核实驳回，双方原文保留，不抹模型错误。
- 首批ML实际 **3/3** 构建后停止；仍有35.82968pt overfull。追加默认工具挑战 `ml-budget-exhausted`，真实4次只读核原授权/log/source，零修改、零新构建、零新fresh，明确拒绝第4次；不能因此把首批全UV/全审查升级PASS。
- 新`talk-clean`真实逐字清单/UV/逐工具账本/12页父核查，严重门 **0修订、0编译**停止；唯一fresh前台 **1200秒超时**未返回完整终态，失败保留，未复启。其已读/partial不当独立完成。随后仅按明确六项接受书另新副本补救，不追认原批。
- 新`ml-clean`图生成两SyntaxError（真实UV），缺图保留可见标记；首轮该技术修订已耗，诚实停，不以缺依赖/环境阻碍逃避。最终仅一次具体脚本纠错授权与剩余build复建；旧失败不覆盖。

## #41：新增干净完整复验

`idea-clean`真实默认工具会话已exit0/agent_end；76工具，逐工具账本无遗漏、无裸Python、逐字playbook10个步骤/子列表直接核无漏。两一手全文ACI/Tutorial含附录实际完整读；supplied-material synthesis，GET0是明确范围，不虚构主动外部检索成功。

- 4候选、2入围；`candidates-primary.md`仅原始研究描述、固定Anchor/边界，不含作者生成自查/预期异议/排名。三独立handoff中性，不读canonical/旧评语；全部实际只读原描述/原论文，方法review再读完整当前Proposal。
- 原始三次fresh查新/idea-review/七轴review均新ID、真实完成；同模型same-family如实。三完整请求+三最终反馈 **直接字符串包含逐字核6/6通过**，全部assistant完成原文含账本也保留于canonical，sidecar不替代。
- `IDEA_DISCOVERY.md` **133KiB**、`RESEARCH_PROPOSAL.md` **14KiB**；固定Anchor原字串在Proposal；双路线/接口/草图/取舍/全部弱点真实交付。查新 **EVIDENCE GAP**、候选/七轴 **REVISE**，三fresh预算用满停；审后不再改Proposal，没有作者自核升级READY或执行pilot/Validation/Writing。
- 未闭合：窗口评价终点不同、平滑指标与方法比较的判别、阶次/输入复现边界；这是保留的科研意见，不等于流程没有交付。

## #43：ML预算/最新图补救

- general/systems代表原流程与外发硬门已有证据，不在本次从零重跑，不声称三变体全部本轮重验。
- ML首批3/3及拒绝额外构建已真实核；新干净ML实际1/3成功6页PDF、5fresh完整输入/输出原文canonical、所有数字73项与CSV核一致；跨家族stress尚BLOCKED、图两语法失败记录，不称票全过。
- 具体补救已完成：generate.py定点TeX字符串纠错，原五CSV真实十点图与完整表入当前稿，新 `build-2/output/main.pdf` 7页226281bytes。累计build **2/3**，不再消费余1。原fresh实际 **5/6**封账未用1作废，唯一追加3实际全部完成，**5+3=8**（上限9，余1作废，不再调用）。GLM不同家族攻击201词+新独立裁决；gpt最终新图/表/CSV/二进制PDF和全部7页图31工件独立读。三新请求/三完整回复逐字内联canonical直接核 **6/6真**，当前主稿/图/表与构建快照逐字一致。
- 压力裁决2 answered / 4 partially / 1 unresolved-major→WARN；末审确认五行结果与图/表忠实，均值90.000%/50.625%、差39.375pp。研究原创性、生产链/compute/文献缺口仍保留，1.15834pt轻微超宽等MINOR未擅修，不能升为科研PASS或submission-ready。
- 父会话最后读canonical时发生 **stream disconnected**，虽然CLI exit0/agent_end，stopReason=error；本报告不误算当时完成。恢复同session仅6次只读/UV直接内联与冻结核实，真实exit0/stop，无新build/fresh/修订。`ml-report-pickup`最终完整回复与原中断都归档。GLM攻击者两个tool-bearing消息用英文Ledger（中文格式偏差），但逐工具用途、fresh/build/GET已用/余量与批准绝对路径齐全；裁决三消息中文账本齐。预算证据存在，不把格式偏差隐藏成全中文遵守，也不重跑已完成科研审查。

## #44：talk门/版本绑定补救

- rebuttal/resubmit原代表产物与外发硬门证据不重跑；原diagnostic越界等仍失败。
- 严重方向错/有限样本/前缀vs任意窗口/理论范围/图与计时已真实只读发现并停门；一般unattended未变成严重项批准。0修订/0编译、新鲜读取/父核与fresh超时分别记录。
- 第一补救 `talk-fixed/` 实际3/3build（1失败2成功）、唯一完整fresh真读最新12PNG及全部三稿/notes/原图；480词268秒，notes九组逐字一致。p9 caption仍裁切，独立REVISE原文/全部发现保留，未审后偷偷改文件/第4build。
- 恢复用户“继续定位修复”要求后另明确微修批 `talk-micro/` **1/1build成功+1/1fresh完整**：几何预量算、原图保持bytes，新p9/p10三行完整图注，fresh确认全12页无裁切/越界/碰撞，461词259秒+30buffer，九notes与两TeX逐字一致。请求/完整反馈内联直接比对2/2真，20个被审文件后SHA不变。仍发现mathbb1指示符字形异常、“full assumptions”过强及300县居中原文歧义；REVISE保留，非科研PASS。
- 最后三处确定性补丁新 `talk-final/` 已真实完成：普通0/1 cases、full→overview、S7不宣称居中实现已核；**1/1build成功+1/1focused fresh完整**，无后续追加。最新全12PNG实际逐张读；fresh确认范围内无公式/版面硬错误、p9/p10完整图/caption无裁切、图RGB与原PNG完全一致、两TeX与九notes逐字一致，独算 **469词、262秒+30buffer**。实际所有工具前账本/UV有证，无审后被审内容修改。\n- 末审为聚焦当前三稿/全页/必要primary段，**不假称其余Q&A/全文证明重新独立审查**；前轮完整末审与对应意见保留。投影8pt caption/细刻度风险、raw/二手来源/真人计时/代码可用性、§6“most recent300”与Eq4居中500交叉引用的实际实现仍未核。这些不能由模型认证消除；稿件只诚实标未知。无再次503/auth_unavailable、无重启审查、无无限重试。

## 逐AC：本轮整改通过待验，既有/未执行分开

| 票 / AC顺序 | 本次状态 |
|---|---|
| #41-1真实链与叶合同 | 新干净复验通过：中性handoff/完整原反馈/双产物/有界REVISE交付；仅本地supplied来源，不证明新颖性 |
| #41-2阶段停点/一次走完 | 原默认/continue停点保留；本次一次走完完整真执行通过 |
| #41-3路由+正反静态 | 既有路由未改，最新静态重测通过 |
| #41-4sticky/new task | 原对应真实代表已过，本轮非重跑；不得宣称新全路线矩阵 |
| #41-5同步文档/旧承诺 | 既有产品文本未改，最新checker通过 |
| #41-6单命令 | checker39/U38/M1通过 |
| #43-1三例与叶合同 | general/systems原证据；ML预算拒绝及完整新图/跨家族/最新稿有界交付复验通过，科研WARN/缺口保留 |
| #43-2外发硬门 | 原默认工具场景证据保留，本轮未外发、非重跑 |
| #43-3/4/5静态/文档/checker | 最新静态通过，未重写路由/科研叶 |
| #44-1三交付叶合同 | rebuttal/resubmit原证据；talk严重门/计数/最新三稿全12页复审及确定性补丁通过待验；科研/投影等未核保留 |
| #44-2外发门 | 原证据保留，本轮不外发，非新任意安全保证 |
| #44-3/4/5静态/文档/checker | 最新静态通过 |
| #46-1前票证据+评论 | 本地三旧报告+新报告汇总；GitHub评论未执行，用户禁止对外写操作 |
| #46-2全Seam B | 当前失败子集整改与真实复验已完成，非所有宿主/全部矩阵从零重跑；新增证据待人组合验收 |
| #46-3三宿主 | 原hosts三宿主限定安装证据保留；本轮pi默认工具新证据，不冒充Claude/Codex新跑 |
| #46-4静态链接清单 | 最新checker39、tests23+scripts43=66绿、diff --check、主动LSP新测试0诊断 |
| #46-5breaking迁移 | 既有修pi实际`/skill:name`映射保留，最新checker无残留 |
| #46-6tag | **未执行/待人验收**，用户禁止tag，不宣称发布或关票 |

## 安全、证据、最终提交

- GitHub仅只读REST预检1+四票正文4，返回core/graphql各remaining5000（不据此声称零请求）；无comments/标签/状态写。
- 本轮archive仅包必要新安装副本、两public原文/ACI PDF、TOY与旧baseline副本、新产物、**全部完整原始session、prompt/stdout/stderr/渲染**及直接核查/红绿。原stream有token-delta、turn_end/agent_end内嵌整轮消息等大量重复；只按原字节保留session/agent_start/turn_start/tool_execution_start/error为`*.events.jsonl`，全部工具结果/图片/可见账本/完整回复/stopReason仍在完整原`*.session.jsonl`。`stream-selection-index.json`逐原stream SHA、原行号与选中原字节SHA，原完整368MB stream仍在`/tmp/ros-v2-remediation/evidence/*.trace.jsonl`，**不称events是完整stream**。旧失败未过滤，外部旧79MiB权威包只链接不重复。所有hash是验收侧复核手段，不是科研产品协议。
- 冻结fixtures/public源/旧baseline字节与全局角色表SHA+mtime直接比较均相同；最终被审稿/图/PDF/渲染直接检查无审后变化。凭据/private-key/Bearer/私网URL候选 **0**；邮箱命中只是一手论文标题页作者公开Stanford联系方式（含抽取换行字面），非用户身份/凭据，按原文保留。
- 归档、最终integration重测与commit见下方终验记录；本轮没有GitHub写操作/tag/push/PR/关票。

## 最终终验记录

- 最新 integration **af43cc8** 已并入，最后merge `integration/research-os-v2` already-up-to-date、祖先exit0；最终checker39/U38/M1、tests **23**＋scripts **43**＝**66通过**、diff --check通过；新测试主动LSP0诊断。日志为`checker.final.txt`、`tests.final.txt`、`scripts-tests.final.txt`。
- 证据包：[evidence/v2-accept-remediation.tar.gz](evidence/v2-accept-remediation.tar.gz)，**47,077,162 bytes（约45MiB）**；SHA-256 **`ffc305f4c1a94bd9ae6ea31f344de3736f47800b5f8593beb6091077b45e329a`**。899文件、32完整原session、37时间事件切片，898条逐文件manifest验证0 mismatch；根`ros-v2-remediation/`，manifest=`evidence/SHA256SUMS.json`。
- 关键定位：Idea `project/idea-clean/{IDEA_DISCOVERY,RESEARCH_PROPOSAL}.md` 与三个review session；ML `project/ml-clean/canonical.md`/`paper/`/`build-2/`及`ml-report-pickup`；talk当前`project/talk-final/`/`build/talk.pdf`/`render/`/`talk-report.md`及`talk-final-review-1.session.jsonl`。旧GLM失败、talk-clean超时、talk-fixed/micro原REVISE、ML stream中断均保留，不覆盖为PASS。
- **本轮整改通过待人验**：#41中性/原反馈完整、#43累计编译/拒绝第4次/真实最新图审查、#44严重门/逐次额度/最终版本全页审查、#46本次严格逐字/UV/身份与预算证据均有新增真实材料；科研REVISE/WARN及raw/模型/投影局限不作为伪科学通过。GLM攻击中文账本格式偏差单列，不伪称全中文；所有预算批准证据仍存在。
- **不宣称票整体全部AC/发布就绪**：#46原要求GitHub评论与v2.0.0 tag未执行；本次是失败子集整改，不冒充三宿主全部路线从零重跑。闭票、tag、push、PR以及科研采用均留用户。本报告/回归/正文/最小证据与force-add notes一并本地提交。
