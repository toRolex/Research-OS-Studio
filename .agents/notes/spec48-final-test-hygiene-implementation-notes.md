# #60 最终测试卫生修复

日期：2026-10-24。直接执行：用户指定实现 worker、禁止继续派发。
当前 T3 隔离分支 `t3/fix-ticket60-test-contracts` 已快进合入候选
`fd3d5e165423f9e4f3e7d335796d0552619a6cb7`；不写 integration/主目录。

| 单元 | 状态 | 产物与验收 |
|---|---|---|
| #49 语义路由合同 | done | `logs/red49.{cmd,log,rc}` 为 rc=1；定向绿包含完整 #49，含 ML/Systems 旧路由反例 |
| 残余安装 argv 与单宿主落盘 | done | `logs/redargv.{cmd,log,rc}` 为 rc=1；真实绿只一个修复包、一个项目宿主目录，7 条 sibling 边通过 |
| 定向与完整 suite | done | 定向 27 passed + 2 subtests；全套 348/348 nodes / 34 files 实跑，342 passed / 原 6 failed，无遗漏/重复/skip/timeout |

已读全局 Multi-Agent、model-availability、CODING_STANDARDS、pre-implement、
指定 `~/.claude/skills/tdd/{SKILL,tests,mocking}.md`、GLOSSARY、ADR-0005。
测试 seam 由本次用户指令明确指定；不修改产品，不恢复旧兼容承诺。
每个子进程限时不超过 180 秒；Python 仅 uv；串行、树外 TMPDIR。
初始 df 可用约 5.6 GiB，不删除历史/他人安装数据。

## 决策与偏离

- 仅在外部进程边界 mock argv 安全回归，真实安装另行验证；避免为了复现而制造新的全宿主副本。
- 无产品范围偏离；独立产品合同 review 的原始结论不由本测试补丁重写。
- 删除的是 #49 对无语义作用的逐字承诺要求，而非删除路由约束；改核三个专业路由、统一真实入口、有效资源、只读边界与三个宿主映射。
- 全装原测试 `len(repairs)>1` 正是在要求误装多个宿主，随单宿主 argv 修正为精确 `.claude/skills` 路径，并拒绝额外项目目录和 HOME 内 Skill 副本。

## 验收证据与限制

- `/tmp/spec48-final-test-hygiene/REPORT.md` 汇总所有命令/rc、diff、失败节点与边界。
- 原残余 4 项加新 argv 回归 5/5；#49 22/22；A1/C01 1/1、B2 2/2、C7 7/7、writing 3/3、tracked scan 1/1、copy isolation 1/1，均在完整 suite 中实际执行。
- 收集与实际执行 node 集合 SHA-256 均为 `0e8c8732f9518816b73497e5efcbf12ee4c287979170e2c518805a6f8b34ac34`。
- 单宿主真实全装 41 个 slug / 333 文件与源内容逐项相同，0 symlink / 差异；项目仅 `.claude` 目录，HOME 空，详见 `install-audit.json`。
- checker rc=1，仍是原 9 条 archive 缺链；与历史日志 `cmp` rc=0，未隐去原六个 suite 失败，不宣称全绿。
- 全套测试期间未再变更测试；只补验收 notes。无 push、tracker、integration/主目录、历史清理或继续派发。结束 df 可用约 5.4 GiB。
- 本轮不重做自然语言独立 review、不认证真实 agent 科研执行或跨宿主运行时；产品文件相对候选零变更。
