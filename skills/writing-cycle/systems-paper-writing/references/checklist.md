# 系统论文投稿前自检清单

供 [SKILL.md](../SKILL.md) 第 5、9 节使用：投稿前按阶段自检。改编自 Orchestra `systems-paper-writing/references/checklist.md`，许可见共置 `LICENSE-Orchestra.txt`。venue 专属项按 [venue 与 reviewer 方法](venue-and-reviewer.md) 现场核对当前官方 CFP，不缓存年度规则。

## Stage 1 结构完整

- [ ] Thesis 可按「X 对处于环境 Z 的 Y 更好」判定，并出现在 Abstract（S3）、Introduction 与 Conclusion
- [ ] Introduction 有 3–5 条编号、可检验的贡献
- [ ] 每条贡献带 §N 交叉引用
- [ ] 每条贡献在 §5 有对应实验或被显式标为缺口
- [ ] Abstract 150–250 词且自包含（无未定义术语）
- [ ] Introduction 覆盖 问题 → Gap → 洞见 → 贡献
- [ ] Background／Motivation 中术语先定义后使用
- [ ] Design 含架构图 + 模块细节 + alternatives
- [ ] Implementation 含语言、LOC、框架与关键决策
- [ ] Evaluation 含 setup + end-to-end + microbenchmark／ablation + scalability（缺失项记 gap）
- [ ] Related Work 按方法分组并有显式区别
- [ ] Conclusion 为 3 句（问题、方案、结果）
- [ ] 篇幅符合现场核对的当期 venue 规则；Design 与 Evaluation 未被过度压缩

## Stage 2 写作质量

- [ ] 前置引用有显式指针（「as we show in §N」）
- [ ] 缩写首次出现即展开；术语无孤儿
- [ ] 系统名全文大小写一致
- [ ] 图／表在正文中被引用后才出现
- [ ] 图 caption 自包含；评估图 caption 含关键发现
- [ ] 架构图出现在前 3 页内
- [ ] 图中字体打印后可读；灰度可辨；全篇图风格一致
- [ ] 引用格式统一；`Section~\ref{...}` 不断行
- [ ] 参考文献元数据完整
- [ ] LaTeX 日志无大量 overfull hbox
- [ ] 无无证据的 hedge；定量陈述带数字
- [ ] 贡献具体，不用无解释的「novel」
- [ ] 相关工作比较公平准确

## Stage 3 评价严谨

- [ ] Baseline 是当前 state-of-the-art，不是 straw man
- [ ] Baseline 在相同配置下经过调优
- [ ] 硬件、软件版本与配置完整写出
- [ ] 负载描述足以复现
- [ ] 有不确定性（error bars／多次运行／置信区间）
- [ ] 排除 warmup
- [ ] 每条结论三处一致（段首假设、段尾结论、图 caption）
- [ ] Ablation 隔离每个设计组件
- [ ] Scalability 展示规模增大的行为，或有显式 gap
- [ ] 有利与不利结果都如实讨论
- [ ] 给出绝对值，不只相对百分比
- [ ] source／超参／负载来源足以让独立团队复现

## Stage 4 设计质量

- [ ] 每个主要设计决策至少讨论一个替代方案
- [ ] 替代方案是真实的，不是 straw man
- [ ] 每个替代方案的 trade-off 显式写出
- [ ] 未选原因是技术性的
- [ ] 失败情形被讨论或评价
- [ ] 边界条件与 threat model／假设显式写出
- [ ] Limitations 诚实，不隐藏

## Stage 5 学术诚信

- [ ] 每条引用经核实；未核实标 `[CITATION NEEDED]`
- [ ] 引用不来自记忆
- [ ] BibTeX 元数据完整
- [ ] 无编造的标题、作者、venue
- [ ] 自引相关，不为凑数
- [ ] 观测来自真实数据，结果来自实际运行
- [ ] trace 标注来源；无未披露的选择性挑选
- [ ] 按当前 CFP 处理 LLM 披露
- [ ] 无段落级抄袭；结构性借鉴已标注
- [ ] 相关工作为原创改写

## Stage 6 Venue 专属（现场核对当前 CFP）

- [ ] 系统设计与实现，而非仅算法
- [ ] 真实负载评价；微基准不是唯一证据
- [ ] 展示延迟、吞吐、成本或能耗等实际收益
- [ ] 与当前 state-of-the-art 系统比较
- [ ] 无同时投稿冲突；预印本政策符合当期规则
- [ ] track 选择正确，并满足其专属标准
- [ ] 双盲与匿名要求满足（作者、单位、系统名、自引、致谢）
- [ ] 页限、模板、字号、文本块、页码符合当期要求
- [ ] 图在黑白打印下可辨
- [ ] artifact evaluation 是否参加已决定（如适用）
- [ ] LLM／AI 政策已核对并按要求披露

## Stage 7 最终检查

- [ ] PDF 渲染正确（无缺字、无坏图）
- [ ] 源码中无 TODO／FIXME
- [ ] `[CITATION NEEDED]` 已处理或移除
- [ ] 投稿系统作者信息／匿名状态正确
- [ ] 补充材料已匿名（如适用）
- [ ] 文件大小符合系统限制
- [ ] 标题、摘要与投稿系统一致
- [ ] track／topic 选择正确
- [ ] 六维自检（Original Ideas、Reality、Lessons、Choices、Context、Presentation）每维一句话可回答；弱项已修
