# v2 accept deliverables (#41/#43/#44)

## 基线/批准 seam

- 自有 worktree `v2/accept-deliverables`，HEAD `67a04ff`；已确认 integration 基线为祖先；用户要求交付前 merge 最新 integration 并重测。
- 已读取共享批准合同、release 验收、用户指南、#37/#41/#43/#44 GitHub正文与评论及相关票 notes。
- 已调用 pre-implement、github-api-rate-limits；tdd 工具不可用，完整读取 `/Users/rolex/.agents/skills/tdd/SKILL.md`。沿用已批准 Seam A checker、Seam B 真 CLI/tool trace+机械快照；正文 bug 若发现，先红再修。无 mock/合成工具输出。

## 决策

- 仅 /tmp 项目限定安装当前 tip；pi 默认内置工具，禁扩展/全局上下文以免污染全局环境。skill 从安装副本实际全文读取。
- 生成研究材料允许明确标注 toy 的极小 CPU 数据，但验收报告、论文稿、独立审查、Proposal、rebuttal/talk 均必须由宿主执行 skill 产生。
- fresh 审查由真实主宿主自己用 bash 启动新 pi --session，独立上下文读取原始输入；不让验收代理先写审查。
- 不 push/tag/PR/关票，不修改共享 release 矩阵、不修改原 main 用户资料。报告独立 `docs/acceptance/v2-accept-deliverables.md`。
- GitHub 4票合并为一次 GraphQL（cost 1，remaining 4996），因为需合并四端点+评论；只读。

## 过程

- Phase0 default真实trace停stage-checkpoint，零研究材料写入；JMLR/arXiv页面GET核实成功。一次走完另外新session；JMLR/arXiv真实PDF已下载/提取，部分NeurIPS SSL失败但合理替代一手来源继续，不视永久阻碍。
- 默认sticky续接research-lit真实read暴露安装路径bug：`../source-verification.md`仅仓库category共有、flat副本不存在；宿主如实记录ENOENT。先写Seam B mechanical flat-copy回归，research-lit/novelty-check两subtest红（evidence/source-relocation.red.txt）。只把原共用正文逐字复制到两个skill references，并改两个链接；绿及checker OK。不改科研逻辑，保留仓库共有文件兼容旧外部链接。
- 默认工具三writing门实测已停且未写；批准后后台真实CLI继续，toy原始fixture stdlib通过UV实际执行，输入不可写。
- fresh方法/专项审查要求由主宿主write prompt及新pi session，不由验收代理生成。
- 三写作完整稿均真实生成编译：general 4页、ML 4页、systems 5页；PGFPlots/TikZ现有工具替代缺失matplotlib，无安装。计划与claim/citation已fresh审查，真正独立attack→judge继续，原始反馈可几十KB，耗时不能用自审替代。
- rebuttal真实ACI论文+内部toy concern 7卡；真实strategy门→批准→strict/rich→fresh压力反馈 needs revision，主宿主核实并修coverage/miscoverage、非嵌套定理假设/窗口等；wording门再次停→确认后495词粘贴版与Candidate字节相同，不外发。
- talk真实ACI三材料+9逻辑页/12物理页Beamer已编译，3次构建预算到顶，fresh七维审查继续；不得用编译成功称内容安全。
- resubmit冻结宿主真实general候选6文件为old-submission，只读SHA基线；现有官方acmart.cls及官方GET README，raw样例失败按已装官方sample回退，新稿真实编译报abstract顺序错误。宿主偷偷在scratch“诊断”改源码且awk丢abstract，随后自己核实纠正并标无效PDF，原2次额度已用；后续单独显式paper-compile-repair精确diff门+新增1次CPU构建授权，不能把scratch成功当新稿成功。过程失误与预算保留。
- 首次flat复制回归绿日志其实第二断言因mac /tmp→/private/tmp未resolve仍红；完整复测暴露后修`leaf.resolve()`，真正17+41全绿。保留红/原失败日志不抹去。
- Idea真实查新多来源尚有全文缺口→fresh查新EVIDENCE GAP/idea review REVISE/七轴refinement REVISE，39KB发现报告+20KBProposal真实交付且Anchor不变，未启动实验。主host tool history与三独立session完整保留。
- ML主宿主超过初3编译到5，fresh复审抓旧PDF（scratch新PDF没拷贝），真实修复最终5页但不追认历史预算通过。general5页/systems6页完整稿+全部fresh报告均交付。
- talk首次fresh审查真实揭露数学方向反、理论scope/计时等，主宿主未经严重发现另确认即v2/第4编译，属门失败。随后本代理明确有界批准600词/新增≤2编译/1fresh聚焦复审，主宿主597词约247s+23s停顿+30s缓冲；旧v2亦在evidence归档避免被删除，原baseline保留。最终fresh复审43KB已实际返回：α方向已修/≤600词通过/source可见，但假设限定、summary、均线caption、图缩小回归和notes差异未净。作者随后在剩1次编译内处理文字并采用trial最终PDF，无第三fresh；验收version-check明示最终PDF/script hash均与fresh所审版本不同，不继承旧审查全过。图偏小保留未解决，无真人排练/投影证据。
- 已先后merge integration1e057fe/4da8b4d/e4de7a0，最新54bcf1b；当前checker39/U38/M1、tests19/scripts43共62真绿；安装270文件hash一致。每次merge后都重测，latest真实宿主核对Idea最终文件原反馈（两轮），不冒称未变旧科研全过程全重跑。最终active LSP新回归1文件0诊断；62静态全绿；全局pstack hash不变。证据敏感扫描候选0，原完整trace/session版本仍在，从真实write payload逐字恢复首版Proposal/strict文本至evidence/original-write-versions，明确是恢复非宿主重新生成。

## Deviations

- 第一条skills安装命令误在本自有worktree执行，生成`.pi/skills`与skills-lock.json（未触碰全局或原main）。立即移到/tmp evidence保留记录，工作树零安装残留；实际代表测试全部使用/tmp限定副本。这是验收操作偏差不是产品行为。
- 宿主idea-once的少量材料解析用了python3（违反UV要求），工具轨迹原样保留，不假装合规；后续明确加强并复测。
