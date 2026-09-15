# 数学审查规则

对每个 theorem、lemma、proposition 及其应用，完整检查 A–H；corollary 与未编号的非平凡断言按同样标准处理。对不适用项说明理由，无法完成的项保留为缺口。直接读取完整数学原文，不把作者/修复者摘要当成审查输入的替代物。

## A–H 必查项

A. **DEFINITIONS**：列出含义有歧义、随位置改变或定义不全的每个符号。
B. **HYPOTHESIS DISCHARGE**：对每次引理/定理的应用，而不仅是其陈述，列出全部假设、是否满足及具体位置。
C. **INEQUALITY AUDIT**：逐步检查方向、绝对值及凸性、PSD、可积性等条件，不跳过不等式链的中间步骤。
D. **INTERCHANGE AUDIT**：标记每次 limit / derivative / expectation / integral 交换；说明依据 DCT/MCT/Fubini/Leibniz 或哪个精确结果，以及已验证与缺失的条件。
E. **PROBABILITY MODE**：追踪 a.s.、in probability、in L²、in expectation、w.h.p.；每次转换必须有论证。
F. **UNIFORMITY & CONSTANTS**：每个 O、o、Θ、≲ 指明一致性参数集合与隐藏的参数依赖；“O(1)”不等于对 d,n,K 都是普适常数。
G. **EDGE/DEGENERATE CASES**：尝试用一维、低秩、极端参数构造击破每个关键引理。
H. **DEPENDENCY CONSISTENCY**：检测环、语义循环和指向尚未证明结果的引用；合并全局依赖后再判断。

## 每条发现

以自然 Markdown 记录：

- 编号；status；impact；由两轴解释的 severity；下表 category。
- location：文件/行、章节/公式。
- statement：原文到底声称什么。
- why wrong/unjustified：具体缺失推导、违背条件或矛盾，不能只有“可疑”。
- counterexample：已代数核实 / 未找到 / 待核实候选，附构造或尝试。
- affects：哪些下游结果因此失去依据。
- minimal fix direction：补推导、补引用或需用户决定的命题/假设变化。这里只指方向，不起草或应用 LaTeX 补丁。

## 问题分类

### A. Logic & Proof Structure

| Category | 含义 | 例子 |
|---|---|---|
| UNJUSTIFIED_ASSERTION | 无证明或引用的断言 | “Hessian 分解成 Gram blocks” |
| UNPROVEN_SUBCLAIM | “显然/可得”掩盖非平凡引理 | 未核对便称对称性使交叉项消失 |
| QUANTIFIER_ERROR | ∀/∃ 次序或范围错误 | 对每个 π 存在 ε 与存在统一 ε 混用 |
| IMPLICATION_REVERSAL | A⇒B 被用为 B⇒A，或只证单向却称等价 | 充分条件被当必要条件 |
| CASE_INCOMPLETE | 遗漏边界/退化情形 | 奇异协方差、零权重、非唯一 argmin |
| CIRCULAR_DEPENDENCY | 引理使用依赖自身的定理 | 跨节语义循环 |
| LOGICAL_GAP | 前文不足以推出后一步 | B=Θ(1) 未分析 W 就推出 β_K=0 |

### B. Analysis & Measure Theory

| Category | 含义 | 例子 |
|---|---|---|
| ILLEGAL_INTERCHANGE | 未满足定理条件便交换运算 | 在 E 下求导但没有支配论证 |
| NONUNIFORM_CONVERGENCE | 逐点被当成一致收敛 | 交换 sup 与 limit |
| MISSING_DOMINATION | 引用 DCT 却未给出可积支配函数 | 依赖 n 的上界被当固定支配函数 |
| INTEGRABILITY_GAP | 使用未证明/假定有限的矩 | E|X|^p |
| REGULARITY_GAP | 未建立就使用可微/Lipschitz/凸性 | 对不可微点套 Taylor |
| STOCHASTIC_MODE_CONFUSION | 混同随机收敛模式 | 依概率收敛直接取期望极限 |

### C. Model & Parameter Tracking

| Category | 含义 | 例子 |
|---|---|---|
| MISSING_DERIVATION | 量未从模型中推导 | risk functional 中 B、W 未定义 |
| HIDDEN_ASSUMPTION | 证明偷偷使用未声明条件 | 未声明 Gaussianity |
| INSUFFICIENT_ASSUMPTION | 假设太弱且有反例 | 矩条件仍容许两点分布 |
| DIMENSION_TRACKING | 参数依赖未明确 | d 只通过 κ 进入却未解释 |
| NORMALIZATION_MISMATCH | 坐标/缩放约定冲突 | 重缩放与原坐标混用 |
| CONSTANT_DEPENDENCE_HIDDEN | 把依赖参数的 C 当普适 | C 依赖 d,n,K |

### D. Scope & Claims

| Category | 含义 | 例子 |
|---|---|---|
| SCOPE_OVERCLAIM | 结论比证明更广 | 仅有 generic overlap 却宣称 β_K=0 |
| REFERENCE_MISMATCH | 引用定理与应用处条件不符 | 只查名称而未核对 signature/假设 |

## 双轴严重度

**Proof status** 描述问题，而非修复进度：

| Status | 含义 |
|---|---|
| INVALID | 原陈述为假，存在核实的反例或矛盾 |
| UNJUSTIFIED | 可能为真，但当前证明没有建立它 |
| UNDERSTATED | 当前论证需要更强假设；指出具体缺失，不先假定加强后就成立 |
| OVERSTATED | 当前论证至多支持更弱结论或附带限定 |
| UNCLEAR | 记号、定义或语义有歧义，不一定数学错误 |

**Impact**：GLOBAL 破坏主定理/核心依赖链；LOCAL 影响旁支但不影响主定理；COSMETIC 仅影响表达。

| Severity | 典型组合 |
|---|---|
| FATAL | INVALID + GLOBAL |
| CRITICAL | INVALID + LOCAL，或 UNJUSTIFIED + GLOBAL |
| MAJOR | UNJUSTIFIED + LOCAL，或 UNDERSTATED/OVERSTATED + GLOBAL |
| MINOR | UNCLEAR + COSMETIC，或不改变论断的记号、清晰度、维度记录问题 |

未列组合根据实际依赖影响解释分级，不把改假设/弱化结论硬塞入 MINOR。即使没有 FATAL/CRITICAL，也不能跳过尚未闭合的 MAJOR 义务宣布完整证明。

## 常用定理侧条件

这是检查起点，不替代实际引用版本的精确假设；对每次应用读取 statement 并逐条 discharge。

| 定理/方法 | 必查条件 |
|---|---|
| DCT | 逐点 a.e. 收敛；可测；存在同一个可积支配函数 |
| MCT | 可测、非负、单调递增；扩展实数积分解释一致 |
| Fubini/Tonelli | 产品可测；Fubini 的绝对可积或 Tonelli 的非负条件；核对测度空间假设 |
| Leibniz integral rule | 所用版本要求的连续/可微性；导数的局部统一可积支配；变积分端点项 |
| Implicit Function Theorem | 连续可微；相应 Jacobian 非奇异 |
| Taylor with remainder | 足够阶可微性及所用余项形式（Lagrange/integral）的条件 |
| Jensen | 凸性；相关变量和函数的可积性/扩展值条件 |
| Cauchy–Schwarz | 正确内积空间；两个因子的平方可积性 |
| Weyl/Davis–Kahan | 对称/Hermitian；适用扰动界；Davis–Kahan 所需谱间隙 |
| Analytic continuation | 适用解析性、连通域和恒等定理条件 |
| WLOG | 声称的对称不变性；约化无损并可逆；显式微命题证明 |

## Counterexample red team

每个 CRITICAL/MAJOR 问题以及每个关键引理均尝试反例，尤其：新不等式、identifiability/uniqueness、curvature/PSD/strong convexity、一致参数断言及收敛模式升级。

| 策略 | 操作 |
|---|---|
| Dimensional collapse | 取 d=1 或 2、K=2、较小 n，检查仍满足原假设 |
| Degeneracy | 奇异协方差、极小/零权重、重合均值、相同分量、非唯一解 |
| Extremal distributions | 两点 ±a、没有统一 sub-Gaussian 参数界的有界分布族、重尾分布；单个有界随机变量本身是 sub-Gaussian，不把它误当反例 |
| Adversarial parameter scaling | 令被忽略项主导，检查是否仍在声明 regime 内 |
| Numeric falsification | 构造候选小域搜索目标；本只读 Skill 不执行计算，返回待用户另行验证的候选 |

只有代数核实满足全部假设且违背结论，才能称“找到反例”。数值例子、未核实参数或尚待证明的构造都标为 candidate。每次尝试记录对象、构造、假设满足情况、结论与失败理由；失败尝试不能省略，也不能作为正确性证据。

## 整体闭合

- 证明结束处与定理陈述的量词、常数、适用 regime、一致性范围完全一致。
- 每个 DAG 节点有完整论证或显式假设；必要假设必须出现在相应声明中。
- case analysis 划分整个定义域，覆盖边界与退化情况。
- 归纳核对 base case、step、IH 的正确用法以及良基/严格递减度量。
- WLOG 的每次约化有无损 micro-claim。
- 比较原定理与修复后原文时，任何假设加强都要指出；用户未批准的变化不是成功修复。
