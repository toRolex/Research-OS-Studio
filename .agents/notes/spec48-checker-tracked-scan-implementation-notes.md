# Checker tracked Markdown 扫描边界

## 状态
- 定位与 TDD：done；`logs/red.stdout` rc=1 明确在进入小 fixture `.pi` 前失败；`logs/green.stdout` rc=0。
- 最小修复：done；只改全局 Markdown 清单，不改 copier、忽略集、历史红灯或其他票目录；`checker-green` rc=1、原九条 stdout 原始字节 cmp=0。
- 串行初验：done；clean 实现提交 `bde88be847dcc5cfdb06776dc216aa13fe94d710` 上 sentinel rc=0；214 联合 rc=0（87 subtests，99.289 秒）；全套 rc=1（6 failed／272 passed／131 subtests，121.848 秒）。`compare-clean` rc=0：六个失败 nodeid 精确匹配既有基线，checker 原九条 stdout 原始字节 cmp=0。
- 只读 parent 扫描探针：done；`parent-probe` rc=1（仅原九条诊断），0.283 秒；exec 本分支源码、仅将 `__file__` 指到 parent，scandir 对不在 tracked 祖先集合内的目录一律先拒绝。没有拒绝触发，stdout 精确 cmp=0；未写 parent 文件；前后 parent HEAD 均 `86caa4fd76792b056f31d5c083fb7cd918760a4c`。不外推为 parent 全套通过。
- integration 同步／最终交接：待验收；读取具体 integration tip 并在本分支 merge，然后在 clean worktree 复验，最终身份／diff／日志见外置 REPORT。

## 边界与决策
- 指定 implementation worker，用户禁止继续派发，直接执行；已读全局 Multi-Agent/model-availability/CODING_STANDARDS、pre-implement、指定 TDD 三文件、GLOSSARY 与 ADR-0005；Python 仅 uv。
- 已批准 seam：checker 执行与文件系统扫描边界。小型 fixture 的 scandir 哨兵验证不进入 ignored 树，同时验证 tracked 内容与损坏链接；不遍历或复制真实 ignored 大树。
- 原全局 `ROOT.rglob("*.md")` 在 tracked 判断前遍历整树。`skill_dir.rglob` 仅在指定 experiment skills 内部，没有仓库根 `.pi/.agents` 的同类泄漏证据，不扩大修复。
- 原清单未作字典序排序；必须保留本机原遍历顺序，而不是用 sorted(tracked) 改变九条历史诊断顺序。不得以本轮修复解释原 timeout 全部耗时。
- 由既有 tracked 集合生成候选及祖先集合；只浅读这些祖先的目录项，维持原目录枚举／栈遍历顺序。ignored 目录自身名字可在祖先目录项中出现，但不进入其内容；tracked `.agents/notes` 仍须访问。缺失 tracked Markdown 自然不在目录项中，和旧行为相同；保留 symlink 目录不递归与原链接／元数据诊断。
- 小 fixture 同时覆盖 ignored `.pi` 与 `.agents/evidence` 哨兵、force-tracked ignored notes、tracked 缺失文件、损坏／越界／存在但 untracked 目标、原元数据错误和本机原诊断排序。Python 3.14.4 实测，不承诺其他 Python 版本未文档化的 rglob 顺序一致。
- 风格核对：KISS（沿用 tracked 集合，仅为保持原诊断顺序浅枚举祖先）、YAGNI（不新增忽略规则／配置）、DRY（全局清单单一入口）；无 TS 变更。独立 Git worktree；Python 仅 uv；没有 gh／tracker／push。

## Deviations
- 无。
