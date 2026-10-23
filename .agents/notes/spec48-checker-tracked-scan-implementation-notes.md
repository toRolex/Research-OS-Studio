# Checker tracked Markdown 扫描边界

## 状态
- 定位与 TDD：done；`logs/red.stdout` rc=1 明确在进入小 fixture `.pi` 前失败；`logs/green.stdout` rc=0。
- 最小修复：done；只改全局 Markdown 清单，不改 copier、忽略集、历史红灯或其他票目录；`checker-green` rc=1、原九条 stdout 原始字节 cmp=0。
- 串行验收／integration 同步／交接：进行中；先提交形成 clean worktree，再跑新反例、214 联合、全套、原九条 checker 精确比较；每命令 ≤180 秒。

## 边界与决策
- 指定 implementation worker，用户禁止继续派发，直接执行；已读全局 Multi-Agent/model-availability/CODING_STANDARDS、pre-implement、指定 TDD 三文件、GLOSSARY 与 ADR-0005；Python 仅 uv。
- 已批准 seam：checker 执行与文件系统扫描边界。小型 fixture 的 scandir 哨兵验证不进入 ignored 树，同时验证 tracked 内容与损坏链接；不遍历或复制真实 ignored 大树。
- 原全局 `ROOT.rglob("*.md")` 在 tracked 判断前遍历整树。`skill_dir.rglob` 仅在指定 experiment skills 内部，没有仓库根 `.pi/.agents` 的同类泄漏证据，不扩大修复。
- 原清单未作字典序排序；必须保留本机原遍历顺序，而不是用 sorted(tracked) 改变九条历史诊断顺序。不得以本轮修复解释原 timeout 全部耗时。
- 由既有 tracked 集合生成候选及祖先集合；只浅读这些祖先的目录项，维持原目录枚举／栈遍历顺序。ignored 目录自身名字可在祖先目录项中出现，但不进入其内容；tracked `.agents/notes` 仍须访问。缺失 tracked Markdown 自然不在目录项中，和旧行为相同；保留 symlink 目录不递归与原链接／元数据诊断。
- 小 fixture 同时覆盖 ignored `.pi` 与 `.agents/evidence` 哨兵、force-tracked ignored notes、tracked 缺失文件、损坏／越界／存在但 untracked 目标、原元数据错误和本机原诊断排序。Python 3.14.4 实测，不承诺其他 Python 版本未文档化的 rglob 顺序一致。

## Deviations
- 无。
