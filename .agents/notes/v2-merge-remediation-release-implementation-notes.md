# #37 最终集成与release验证 notes

## 输入与边界

- 起点 integration/research-os-v2 `af43cc8`，工作树干净；`v2/accept-remediation` 精确 tip `fa9065226`。`git merge --no-ff` 成功，新执行基线 `5efd2daffc68612def5e4660defb68db5a7780e3`。
- 完整读 docs/acceptance 四报告、#37/#41–46原票正文及全部评论、`/tmp/research-os-v2-notes/shared-contract-approved.md`。原合同复制只作本地验收指针，不引入产品schema。
- github-api-rate-limits/pre-implement已加载；首预检core/graphql remaining5000。gh当前版本禁止 --comments 与 --json同时用，明确无网络失败，改 --json comments成功，不无限重试。
- 只在本integration工作树与独立/tmp项目；不改main/全局，不tag/push/PR，不关#37/#46。允许达标前票gh评论/close，明确本地commit未push。

## 判断原则

- 科研REVISE/WARN、原审计FAIL经门纠正/预算用尽停止是有限流程合同的结果，不要求学术结论PASS或真人投影。
- 旧实际越界保留失败；以新增干净Idea/ML/talk复验+未受本次正文diff影响的已固定general/systems/rebuttal/resubmit/validation/proof/pickup证据组合。当前tip重跑受影响路线/门/只读/串行场景，不从零重复所有科研长输出。
- TOY实测与真实公开论文分列。UV、调用身份、fresh隔离、写域等纪律不以模型自称通过替代。

## 分工

- v2-release-ac-review：独立逐#41–45原AC核报告与关键原始证据，不写文件或gh。
- v2-release-host-regression：读取原79轮及新fixtures；当前tip三宿主安装hash/字段，默认工具组合回归，逐字todolist/亲自核实/串行/只读冲突；独立报告与归档。
- v2-release-security-tests：新增45MiB归档安全扫描与898条manifest，UV checker+两suite全tests；不输出凭据值，有真候选先协调。
- 模型均 cliproxy/gpt-6.1-sol high，按本机pstack审查/验证角色。禁止子代理自行commit，主代理整合提交。

## Progress

- no-ff merge完成；四报告与七票原文读完，原approved合同读完。只读原工作区ADR0006/0007已完整读，未提交用户资料。
- 另派v2-release-gate-combinations补当前tip预算/外发/严重修订跨票门；host agent仍负责14具体playbook路由与三宿主。固定原素材引用，不重演全部科研长输出。
- 主最终doc sweep发现根README安全第2条和英文核心原则仍有无条件产物后停止；现checker只检测两literal未捉。sol medium先新真实副本反例RED两subtest、合法叶停止正例，再仅加现literal两条并改中英两句，GREEN T46 8/8、checker39、两Python LSP0。主读diff与notes后提交 `ecdddab828ef027590d1b49eb3870435bf995a71`。
- `git diff 5efd2da ecdddab -- skills`为空。宿主执行5efd2da安装仍是当前产品skills，静态在ecdddab重跑；不以不相关doc/checker变更要求从零科研重演。
- gh预检第二次core/graphql仍返回5000；这是实返回，不据此称零请求。已知读取七issue via gh JSON（评论字段同批）。
- 独立AC reviewer已直接核四报告/原票/关键叶/原始session与固定物，#41–45全AC达标。其最终存在两个assistant正文，工具仅回最后短总结；主用UV读取retained session提取首份完整逐AC正文落 `docs/acceptance/v2-release-ac-review.md`，未伪造其结果。notes/report commit `464b2727f4e55f91dcb46fe9608a0a993937cb15`；最初commit diff check捕到Markdown尾双空格，立即消除并amend，主最终commit无该空格。
- security中间已实核新增898manifest/真凭据0；ecdddab UV tests23+scripts45=68，精确stage日志读到。基于此先gh预检后 `gh issue close --comment` 顺序5票全成功（评论含local未push/逐AC/toy/旧失败与过程偏差），#41–45已CLOSED。
- #37/#46进度context评论分别 `5968914862` / `5968915099`，注明hosts/gates组合正在末验、首route清单/虚报仍待唯一有界重测。一次合并GraphQL回查7状态cost1，remaining4971/resetAt2026-10-03T12:25:04Z，#37/#46 OPEN。gh预检仍core/graphql5000但与GraphQL实监不同，不据此称零消耗。
- 已知GitHub写动作：5次close（各带评论，gh内部请求数未监不能杜撰REST精确耗费）、2次context comment。未tag/push/PR/关#37/#46。
- 原archive安全独立报告与notes提交 `885e5e4`，四包5753regular/约546MB原字节、148初筛falsepositive/已脱敏、28PDF与JSON转义补scan，真secret0；新45MiB898payload全部match，无清洗无需改hash。
- 当前门组合8+同session唯一ML澄清均exit0/stop/agent_end；budget missing/failed累计/unknown预留、两pickup真实旧五件、ML终止后build拒/外发、talk严重项及唯一获准候选write→read。报告/577文件12MiB归档commit `eaa76f0`。ML首与talk诊断合理route-only不假称执行级联，ML追加澄清/获准talk审查候选分别真实证明执行分支；不重新从零科研。
- 主完整read门报告/notes/部分final核范围，独立安全末验门包577regular35,203,600bytes、576manifest hash+size match、4PDF104JSON转义scan真secret0，SHA2291c39c...efc1前后稳定。
- hosts组合机械核初用所有assistant散句字符串包含，主要求single首次清单块核编号/子列表，不能散句累计冒充逐字清单；初索引只认英文todolist又误判Codex中文“级联清单”，原first含step1块真六句齐，不假红。已启动唯一额外清单重跑仍原样保留，185.75s真实叶/resources/6句终态。route-only Claude/Codex首失败已实际有界重跑全文/逐字达标；Codex direct裸Python/Claude newtask漏正文原失败保留，针对重跑不改产品去追模型。
- hosts全部45CLI结束：43完整真实exit0模型、1pickup部分timeout、1slash空调用；pickup唯一208.51s35tools/stop/mismatch203.81s0变化重测，setup轻回归完成。当前“冲突”副本实际已修后一致，本轮仅旧物保留/路径门，不假称又跑修改冲突；原79轮真冲突固定证据可继承。
- host父51tools/285s实际读canonical4716行、原批准/反馈、当前稿/CSV/build2/7PNG/PDF绑定，UV Decimal50.625/90/39.375核，未新build/fresh。810安装+612fixture+global SHA/mtime同。15,807,902bytes/928file包SHAd80e...cadc，927manifest双核match；安全独立末验928regular/57,045,065bytes456JSON解码真secret0。两新包1503payload全SHA+bytes同，无清洗hash不变。
- 主在eaa76f0又实跑checker39/tests23/scripts45=68全部exit0，日志/tmp/ros-v2-release-final，diff --check过；后仅docs/archive/notes，产品skills树f673b96d不变，不谎称模型在最终docscommit从零重演。
- #46行为/静态/安装/migration AC2–5有限代表覆盖达标；AC6tag用户禁止，#37/#46继续OPEN。Codex direct重跑review-rules截断未补是具体额外资源纪律局限，不把入口验证泛化全叶正确；Claude最后gap解释质量局限单列。可交release review候选，不称已发布/所有宿主永远安全，后续若人要求补该单场资源严谨性，只补这一场而非全部科研。
- 完整最终归档/文档提交 `eadfe77ed16ae0bb5dd4cabf1c01a1fa54a47ec1`，工作树当时干净，最终checker再39、合并全diff --check过。
- 最终#37/#46补context请求前rate预检正常5000，`gh issue comment 37` GraphQL EOF，后REST查询两票comments及rate预检均EOF；一次清代理直连预检也EOF。共3有界恢复尝试后停，不假称评论已送达，不继续网络循环。两原进度context先前已真实送达；最终正文保存 `/tmp/ros-v2-release-issues/final-context.md`。
- 因此当前精确余AC还有#46-1完整最终归档/commit汇总评论补送（不是前票证据缺失）及#46-6 tag。不需要科研长输出重演。前票close成功和当时GraphQL状态回查有实证，不因本末EOF重写其状态。

## 最终步骤8 closure（本地发布边界）

- 本轮起点 `bc08199137d2a29a83f361a9f15659a8fab34dc3`，integration工作树干净；main仍 `837d1e86b18f1f753964d51d18a64e069011209a`。完整读最终release、independent-verify、merged-host-smoke、六项修复报告及原#37/#46正文，#38–45本轮GraphQL实核全部CLOSED。
- 用户/主agent接受披露局限的有限代表验收，解除此前临时禁tag，明确授权本地 `git tag -a v2.0.0 <本收口commit>`；不移动已有tag，不push/PR，不删worktree，不改main/全局。创建前两次读refs/tags均无v2.0.0；若最终创建时出现同名冲突，停报告而非强制覆盖。
- 最终实跑UV checker39/U38/M1、tests29＋scripts45＝74全绿，两diff check通过。只更新release汇总/本notes；最终合同六项＋dot错base已TDD闭合，受影响宿主轻验已归档。不重复科研实验、不扩manifest，不把静态当行为、不追认历史UV/存储/清单/fresh失败为全纪律PASS。
- 本轮rate预检REST/GraphQL均remaining5000/reset epoch1791041030；读取10票选GraphQL合并最小字段（REST需10请求），实际cost1/remaining4999/resetAt2026-10-03T15:24:11Z。随后按REST向#46发最终静态/行为/commit/tag/局限/本地未push评论并close，再#37摘要并close；最终合并回查37–46全部CLOSED。所有写动作和最终commit/tag/状态由执行结果确认，不在提交前伪填成功。
- 提交策略按本轮明确Git命令授权：文档commit在integration，annotated tag目标精确该commit；最终HEAD/tag target/worktree/main核对。若EOF只最多3有界恢复，先读确认实际写入，不能盲重发造成重复或伪报关闭。

## Deviations

- 无新增产品runtime/validator。扫描、manifest与trace机械检查只属于验收侧，不作为科研产品协议。
- 历史不tag/不关37与46仅适用于前批；本轮用户明确新授权取代，不回写历史记录。
