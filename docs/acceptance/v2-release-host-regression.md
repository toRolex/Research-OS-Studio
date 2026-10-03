# #46 当前 tip 独立三宿主组合回归

**本票要求的有限宿主组合代表已跑并恢复关键入口/清单；不宣称 #46 全 AC / 发布通过。** 新 tip 轻量组合与旧固定完整流程分开；首失败、超时、UV偏差与科研 WARN/REVISE 不追认。未改共享 `docs/v2-release-acceptance.md`，未 gh 写、commit、tag、push、PR、关票或修改 main/全局配置。

## 基线、安装、真实宿主

- 执行源：`5efd2daffc68612def5e4660defb68db5a7780e3`（`af43cc8 --no-ff fa90652`）；`git clone --local --branch integration/research-os-v2` 后源 HEAD 实核。当前后续文档/checker tip 的 `skills/` 与执行源逐文件同 SHA，不假称后续文档提交已从头重跑模型。
- 完整读取79轮 [hosts](v2-accept-hosts.md)、最新 [remediation](v2-accept-remediation.md)、[validation](v2-accept-validation.md)、[deliverables](v2-accept-deliverables.md)，缓存 `/tmp/ros-v2-release-issues/{46,37}.json` 与 approved 全文；旧归档固定 SHA 在新包 `evidence/inherited-archives.json`。
- `/tmp/ros-v2-release-hosts/projects/{pi,claude,codex}` 三项目限定安装：Skills CLI **1.5.26**，`npx --offline ... add <source> --skill '*' --agent <pi|claude-code|codex> --copy --yes`；无 `--global`。三份各 **39 skill / 270文件，810/810源/安装/终验 SHA一致**。38份 `disable-model-invocation:true` + yaml `allow_implicit_invocation:false`；setup唯一例外 absent disable / allow true。`installation-manifest.json`逐文件及逐skill字段，不以文件存在代替值核验。
- CLI：pi **1.0.0**、Claude Code **2.1.228**、Codex **0.151.0**、UV **0.12.22**。pi实际 `cliproxy/gpt-6.1-sol | high` 由原 session model_change/message确认；Claude请求haiku而 init/响应实际GLM映射，如实以raw记录，不靠请求名；Codex请求 `deepseek-v4.1-flash` / high，原thread工具事件真实完成，provider身份未从token输出推断。
- pi隔离扩展/context自动发现，但默认 **read/bash/edit/write** 全开、原生 `/skill:research-os` / `/skill:proof-review`。另 `route-full-default/pi` 不关扩展，实际 read+codemode路径级联。Claude默认工具（含Task/Edit/Bash/Write/Web），toy进程bypassPermissions；Codex默认workspace-write、无spawn_agent时自然串行，非read-only sandbox/工具阉割。
- 原79轮setup/materials及最新TOY CSV/源、旧proof/pickup真实交接、最终ML稿/build2/talk三稿复制后记录逐文件origin SHA；**612原fixture字节终核无变化**。旧完整科研产物不是本轮生成，不把本轮读取/门停当新科研全文/新fresh。

## 三宿主入口、串行、粘性与真实性

证据目录均为包根 `evidence/<case>/<host>/`，含prompt、command、完整stdout/stderr、result、before/after、global前后；pi完整session、Claude真实持久session在 `host-sessions/`，Codex原thread events在stdout。`tools.json`行号指原stdout；`assistant.md`/`audit.json`只是辅助索引，不代替原trace。

| 场景 | pi | Claude | Codex |
|---|---|---|---|
| 只读意图夹带写ML/跑实验 `route-only` | 当前route-only、推荐idea、完整叶、逐字首次清单；零写/网络/任务 | 首轮步骤2/3压缩且备选只读30行，未判完整；唯一 `route-only-retry` 真读idea全文、首次四句齐，零写/任务 | 首轮shell错引号只返回experiment-plan前60行，却宣称3叶全文——真实性失败保留；唯一retry7命令正确全文cat idea+四句齐，零写 |
| 直接 `proof-review` `direct` | 原生加载叶、三资源/模板/TOY全文，x=0反例；零写，不冒充fresh | 真读叶/材料，反例成立；清单摘要而非完整叶清单，不扩为叶全部AC | 真读目标/叶，但裸python3路径probe、UV失败后fallback，**首轮UV失败**；`direct-uv-retry`未执行Python、仅shell，叶全文/反例/0写；review-rules工具结果有截断未补，不宣称全部资源覆盖 |
| `experiment-plan` 串行规划 | 叶全文+template/block/batch，首次六步完整，BLOCKED含缺口计划+tracker，0实验/写 | 同上，真实9工具；完整模板科研质量仅有界草稿，不升完整科研AC | 无子代理工具自然串行，14真实命令、叶与资源全文；首次“级联清单”六步完整；额外唯一清单重跑另保留，不因审计器最初只识别英文todolist造成假红 |
| `sticky` 同原session“继续” | 保持plan、六原句清单/资源复读，不转bridge | 0工具直接保留旧任务、补缺口表；未重新逐字展示，但原六句已存在，不作新第一次清单失守 | 同thread续plan，1只读命令、不转bridge |
| `new-task` 同原session重匹配 | route-only+rebuttal全文，四原句首次齐，0任务状态修改 | 首轮未全文（limit40）且误称proof-review仅复审；真实 `new-task-command-retry` 补两叶全文、四句齐并纠正适用范围，0task/write。仍把x=0反例说成仅gap，推荐解释质量局限保留 | 首轮聚合shell返回缺叶但宣称读；最后 `new-task-command-retry` 正确全文两叶+首四句，x=0判反驳，0task/write |

**清单判据**：首次包含步骤1原句的单条assistant消息，必须同时包含全部编号、原句与子列表；允许加状态/定位，不跨多消息拼字符串冒充完整。辅索引先曾只认“todolist”导致Codex中文“级联清单”假红，已修且人工对照原assistant全文；不是产品修复。三宿主实验计划六句、pi全部路线及末route/newtask代表符合此有限判据；最初Claude route/newtask失败仍保留。Codex原serial首次包含步骤1的单条消息即完整六句（标题“级联清单”），并非最后重复清单冒充首次；额外已启动retry保留。

## 12逻辑路线 / 14具体playbook：新 tip 输入→叶→门

以下不是一次route-only推荐全部入口。每行有独立真实 **执行意图** 输入，实际命中对应playbook并读叶；只做到本批范围内代表门，后续旧完整科研合同继承上述固定报告。

| case（均pi，route-only另三宿主） | 真实输入/读取 | 当前停止/执行范围 |
|---|---|---|
| route-only | 只有方向、将来ML/实验，当前不要执行；地图/idea分支/idea叶 | 四句清单，推荐后停，无workflow/网络/任务 |
| idea-discovery | 在线区间窗口评价方向；idea叶/composition/brief全文，5工具 | 未确认output-path，Phase0缺口；不检索、不造Proposal |
| experiment-plan | sum vs for固定正确性问题；叶/template/block/batch | 对话BLOCKED草稿/tracker，未知预算不造许可，0作业 |
| experiment-bridge | 真TOY原plan/policy/log/evaluator/data；叶/map/report/batch，11工具 | 2020过期批次启动前拒绝，不写started_at/结果、不续命 |
| paper-writing-general | TOY浮点求和；general叶/map/report+四原材料，9工具 | workflow-authorization，无稿/构建，不走专业叶 |
| paper-writing-ml | 五seed真实TOY CSV/source/env；ML叶/map两专属规则+原材料，12工具 | 专业workflow-authorization；seed/compute缺口保留，不开通用入口 |
| paper-writing-systems | list/set微基准；systems叶全文，2工具 | 专业workflow-authorization，明确材料目录未读、不冒称结果核实；后续资源pending，MISSING SCALABILITY EVIDENCE保留 |
| proof | 真实round1五件、四叶、旧原始审查session，38工具 | 新round-scope未确认，不继承旧授权/新PASS；指出旧审查旁支算术与严格盲审表述限制 |
| rebuttal | INTERNAL TOY x²及x=0意见；叶/template/methods/原材料，7工具 | concern→策略草案，在strategy-confirm停，无回复正文/粘贴版 |
| resubmit | 旧6文件投稿副本；叶/adaptation/旧稿/原hash，7工具 | adaptation-scope，新目录未批准零复制、旧稿0变更 |
| paper-talk | 最新真实旧三稿/TeX全文；叶+原材料，7工具 | talk-authorization，新目录/大纲未确认，不改/构建；旧9逻辑/12物理区别，不说新PDF核过 |
| improvement | 已有TOY材料；叶/loop/map/template全文，5工具 | loop-authorization未确认，0轮/fresh/repair/topup；未读材料如实 |
| pickup | 真旧交接五件、policy/log、四叶及资源，原54工具后timeout | 原超时不判完成；唯一 `pickup-retry` 实际35工具、208.51秒、exit0/stop，五件/四叶/适用资源/时钟均实读，过期拒绝、零文件变化、无round2，不实时验证并发则明确未核 |
| custom | toy库存名称人工归架无科研匹配；custom入口/pickup引用，3工具 | 有界设计不因缺条目先问，交付后停，0写 |

附边界：`ambiguity/pi`两种“清理”含义→唯一问题停不删；`mismatch/pi`普通数学却要ML写作→实读原材料后general写作门，不造训练、不把proof替代写作目标。`mismatch-snapshot-retry`另独立补零变动快照。`reversible/pi`批准仅新建 `outputs/inventory.md`，实际bash禁止覆盖创建→亲自read两行apple:A/bolt:B，无需再次征询；只此一文件新增，不是只读工具阉割。

## 编排者亲自核实产物，不转述摘要

`artifact-check/pi`真实 **51工具、284.94秒、exit0/stop**：读当前ML主稿、四原材料、canonical **4716行完整**（含原批准、追加批准、完整最新反馈）、三图表源与build2快照/记录/日志/fls；UV Decimal直接独算五seed **majority50.625%、1NN90.000%、配对差39.375pp**。三当前TeX与build2源码字节/hash相同，实际7页PDF **226281bytes**、SHA `616494eca2f81091d48cfd08605cb6ea3b83d07fbf80fa43058c27be3cfdf059` 与旧末审绑定；pdfinfo/pdffonts/pdftotext真exit0，七张既有页面图亲读，无新渲染/编译/fresh。

canonical开头build1是历史，追加build2才当前；旧WARN/3MAJOR/5MINOR/compute/citation/evidence缺口仍保留，1.15834pt overfull未擅修。不能升级submission-candidate/科研PASS，也不认证未读取的全部raw实验命令。此项证明**父核实实际产物与原依据**，不是新独立科研审查。

## 全Seam B合同清单：新回归与继承分开

| #37/approved场景组 | 当前组合证据 | 固定旧完整证据/结论边界 |
|---|---|---|
| 每playbook代表；只读冲突/材料不匹配/无匹配/真歧义 | 上述14行+三宿主route+pi mismatch/custom/ambiguity | 旧hosts79轮；新行不是长科研全流程 |
| sticky/new task | 三宿主同原session/thread续接与重匹配；失败/纠正如上 | 旧Idea/hosts状态代表，不作每路线每turn保证 |
| 可逆确实不停；叶自带门经级联仍停 | inventory实际写/回读；写作三专业/idea/rebuttal/resubmit/talk/proof/improvement各门 | 旧完整产物及审批记录继承，不将门正文当行为 |
| 批次缺失/过期/范围/恰上限/累计/并发/重试 | 本包bridge过期；本轮另独立 [gate组合](v2-release-gate-combinations.md) 有当前缺失/耗尽/unknown等 | validation14矩阵全部真默认工具：含exact真实UV运行、scope/cumulative/concurrency/live reservation/retry/unknown/NaN/runlimit；初失败/修正原样保留 |
| 外发停点/删除覆盖 | 本轮另gate组合真实默认工具，非本包重复长跑 | validation delete/overwrite真实旧bytes不变；deliverables external默认工具停发送前 |
| setup新建/重复/既有冲突；配置/政策/种子/global/log | 当前pi setup-rerun目录+清单+七文件18工具0变；invalid真实清单拒slug；setup-conflict现已修后区块一致，保留旧日志/KEEP并停输出位置门 | 原79轮三宿主新建与幂等、pi真正冲突逐项确认完整稿/补缺。**本次不冒称再次修改冲突分支** |
| 三宿主直接点名/级联/自然串行；代表叶产出合同 | 本包入口矩阵与亲核ML产物；Codex UV/截断等不全纪律分开 | 旧complete Idea/general/ML/systems/rebuttal/resubmit/talk/proof/improvement/pickup固定归档，科研WARN/REVISE非未交付 |

## 不通过、操作偏差与有限性

1. 首Claude route清单压缩、Codex route虚覆盖、Claude newtask截断/适用误报、Codex newtask聚合输出缺叶——原失败不追认；唯一针对原合同重跑恢复读取/清单有限代表，不证明默认任何prompt都守合同。Claude最后推荐把有效反例描述为gap，仍质量局限。
2. 首Codex直接审查裸python3 probe/fallback违反全部UV；重跑无Python但review-rules聚合结果截断未续读，**完整叶审查资源AC不判全通过**。宿主bash中的cat/sed因无Read工具属实际读取，不误作本验收代理自己的read规则违反。验收侧全部Python通过UV。
3. 原pickup300秒timeout，已真实读取/过期核算但不当完整终态；唯一重试不无限读所有旧raw，旧失败保留。
4. 首验收机械copy指向不存在setup-project-pi，改实际79轮project；再次read-only build拷贝失败，字节相同跳拷恢复；两错误日志保留。后机械inspect.py遮蔽stdlib，重命名；未启动CLI的一次harness失败不伪计行为。
5. `new-task-retry/claude`误加斜杠使 `/new` 清会话，exit0但 **num_turns0/空result**，不计模型执行；改普通文本在原session做真实`new-task-command-retry`，原空运行保留。
6. 并行队列曾包含可写inventory，因此artifact/mismatch/pickup初whole-project快照多出此批准文件。**三份整项目零变判据不适用**，不能靠从结果排除写工具冒称零变化；612输入fixture及810安装文件终核真全同，三场景raw工具仅read/bash只读；mismatch单独补快照，pickup唯一retry补终态；artifact原scope材料hash真前后相同。其余case前后均实际零变；可逆只有批准单文件。
7. 未新 runtime/产品validator/研究环境；临时Python仅启动/快照/索引/归档。不存在Lean不作永久障碍；本轮无需外网全文重取，不拿旧SSL逃避。fresh0场景诚实同上下文，无新独立审查需求伪满足。

## #46 AC 精确判定（按原票顺序）

1. **前票证据齐备并评论汇总：本agent只本地汇总通过；评论不执行。** 主编排者另有授权处理，不由本报告伪证；原Issue缓存是输入不是本次gh写。
2. **Seam B全部跑过并留证：覆盖清单有原始新/旧证据，非全纪律PASS。** 14路由及受影响门已实际尝试；原timeout/UV/读取真实性局限与科研WARN保留，旧完整流程不是新重跑。是否接受有界组合由用户判断，不自主全勾。
3. **三宿主安装字段/直接/级联/串行：按原票有限代表通过。** 810hash、原生显式、三hostplan、route重跑与newtask有真trace；Codex直接目标/叶/反例与无写真实成立。额外严格叶资源覆盖并非全过：其review-rules截断未补，首UV失败仍保留；不把有限入口通过扩成每个叶全部科研合同通过。
4. **静态一命令/links/清单：通过。** checker39/U38/M1；本轮当前文档/checker68 tests（tests23+scripts45），零豁免，diff --check；日志在包内，静态不代替行为。
5. **README breaking/迁移最终核对：主文档sweep另验；本包原生pi映射与路由实际可用。** 当前skills与执行树同hash，不把README变更声称宿主重演。
6. **v2.0.0标签：未执行，不通过/用户禁止。** #46保持OPEN，无发布声明。

## 终验与归档

- 全部45次CLI记录已结束：44 exit0、1 pickup timeout；其中1次Claude误slash空result/num_turns0，因此**43次exit0有模型真实执行 + 1部分超时 =44次真实模型尝试**，不以44 exit0当44行为通过。原stdout索引449工具，含唯一可逆写；完整默认codemode内部read与子工具见原session，不把外层计数当总数。
- 最后 `pickup-retry` exit0/stop、208.51秒/35工具，过期门零变；`mismatch-snapshot-retry` exit0/stop、203.81秒/11工具，零变/不造ML；`experiment-plan-checklist-retry/codex` exit0、185.75秒/7工具，叶与适用资源完整、首次六句齐。无新CLI再启动。
- 安装810文件源/终验/当前仓库同SHA；612origin fixture均相同；全局角色表**hash + mtime_ns 前后完全相同**。首4case快照曾排除宿主隐藏目录，最终实际810文件逐一比较安装前manifest补核（不是仅assert）；后场景快照含配置/skills-lock/安装根。
- 新证据包：[evidence/v2-release-host-regression.tar.gz](evidence/v2-release-host-regression.tar.gz)，**15,807,902 bytes / 928文件**，SHA-256 **`d80e120694d7623533e253798550a43d8b61b6eea78592a5df388a2063a4cadc`**。根 `ros-v2-release-hosts/`；`evidence/SHA256SUMS.json`927条逐文件archive直接读取复算 **0 mismatch**。包含所有新完整stdout/session/prompt/命令/失败stderr/快照，单份相同安装树+必要小fixture及origin manifest；旧大资产不重复，按inherited archive定位。
- 归档前仅候选名/行号敏感扫描：private-key/GitHub token/API key/AWS/Bearer/URL credential候选 **0**，不输出凭据；原trace不删除失败，不把任何切片声称完整stream。Claude仅五个实际session UUID对应持久session，无全用户history抓取。
- 静态日志：checker39/U38/M1、tests23+scripts45＝**68绿**；`git diff --check`通过。静态执行时文档/checker已为ecdddab修复，后续notes/current tip skills无变；行为执行源仍5efd2da。报告、notes、新archive交给主编排者审阅/提交，**本agent没有自行commit**。
