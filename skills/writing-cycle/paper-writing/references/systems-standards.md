# Systems Writing and Evaluation Standards

按需用于以系统设计、实现或实测为主要贡献的论文。此摘要依据同包 Systems 专业参考整理：Orchestra Research `systems-paper-writing` 与 ARIS `writing-systems-papers`；相应 MIT notice 随本 Skill 安装于 `LICENSE-Orchestra.txt` 与 `LICENSE-ARIS.txt`。逐节写作、评价、checklist、venue/reviewer 方法分别见同包 `systems-writing-methods.md`、`systems-evaluation-methods.md`、`systems-checklist.md`、`systems-venue-and-reviewer.md`，报告骨架见 `../templates/systems-paper-writing-report.md`。

## 设计叙事

- 从问题、约束和目标出发，说明关键设计选择、替代方案及取舍；把系统贡献与组件罗列区分开。
- 描述架构、实现和端到端路径，使读者能把设计理由映射到实际机制。报告原型/生产系统、实现覆盖面与未实现部分。
- 结构可按贡献选择：背景与动机、设计、实现、评价、局限和结论承担不同职责，不为套页数而重复内容。

## 评价证据

- 明确系统问题、工作负载、数据来源、环境、硬件、配置、度量和比较对象；说明 baseline 选择及资源是否公平。
- 将 end-to-end 结果、microbenchmark、扩展性/负载变化和消融用于各自能回答的问题；局部微基准不能代替整体效益。
- 报告测量方法、重复次数、波动/区间、统计聚合与异常处理；解释瓶颈、成本、失败条件及适用边界。
- 给出复现关键结果所需的软件版本、参数、工作负载和制品可用性；未获得的证据标为未核实，不推测补齐。

## 审查与 venue

逐项检查问题重要性、设计必要性与正确性、端到端有效性、评价公平性、可复现性及现实影响。当前 venue 的格式、匿名、artifact、伦理和投稿要求须从官方 CFP/作者指南现场核对；历史页数示例不是当前规则。

## 缺口边界

可按有效委托补查现有材料或交由相应研究能力补做获准分析。缺数据时保留可见缺口并说明它限制的主张；本写作参考不授权部署系统、运行基准或修改原始结果。
