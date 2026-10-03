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
- gh预检第二次core/graphql仍返回5000；这是实返回，不据此称零请求。已知读取七issue via gh JSON（评论字段同批），无GitHub写操作至此。

## Deviations

- 无新增产品runtime/validator。扫描、manifest与trace机械检查只属于验收侧，不作为科研产品协议。
