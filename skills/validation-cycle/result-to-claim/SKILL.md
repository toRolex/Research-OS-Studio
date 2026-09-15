---
name: result-to-claim
description: 将已有实验结果转为范围受限的候选主张：逐项核对证据存在性、统计可信度与 Claim 范围，把部分支持缩窄为可辩护主张并列出反证缺口；最终采用由用户决定。
disable-model-invocation: true
---

# Result to Claim

把已有结果变成**范围受限的候选主张**，而不是把数字变成结论。它回答"这些结果能说什么、不能说什么、还缺什么"，产出候选 Claim 后即停止；采不采用由用户决定。

## 调用与授权

这是 **user-invoked Workflow**：用户显式要求"结果能支持什么 Claim"时使用。模型不自动启动它；本 Skill 也不启动其他 user-invoked Workflow。输入可以是外部现成结果，不要求先运行本产品的实验、分析或审计。

- **User** 决定待判定的 Claim、证据范围、输出位置，以及最终是否采用候选主张；另行决定是否补实验或进入写作。
- **Agent** 只读本次相关材料，按 Phase 1–5 逐项判定并写报告；不实现代码、不运行实验、不修改任何研究材料。
- **输入**：待判定的 Claim 原文及其声明范围、结果文件与原始输出、baseline（数值与出处）、配置与 seed、attempt 记录（含失败与无效）、已有分析／审计报告（如有）。摘要、排行榜或执行者口头结论只作待核对线索。
- **前置解决**：先确定待判定 Claim 集合、结果集合与输出模式。Claim 含糊、结果集不明或两者无法对应时，提一个聚焦问题并停止；不替用户选 Claim，不从目录猜测结果集。
- **复用内部能力**：统计与完整性判断复用已安装的 `analyze-results` 与 `experiment-audit` 的方法——已有它们的报告时直接采用其结论（注明出处与版本）；没有时按本 Skill 共置 [判定细则](references/claim-judgment.md) 自查。经用户明确授权，也可在本次职责内请二者贡献对应检查（它们支持 composed）；无论哪种方式，都不启动其他 user-invoked Workflow，不把它们的缺席当作通过。
- **资源**：仅使用已有且获授权的读取与比较能力。简单描述统计沿用宿主已有工具；算不出的保留 `reported` 并记缺口，不安装环境或服务。
- **写入范围**：默认在对话返回候选报告。落盘只写用户明确允许的报告文件：提出具体路径并确认，沿用现有 Research Workspace，不另建中央目录。已有文件先读，冲突时展示差异并询问。不改结果、日志、配置、代码、数据、evaluator、真值来源或论文正文。
- **预算**：一次有界判定。读到账本、存在性、统计检查与逐 Claim 判定所需的材料即止；优先读尾部与定位，避免整 log 加载。首个耗尽的限制即停，保留未审 Claim 与缺口，另行请求扩展而非循环。
- **停止条件**：报告交付即停止。不运行、重跑、修复或扩展实验；不改 ground truth、metric 或选择规则；不启动 Writing、补实验或任何其他 Workflow。需要的补证只是提议。

## Phase 1: 建立材料账本与证据存在性

列出本次范围内的每一项，只记位置与状态，不预判支持关系：

- 待判定 Claim：原文、声明的 population／setting／metric／时间范围／比较对象、引用编号。
- 结果文件：每个引用数字对应的文件、key、值、所属 attempt、读取范围与可核对性。
- baseline：数值、出处（本地复现还是引用外部数字）、配置与数据划分；引用型标 `reported`。
- attempt 集合：成功、失败、崩溃、超时、无效、被排除的每一次；只剩 winner 汇总时回溯原始集合。
- 已有分析／审计报告：路径、版本、结论摘要；只导航，不替代本 Phase 的存在性核对。

然后对每个引用了具体数值与来源的 Claim 做**机械存在性核对**（用宿主已有读取能力逐项定位，不需审查者）：

- `verified`：文件存在且该值确实在其中。注意这只证明证据**存在**，是否**支持** Claim 由 Phase 3 判定；存在性通过不替支持判定通过。
- `path_missing`／`value_not_found`：文件不存在或值不在文件中，即为**无证据引用**——该 Claim 直接记 `unsupported（evidence-not-found）`，不再为它消耗审查调用。
- `unparseable`：引用没有可解析的值或来源；正常进入 Phase 3，但必须记录该引用缺口，不得把它当 `verified`。

文件存在不等于支持结论；缺席的 attempt 与来源保持 `unknown`，既不按通过计，也不按失败计。

**完成条件**：每个待判定 Claim 都有存在性结论与定位；缺失对象与无法建立的引用已单独列出。

## Phase 2: 统计可信度

判断支撑每个 Claim 的数字在统计上能走多远。已有 `analyze-results` 报告时采用其"不确定性／分母／偏差"结论；否则按 [判定细则](references/claim-judgment.md) 的统计部分自查，逐项给出结论、定位与影响范围：

- **重复与不确定性**：多少 seeds／runs、spread 多大、结论对哪个子集敏感；小样本的"稳定"措辞降级为单点观察。
- **选择偏差**：是否只报最佳 seed／checkpoint／子集；失败与被排除项是否可见且理由一致；winner-only 汇总必须说明分母。
- **多重比较**：试过多少 metrics／配置／子集，报告了其中几个；只报最优的写出分母。
- **失败与无效记录**：崩溃、超时、无效输出的原始位置与判定规则；事后排除明确标出。
- **数字对应**：报告数字与原始 key／值／聚合口径是否一致；比较双方配置、划分、seed 是否对齐。

一条线通过不替另一条通过：数字对应无误不能证明没有选择偏差。

**完成条件**：每个 Claim 的统计支撑强度、不确定性与分母已写明；不可重算项保持 `unknown`。

## Phase 3: 逐 Claim 范围与支持判定

逐条读 Claim 原文，把"在该固定设置观察到"与"普遍有效、因果有效、优于所有方法"分开。每个 Claim 只取其一，并给出定位：

- `supported`：证据存在、统计可信、声明范围不超出实际测试范围。
- `needs-narrowing`：部分支持——必须同时给出**缩窄后的候选表述**（更窄的 population／setting／metric／时间，或加不确定性限定），禁止停留在含糊的"部分正确"。
- `unsupported`：证据缺失、统计不可信或反证成立；写明是哪一条断裂。
- `unknown`：关键材料缺失导致无法判定；不得因没有反证而写 supported。

完整性疑虑压低上限：`experiment-audit` 报告或自查发现 fake ground truth、phantom results、代码与结果不对应或 scope overclaim 时，该 Claim 不得记 `supported`，按其性质改判或降级，并在报告中标注受完整性限制。整体置信度低（证据薄弱、独立审查不可用或分歧未解）时按不确定处理，不采用为 supported。

缩窄规则与评价类型上限（`real_gt`／`synthetic_proxy`／`simulation_only` 等对应什么 Claim 天花板）见 [判定细则](references/claim-judgment.md)。每个判定附反证／缺口：不支持或限制该 Claim 的失败记录、负结果、未测范围与最小补证动作；补实验本身不在本 Skill 内。

**完成条件**：每个待判定 Claim 都有结论、支持范围、缩窄候选（如需）、反证与缺口；最终采用仍由用户决定。

## Phase 4: 独立复核

有已授权的独立审查者时，在全新上下文中请求一次只读复核；已有不同模型可用时优先使用，不强制特定 provider。提供待判定 Claim、原始结果与 Phase 1–3 案卷的路径——绝不只给执行者摘要。提问："Do these results support the stated reading? What is the weakest link — existence, statistics, or scope?" 将实际 briefing 与完整回复保存在授权的报告位置。对照原始段落调和分歧，保留未解决的分歧；模型一致不是科学证据。

无独立审查者或超出授权时，标注输出 **single-agent assessment; independent verification not performed**。不冒充第二审查者，不反复寻求更有利的结论。

**完成条件**：实际回复已被考虑并保留，或缺失的独立验证已明确记录。

## Phase 5: 报告与停止

用 [候选 Claim 报告模板](templates/claim-report.md) 输出自然 Markdown 报告：材料账本、存在性结论、统计可信度、逐 Claim 判定与缩窄候选、反证与缺口、复核限制。报告结束后停止：未运行、未修复、未修改、未启动任何实验或 Workflow；用户决定是否采用候选、补证或进入写作。

**完成条件**：每个待判定 Claim 的结论与依据可追溯；未决缺口与复核限制如实列出。然后停止。

## 判读规则

- 文件存在不等于论断成立：结果在场只证明有输出，不证明数字正确、比较公平或结论成立。
- 分母优先：任何"最好""提升""稳定"陈述必须同时给出分母；没有分母的胜出陈述降级为单点观察。
- 缩窄必须具体：新的范围或不确定性措辞写进候选表述，不用"基本成立""大致支持"代替。
- 存在性判定驱动门槛、不断言支持：机械核对只能否决无证据引用，不能确立任何 Claim。
- 低置信度按不确定处理：材料不足、审查不可用或分歧未解时记 `unknown`／`needs-narrowing`，不因“没有反证”升级。
- 报告数字永远可被更原始的材料推翻：核对链是账本 → 原始输出 → 派生统计 → Claim，逆向回溯，顺向不升级。

## 来源

改编自 wanshuiyin / ARIS `skills/result-to-claim/SKILL.md`（MIT，`Copyright (c) 2026 wanshuiyin`；采用 revision `0472e530251cdbd3364c33b110063c58f819edd7`，当日 HEAD 一致；该目录仅此文件，无共置资源）。保留存在性与支持判断分离、三档 verdict、"单点阳性不支撑一般 Claim" 的范围诚实、完整性疑虑降级与 verdict 记录；统计与完整性检查口径复用本仓 `analyze-results`（不确定性、选择偏差、多重比较）与 `experiment-audit`（fake ground truth、phantom results、scope overclaim、评价类型）的方法。删除固定审查后端与模型路由、固定实验跟踪／远程日志来源、上游跟踪目录与 helper 脚本、机器 JSON verdict、wiki 边／pipeline 路由、自动消融与跨 Workflow 推进。完整 MIT notice 见 [LICENSE](LICENSE)。来源版本、作者与复制范围集中记录于仓库来源说明；使用本 Skill 无需访问产品仓库或上游。
