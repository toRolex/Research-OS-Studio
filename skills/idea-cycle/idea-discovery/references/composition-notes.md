# Discovery 组合配方

本文件说明 `idea-discovery` 如何组合独立能力，不是中央协议，也不把职责表变成必经流水线。先识别目标缺口与已有证据，再按需选择能力子集、排序或回访；达到本次目标即可交付。叶 Skill 的来源、预算、原文评审和写入约束始终有效。

## Required skills

若通过通用 Skills CLI 单独安装 `idea-discovery`，其正文明确要求可解析以下五个必要兄弟 Skill：`research-lit`、`idea-generation`、`novelty-check`、`idea-review`、`idea-refinement`。这些能力各自承担不同职责，不是 Discovery 入口内可省略的别名。`creative-thinking-for-research` 是可选能力，仅在生成受阻且该 skill 已安装时使用。

可用 CLI 一次成组安装入口和必需依赖。CLI 1.7.4 语法示例：

```bash
npx skills@latest add toRolex/Research-OS-Studio \
  --skill idea-discovery research-lit idea-generation novelty-check idea-review idea-refinement \
  --agent codex --copy -y
```

使用其他版本时先核对 `skills add --help` 是否支持多个 `--skill` 值；否则对同一项目逐个执行安装命令，或安装整包。安装后按宿主实际位置解析 Skill 正文及其共置 references/templates/LICENSE，不依赖源码 checkout、开发路径或本文件路径推导其他目录。

若入口已安装但任一 Required skill 未安装、不可读或其资源缺失，相关职责标记 **DEPENDENCY MISSING / BLOCKED**：只完成不依赖它的工作，并列出缺少名称、受影响目标与补装命令；不伪称已运行，也不以自己顺序执行冒充 `idea-review` 独立审查。组合说明文件可达并不能替代兄弟能力可达。

## 能力选择

以下是可分派的能力职责，不是阶段要求；根据本次目标选择，并按宿主支持映射执行者。宿主无相应独立能力时，按叶规则报告缺口，不将顺序代跑冒充独立工作。

- **literature**：被选中的文献检索或 prior-work 核对。
- **ideator**：被选中的候选生成或方法细化。
- **reviewer**：仅在需要独立挑战且有真实独立 reviewer 时执行审查。

目录的面向使用者映射如下，标签仅作导览，允许按缺口省略或回访：

| 阶段标签 | 叶能力 |
|---|---|
| 文献 Landscape | `research-lit` |
| 候选生成与筛选 | `idea-generation` |
| 查新 | `novelty-check` |
| 独立评审 | `idea-review` |
| 固定边界收敛 | `idea-refinement` |

全链是可选配方。完整方向到 Proposal 时，通常组合全部五种必要能力；已有文献时可从候选或查新开始，现成候选可只做查新、评审或细化，已覆盖缺口可省略。生成、查新与独立评审的次序依赖目标和现有证据；新增证据可触发回访与重排。逐个能力检查其自身完成条件和额度，跳过项记录理由与覆盖边界。

| 能力 | 适用缺口 | 典型贡献 | canonical 章节（需要综合报告时） |
|---|---|---|---|
| `research-lit` | 文献范围或来源证据不足 | 有出处的 landscape | `#文献 Landscape` |
| `idea-generation` | 缺少候选或探索视角不足 | 候选池与筛选 | `#候选池与筛选` |
| `novelty-check` | 候选主张尚未对照 prior work | closest-work 比较或证据缺口 | `#查新结论` |
| `idea-review` | 需要独立挑战与裁决 | findings、来源定位、未解决意见 | `#独立评审` |
| `idea-refinement` | 方法选择/收敛或 Proposal 未完成 | 固定 Anchor 下的路线取舍 | `#收敛与 Proposal` |

canonical 路径是报告已授权且显式传入时的贡献目标，不因文件存在而自动获得写入权限。内容保留叶能力的原始实质结论。仅运行局部能力时可单独交付其报告，不强制制造完整 Discovery 报告或 Proposal。

## 能力结果与缺口

使用独立评审时，实际评审请求与原始回复须逐字完整内联到获准 canonical 的 `#独立评审` 章节；保留轮次、来源定位与未解决意见。链接或摘要不替代评审原文。没有使用评审职责时，不制造空评审章节。

- 无可用检索时，`research-lit` 可按其规则继续 supplied-material synthesis，并限定已供材料覆盖；不能推断“无文献存在”。
- 没有可读研究材料时，先报告阻塞的生成/评审职责与所需材料；仍可完成不依赖这些材料的范围澄清。
- 无真实独立评审者或 reviewer 无法读取原文时，标记 **REVIEW UNAVAILABLE / EVIDENCE GAP**；自查不升级为独立裁决。
- 参考论文全文不可读时保留具体缺口，不凭记忆补写，不必阻止其他适用职责。
- 额度耗尽时停止该类新工作，使用现有证据完成其余已授权职责，报告未检查项，不循环扩大预算。
- 用户提出主要目标替换时先确认；独立候选分支的越权、超额或文件冲突只阻塞该分支。
