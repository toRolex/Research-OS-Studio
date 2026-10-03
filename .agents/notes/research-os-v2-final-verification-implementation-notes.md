# v2 final merge / verification（#37–#46）

## 范围与决定

- 本地 `integration/research-os-v2`：由 `70306a9` 对 `v2/review-fixes` tip `70d93dd561279ef92aa09ccb79cff024792feccf` 执行 `git merge --no-ff`，merge `a5f6b82`；无冲突，无待解决文件。未动 main、不删 worktree、不 push/tag/PR/关票。
- 完整读取 approved `/tmp/research-os-v2-notes/shared-contract-approved.md`、checker、回归测试、入口正文及各票 notes。notes 的历史状态不冒充当前状态。
- 首轮 UV checker：39 / U38 M1；tests 16 + scripts tests 41 = 57 全过；工作树及合并 diff --check 通过。

## 独立复核

- 门解析共享 gate_problems：none 混门、重复 none、格式错仍报错；当前 skill SKILL.md/references 的 resolve 边界拒绝跨 skill、symlink 逃逸。默认仓库扫描要求追踪来源；外部合同保持独立。
- 异构 compute 按原字段位置逐单位比较、重复单位与字段数量配对拒绝，CPU/GPU 不互相抵扣；NaN 拒绝、恰好上限允许。
- 默认入口扫描全部追踪 skills Markdown 的 Role 引用；回归含 playbook 与模板 ghostwriter。
- 入口已要求逐字 todolist、逐步状态、读叶全文、编排者自己核实产物/依据/读取覆盖，不把同上下文核实写成 fresh review。21 处叶正文 model-invoked 旧描述已修；仍存在的 composition / 产品地图 U/M 历史术语不在本轮扩大改写。
- 完整读取原 `codex-route.jsonl` 与 `pi-serial.jsonl`：Codex reasoning 确实 route-only，experiment-plan 是推荐不是执行；仍未读推荐叶且“论文骨架”无依据。pi 承认缺叶路径而停止。release 文档纠正合理，没有把这些格翻成通过。

## 小修与红绿

- 独立复核发现扁平布局的安装根推导少一层：SKILL.md 路径的父级是 research-os skill 目录，不是包含各 skill 的安装根。先在既有回归增加明确层级断言：7 项中 1 红。保守改成“当前入口 SKILL.md 所在 skill 目录的父级”，仍以实际文件核实，不猜测已读。这不是 Seam B 重跑。

## 最终静态验证

小修后再次执行：`uv run python scripts/check-skills.py` OK（39 / U38 M1）；`uv run python -m unittest discover -s tests -v` 16/16；`uv run python -m unittest discover -s scripts -p 'test*.py' -v` 41/41。两轮完整验证均 57/57。`git diff --check` 与 `git diff 70306a9..HEAD --check` 通过；主动 LSP 检查 `scripts/check-skills.py` / `tests/test_review_fixes.py`，2 clean、0 diagnostics。

## 真实阻碍（全部保持）

- #37：完整路线/材料边界、粘性/new task、逐字 todolist、编排者核实、三宿主显式/级联/串行行为尚无当前集成 tip 完整证据。
- #38：route-only 三宿主完整叶核实及零副作用仍待重跑；Codex 推荐不等于错误执行，但不满足全部合同。
- #39：未点名不触发、直接点名、级联叶审批真实停点未汇总成当前可复核矩阵。
- #40：真实可用模型逐角色确认、新建/幂等/冲突/不可用模型停点、全局角色表及既有日志快照未在当前 tip 重跑。
- #41：arXiv 两次 SSL_ERROR_SYSCALL；方向到候选/查新/独立评审/Proposal、粘性与 new task 未走通。
- #42：历史十场景仅低消耗授权门；非叶全阶段科研交付，未在当前 tip 重跑。
- #43：通用/ML/systems 三份真实材料的候选稿+审查报告、外发硬门证据仍缺。
- #44：历史 toy 轨迹不是三份真实材料当前验收；rebuttal bash 写工作材料不能证明叶写入门；paper-talk 自检非独立 reviewer；未做 Beamer/PPTX。
- #45：仅历史 pickup 过期/unknown 零写入；有效授权成功恢复、真实 proof 固定命题及独立 review、improvement 有界循环仍缺。
- #46：完整跨票矩阵、当前三宿主直接/级联、串行读完叶、前票证据可访问归档不足。不打 v2.0.0。
- 原始轨迹仍只在本机 /tmp，GitHub 评论仅提供相对仓库路径+本地 commit，不冒充可访问 GitHub 证据；未 push 是明确交付限制。

## GitHub 与清理

- 已先加载 rate-limit skill/preflight。读取 #37–#46 用单次 GraphQL（需合并 10 端点），cost 1，remaining 4999；全部 OPEN。后续评论选 gh api REST comments endpoint 顺序写，每票只一次；单票数据有 REST endpoint，10 次 POST 消耗可计，不需要 gh issue comment 的额外 issue node 查询。失败即报告停止不无限重试。
- worktree/分支与外部 /tmp 原始证据仍保留；代码提交后可清理测试缓存，但未 push 的唯一提交及未归档行为证据不宜清除。没有执行清理。
