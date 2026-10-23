# #60 C07 兼容入口与历史来源 implementation notes

## 状态

| Work unit | 状态 | 产物与验收证据 | 下一步／阻塞 |
|---|---|---|---|
| W1：修复 C07 活文档映射并以安装后的 Research OS seam 验收 | done | 产品提交 `1bad19cde12b5fab8cdf5691ed584727773c4945`；`/tmp/spec48-contract-fix-D/REPORT.md`；red/green、回归及 checker 日志见报告所列 `/tmp/spec48-contract-fix-D/logs/` | C07 单元完成；#60 总体验收、merger 与独立复审留给 parent |

## 入口判定与边界

- 入口判定：这是用户明确限定为 C07 的单一文档合同修复 work unit，用户同时禁止继续派发，因此直接执行而不拆派。
- 仅修改 `skills/general/research-os/SKILL.md` 与 `docs/upstream-sources-and-licenses.md` 的 C07 相关段落；测试只补一个同属 C07 的安装后合同检查。本 notes 是本单元要求的因果记录；验收报告写到 `/tmp/spec48-contract-fix-D/REPORT.md`。
- findings 是自然语言合同矛盾，不是已复现的真实 agent 行为。保留 upstream 来源、revision、旧本地路径与方法沿革，但把旧入口和阶段审批标清为历史；现行路由以统一 `research-os` / `paper-writing` 入口、`discovery` 配方及其共置许可资源为准。
- 不写 integration 或主目录，不 push、不操作 tracker、不派发，不改历史 acceptance/archive 或其它 findings。

## 实施记录

### W1 / Red 前

- 已完整阅读指定 findings、41-skill coverage 与 #48 缓存 spec；C07 对应 ID9/17、TD4/5、AC1/2/3。保留上游来源可追溯性；不把旧 `idea-discovery` 阶段门或独立写作控制器承诺当作当前合同。
- 测试 seam：通过缓存 Skills CLI 在树外临时项目安装 `research-os`，检查安装后的入口是否只映射到现存统一写作入口和当前 `discovery` 配方；同时核对来源记录将旧路径限定为历史，并把当前配方、专业入口、许可证落点映射到真实文件。此检查应在当前文本上因旧承诺/历史描述而失败。

### W1 / 实施与验收

- 新增安装后合同检查先红：`/tmp/spec48-contract-fix-D/logs/c07-red.log`，exit 1；真实安装后的入口仍包含“旧专业入口作为兼容调用保留”。只修复两份指定文档中的 C07 语义；上游 revision、来源路径与历史方法保留，旧阶段审批明确标记为历史。
- 同一 seam 转绿：`c07-green.log` exit 0（1 passed、5 subtests）；完整 Discovery 与 paper-writing 相关回归分别 2 passed/30 subtests、3 passed，exit 0。
- 在本分支合并明确 `integration/spec-48` tip `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e` 后复验：Discovery 2 passed/30 subtests、paper-writing 3 passed，均 exit 0。合并结果 `Already up to date`。
- 静态 checker exit 1，仍仅报告既有 9 条 acceptance `.tar.gz` 缺失引用；未改归档。既有 6 条全套失败不在本次范围，未运行全套、未改相关 tests/archive。
- 全部命令串行，树外 `TMPDIR=/tmp` 且单条 180 秒上限。完整命令、实际返回码与证据限制写入 `/tmp/spec48-contract-fix-D/REPORT.md`。分支 `t3/c07-legacy-entry-compatibility`，worktree `/Users/rolex/.t3/worktrees/Research OS Studio/t3-06e37020`；候选 `f7b03400a4b77bc77265e9076199977815163a87` 已合并。本单元未触碰 integration/主目录、未 push/操作 tracker、未派发。

## Deviations

- （无）
