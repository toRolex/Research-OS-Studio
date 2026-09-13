# 重述回归（仅 --restatement-check）

用户明确 opt-in 才执行额外的全篇重述扫描，顺序在全局闭合之后、停止/交付之前。不替代默认的命题—结论核对和本轮已知下游同步。

## 算法

1. 在获准读取的所有相关 `.tex` 中找带 `\label{...}` 的 theorem、lemma、proposition、corollary 环境，记录标签、完整声明和文件范围。不能仅凭正则命中就忽略宏展开或嵌套造成的歧义。
2. 针对每个标签收集 `\Cref`、`\ref`、`\cref` 及周围两句话；收集提到标签、非正式定理名或常数的表格行，Key Contributions/Summary/Main Results 的条目，摘要、引言、讨论和图注中的释义。保留候选原文与准确位置。
3. 对齐规范声明与重述：仅规范化 `\,`、`\;`、`\!`、`~`、空白和行内/行间数学分隔；不删除数学限定。逐对检查以下六种漂移。

| 漂移 | 检查 |
|---|---|
| conditional_loss | under assumption X、w=1 或部分 regime 有条件结论被改成无条件 |
| scope_change | O(K²) 与 O(d²K²)、√n 与 n 等速率或范围不同 |
| quantifier_loss | n≥n₀、sufficiently small γ 等量词/阈值丢失 |
| regime_envelope_change | Cγ/(1−Δγ) 与其平方等适用 envelope 变化 |
| constant_change | 数值常数或参数依赖不同 |
| variable_rename | 相同角色换符号但没有显式别名 |

4. 自然 Markdown 输出每条发现的 label、canonical_location、restatement_location、drift_type、canonical_excerpt、restatement_excerpt、severity、note。默认关注 MAJOR 的主结论过强/假设遗漏；纯排版 MINOR，若下游证明实际使用错误重述则请求 proof-review 判断是否 CRITICAL 并作为正常数学问题处理。不能仅按字符差异判数学错误。

## 边界与失败

该检查给建议，不自动修改，独立列在常规问题之外；单凭发现重述漂移不自动改变证明结论。若漂移确实破坏推理，由 proof-review 在普通问题中解释影响，不能借“可选”掩盖已知错误。

文件不可读、编码/解析错误、标签重复歧义、没有带标签的规范定理环境或授权范围不覆盖扫描时，记录“重述检查不可用”、具体缺口与已查范围；不能把空发现写成“无漂移”。可选扫描不可用本身不阻塞其它步骤，但它揭示的正文读取缺口、已知下游不同步或数学阻塞仍按主流程停止规则处理。
