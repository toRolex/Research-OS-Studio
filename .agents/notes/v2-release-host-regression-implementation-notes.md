# #46 当前 tip 独立宿主组合回归 notes

## Scope
- 用户指定 tip `5efd2daffc68612def5e4660defb68db5a7780e3`；开工 rev-parse 一致。只新增本 notes、独立 report、独立 archive。共用 release 文档不改；无 gh 写、commit、tag、push、PR、关票、main/全局配置修改。
- 已先读 pstack；完整读79轮hosts、最新remediation/validation/deliverables、缓存#46/#37及approved合同。
- 继承固定科研完整流程，不把旧产物在新 tip 改称重跑；新回归优先14具体playbook的路由→叶门、三宿主入口/串行/逐字清单、只读冲突、sticky/new task、受影响预算/外发停点。

## Decisions
- 默认工具执行：pi 内建read/bash/edit/write齐全（隔离扩展/context发现，另完整默认工具代表）；Claude默认工具；Codex workspace-write默认工具。不用read-only工具阉割制造通过。
- /tmp中的脚本仅本次验收机械快照/启动/索引，不进入产品、不创建runtime或validator。全部Python执行UV。
- 有界真实session，timeout保留原trace；环境重试最多一次。模型科研评价REVISE/WARN保留，不追科学PASS。

## Progress
- 源clone实际5efd2da；三宿主各39×270限定安装，810文件源/安装/终验/current同SHA；setup唯一allow true，38 explicit字段真核。
- 45次CLI记录全部结束：44exit0+1timeout；其中Claude误slash空result/num_turns0不当模型执行，43exit0有模型+1部分timeout。14playbook独立输入到叶门、三宿主route/direct/serial、原session sticky/newtask均真执行。
- 首route/newtask读取虚覆盖/压缩清单保留，唯一针对重跑恢复；Codex首direct裸Python偏差保留，重跑无Python但resources截断未补保留有限叶检查限制。无科研长输出重做；ML父51工具亲读当前稿/CSV/canonical4716行/最新PDF/hash，Decimal独算50.625/90/39.375，不转述摘要。
- 首pickup300s超时保留；唯一轻量pickup-retry208.51s/35tools/stop，过期不续命零变；mismatch单独快照203.81s零变；serial唯一重跑185.75s/7tools完整首次六句。
- setup-rerun现存七件+真实清单18tools零变，invalid真清单拒slug；conflict为原已修后一致副本，本次只读保留旧日志/KEEP与输出位置未批门，真正冲突变更继承旧79轮不假新。
- static23+45=68绿，checker39/U38/M1，diff check过；612origin fixture无变；global hash+mtime_ns同。
- 新archive15,807,902bytes/928files，SHA d80e120694d7623533e253798550a43d8b61b6eea78592a5df388a2063a4cadc；927manifest archive直接复算0mismatch；敏感候选0。新完整raw不删旧失败，不重包旧大资产。

## Deviations / causality
- 旧setup-project-pi目录不存在，合理用原79轮project真实完整seed替代；再次拷read-only build失败改equal→skip，不chmod原件，两失败日志保留。
- 验收inspect.py遮蔽stdlib导致harness import失败，重命名恢复；该次无CLI不能计行为。
- new-task-retry误加slash导致Claude /new清上下文且0turn；纠正普通new task原session重跑，空运行trace保留。
- 最初清单索引只认英文todolist，Codex中文级联清单假红；改以首含步骤1原句单assistant block判全部句/子列表并人工读，对旧首serial6句齐恢复正确判定；已launch额外retry原样保留，不以分散substring拼齐冒充首次。
- 并行队列可逆写污染artifact/mismatch/pickup whole-project快照新增outputs/inventory.md；这些整快照零变不适用。原fixture/安装逐文件真前后同，工具read/bash只读可核；mismatch及pickup唯一独立尾重跑补0变。不删污染trace、不重做全部科研。
- 不改产品去追模型样本；无新runtime/validator、不commit/gh写/tag/push/PR。主报告AC按本票有限直接/级联通过与额外完整叶纪律局限区分。当前已停止所有模型CLI，交主安全扫描/提交前通知。
