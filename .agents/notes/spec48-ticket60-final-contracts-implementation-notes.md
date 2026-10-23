# #60 C02/C04 final-contract seams — implementation notes

## 状态

| work unit | 状态 | 产物与验收证据 | 下一步 / 阻塞 |
|---|---|---|---|
| C02：proof-repair → proof-review 授权级联与真实 fresh reviewer | done | 安装后 RED→GREEN：`c02-red.log` rc=1 命中仅 `user-invoked` 拒绝；`c02-green-final.log` rc=0；后续 `postmerge-final-contract.log` 2 tests rc=0 | 此 unit 不代表 #60 全票最终验收；交 parent 继续 merger/独立复审 |
| C04：独立第二意见的授权继承与额度内有界重试 | done | 安装后 RED→GREEN：`c04-red.log` rc=1 命中每轮用户点名旧句；`c04-green-final.log` rc=0；后续 `postmerge-final-contract.log` 2 tests rc=0，保留 fresh/材料/身份/外发/费用/fallback 门 | 此 unit 不代表 #60 全票最终验收；交 parent 继续 merger/独立复审 |
| 报告、notes commit、integration-tip 自分支复验 | 进行中 | 产品 commit `fd87f0b6fdc1023b2e0b272e3205e8d7428f378a`；合入 `integration/spec-48` tip `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e` 时为 Already up to date；后合入回归：final contracts 2/2、contract-M 4/4 | 写精确报告与 diff/日志哈希；单独 force-add 本 notes 至忽略目录并提交 |

## 入口判定与边界

入口判定：直接执行，不拆分派发；用户已指定 C02/C04、文件范围、测试 seam 和禁止继续派发，所需 findings/spec 已提供。

先将候选 `f7b03400a4b77bc77265e9076199977815163a87` 合入当前隔离分支；当前 worktree 为 `t3/fix-review-contract-seams`，不改 integration 或主目录。输入 `/tmp/spec48-ticket60-final-contracts/FINDINGS.md` 明确是合同矛盾，不是实际 agent 行为复现；C01/C03/C05–C07 不属于本 work unit。

预先约定的 TDD public seam：用真实 Skills CLI 在树外临时项目安装 `proof-repair` 与 `proof-review`，检查安装后两份资源合同是否与 repair Skill 的委托继承正文一致；测试只断言可读合同闭合，不宣称运行时已被证明。测试串行执行，每条命令 `<=180s`、`TMPDIR` 在 worktree 外；保留原始 red/green/回归日志及真实退出码。新增 fixture 使用仓库跟踪的测试代码，不复制 ignored 文件。

## 决策

- C02 修复必须区分 standalone 未授权范围与有效父委托内的正文级联。`disable-model-invocation` / `user-invoked` metadata 本身不否定合同允许的级联；但存在、实际宿主可调用 proof-review、真实 fresh 独立上下文、原始材料完整可读仍是能力条件，任一缺失则 blocked，不以自查代替。
- C04 只继承明确覆盖第二意见/路线/额度的委托；有效范围内、同一已授权路线的本地有界重试沿用总额度，不重复请求。保留可信 provider/model 身份核验、未知 fallback 禁止、未授权外发和收费停止门，以及不盲目重发可能已执行调用的规则。
- 叶 Skill 返回本身不要求调用者再次向用户索取点名；调用者继续与否按仍有效的父委托判断。修改只限两份指定 reference 与必要测试。

## 执行记录

- 按 `docs/adr/0005-pure-agent-skills-product.md`、`GLOSSARY.md`：Internal Skill 可由 Workflow 在当前研究委托内调用；`disable-model-invocation: true` 禁止按 description 自动触发，但不禁止用户点名或 Playbook 正文级联。RED 使用真实 Skills CLI 1.7.4 安装后的 `proof-repair` 包，非源码树断言。
- C02 首次 GREEN 前有两次测试断言词组过窄的失败（分别期待“有效父委托”“正文级联”，而实现语义已表达为“有效委托内级联”）；不改产品语义，只把断言改为该合同分支的原文语义。保留这些尝试日志，不将其记为行为 RED。
- C04 RED 使用真实 Skills CLI 安装的 `proof-review` 包，失败明确定位旧的每轮用户请求门；随后修改该 reference 的授权、重试与完整响应核验表述。
- C04 同步了 `independent-review.md` 中的失败后处理和完整响应验证两处旧的“不重试”正文，避免新首句授权继承但同文仍禁止额度内重试。未知身份、路线改变、超限费用/外发、额度耗尽及可能仍在执行的超时仍停止或等待用户决定。
- 首轮 `test_spec48_ticket60_contract_M` 回归发现其旧迁移校验要求所有历史 proof-review references 字节级不变；C04 有意修改 `independent-review.md` 后该单项失败（其他 3 项通过）。将该文件从历史字节等同例外改为验证新合同片段，其他资源仍保持 hash 等同；证据见 `/tmp/spec48-contract-fix-B/logs/ticket60-contract-M-regression.log`，rc=1，待复验。
- 最终串行验证（每条使用树外 `TMPDIR=/tmp/spec48-contract-fix-B/tmp` 和 uv，单测命令均低于 180 秒）：安装后 C02/C04 2/2、ticket60 contract-M 4/4、`git diff --check` 均通过；Skills checker rc=1 且仅报已知 9 条 acceptance archive 目标缺失诊断，与既有记录一致，未修改归档。既有 6 个历史失败未运行、未改写。
- 开发工作树 `/Users/rolex/.t3/worktrees/Research OS Studio/t3-177f5d04`，分支 `t3/fix-review-contract-seams`。候选 f7 与当前 integration tip `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e` 已合并/为祖先；交付前再次在本分支 merge `integration/spec-48`，结果 Already up to date，并在其后完成上述复验。产品只提交到本分支；未写 integration/main、未 push、未操作 tracker、未派发。
- 偏离：首轮 pre-fix RED 与紧随的 GREEN 尝试用 `python3` 直接执行而非 `uv`；最终串行 GREEN/回归均改用 `uv run --no-project python -m unittest`。初始 RED 日志保留原状，最终 GREEN 及回归另有 uv 日志。

### Deviations

- 暂无。
