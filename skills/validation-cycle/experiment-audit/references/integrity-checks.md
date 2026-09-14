# 完整性检查细则

本文件详列 [Experiment Audit](../SKILL.md) 第 3 步 A–F 的具体判断问题。每个问题针对 primary artifact 本身，结论必须给出实际文件与行号定位；不能定位即保持 `unknown`。

## A. Ground truth provenance

对每个评价脚本：

1. "ground truth" / "reference" / "target" 到底来自哪里？
2. 它从数据集加载，还是由模型输出生成/派生？
3. 如果是派生的，是否明确标注为 proxy evaluation？
4. 该 benchmark 有官方 eval 脚本时，是否使用了官方脚本？

**FAIL**：真值来自模型输出且没有明确的 proxy 标注。

## B. Score normalization

对每个 metric 计算：

1. 是否有 metric 除以被评对象自身输出的 max/min/mean？
2. 归一化分数之外是否同时报告 raw score？
3. 是否有分数可疑地接近 1.0 或 100%？

**FAIL**：归一化分母来自预测统计量。

## C. Result file existence 与数字对应

对报告/narrative 中的每个 claim：

1. 引用的结果文件是否真的存在？
2. 该文件中是否存在声称的 metric key？
3. 声称的数字是否与文件中的值一致？
4. 实验 tracker 状态是否为 DONE，而不是 TODO/IN_PROGRESS？

**FAIL**：声称的结果引用不存在的文件或数字不符。

## D. Dead code

对评价脚本中定义的每个 metric 函数：

1. 它是否真的在某个评价管线中被调用？
2. 它的输出是否出现在任何结果文件中？

**WARN**：metric 函数存在但从未被调用。

## E. Scope

1. 实际测试了多少 scene/dataset/configuration？
2. 每个 configuration 有多少 seed/run？
3. 报告是否使用 "comprehensive"、"extensive"、"robust" 一类词？
4. 实际范围是否支撑这些声明？

**WARN**：范围措辞超出实际证据。

## F. Evaluation type

把每个评价归类为：

- `real_gt`：使用数据集提供的真值；
- `synthetic_proxy`：使用模型生成的参考；
- `self_supervised_proxy`：设计上无 GT；
- `simulation_only`：模拟环境；
- `human_eval`：人工评判。

## 尝试完整性

- 列出所有 attempt 及其状态（成功、失败、超时、崩溃、无效、取消、重试、预算耗尽）。
- 检查时间范围与输出位置是否完整，是否存在 winner-only 汇总、被覆盖的旧结果、重用的 attempt 名称、静默排除或只报告最佳 seed/checkpoint。
- 失败与排除是否保留原始输出和一致理由。

## 代码—运行对应

- 声称的执行入口、固定配置、数据加载和指标计算是否可在日志、输出和运行记录中找到对应版本与调用痕迹。
- 代码存在本身只证明代码存在；缺少运行对应时记录为断裂。

## 事实分级

- `observed`：primary artifact 直接显示；
- `derived`：由已读材料透明推得；
- `reported`：只在摘要/报告中出现，必须回溯；
- `unsupported`：现有材料不能支持，不得升级为通过。
