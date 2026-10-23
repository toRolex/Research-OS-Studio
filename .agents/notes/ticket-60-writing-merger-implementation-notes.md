# Ticket 60 writing merger — implementation notes

## 状态

| Work unit | 状态 | 产物 / 验收证据 | 下一步 |
|---|---|---|---|
| 串行合并 proof+docs 候选与 W1 writing，保留新委托语义及两包资源归属 | done | first merge `1dcc1138db0fb446402dc1113fbb534991aa750c`，W1 merge `933bb17ae1cd88516b183653ac872a723cf81535`，文档语义对齐 `925896c1eb5ba22e1f954ef99e6615e74b0a4c3b`；指定 clean-candidate 测试见 `/tmp/spec48-ticket60-writing-merger/logs/final-*.log` | 候选仅供后续统一验收，不纳入 integration |
| 形成仅候选的 clean SHA、测试证据和 notes commit | done | 最终候选 SHA、双亲、clean 状态与证据汇总见 `/tmp/spec48-ticket60-writing-merger/REPORT.md`；checker 原 9 条输出 exact cmp | 候选等待 Discovery/bridge 后统一组合验收与 promotion |

## 入口与范围

直接执行，不再派发：这是已拆分且输入报告齐备的串行 merger work unit，用户明确要求停止继续派发；当前隔离 worktree 已位于指定基线，可承载独立候选。范围仅为先 merge proof+docs 候选 `b9e237e2a4d9128a6fe494bac29f15e63d3b47e4`，再 no-ff merge W1 `3bf2fa3a6a4e10b78a455d302474607ea1013038`，最小化解决相关冲突、验证、记录候选；不接 Discovery/bridge 未提交内容、不进 integration / 主目录、不 push / tracker、不扩大历史 archive 处理。

## 决策与因果记录

- proof-review 的 15 份方法材料、许可/NOTICE 和完整专业资源仍由 `proof-review` 拥有；写作 ML/AI 与 Systems 专业资源、模板和许可均由统一 `paper-writing` 包拥有。资源重命名、归属或许可有差异时，必须以实际源 diff 和文件/hash 核查，不按旧 README 快照恢复。
- README、地图、checker、测试说明只保留现行研究委托语义与资源归属；旧控制器/slug 删除优先于历史兼容宣传，只有明确标为历史或退役的叙述可留。
- 目录和徽标按当前实际树同步，不设目标数量；checker 的既有错误/历史 archive 诊断集合不得借本任务扩大或静默修复。
- CLI 安装证据仅能从资源 payload 相对已验证来源未变时继承；若变动，则重跑对应代表包的真实 Skills CLI 并记录新 hash/链接。

## Deviations

- W1 的 `docs/README-en.md` 冲突带回已删除的 `proof-orchestrator` 并列项及已删除的 ML/Systems Skill slug；删除旧 proof 行，只保留 proof-review 条目与 W1 的统一 `paper-writing` 行。
- `skills/README.md` 冲突的 W1 侧同样恢复旧 proof 控制器，proof+docs 侧的 Validation Cycle 行保留；写作行采用 W1 的统一入口及专业资源说明，去除两个旧 Skill slug。English README 的徽标依据合并后实际 43 个 `SKILL.md` 修正为 43，不按源报告的中间态计数。
- 合并审查发现 English README 的写作流程图仍说叶 Skill 在计划、图表、起草和编译前逐阶段过授权门；该句与新委托合同冲突，改为跟随现有委托、不附加阶段门，并明示只读、目标变化、越权/超额、外发及破坏性操作硬门。
- 二次交叉审查发现 `skills/README.md` 的编译/引用修复手工验收段仍要求“用户另行显式调用”，与统一 `paper-writing` 委托内级联合同冲突。以 `925896c` 局部修订为：区分独立点名与已授权父委托的路径级联；保留精确 diff、构建/预算和逐项批准的真实叶安全门，不把修订扩大成自动写入授权。
- 完成树实际含 43 个 `SKILL.md`（4 general、7 idea-cycle、1 organization、17 validation-cycle、14 writing-cycle），因此将 English README 徽标改为 43；不将树规模作为验收目标。实际 CLI 对 `research-os` 报告 Found 43 skills，30 个安装文件与候选 package manifest 完全相同。
- 三个专业许可证均在当前目标包中保留完整字节：ML/Orchestra SHA-256 `80b5899a9ab121a2d4aae63724f0c11defba7f23da487086932bb9abfb0f2a00`，Systems ARIS `e30cf5dd5f49b4f9b656590e23d782b4756c924a9f0ff0162b3e7b5d87006bf5`，Systems Orchestra 与 ML/Orchestra 相同；proof-review LICENSE 与基线旧 LICENSE 字节相同（`e30cf5dd5f49b4f9b656590e23d782b4756c924a9f0ff0162b3e7b5d87006bf5`）。M 测试覆盖 15 份 proof reference 逐字节映射和本地链接。
- 最终 payload 对照：`proof-review` 相对 proof+docs CLI 验证源 b9 无变化；`paper-writing` 相对 W1 CLI 验证源 3bf 无变化，继承 W1 真实 21 文件 CLI manifest `0c1171d271c825311694aa184edef161776d7f4ee691bcb443f8715c99fe5eb9`。`research-os` 相对 b9 有 W1 活调用/路由改动，故重新运行真实 Skills CLI；独立 `/tmp` HOME/cwd 安装 30 文件成功，安装与候选 payload manifest exact cmp，SHA-256 `5079be58d55126792eccba599e5fcd7b4b6d0874595c1145165d352f2161ec25`。
- 最终文档树 clean-candidate 分组验证：M 4、writing 新合同 3、#55 17、#57 13、policy 4、#43 8、#38 21、accept-remediation 4、#46 manifest 9、tracked scan 1 项均 return code 0；每项独立 alarm 180s，串行，`TMPDIR=/tmp/spec48-ticket60-writing-merger/tmp`。checker 实际 return code 1，SHA-256 与 `/tmp/spec48-closed-baseline/logs/head-checker.log` 完全相同（`acbd51e6f5e308fc570dced0eb6f46d3c9df9eb5de0323fc74271c38a0ff1cbf`），只含既有 9 条 acceptance archive 历史诊断。
