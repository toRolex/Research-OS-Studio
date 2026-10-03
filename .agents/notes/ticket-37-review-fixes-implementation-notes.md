# #37 review fixes implementation notes

## Scope / inputs

基线 97f185e，v2/review-fixes；仅本 worktree。已读 approved `/tmp/research-os-v2-notes/shared-contract-approved.md`、原工作区只读 spec/ADR 0006/0007/CONTEXT，以及集成/#38/#39 notes。沿用批准的 Seam A（checker CLI 与合同文档），不声称 Seam B 已验。不派 agent、不 push/PR/关票。

## Tooling

use_skill pre-implement、writing-for-agents 已加载；use_skill tdd 不在注册表，改为完整读取 ~/.agents/skills/tdd/SKILL.md 及 tests/mocking。UV skill 未安装/注册，全部 Python 命令仍用 uv run。

## Decisions

- 完整读取 checker 后再修改；先 CLI 损坏副本反例红，再最小修复绿。
- 新回归 fixture 仅复制 git 追踪文件，再单独加入未追踪引用反例。不改变现有复制 ROOT 的测试：既有测试刻意用 git add -A 构造仓库，其中未追踪目标的 checker 拒绝需求仍应保留；补独立反例证明，避免把测试清洁性改动扩散到所有历史测试。

## Progress

- 阅读合同、checker 全文与已有配置/门测试完成。
- Red 1：新增 none/来源 CLI 反例，5 个失败（none 4，setup 跨 skill 1）；统一 gate_problems 后绿。叶跨 skill 使用真实 paper-plan 标题锚点，避免以坏锚点假阳性。
- Red 2：异构 CPU 1/单次 2 + GPU 100/单次 0、重复单位、缺单次单位配对、默认 Role 引用，共 4 个失败；按原字段位置逐单位比较、查重复与数量配对，默认扫追踪 skills Markdown Role 后绿。补额外单次、缺单位、NaN、恰好上限案例。
- Red 3：编排合同/叶触发描述 2 个失败；补 todolist/逐步状态/核实产物，21 份 SKILL.md 共 21 处 model-invoked 改为显式或授权路径级联（review 提到22处，当前基线实际21处）；仅触发描述变化，科研正文与 composition docs 不动。
- 门三套逻辑收敛到同文件 gate_problems：none 全行解析、格式、ID/基线、approval、resolve 后当前 skill 的 SKILL.md/references 来源、锚点。外部 --skip-suite 不要求本仓追踪，仓库默认要求追踪。移除重复 regex/锚点辅助。
- 新 fixture 复制 git ls-files；独立未追踪级联目标测试拒绝，保留历史复制 ROOT 测试不动。

## #46 原轨迹核实

完整读取 /tmp/ros46-install-k0vn/codex-route.jsonl 与 pi-serial.jsonl：Codex reasoning 明确 route-only，最终回答推荐 experiment-plan，未执行；不能据最终入口名断言路由执行错选。但推荐未读叶全文且声称论文骨架无依据。pi 明示叶路径不知而 blocked，未冒充读取；扁平安装路径映射缺文档。补当前路线与推荐入口区分、仓库路径到宿主扁平安装映射、串行仍需读叶全文及缺路径 blocked。没有重跑模型（本次明确不派 agent，且不足以仅凭一次采样宣称行为已修复）。

## Deviations / acceptance gaps

- 无真实宿主科研项目轨迹；编排者核实、逐步 todolist、跨宿主显式策略仍待 Seam B，静态测试不伪造行为通过。
