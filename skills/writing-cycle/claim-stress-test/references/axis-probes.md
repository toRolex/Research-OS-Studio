# 可选六轴探测 — 扩展证据，不扩展裁决

仅 SKILL 第 2 步已获用户明确扩展要求及额外预算时读取。默认关闭；适合高影响稳定稿最终压力测试，不是常规步骤。

## 1. 六个独立探测

用六个 fresh、只读、与执行者不同模型家族的 reviewer，各收到相同原材料路径、客观限制、[攻击提示](attack-prompt.md)中的独立性与事实定位规则，再分别用下列任务替换单段最终攻击任务：

```text
This is an evidence-gathering axis probe, NOT the final rejection verdict.
Read all supplied originals yourself. On the assigned axis alone, return
the strongest approximately 120-English-word thrust with precise source
locations and the load-bearing evidence or gap. If the current text defeats
that attack, state the limiting evidence instead of fabricating a flaw.
Do not rank against other axes, score the paper, or emit an acceptance verdict.
After the thrust, add a separate Coverage section listing every original
file actually read, every unread file and reason, and any essential support
that could not be checked. This is not part of the 120-word thrust. Never
confuse supplied paths with actual reading.
Assigned axis: [one of the six below]
```

六轴逐一覆盖：theorem validity、assumption-vs-claim mismatch、missing proof obligations、limit-order ambiguity、claim-vs-evidence gap、scope overclaim；完整定义见攻击提示。不因初期看似有强论点就省略余轴。

使用现有宿主允许的并行读取，或按相同六任务顺序运行；每个任务都独立上下文。探测仅返回结果，不写共享材料。并行不可用不改变后续裁决，也不授权引入新编排器。此分支共六次探测、一次最终攻击合成、一次裁决，比默认两次增加六次 reviewer 调用；预算不足先报告，不静默削减。

**完成条件**：六个轴的原始回复、实际读取/失败情况齐全，分别标轴保存；任一必需探测失败则本扩展分支 `ERROR`，保留已有结果，不声称完成六轴。

## 2. 单一攻击承诺

另开 fresh reviewer，让其读取六份原始探测和全部原材料，发送[完整攻击提示](attack-prompt.md)，追加：

```text
You additionally receive six raw axis probes from this invocation:
[paths or verbatim raw probe responses]
These are candidate evidence, not authoritative judgments. Re-read the
original paper and supporting materials. Select and fuse AT MOST TWO axes
into the single most damaging approximately 200-English-word rejection
paragraph, no more than 250 words. Do not list all six, vote, average scores
or use an executor-selected shortlist. Output the committed memo and a
separate Coverage section as required by the attack prompt; only the memo
will be passed to the adjudicator.
```

这是有意且唯一的“原材料 + 当次探测”输入分支，不携带过去 review/作者解释。保存逐字最终 memo；第 3 步裁决者只接收该 memo 和原材料，不接收探测或攻击合成上下文。

**完成条件**：一段符合主提示的承诺 memo，报告另存六轴原始探测及合成任务原文；回到 SKILL 第 3 步执行与默认完全相同的独立裁决。
