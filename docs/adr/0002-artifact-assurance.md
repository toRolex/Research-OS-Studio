# ADR-0002：Artifact handoff 与六轴 Assurance

- 状态：已接受
- 日期：2026-09-04
- 范围：Artifact、Claim/Evidence、Assessment

## 决策

Artifact 是 workflow 和 Workstream 之间唯一规范交接接口，使用明确的 `contract{name,version}`、`target`、`type{name,version}` 和对象类型 `spec`。Artifact 的版本、provenance、relations 与 assurance 必须可审计；失败、阻塞和旧 revision 不得被新结果静默覆盖。

Evidence 与 Claim 都是一等 Artifact，P0 规范关系只有 Evidence → Claim 的 `supports`。supports 只表达在指定方法、条件和 scope 内用于支持，不代表证明、真值、全局 verified 或人类接受。

Assurance 使用六个彼此独立的维度：`structural_conformance`、`empirical_reproducibility`、`mathematical_argument_review`、`formal_verification`、`independent_review`、`human_acceptance`。Assessment 是独立、不可覆盖的 Artifact，必须保存 subject、精确 scope、verdict、method、evidence、assessor、时间和 validity。不得压缩为单一等级；同维度、重叠 scope 的有效冲突阻塞依赖 gate；新 Artifact revision 不继承旧 Assessment。

## 原因

运行成功、数学审查、Lean kernel pass、独立 review 和用户接受回答不同问题。分轴记录可以避免 assurance 混淆，并使 Workstream 之间的依赖可重放。

## 后果

- validator 必须验证关系方向、scope、冲突和 fixed target 漂移。
- 迁移和修订产生新 Artifact，不覆盖旧 fixed target。
- Publication 只能纳入明确固定的 Claim、Evidence 和 Assessments。

## 证据

`CONTEXT.md`、`PRODUCT.md`、`planning/research-os-wayfinder/resolutions/D03.md`、`planning/research-os-wayfinder/resolutions/T10.md`，以及已验证的 Artifact 原型提交 `3428eb72aa31ed532a036909e857e768441c0bcb`。
