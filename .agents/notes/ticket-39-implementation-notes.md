# Ticket 39 implementation notes

## 范围

#39 拥有存活叶 skill（不含 setup、不含待删除 router `ask-research-os`、不含尚未落地的 research-os 入口）。本分支在 integration tip `837d1e8` 上，ask-research-os 仍在树里：不删、不改它的科研导航，只把它排除在本票基线之外。setup 的 frontmatter 翻转与 yaml 归 #40；本票 checker 对 setup 保持「当前仍是显式调用 + yaml false 也合法」的兼容，不把 setup 写成 model-invoked。

## 决策

- 调用策略 seam：除 setup 外 `disable-model-invocation: true` 必须出现在 frontmatter 正文（注释行不算）；`agents/openai.yaml` 必须含 `allow_implicit_invocation: false` 的值，不只是文件存在。setup 允许缺 disable 或缺 yaml，但若已有这两项则值必须仍是显式/false，避免半翻转。
- 门声明格式（共享合同）：`Gate: <id> | before=<event> | approval=explicit-user | source=SKILL.md#<锚点>` 或整行 `Gates: none`。source 必须是当前 skill 的 SKILL.md 或 references/ 下存在的锚点。
- 基线只覆盖本票拥有的叶。setup / ask-research-os / 未来 research-os 不进 EXPECTED_GATES。后续入口票把行加进同一 scripts/check-skills.py。
- 人工盘点只标「副作用或扩大范围之前必须等用户明确决定」的既有停点。只读默认、事后停止、完成条件、内部能力复用不算新门。不改科研步骤正文。
- README 分类表只改 U/M 表述为「除 setup 外全部显式调用」。setup 行仍写 user-invoked，因为本分支还没做 #40 翻转；不把 ask-research-os 标成将删除。

## 叶门基线（人工）

有门：idea-discovery（stage-checkpoint, output-path）、idea-generation（write-path）、idea-refinement（anchor-clarify）、idea-review（scope-clarify）、creative-thinking-for-research（write-path）、research-lit（external-search）、novelty-check（Gates: none）、experiment-plan（output-path）、experiment-bridge（run-authorization）、run-experiment（run-authorization, milestone-start）、experiment-queue（batch-authorization, precondition-block）、monitor-experiment / training-health-check / analyze-results / experiment-audit / result-to-claim（write-path；result-to-claim 另加 narrow-adopt 不标——采用是交付后用户决定，不是停点）、formula-derivation / proof-writer（write-authorization）、proof-orchestrator（round-scope, external-action）、proof-review（Gates: none）、proof-repair（repair-contract, assumption-or-claim-change, compile-authorization）、paper-writing / ml-paper-writing / systems-paper-writing（workflow-authorization）、paper-plan（write-authorization, framing-confirm）、paper-drafting（boundary-confirm, venue-conflict）、academic-plotting（figure-choice, external-resource）、paper-compile（build-scope）、paper-compile-repair（repair-scope, round-diff）、citation-audit（audit-scope）、apply-citation-fixes（apply-authorization）、paper-claim-audit（report-target）、claim-stress-test（report-target）、rebuttal（strategy-confirm, wording-confirm）、paper-talk（talk-authorization, outline-confirm）、resubmit-pipeline（adaptation-scope, change-confirm）、research-improvement（loop-authorization, experiment-topup）。

## Deviations

- 共享合同示例锚点是 rebuttal「回应策略」；正文标题是「制定策略，交用户选择」，source 用实际标题锚点，不改标题去贴示例。
- TDD seam 未经用户当场口头确认。任务已指定 seam：调用策略值、门声明基线、损坏副本反例、README 分类表述。按该 seam 写测试。
- `.agents/notes` 被 gitignore，notes 只留本地。
