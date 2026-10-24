# #60 最终修复候选 merger — implementation notes

## 状态

| Work unit | 状态 | 产物 / 验收证据 | 下一步 / 阻塞 |
|---|---|---|---|
| 按精确顺序合并合同候选与安装引用源，保留新正文/恢复/安全门及同包 mandate 链接 | done | 候选 `4f490fde280d5662f4e1fca09d5ddaf99206ee9b` 快进后，安装源 `30891d3b2099fcb3bac4c2e10486166c81c99d93` no-ff；合并提交 `179af18f79f636ff8356041af9f3e8f4378eed95`，双亲及 diff 已核 | 无；待汇总验收证据 |
| 串行定向/相关回归、checker 精确对照、真实 Skills CLI 41 包与代表单装 | done（执行完成；保留两项单装/语义复审风险） | `/tmp/spec48-final-fix-merger/logs/`、`audit/summary.json`、41 包源/安装 manifest 与 links JSON；定向/相关组 111 tests 通过；checker 原 9 条逐字节 cmp 相同 | parent 后续独立合同复审及全套测试；核查本 notes “Deviations / Risks” |
| 汇总完整候选报告并提交小型 notes commit | done | `/tmp/spec48-final-fix-merger/REPORT.md`；产品候选 `179af18f79f636ff8356041af9f3e8f4378eed95`；notes-only commit 随报告记录 | 后续由 parent 独立合同复审与全套测试 |

## 入口与范围

- 入口判定：直接执行；当前任务明确禁止继续派发，且指定精确双源与验收范围。
- 当前隔离 worktree：`/Users/rolex/.t3/worktrees/Research OS Studio/t3-69c5d6f0`，分支 `t3/merge-ticket60-fixes`，基线 `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e`，初始 clean。
- 严格只合并 `4f490fde280d5662f4e1fca09d5ddaf99206ee9b` 与 `30891d3b2099fcb3bac4c2e10486166c81c99d93`；先快进合同候选，再 no-ff 合安装引用源。不开 integration/主目录，不 push，不触碰 tracker，不派发。
- 已读取 `~/.agents/Multi-Agent.md`、`~/.agents/model-availability.md`、`~/.agents/CODING_STANDARDS.md`、仓库 `AGENTS.md` 与 `docs/agents/domain.md`。实施记录按仓库规则放在 `.agents/notes/`（被 `.gitignore` 忽略，提交时需显式 force-add）。

## Decisions / Deviations

- 安装源与合同候选只有 `paper-compile-repair/SKILL.md` 一处文本冲突。保留合同候选的完整授权来源、已授权委托内执行、责任/额度、交付与安全门正文；只将中央 mandate 相对路径改为新同包 `references/mandate.md`。不接受安装源旧块覆盖新合同正文。
- 合并后 12 个 mandate 同包文件均逐个 SHA-256 为 `60c40e03b390ed08241067d7e256094cb6fdf5af35343a930e0ec6a1bd0899a0`，与分发摘录完全相同；paper-writing composition map 使用可发现 `proof-review` slug。全基线至候选 `git diff --check` 与冲突标记搜索通过。
- 测试与 CLI 安装脚本两次发现调用方式偏差，均保留原日志/returncode且不作通过证据：A1/#56/#58 的 `unittest` module 入口缺少 `tests/spec48_workcopy.py` import path，改用 `unittest discover -s tests` 后测试通过；CLI 第一次未 `cd` 到隔离 cwd，生成物写入当前候选 worktree（没有触及 integration/主目录），核实来源后清除，再从各自树外 cwd 重跑，后续 CLI 日志/manifest 才计入证据。
- 真实 full install 的 394 条 concrete local path 全部解析、源安装 hash/mode 一致。代表单装中 `paper-writing` 的 20 条 sibling 资源缺失有明确 `blocked` 边界；但 `paper-compile-repair` 独装有 7 条指向 `paper-compile` 的链接缺失，虽 mandate 已共置，其“全部依赖随包提供”声明未给出 blocked 说明。按“仅合两来源、不扩本包范围”记录为残余，不在本轮添加源改动。
- C01–C07 指定测试集通过；更宽短语扫描发现未列入原 C06 文件清单的 `paper-claim-audit/SKILL.md:19` 有“其他专项审计由用户另行点名”措辞。语义需由 parent 下一轮独立复审判别，未算作本轮已解决/已定性。

