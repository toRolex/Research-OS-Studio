# 15 个用户 workflow

名称来自实际 `core/catalog.json`，不是愿景列表。所有 workflow 用户显式发起，读指定 pinned input，输出 candidate／报告／零到多个建议，然后停止。建议不是授权。当前实现接收固定 candidate 数据，不承诺自动完成文献检索、研究评审或创新判断。

| workflow | 输入与行为 | 输出／确认边界 |
|---|---|---|
| `setup-research-os` | 已验证安装资源＋项目目录 | 项目设置和投影；不启动研究 |
| `research-charter` | typed research-question、边界、成功标准、预算、不变量 | candidate charter；不改用户条件 |
| `research-literature` | pinned charter 与用户已有固定 citations | literature-review；当前不搜索，queries 为空 |
| `research-gap` | pinned literature-review | 有／无证据 gap；缺证据必须 unsupported |
| `research-idea` | pinned gap；多个候选时用户明确 selection | ideas／assumptions／tests；不宣称 novelty |
| `research-novelty` | pinned idea＋literature | bounded comparison；当前 verdict 为 inconclusive |
| `research-reflect` | 用户选择的外循环 Artifact | 保留 failures／uncertainties；不改研究方向或预算 |
| `design-experiment` | Project／Workstream fixed refs、固定 source、假设、数据、controls／metrics／矩阵、判据、预算 | experiment-design |
| `prepare-experiment` | pinned design、显式命令、ledger、ordinary 或 bounded_autonomy | preparation、逐 attempt 日志；有界失败保留 |
| `run-experiment` | 同一 pinned design＋preparation、命令、结果路径、ledger | run、实际结果；ordinary 首败停止 |
| `analyze-experiment` | pinned run 与结果 bytes、固定 analysis candidate | analysis；没有补跑实验 executor |
| `assess-result-to-claim` | pinned analysis＋Claim、scope／method／conditions 与显式 verdict | result-to-claim 结论；仅 supports 生成 Evidence，不自动变六轴 Assurance |
| `math-proof` | 已确认的 statement、examples/counterexamples、lemma map、有限 attempts | typed proof-run、准确 proof-gap／budget／user stop；不启动 Lean |
| `lean-formalize` | 固定 statement／proof／独立 review 与形式化 metadata、明确授权 | real build/audit/comparator/kernel replay；工具不可用 exit 3 |
| `freeze-publication` | staged manifest、Project user principal、最终 digest 确认串 | immutable Publication 与 receipt；错误确认／不闭合／冲突阻止冻结 |

## 实际命令形态

`CLI` 以下表示 PATH 中由持久 `uv tool install` 安装的 `research-os`。若未配置 PATH，可先用 `uv tool dir --bin` 查询实际 executable 目录；不要硬编码某个平台的默认路径。

```text
CLI setup-research-os --project PROJECT
CLI workflow research-charter --project PROJECT --request requests/charter.json
CLI workflow research-literature --project PROJECT --request requests/literature.json
CLI workflow design-experiment --project PROJECT --request requests/design.json
CLI workflow math-proof --project PROJECT --request requests/math.json
CLI workflow lean-formalize --project PROJECT --request requests/lean.json
CLI freeze-publication --project PROJECT --manifest stage.json --principal PROJECT_USER_PRINCIPAL --confirm 'EXACT_FINAL_DIGEST_CONFIRMATION'
```

除 setup／freeze，其他研究 workflow 使用 `workflow NAME --request`；多数也有同名短命令。`research-charter --input --output --report` 是兼容入口，`--input` 现在是完整 typed pinned request，不是裸 `question.md`。setup／freeze 使用独立命令，不承诺 generic dispatcher 覆盖其执行分支。

`PROJECT`、`PROJECT_USER_PRINCIPAL`、digest 和确认串均为占位符：PROJECT 必须替换为科研项目绝对路径；principal 必须存在于固定 Project Artifact 且具有 `user` role；digest／确认串必须来自实际 bytes 与 preflight，不能原样复制示例。

outer request 最小形态（输入必须是现有合法 typed question 文件）：

```json
{
  "inputs": [{"path": "question.json", "sha256": "REPLACE_WITH_ACTUAL_64_HEX_DIGEST"}],
  "output_path": "charter.json",
  "report_path": "reports/charter.json"
}
```

outer 和 math CLI 当前按 path＋SHA-256 固定所读 bytes；计算 handoff 使用 path＋SHA-256＋完整 Git commit。测试另行提交所有重要 Artifact；不虚称所有 workflow 都强制 commit。分析的 run commit 必须包含其 result bytes，不能先提交 run 后才首次提交 result。

## 预算和失败

计算六维预算为 `seconds`、`cost_usd`、`tokens`、`gpu_hours`、`attempts`、`rounds`。本地 reference 用 CPU、零 cost/tokens/GPU，真实进程；显式 bounded_autonomy 用完 attempt 后不得执行下条命令。失败记录新路径追加，不能删除 ledger 重置预算后装作同次授权。

数学量词／定义域／假设／结论改变须新 statement revision 与用户新确认。当前普通 proof CLI 输出后停止；独立 review 的公共 API 接收**原始 statement/proof record**而非 typed envelope，需要显式、可审计的 record projection。此接口不等于已接纳 `independent-proof-review` discipline，也不是宿主真实隔离能力证明。

模板与具体请求见 installed `templates/`、各 canonical skill 及 [reference 复现](references.md)。不要把测试 fixture acceptance 文本套到真实研究上。
