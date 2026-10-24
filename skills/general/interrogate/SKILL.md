---
name: interrogate
description: "对研究材料、证明或代码变更发起对抗审查：多个独立 reviewer 从不同角度挑战，主审综合具体 findings 给出有理由的判断。触发词：对抗审查、独立挑战、挑战这个、多模型审查、压力测试、找盲点、tear this apart。"
disable-model-invocation: true
---

# Interrogate

按会话实际可用的子代理能力，为本次 reviewer 集合中的每个实例派一个真正 fresh 的只读上下文。独立性来自判断前的上下文/输出隔离，不是分配人设；不同模型可增加来源多样性，但不是数学正确性证明。交付物是主审综合后的判断，不是票数或转述。本调用始终只读：不自动修订、不自动应用任何变更；后续修复由调用者按其研究委托的授权另行组织。

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

全局项目角色表 `.agents/research-os-models.md` 仍是八角色各一行，`reviewer:` 是一个模型/档位绑定，不是审查者列表。下面是本次调用的派发集合和输入边界，保存在 brief/返回报告中即可，不写第二张角色表。默认 A/B 都解析同一已确认 `Role: reviewer`，但必须分成两个 fresh 只读上下文；如实标 same-model，不能把两个实例当两个模型/家族来源。

### Reviewer dispatch contract
```json
{
  "reviewers": [
    {"id": "A", "source": "role:reviewer"},
    {"id": "B", "source": "role:reviewer"}
  ],
  "context": "fresh",
  "readonly": true,
  "reviewer_inputs": ["intent", "source_material", "rubric"],
  "reviewer_reads_peer_findings": false,
  "lead_reads_after": "all_reviewers_complete",
  "require_distinct_models": false
}
```

集合数量等于 `reviewers` 的条数，至少两条，id唯一。用户/有效原委托可提供本次集合覆盖默认值；不同模型的条目用 `source: explicit`，逐项给出真实 `model`、受支持的 `thinking` 和 `authority`（原请求/委托来源）。字段只是授权索引，不是凭它自授权限；核对原话、材料范围、次数与剩余额度后才派发。不得从其他角色的模型绑定推导 reviewer 替代权。

只有文件/角色行缺失时，才可从当前真实可用能力透明回退：把实际模型/档位及缺失原因列成本次 `source: session` 条目并记录来源。显式选定模型不可用或档位不支持时，已有明确替代授权可核验继承并披露；否则先停该派发请用户确认，不静默换模型/档位、不改角色表。行重复/格式错仍停澄清。需要多模型挑战时将 `require_distinct_models` 设为 true，并列至少两个不同且获授权的模型；不足则该请求 blocked，列缺项，不悄悄以 same-model 降级。只有同模型但能提供多个真实fresh上下文时可完成默认独立审查，不冒充多模型。工具无法隔离上下文、阻止peer输出访问，或额度不能支持所需数量时，同样 blocked，不自扮reviewer。

读取 [references/reviewer-prompt.md](references/reviewer-prompt.md)，用同一模板填入意图、审查材料、[references/rubric.md](references/rubric.md) 与 [references/code-quality-review.md](references/code-quality-review.md)（代码变更）或 [references/research-review.md](references/research-review.md)（研究材料/证明），派发给每个 reviewer，要求只读。reviewer 各自给出 findings，互相不可见。

派发前按上面的输入边界核对每份prompt：只含意图、原始材料及rubric，不含peer findings、先前reviewer摘要/裁决，也不共享reviewer输出位置的读取权限。各自完成判断前不得互读；主审仅在全部reviewer完成后取得其输出做Step 4/5综合。声明与正文若冲突则停止该派发并澄清，不能只留“独立”字样却给前序意见。

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
- Reviewer [id]: [模型/档位、角色或本次显式来源、授权依据、实际fresh上下文与隔离核对], [N findings]（每个实例一条；same-model不计为多个模型来源）

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
