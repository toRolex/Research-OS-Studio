# 跨位置重述回归（可选）

仅在用户指定重述检查或 `--restatement-check` 时执行；默认未运行。它检测 canonical theorem 与论文其他位置重述的漂移，区别于“证明结尾是否与该定理一致”。本检查只报告，不修复。

## 1. Canonical statement table

在批准的论文范围内读取全部 `.tex` 的 theorem、lemma、proposition、corollary 环境及其 label。每项记录 label、完整陈述、文件/行范围。普通 Markdown 以用户可辨识的标题或命题编号对应；有歧义就请求澄清，不自行选 canonical。

完成条件：每个可定位的 canonical statement 已列入，未读文件明确列出。

## 2. 收集候选重述

对每个 canonical label（例如 `thm:foo`）搜集：

- 每个 `\Cref{thm:foo}`、`\ref{thm:foo}`、`\cref{thm:foo}`，连同周围两句。
- tabular 中提及 label、定理俗名或对应常数的行。
- Key Contributions、Summary、Main Results 列表。
- abstract、introduction、discussion、captions 中复述该定理的句子，包括没有显式引用的复述。

完成条件：批准范围的上述位置全部扫描，或列出不能覆盖处。只搜索 label 不足以声称完成。

## 3. Normalized diff

为比较去除 `\,`、`\;`、`\!`、`~` 等排版差别，归一化空白和行内/展示 math delimiters；只在分析中归一化，不改文件。逐对比较真实语义：

| 类型 | 检查 |
|---|---|
| conditional_loss | 原文“在假设 X 下”或“w=1”，重述丢了条件 |
| scope_change | O(d²K²) 变成 O(K²)，或 √n 变 n |
| quantifier_loss | 缺失 n≥n₀、充分小 γ 等量词/regime |
| regime_envelope_change | Cγ/(1−Δγ) 与其平方混淆 |
| constant_change | 数值常数或参数依赖改变 |
| variable_rename | 同一角色换了符号却没有显式别名 |

完成条件：每对候选已比较，或注明语义不确定；不能用字符串不同直接认定数学错误。

## 4. 报告与边界

每条漂移记录 canonical 定位与摘录、重述定位与摘录、类型、严重度和具体理由。实质范围漂移通常 MAJOR；纯排版可 MINOR；若下游证明把错误重述当真并因此失去依据，应另列影响证明正确性的常规问题，并解释是否达到 CRITICAL。

无可辨 canonical、label 重复无法消歧、文件不可读或内容不全时报告“不可完成/部分完成”及原因，而不是空清单等于“无漂移”。默认未启用写“未运行”。

漂移报告不能把存在 gaps 的证明变成正确证明，也不能因证明本身无 gap 就抹去错误重述。最终分别报告证明审查与重述检查状态；是否修订交给用户。
