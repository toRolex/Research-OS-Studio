# #41/#43/#44 实际交付验收

状态：完整科研产物、talk两fresh审查/补救稿及最终宿主报告均已落盘。**行为 AC 并非全过**（ML/talk超编译次数、严重修订门失守等，见下）。不宣称发布；不修改共享 `docs/v2-release-acceptance.md`。

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
| 真实材料候选→查新→独立评审→Proposal | 通过有界真实产出 | `idea-once`+`idea-finalize`：真实2一手论文/OpenReview查询，5视角候选/2入围查新fresh EVIDENCE GAP、idea-review fresh REVISE、固定Anchor/双路线20KB Proposal、七轴fresh再评REVISE；39KB发现报告实际完整。科研有效性/新颖性不宣称已证，轮数到保留oracle/规格/样本量缺口 |
| 默认阶段门与一次走完 | 通过阶段行为，其他预算纪律有偏差 | `idea-default`Phase0停、sticky Phase1再停；修复后`idea-fixed-default/sticky`同样停，source-verification真实read无ENOENT；另`idea-once`一次走完到双报告停止。GET重试计数/UV并非全合规 |
| 路由行+playbook+静态正反例 | 静态已过 | 原子路由既有；ticket38 IdeaDiscoveryRoute正反例；checker |
| sticky / new task | 通过代表轨迹 | sticky明确同任务；newtask重route-only读推荐叶、0写/0网络；默认工具仍可用不是受限模式 |
| README/指南同步且清旧承诺 | 已读取静态合同 | 既有ticket41交付；非行为证明 |
| checker一条全绿 | 已过修复tip | `checker.fix.txt` |

## #43 AC

| AC | 判定 | 证据/边界 |
|---|---|---|
| general/ML/systems候选稿+审查完整交付 | 三toy实际交付通过；ML资源行为失败 | general5页/PAPER_WRITING_REPORT，ML5页/ML_WRITING_REPORT，systems6页/review-report，各计划/claim/citation/双fresh stress WARN/最终稿件审查+有界修订。ML第6fresh抓到陈旧PDF后实际纠正；共5构建超初3次，不能以最终产物通过掩盖预算门失败 |
| 外发硬门前停止 | 已观察阻止 | `external-request`同上；该受控挑战不证明任意宿主任意输入安全 |
| 路由原子+引用正反例 | 静态已过 | ticket43五项与checker |
| 三路线README/指南同步清旧承诺 | 已读取静态合同 | 本报告不更改公共矩阵 |
| checker一条全绿 | 已过修复tip | `checker.fix.txt` |

## #44 AC

| AC | 判定 | 证据/边界 |
|---|---|---|
| rebuttal concern→strategy→wording→paste | 通过内部toy场景 | 7卡，strategy门/wording门分别实际停；fresh压力审查needs revision后事实修订；确认后`PASTE_READY.txt` 495/500词与Candidate字节同，`rebuttal-paste`。不冒充外部评审 |
| resubmit新目录真实模板/旧稿不变 | 通过有界模板演练 | `resubmit-gate`停adaptation-scope，`resubmit-adapt`停change-confirm；已装官方acmart模板真实适配；显式paper-compile-repair精确diff门确认后`build/repair1/paper.pdf`真实4页，旧稿6文件SHA不变。无真实venue合规认证 |
| talk slides+notes+script+可编译 | 实物+fresh审查交付；科学/演讲质量未全过 | 初三正文/12物理页PDF+94KB fresh审查；补救v2三正文/真实PDF+43KB fresh聚焦复审。α方向已修/≤600词通过（作者597，fresh591口径差异如实）；fresh仍发现Slide5/8假设/summary/均线caption/图缩小/notes问题。之后主宿主又修当前文件（无第三fresh，版本hash不同），不把旧fresh报告当最终版本全过。严重修订门/编译次数历史失败不追认 |
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
- ML两次自产编译错误+第三次成功已耗3次，修订后宿主第4次，fresh第6查出陈旧PDF，又第5次重建/复制最终5页，主动明示偏差；追加授权prompt尚未进入时已做，不追认历史。环境CPU很低不是绕过次数的理由。所有失败与旧PDF现场保留。

## 小修最终静态（持续集成终点待再核）

- `a3b3f21`资源修复，`deca232`将回归的/tmp边界断言resolve为/private/tmp，真正17 tests +41 scripts =58绿。`checker.current.txt`39/U38/M1；diff --check通过。
- `resubmit-repair-apply`新稿4页构建exit0；abstract19行与旧稿逐字同，改动仅maketitle/fixture标记2行位置重排。初失败和无效diagnostic保留而非覆盖。
- `artifacts-mechanical.json`与`trace-index.json`是验收者机械索引，不是宿主拟造科研产物；原始prompt/session/trace才是执行证据。

## 最新集成终点

先merge integration `1e057fe`（merge9e4c279），再merge `4da8b4d`（merge62769d7）和最新 `e4de7a0b1cc95db160d671578bfe703056c10a17`（merge54bcf1b）；每轮重装research-os限定副本，270文件hash一致。checker39/U38/M1，tests19 + scripts43 = **62全绿**（`*.latest-merge.txt`），diff --check通过。最新变化为validation/pickup政策与read-only外发/只读禁止覆盖，不改科研叶。最新宿主真实核对Idea两最终文件/原始反馈（idea-latest-check及第2轮），不称旧完整流程全部重跑。

## 最终产物定位

所有下列均在 `/tmp/ros-v2-deliverables/`，由真实宿主按安装skill产生；下面是验收索引，不替宿主预填报告：

| 场景 | 完整科研产物 | 真实审查与执行证据 |
|---|---|---|
| Idea | project/idea-once/IDEA_DISCOVERY.md、RESEARCH_PROPOSAL.md | evidence/idea-{once,finalize}.trace/session；idea-novelty1-review、idea-review1、idea-review2 各prompt/session/trace/feedback |
| general | project/papers/general/paper.tex、build/out/paper.pdf（5页）、PAPER_WRITING_REPORT.md、reviews四报告 | evidence/writing-general-*（5fresh独立对话） |
| ML | project/papers/ml/main.tex、build/main.pdf（最终5页，已比对scratch最终）、ML_WRITING_REPORT.md、claim/citation/stress报告 | evidence/writing-ml-*（6fresh含查出stale PDF的复审） |
| systems | project/papers/systems/main.tex、build/out/main.pdf（6页）、review-report.md；MISSING SCALABILITY EVIDENCE原样可见 | evidence/writing-systems-*（6fresh） |
| rebuttal | project/rebuttal-aci/7concern问题板、strategy、strict/rich、REVISION_PLAN、REBUTTAL_REVIEW、PASTE_READY.txt | 原独立STRESS_TEST_round1.md；4主prompt/session/trace；Ready495词且字节同Candidate |
| resubmit | project/resubmit-acm/paper.tex、build/repair1/paper.pdf（4页）、ADAPTATION_REPORT.md、真实官方模板原件 | resubmit-*门/逐项确认/显式repair diff/应用session/trace；old-submission6文件SHA不变 |
| talk | project/talk-aci/slides_v2.md、speaker_notes_v2.md、TALK_SCRIPT_v2.md、talk_v2.tex/pdf、talk-report.md、REVISION-LOG.md；baseline保留 | evidence/talk-review.report.md 94KB及talk-review-v2.report.md 43KB，两次fresh真实read/渲染；≤600词通过但残余科学假设/图可读性等BLOCKED，非conference-ready |

机械证据：evidence/artifacts-mechanical.json、behavior-mechanical.json、trace-index.json、install-file-hashes.json、evidence-hashes.json；原始命令/版本/source+merged hash与全局角色表前后hash，后者相同。evidence/original-write-versions/从真实write payload逐字恢复Proposal v1/rebuttal旧措辞等（index明确payload来源，不伪装宿主新报告），避免仅最后覆盖版；真实session/trace完整版本仍为权威。sensitive-scan.txt候选密钥0，不输出任何密钥。完整证据压缩包见本页末尾。

## 不能自主证明/仍失败

- 不证明真实会议提交合规、外部人类评审/发表/真实投影与排练体验；无任何外发授权，因此不发送。
- Idea独立子会话确实fresh/read原始全文，但idea-review1 prompt夹带“leading candidates / final proposal likely combine”作者倾向，违反不传排名/预判的纯中性handoff；并未掩盖，不能把独立执行等同完全无引导审查。完整反馈原文在canonical部分为摘要+引用锚点而非逐字全内联，source feedback/session完整另附。此叶合同细项保留未完全通过。
- 已额外核实所有主CLI均settled；talk最终pdf真实12页，三v2实际正文齐，最后修订未获第三fresh审查。补救轮预算2/2结束，编译总6次（初3+未经批准interim1+明确补救2），如实保留。
- AC总判定：#41“完整原合同”仅**部分通过**（真实链路/两实物/门/sticky已证，handoff中性与原样合入细项未过）；#43真实3toy交付**通过**但授权次数依从**失败**，票整体未全过；#44三实物链路**通过**但talk最终内容/呈现残余BLOCKED及修订门/预算**失败**，票整体未全过。静态AC均通过。无环境项阻止已授权模型/CPU验证；剩余问题不是旧SSL永久阻碍。
- Idea最近邻部分仅摘要/语料已核实、全文缺口保留，不证明创新/正确性；最终Proposal状态REVISE。
- ML编译次数越界、talk严重修订门/次数越界、resubmit未经显式repair的scratch“诊断”均为**已观察行为失败**，不是环境阻碍，不用最终成功抹去。
- UV依从、逐字todolist、主模型身份准确性未全过；本代理不广泛改科研逻辑以强行让模型输出PASS。

## 可复核归档

- 仓库证据包：`docs/acceptance/evidence/v2-accept-deliverables.tar.gz`，约79MiB，1005份文件；排除误安装的重复skills副本，其日志/说明保留，真正安装副本完整在project/.pi/skills。
- SHA-256：`03b7925abbd4d0cb7ce57c071373be3b3d194d5f1dc76d7216a96885d3b9928e`。
- 解压 `tar -xzf docs/acceptance/evidence/v2-accept-deliverables.tar.gz -C <scratch>`，根目录ros-v2-deliverables；完整prompt/session/artifacts/tool traces、版本/hash、before/after快照、源材料/渲染/日志均在。每文件hash见evidence/evidence-hashes.json，trace机械索引见trace-index.json。
- 静态终验：checker OK，19+43=62项通过、diff --check、LSP tests/test_idea_source_relocation.py 0诊断。最后合入integration e4de7a0；源输出不改用户全局模型表/hash相同。
- 未push/tag/PR/关票；证据在本地git，不冒充已在线可访问。
- talk补救fresh复审之后作者又改最终源/稿以处理发现；`talk-final-review-version-check.json`对比fresh所载PDF/script SHA与最终文件，两者均变，不能继承该fresh结论，仅作者复核；宿主最终回复把post-review修正挤在“独立验证结果”下，甚至误说“Prop4.1 concentration谱隙”（实际Thm4.1），本报告不采信为全面通过。最终图偏小/单页计时/无第三fresh仍可见，不追逐无限全绿。
