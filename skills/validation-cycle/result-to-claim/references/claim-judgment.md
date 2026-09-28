# Claim 判定细则

[Result to Claim](../SKILL.md) Phase 3 的缩窄、上限与反证。存在性核对留在 SKILL Phase 1；统计检查用已有 `analyze-results` 报告，没有报告时按 [statistical checks](../../analyze-results/references/statistical-checks.md) 做，不在这里重写。不能定位即保持 `unknown`。

## 缩窄规则

`needs-narrowing` 必须产出可直接替换原 Claim 的**更窄表述**。按断裂处选择：

- 一般概括 → 点名实际测试的 population／dataset／scene 子集；
- 因果措辞 → 降为关联陈述（除非设计支持因果）；
- “优于所有方法” → 收为“在配置 X 下优于所列基线”；
- “consistently／robust／extensive／comprehensive” → 删除，或补上实际分母与覆盖范围；
- 点估计 → 加不确定性限定（区间、种子数、敏感子集）；
- 代理指标结论 → 收为“在该代理指标上”；
- 已复现／已证明 → 降为单次观察，除非另有独立复现或证明链。

缩窄后的表述仍须可检验，并保留不确定性来源。

## 评价类型上限

类型判断缺失时记 `unknown`。上限低于声明范围时按上节缩窄或改判。

| 评价类型 | 可支持的 Claim 上限 |
|---|---|
| `real_gt` | 在实测 population／setting／metric 范围内，统计成立时可支持 |
| `synthetic_proxy` | 只能支持“与代理参考一致” |
| `self_supervised_proxy` | 只能支持代理目标上的相对改进 |
| `simulation_only` | 只能支持模拟设置内的陈述 |
| `human_eval` | 只能支持该评分协议下的质量陈述；须说明评分者、盲法与一致性 |
| `unknown` | 不得写 `supported` |

## 反证清单

每条判定逐项写定位：

- 不支持或限制该 Claim 的失败记录、负结果、异常运行；
- 未被测试的 population／setting／metric／时间范围；
- 使结论不成立的已知混淆或设计缺陷；
- 最小补证动作（补哪个 seed／baseline／子集／评价类型即可判定）。

补实验只是提议，由用户另行授权。
