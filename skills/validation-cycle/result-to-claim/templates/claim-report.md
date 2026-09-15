# Candidate Claim Report

这是 [Result to Claim](../SKILL.md) 的自然 Markdown 报告骨架，不是机器 schema。按实际读到的原始材料填写；无法定位的项写 `unknown`，不要省略。

## 判定范围与材料账本

- 待判定 Claim 集合（原文 · 声明范围 · 引用编号）：
- 结果文件（Claim · 文件与 key · 值 · 所属 attempt · 读取范围 · 可核对性）：
- Baseline（数值 · 出处 · 复现／引用 · 配置与数据划分）：
- Attempt 集合（成功 · 失败 · 崩溃 · 超时 · 无效 · 被排除；含回溯到的原始集合）：
- 已有分析／审计报告（路径 · 版本 · 结论摘要）：
- 缺失或相互矛盾的材料：

## Evidence 存在性

| Claim | 引用的值 | 来源文件与 key | 读取范围 | 结论（verified/path_missing/value_not_found/unparseable） |
|---|---|---|---|---|
| [Claim 原文] | [引用值] | [文件:key] | [行/范围] | [四者取一] |

> `verified` 只证明证据存在；是否支持 Claim 见“逐 Claim 判定”。`path_missing`／`value_not_found` 直接记为 `unsupported（evidence-not-found）`。

## 统计可信度

- 重复与不确定性（seeds/runs 数 · spread · 敏感子集 · 是否降级为单点观察）：
- 选择偏差与分母（试过多少 / 报了多少；排除项与理由）：
- 多重比较（试过的 metrics／配置／子集与报告覆盖）：
- 失败与无效记录（原始位置 · 判定规则 · 是否事后排除）：
- 数字对应（报告—原始 key／值／聚合口径 · 比较对齐）：
- 不可重算项（`unknown` 及其原因）：

## 逐 Claim 判定

| Claim | 声明范围 | 存在性 | 统计可信度 | 评价类型与上限 | 结论（supported/needs-narrowing/unsupported/unknown） |
|---|---|---|---|---|---|
| [Claim 原文] | [population/setting/metric/time/comparison] | [verified/…] | [可信/部分/不可信] | [real_gt/…] | [四者取一] |

### 缩窄候选（仅 `needs-narrowing`）

- Claim：[原表述]
- 缩窄后候选表述：[更窄 population／setting／metric／不确定性限定]
- 缩窄依据：[哪条证据只支撑到此范围]

## 反证与缺口

| Claim | 反证／限制 | 未测范围 | 最小补证动作 |
|---|---|---|---|
| [Claim] | [失败记录／负结果／混淆因素及定位] | [未覆盖的 scope] | [补哪个 seed／baseline／子集／评价类型] |

补实验、补分析或修复材料不在本 Skill 内，只是提议。

## Independent verification

[实际审查者与直接读取的原始材料；briefing 与完整回复或其存放位置；分歧处理。若不可用，写 “single-agent assessment; independent verification not performed”。]

## 停止与建议

- 本报告只含候选 Claim：未运行、未重跑、未修复、未修改 ground truth／metric／选择规则，未启动任何实验或 Workflow。
- 最终采用由用户决定：是否采纳候选、缩窄表述、补证或进入写作。
- 输出：[对话返回／写入的授权路径]。
- 未决缺口与复核限制：
