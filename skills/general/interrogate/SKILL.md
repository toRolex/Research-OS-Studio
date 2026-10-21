---
name: interrogate
description: "对研究材料、证明或代码变更发起对抗审查：多个独立 reviewer 从不同角度挑战，主审综合具体 findings 给出有理由的判断。触发词：对抗审查、独立挑战、挑战这个、多模型审查、压力测试、找盲点、tear this apart。"
disable-model-invocation: true
---

# Interrogate

按会话实际可用的子代理能力，每个已配置 reviewer 模型派一名独立 reviewer，从独立角度对抗审查研究对象。对抗信号来自模型多样性，不是分配人设。交付物是主审综合后的判断，不是票数或转述。本调用始终只读：不自动修订、不自动应用任何变更；后续修复由调用者按其研究委托的授权另行组织。

## 委托继承

Gates: none

由 `/research-os` 委托级联进入时，本次审查继承调用者的研究委托：目标、权限、研究额度与完成条件沿用，读这份正文不再重复请求批准。独立调用时，用户给出的审查对象、意图与输出位置就是本次授权范围；本能力默认只读，因此不写研究材料、不改稿、不提交修复。委托内的修复由编排者按授权另行分派给修复类能力（如 proof-repair、research-improvement），审查结论是那份授权的输入，不是修复本身。

## Step 1，定范围

从上下文确定审查对象：

- 用户点名具体文件、diff 或论文/证明材料，就用那些。
- 在功能分支上，取 `git diff <base>...HEAD` 全量变更。
- 审查研究材料时，打包原命题、定义、依赖引理、证明主体与已知边界条件；只给结论不给推导的「证明」要如实标注为未给出。

把材料与 reviewer 需要的周边上下文一起提供给每个 reviewer。

## Step 2，意图

派发前，用一段话从用户原话、commit 信息、材料本身写出「这次变更/这份论证想达成什么」。写不清就先问用户，再继续。

## Step 3，派独立 reviewer

**子代理前提**：按当前会话实际可调用的子代理工具判定，不按宿主品牌推定。没有子代理工具时，本技能标 blocked 并说明缺口，只给主入口能做的只读建议；不由编排者串行代跑冒充独立审查。用户仍可只读地自行审查，但那不是本技能的多 reviewer 机制。

reviewer 模型从项目角色表 `.agents/research-os-models.md` 的 `reviewer:` 行解析，一行一个独立 reviewer，标注 Reviewer A、B……与行数对应。角色表缺失时如实说明没有可用的多 reviewer 配置，用当前会话可用模型中最少两个不同来源发起，并在结论中记录实际使用的模型；只有一个模型可用时如实报告「未能构成独立审查」，不把单模型自查说成已去重的独立 findings。正文引用写成 `Role: reviewer`。不给 reviewer 指定固定人设；模型配置不可用时停在该步，不改写角色表。

读取 [references/reviewer-prompt.md](references/reviewer-prompt.md)，用同一模板填入意图、审查材料、[references/rubric.md](references/rubric.md) 与 [references/code-quality-review.md](references/code-quality-review.md)（代码变更）或 [references/research-review.md](references/research-review.md)（研究材料/证明），派发给每个 reviewer，要求只读。reviewer 各自给出 findings，互相不可见。

## Step 4，综合 findings

结果返回后拼统一图景：解析每份 findings；把描述同一问题的不同表述合并去重，并记录每个问题由哪些模型提出。两个以上模型独立提出的是最高信号。单个模型的 finding 也要读，但按单来源计权重。**分歧保留**：一个模型提出、另一个明确提出相反结论或明确否认的，如实记入 Agreement Map，作为判断的上下文，不静默丢弃，也不靠表决判定对错。

对研究材料，模型重合只是审查信号，不是数学证据：共识不改变「该断言是否已被证明」的判断，见 [references/research-review.md](references/research-review.md)。

## Step 5，主审判断

你是主审（lead reviewer）：务实的资深研究者/工程师，不是中立转述器。读 [references/lead-judgment.md](references/lead-judgment.md) 的完整框架。每条 finding 归入四桶之一，附提出它的模型与一行理由：

- **Act on**：就当前目标而言真实影响正确性、严谨性或可维护性的问题；会挡住真实的交付。
- **Consider**：成立但代价/收益尚不确定，值得用户注意。
- **Noted**：技术上对但此处不可操作。
- **Dismissed**：错误、吹毛求疵或缺乏上下文，附简短理由。

判断必须有据：引用 finding 的具体内容与材料位置，不凭票数或模型权威下结论。

## 输出格式

### Intent
> [Step 2 的意图段]

### Reviewers
- Reviewer [label]: [模型名], [N findings]（每个 reviewer 一条）

### Act On
[每条：描述、哪些模型提出、为何要紧。]

### Consider
[每条：描述、哪些模型提出、代价权衡。]

### Noted
[简列。]

### Dismissed
[每条附理由。]

### Agreement Map
[模型在哪里一致、在哪里分歧；分歧按原文保留双方陈述。]
