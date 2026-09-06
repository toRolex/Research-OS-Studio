# Gates: Ports and disciplines
Scope: 八个 model-invoked disciplines 与 port-first admission evidence；上游仅作为不可信文本读取，未执行任何上游代码、命令或整体 fork。

- [x] G1: port validators 与负面测试通过
  CHECK: uv run --frozen python -m unittest discover -s tests/ports -t . -v
  EXPECT: OK
  EVIDENCE: 2026-09-06，39 tests / OK。覆盖严格 1.0.0 manifest/inventory/release/evaluation-detail schema、来源/许可 unavailable → BLOCKED/3、结构/hash/ledger/product/inventory/decision receipt 错误 → FAIL/1、双侧各两次 receipts、人工 `person:` 决定、fixture/rejected bytes release 隔离。

- [x] G2: 八个 discipline 的 canonical digest 绑定 accepted port，许可/来源缺失不进入产品
  CHECK: uv run --frozen research-os validate-ports --root .
  EXPECT: /"status"\s*:\s*"pass"/
  EVIDENCE: 2026-09-06 用户确认 `ACCEPT PORTS person:rolex 50874399aeb2c943938f3f34acc67c81eda21e2ab0083d10072ead2e5e44f70e`。写入前逐项验证 request SHA-256、8 个 admission digest、source tuple 与 product digest；最终 `validate-ports` status=pass、exit_code=0、release_authorized=true，8/8 external ports decision=adapt、admission=accepted；`validate-repository` status=pass。接纳请求、行为评价与 attribution digest 均固定在 `ports/acceptance-request.json`。

- [x] G3: 计算与数学来源固定、许可保留、minimal adaptation 可追溯
  EVIDENCE: 计算七项来自 `https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git@2349f63ccfd7502aae95ec987b4d0a4c65d69c52` 的精确 skill 路径，MIT 全文固定；数学 `trusted-statement-comparison` 来自 `https://github.com/openai/ten-proofs.git@94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6` 的 `ComparatorChallenges/B_BinaryCodes.json`，Apache-2.0 全文固定。每项保存 snapshot=baseline、adapted、逐文件 keep/modify/delete/add ledger、source receipt、original behavior、review、人工 decision receipt 和 product digest。

- [x] G4: baseline/adapted 评价不执行上游代码且准确限定证明范围
  EVIDENCE: 本地 UV harness `ports/evaluate_port.py` 将固定上游文本/JSON 当作不可信数据，仅做 UTF-8、digest、结构、研究步骤及 user-control boundary 检查；八项 baseline/adapted 各运行两次，共 32 个 detail 结果与 32 个 validator receipts。该证据仅证明固定文本 discipline 的确定性静态/结构化适配检查，**不声称**复现上游 runtime、模型行为、科学正确性或 Lean 验证。
