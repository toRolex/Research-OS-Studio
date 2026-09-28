# Writing Cycle

状态词见 [PRODUCT-MAP.md](../PRODUCT-MAP.md)。目标是规划、起草、绘图、编译、审查、修订，或处理审稿、转投、演讲时阅读。

## 写作内部能力

| 能力 | 角色／状态 | 选择依据与边界 |
|---|---|---|
| `paper-plan` | M／已实现（#19） | 已有材料需 Claim—Evidence 结构、叙事、缺口和写作边界；故事不反向制造证据 |
| `paper-drafting` | M／已实现（#20） | 现成计划与原始 Claims／Evidence／结果；起草可追溯正文，与总 Workflow `paper-writing` 不同 |
| `academic-plotting` | M／已实现（#21） | 真实数据图与标明性质的示意图；保留可编辑／复现来源。ARIS／Orchestra 方法经比较适配，不许伪造数据 |
| `paper-compile` | M／已实现（#22） | 使用已有构建环境产生真实 build／error 记录，可能产生构建文件但不改源码；不等于论文正确性审查 |
| `citation-audit` | M／已实现（#23） | 分开核实引用身份、元数据与语境支持；只报告，不改 BibTeX 或正文 |
| `paper-claim-audit` | M／已实现（#24） | 数字、比较、配置、表格、caption、实验覆盖；不替代证明或一般论证审查 |
| `claim-stress-test` | M／已实现（#24） | 整篇文章最强拒稿论点；攻击者与裁决者分离，不自封最终结论 |
| 独立整篇评审与授权 revision | 内部阶段／已实现（#25） | `paper-writing` 第 7 节的独立 reviewer 直接读原始材料，修订只在当前父 Workflow 批准的写入范围与轮数内；不是可独立调用的只读 discipline，也不借独立高权限入口自动扩权 |

Claim、Citation、Proof（理论内容适用）、Stress 与独立评审是并列按需检查，不是线性证据链。用户已有稿件时只选所需检查／修订，不要求先运行计划、起草或 W3。

## 独立用户入口与专业扩展

| 入口 | 角色／状态 | 选择依据与边界 |
|---|---|---|
| `paper-writing` | U／已实现（#25） | 通用完整 W3：plan、draft、figures、compile、适用 audits、独立评审与授权 revision；不是 drafting 薄壳；不自动启动其他 user-invoked Workflow |
| `ml-paper-writing` | U／已实现（#26） | ML 实验报告：seeds、error bars、compute、limitations 等专属方法；复用内部资产，不自动调用 user-invoked W3 |
| `systems-paper-writing` | U／已实现（#27） | Systems 的 design rationale、implementation、end-to-end、microbenchmark／ablation、scalability；直接组合内部能力，不与 ML 合并、不自动启动通用 W3；缺扩展性等证据时记缺口而不补造 |
| `paper-compile-repair` | U／已实现（#22） | 已知编译错误且希望改源码；显式确认范围后修复并复验，与 check-only 分离 |
| `apply-citation-fixes` | U／已实现（#23） | 已有引用 findings 且希望替换／删除／修正文或 BibTeX；先展示拟修改范围并获授权，与 detect 分离 |
| `research-improvement` | U／已实现（#28），跨流程可选（跨流程能力，物理归位于 writing-cycle/） | 对方法、代码、全部结果、Claims、草稿、diff、历史 findings 做有界 review／repair／re-review；高权限可写入口，在明确 scope、写入范围、轮数、资源及副作用授权内补分析／改稿，补实验须另行授权并在运行数名额内；承接 W3 `auto-paper-improvement-loop` 与 W2 `auto-review-loop` 方法，不是只读审计，不自动启动 experiment-bridge、paper-writing 或专项修复入口 |
| `rebuttal` | U／已实现（#29） | 现成审稿意见与论文证据；原子化 concern、映射证据、区分可答／待澄清／需补工作；补实验另行授权 |
| `resubmit-pipeline` | U／已实现（#30） | 现成稿件换 venue；新目录适配并保留旧投稿，使用内部检查；不要求先运行本产品写作流程 |
| `paper-talk`（Conference Talk） | U／已实现（#31） | 已完成论文到 slides、notes、script；合并 ARIS 与 Orchestra 独有方法，只保留一个入口；审查演讲产物，不是重复审计原论文 |

指定 venue 时，对应写作入口应使用最新官方 guidelines／模板，用户模板冲突交给用户决定。Router 只说明此要求，不替用户联网下载模板、编译、改稿或投稿。Rebuttal、Resubmit、Talk 彼此独立；Workflow 完成不等于论文被接受。
