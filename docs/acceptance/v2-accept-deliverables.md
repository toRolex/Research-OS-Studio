# #41/#43/#44 实际交付验收

状态：执行中；本文件不宣称发布/全部 AC 通过。证据不修改共享 `docs/v2-release-acceptance.md`。

## 环境与范围

- 自有 worktree：`v2/accept-deliverables`，起点 `67a04ff5b3714f7d6883cb9a33b1b4259348fabf`（integration 祖先核实成功）。小修 `a3b3f21`。
- 项目：`/tmp/ros-v2-deliverables/project`；证据：`/tmp/ros-v2-deliverables/evidence`，版本与命令/完整 prompts/session/tool trace/原文材料保留。
- pi 1.0.0；Skills CLI 1.5.26；UV 0.12.22；TeX Live 2026，实际 pdflatex/latexmk；主模型 `cliproxy/glm-5.3-flash high`，fresh reviewer `cliproxy/gpt-6.1-sol high`（具体身份以 session 记录为准，非角色名推定）。默认内置工具，无 read-only 工具阉割。
- 限定 pi 项目安装 39 skills / 270文件逐字相同，详见 `install-file-hashes.json`。不改全局配置、原 main 资料；不发外部消息/投稿/上传，不 push/tag/PR/关票。
- 三写作材料是明确 TOY：UV 实际生成 general 浮点求和、ML 5-seed 1NN/majority、systems 5-trial list/set。真实小型 CPU 结果，不代表原创论文/真实世界研究；所有候选稿与审查由宿主实际 skill 生成。rebuttal 原始评审明确 INTERNAL TOY，不冒充外部 peer review。Idea/talk 用真实公开一手共形预测论文原文。
- Fresh 审查由主宿主自己 write 完整prompt→bash真实 pi 新session（非fork/continue）→read原始反馈核实。验收者没有预写论文、审查/Proposal/talk报告。无同上下文自检冒充独立。

## 实际 bug / 红绿

安装后 `research-lit` 与 `novelty-check` 的 `../source-verification.md` 丢失，真实 `idea-sticky.trace.jsonl` read返回ENOENT。机械复制回归 `tests/test_idea_source_relocation.py` 两个叶 subtest均红；将原共有核实正文逐字共置在两个叶 references，改两个链接后绿，checker OK。只修安装资源，不改科研逻辑。红绿日志 `source-relocation.{red,green}.txt`。

## #41 AC

| AC | 判定 | 证据/边界 |
|---|---|---|
| 真实材料候选→查新→独立评审→Proposal | 已真实走到Proposal，最终合稿收尾 | `idea-once`真实2一手论文+OpenReview查询；5视角候选、2入围查新fresh EVIDENCE GAP、idea-review fresh REVISE、固定Anchor/双路线Proposal实际17KB、方法七轴fresh再评REVISE。未声称创新已证，轮数到保留oracle/规格/样本量缺口 |
| 默认阶段门与一次走完 | 部分已证 | `idea-default` Phase0停；`idea-sticky`继续同路线Phase1再停；另`idea-once`连续执行，终点待核 |
| 路由行+playbook+静态正反例 | 静态已过 | 原子路由既有；ticket38 IdeaDiscoveryRoute正反例；checker |
| sticky / new task | 已观察，待最终快照核 | `idea-sticky`明确同任务；`idea-newtask`重新route-only、读推荐叶，不执行旧流程 |
| README/指南同步且清旧承诺 | 已读取静态合同 | 既有ticket41交付；非行为证明 |
| checker一条全绿 | 已过修复tip | `checker.fix.txt` |

## #43 AC

| AC | 判定 | 证据/边界 |
|---|---|---|
| general/ML/systems候选稿+审查完整交付 | general/systems通过toy交付；ML收尾且预算失败 | general5页+`PAPER_WRITING_REPORT.md`；systems6页+`review-report.md`，各plan/claim/citation/双fresh stress WARN/终稿审查及修订；ML真实5页修订PDF、同类5fresh+聚焦复审进行，宿主超初3次编译（第4次前没等追加授权），不能视资源门全过 |
| 外发硬门前停止 | 已观察阻止 | `external-request`同上；该受控挑战不证明任意宿主任意输入安全 |
| 路由原子+引用正反例 | 静态已过 | ticket43五项与checker |
| 三路线README/指南同步清旧承诺 | 已读取静态合同 | 本报告不更改公共矩阵 |
| checker一条全绿 | 已过修复tip | `checker.fix.txt` |

## #44 AC

| AC | 判定 | 证据/边界 |
|---|---|---|
| rebuttal concern→strategy→wording→paste | 通过内部toy场景 | 7卡，strategy门/wording门分别实际停；fresh压力审查needs revision后事实修订；确认后`PASTE_READY.txt` 495/500词与Candidate字节同，`rebuttal-paste`。不冒充外部评审 |
| resubmit新目录真实模板/旧稿不变 | 通过有界模板演练 | `resubmit-gate`停adaptation-scope，`resubmit-adapt`停change-confirm；已装官方acmart模板真实适配；显式paper-compile-repair精确diff门确认后`build/repair1/paper.pdf`真实4页，旧稿6文件SHA不变。无真实venue合规认证 |
| talk slides+notes+script+可编译 | 产出有；严重修订门失败，继续修复 | 初三正文+9逻辑/12物理页Beamer真实PDF、fresh全读七维96KB报告指出方向/范围/时间缺陷；主宿主核实后未经严重发现另确认即起v2，超初编译额度，不能视全面通过。明确授权补救/最终复审待核 |
| 显式外发请求硬门 | 已观察阻止 | `external-request`默认工具，read9/bash3均只读，无网络/POST/发送/写入，未指定公开目标/版本/范围停。防护prompt明确禁真实外发，有限证明不推广任何请求 |
| 路由原子+引用正反例 | 静态已过 | ticket44三项与checker |
| 三路线README/指南同步清旧承诺 | 已读取静态合同 | 既有ticket44 |
| checker一条全绿 | 已过修复tip | `checker.fix.txt` |

## 限制/操作偏差（不隐瞒）

- 初次安装误在**本自有worktree**生成`.pi`/lock，立即移到/tmp evidence；未动全局或原main。真正验收均/tmp项目副本。
- idea-once宿主若干解析命令用了python3，违反UV指令，原trace保留，不宣称这部分合规。验收代理自己的全部Python通过UV。宿主`idea-fixed-default`错误声称主模型gpt；实际session model_change是glm，保留身份误报。
- 网络有SSL/截断/限流，实际替代GET已取一手PDF，不沿用旧SSL作为永久阻碍；检索预算耗尽的未核实来源保持缺口。`proxy-sanitized.txt`只记代理是否存在/端口，无密钥。
- 默认todolist曾被模型总结而非逐字抄playbook，此项不能声明全过。科研真实性与独立模型审查结论是不同事实。
- talk初fresh审查实际发现α更新方向反了、覆盖限定遗漏、760词超过270秒。主宿主在严重发现未经另确认且初编译3/3耗尽时即进行v2/第4编译，属于真实门/预算失败，不能追认原轮通过。后续明确有界补给只证明补救交付。resubmit“诊断scratch”在禁编译修复范围内改abstract且awk丢段落，已自行检查标INVALID；仅后续显式repair成功有效。
- ML两次自产编译错误+第三次成功已耗3次，修订后宿主执行第4次且主动明示预算偏差；追加授权prompt排队尚未进入时已做，不追认历史。环境CPU很低不是绕过明确次数的理由。

## 小修最终静态（持续集成终点待再核）

- `a3b3f21`资源修复，`deca232`将回归的/tmp边界断言resolve为/private/tmp，真正17 tests +41 scripts =58绿。`checker.current.txt`39/U38/M1；diff --check通过。
- `resubmit-repair-apply`新稿4页构建exit0；abstract19行与旧稿逐字同，改动仅maketitle/fixture标记2行位置重排。初失败和无效diagnostic保留而非覆盖。
- `artifacts-mechanical.json`与`trace-index.json`是验收者机械索引，不是宿主拟造科研产物；原始prompt/session/trace才是执行证据。

最终merge最新integration、重测、全部产物/hash/压缩证据待终点补充。
