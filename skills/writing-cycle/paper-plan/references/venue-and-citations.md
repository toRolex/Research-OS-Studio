# Venue 与引用：规划时的核对方法

此资源将 ARIS venue checklist 和 Orchestra ML/Systems checklists 的检查对象保留为现场核对问题，不缓存年度页数、匿名要求或投稿规则。它不负责复制模板、编译或提交。

## Venue：先确定适用对象

1. 确认会议/期刊、年份或轮次、track、稿件类别（长文/短文/Letters 等）、submission/camera-ready 阶段。未明确时询问，或交付标注未确定的中性计划。
2. 通过用户已有访问能力读该对象**最新官方** CFP、author instructions、style/template、必需 checklist 和 AI/ethics policy。官网入口可用 [NeurIPS](https://neurips.cc/)、[ICML](https://icml.cc/)、[ICLR](https://iclr.cc/)、[ACL](https://aclweb.org/)、[AAAI](https://aaai.org/)、[COLM](https://colmweb.org/)、[USENIX](https://www.usenix.org/)、[ACM](https://www.acm.org/)、[IEEE](https://www.ieee.org/)；先定位目标，不把门户或历史页当成已核对的当前规则。
3. 在计划内记录 URL、实际读取日期、版本/适用对象、所依据条款；无法获取正文则写明失败与未核实项，请用户提供官方资料。摘要、缓存、第三方教程只能导航。
4. 对照用户模板与官方模板，逐项列差异及后果。冲突时停止锁定 venue-specific 结构，向用户展示候选方案；由用户决定。用户选择不符合已读规则的方案也应如实标“已知不符”，不能将选择改写为官方合规。官方资料互相冲突同样询问。
5. 若以后需要复制模板，需单独核对其中 style、bibliography、图片和示例的许可；本能力只记录官方位置与计划要求，不把本 Skill 的 MIT notice 当模板授权。

**完成条件**：以下每个适用项目都有官方依据/明确未核实状态、计划落点及冲突决定，而非一行“符合 venue”。

## 必查项

- 主文限制、摘要字数；标题、图表、结论、limitations、references、appendix、checklist、impact statement 是否计页；补充材料的限制与审稿可读范围。
- 官方模板/版式、字体/页边距、引用格式、图像要求；submission 与 camera-ready 的差异。ARIS 原版 ML 与 IEEE 的计页口径不同，因此不得默认参考文献一律不计页。
- 匿名、作者/单位信息、致谢、经费、仓库链接、自引方式；作者信息来自用户，未知就留占位。
- 伦理/LLM disclosure、broader impacts、数据与代码获取、许可证、human subjects/IRB、敏感资产发布或 safeguard 要求；没有真实资料就记录缺口，不生成批准事实。
- 系统稿的 track 范围、deployment/operational 或 frontiers 证据期待、引言/前页预审要求；不把某年某 track 的充分性标准普适化。

## 研究报告覆盖（方法自查，不冒充官方强制条款）

按研究类型逐项规划位置；不适用写理由，缺失写 `DATA_NEEDED`：

- Claim 与摘要/引言一致；局限、强假设、失效条件、反例和适用范围可见。
- 理论：假设正式先行，完整证明位置和主文 proof sketch；缺失证明不包装为定理已证。
- 实验：baseline 公平性、数据 splits、超参数/搜索范围及选择规则、随机种子/重复次数、error bars 的计算口径（SD/SE/CI）、统计假设和多重比较限制。
- 资源：CPU/GPU、内存、运行时间、每次与项目总 compute；代码/数据/模型版本与获取、重现说明是否已有。
- Systems：硬件/软件、负载、配置、warmup、端到端、microbenchmark/ablation、scalability、绝对和相对指标、失败情况与 trade-offs；模拟不是部署经验。
- 数据/模型：原资产作者、版本与许可，新资产说明、consent、参与者任务/补偿、伦理批准。所有批准/开放承诺由用户提供，不代作。

## Citation scaffolding

保留 Orchestra 的 search → identity verify → metadata retrieve → context validate 顺序，止于规划而不是 bibliography mutation。

1. 从已有文献、笔记、代码引用与 .bib 定位候选。按研究问题、关键技术+应用、baseline 比较、closest work、已有作者扩充必要文献；只在授权检索预算内进行。
2. 核对标题、作者、年份、venue、DOI/arXiv 等身份，优先出版者/官方 proceedings/作者正式稿；可用学术索引和另一独立来源交叉核实。单源、冲突或访问失败均记限制；搜索结果存在不能证明身份正确。
3. 获取可核实元数据；已发布版本优先，但确认它与正在使用的预印本是否相同论点/版本。没有 DOI 也可用官方论文与其元数据，不强行编造 DOI。
4. 直接读支撑引用用途的正文段落、实验或定理条件，记录定位、原意与计划使用语境。关键词命中、摘要提及或身份核实不能代替语境支持。
5. 每节列动机/对比/方法来源等引用角色。凡任何一步未完成，标 `[VERIFY]` 或 `[CITATION NEEDED]` 并说明缺口；不把未核实条目计作已支持论证。不凭记忆写 BibTeX，不自动替换/删除用户引用。

**完成条件**：每条计划引用分别注明身份/元数据与语境核实状态，可供之后写作者回读，不声称完成全文 Citation Audit。
