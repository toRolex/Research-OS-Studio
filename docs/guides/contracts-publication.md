# 契约、Publication、迁移与移植许可

## Artifact／target／relation

Artifact 必需且仅共享四字段：`contract{name,version}`、`target`、`type{name,version}`、对象 `spec`。可选仅 `title`、`provenance[]`、`relations[]`、`assurance[]`；省略不等于显式空数组。不在外壳增加通用 status、tags 或开放 metadata。各 contract／type／validator／migrator 独立精确 SemVer。

```json
{
  "contract": {"name": "research-os/artifact", "version": "1.1.0"},
  "target": {"kind": "git", "path": "claim.json"},
  "type": {"name": "claim", "version": "1.0.0"},
  "spec": {}
}
```

这是外壳示意，空 Claim spec **不能通过**领域 validator；完整实例由 reference 生成。

- 活 Git target 用仓库相对文件 path。fixed ref 为 `{target:{kind:"git",path,commit},sha256}`，commit 完整 40 字符；跨仓库另加无凭据 HTTPS repository URI。
- URI profile 为规范化 HTTPS，无 userinfo／query／fragment，固定内容含 SHA-256；外部不可用不能换 latest／镜像冒充原引用。
- 禁绝对路径、`.`／`..`、目录、symlink escape、缩写 commit、branch/tag/latest、fragment。
- 唯一规范 relation 是 Evidence 内的 `supports`，固定 Claim ref、`scope`、`method`、`conditions`；没有反向持久化关系、weights、weakens 或全局真值。
- scope 是 `whole_subject` 或 JSON Pointer 集。Evidence 覆盖 `/statement` 不代表覆盖一个 whole-subject Claim；冻结时要按真实范围检查，不能扩大 Evidence scope 逃过门。

## 六轴 Assurance

`structural_conformance`、`empirical_reproducibility`、`mathematical_argument_review`、`formal_verification`、`independent_review`、`human_acceptance` 互不线性化。Assessment 固定 Project、subject、dimension、scope、method、evidence、assessor、assessed_at、verdict 和 validity。verdict 为 pass/fail/inconclusive/not_applicable；validity 为 active/superseded/revoked/expired。

同固定 subject、同维度、相交 scope 的有效冲突阻止 gate，不能挑较新或较有利结论。新 revision 不继承旧 Assessment。human_acceptance 只能由 Project 中 user role principal 明确给出；independent review 另需不同 principal、固定输入与 isolation receipt。receipt 机械合规不证明 reviewer 实际独立思考。

Assessment CLI 需显式固定上下文文件：

```text
{"project": FIXED_PROJECT_REF, "evidence": [FIXED_EVIDENCE_REF]}
research-os validate --project PROJECT assessments/human_acceptance.json --context validation-context.json
```

缺 context／digest 漂移失败。validator 报告记录实际执行者版本、subject SHA-256 与证据；退出码 0/1/2/3，不能推导科学判断。

## Manuscript、真实 PDF 与 Publication

当前 publication API 支持两个 profile：empirical-computational 与 mathematical-theoretical。稿件包含标题／authors／body、贡献、Claim／Evidence、conditions／limitations、materials 与 external refs。`manuscript_text` 和 `render_pdf` 是 wheel 公共确定性 API；不要求 LaTeX，也不承诺复杂排版、学术写作或期刊格式。

`manuscript/publication/external-reference@1.0.0` 与独立数学 typed projections 已精确注册到统一 `research-os validate` registry。需要 Project、Evidence 或固定原 record bytes 的类型必须通过显式 `--context` 提供；缺失或漂移时结构化失败。直接 CLI 与两 Adapter 使用同一验证函数，不通过独立 API fallback 掩盖失败。

Publication 顺序：

1. 用户完成稿件、材料、实际 review 与 acceptance，分别验证并固定到 Git commit／digest。
2. 显式构造 publication request：唯一 primary-text、封闭 members（path／ref／role／purpose／dependencies）、Claim／Evidence、完整材料 inventory、所有条件限制、六轴 Assessment refs、external references。
3. wheel 公共 `stage_publication(project, request)` 执行 deterministic preflight；保存 stage JSON。当前没有独立 stage CLI。
4. 用户审阅**最终** manifest 与所有警告，再使用 `confirmation_text(manifest)` 对应的完整 digest 确认；仅 `FREEZE name` 不够。
5. `research-os freeze-publication --project PROJECT --manifest stage.json --principal USER --confirm EXACT_TEXT` 写入 `publications/<name>/manifest.json`、成员和 freeze receipt，已存在拒绝覆盖。
6. `verify_publication(project, name)` 检测封闭包漂移。替代／撤回／stale audit 由公共 API `append_event`／`stale_audit` 留包外追加记录，不改旧包；不承诺防恶意手工改盘。

profile 默认要求 whole-manuscript structural、independent、human，加 empirical 或 mathematical；用户添加 gates 只能加严，不能移除最低条件。普通数学 reference 明确 formal_verification=not_applicable，不把 Lean BLOCKED 改成 formal pass。

Publication 当前 typed member profile 比通用 Artifact registry 窄。外循环与计算运行、result-to-claim 输出按**原字节 material**纳入闭包，不转换成成功的 Claim／Assessment。Claim 与 Evidence 则保留规范 typed 身份。conditions／limitations 必须包含原有论证边界；不能泛化文字隐藏限制。每项外部 reference 要固定 target、purpose、required scope、retrieved_at、resolved_locator、content digest 与 license receipt；两个本地 reference 明确 external refs 为空，不伪造外部文献 receipts。

## 显式 migration

读取与验证不迁移。实际 CLI 参数：

```text
research-os migrate-artifact --project PROJECT \
  --input OLD_PATH --rules RULES_PATH --to-contract EXACT_VERSION \
  --to-type-version EXACT_VERSION --output NEW_PATH --receipt RECEIPT_PATH
```

迁移必须唯一匹配 rule／migrator 与输入输出 validators；无规则／多规则／输入不合法即停止，不串联猜测路径。成功创建新文件、新 Git commit 和 receipt，保留旧 fixed target；工具错误提交失败应回滚，已有文件不能被覆盖。兼容窗口以具体 registry 和 rule 实际支持版本为准，不宣称任意历史版本可迁移。

## Port-first 与 license 硬门

当前已存在八个 external community port 候选及八个 discipline 正文；`ports/inventory.json`、`ports/release.json` 固定来源、许可、snapshot/baseline/adapted、ledger、评价与 product allowlist。`validate-ports --root .` 使用仓库根约定；leaf validator 的 root 语义不同，不用 `--root ports` 包装结果。

这些 ports 已由用户对固定 `ports/acceptance-request.json` 作最终 digest 确认：`ACCEPT PORTS person:rolex 50874399aeb2c943938f3f34acc67c81eda21e2ab0083d10072ead2e5e44f70e`。写入 decision receipts 前逐项重验 source tuple、admission digest 与 product digest；最终 `validate-ports --root .` PASS、release_authorized=true。

接纳前逐项固定 source repo URL、完整 commit、source path、retrieval time、SPDX／license evidence、NOTICE、逐文件 baseline hashes、不可变 source snapshot、原流程与依赖、keep/modify/delete/add ledger、baseline/adapted eval、reviewer 和人工 preserve/adapt/reject 决定。评分不抵消来源／许可／越权硬门；reject 源码不得进入产品树。

公开 GitHub 仓库不自动授予复制／分发许可。当前根目录未交付可据此宣称整个 Research OS Studio 发行包采用 MIT／Apache 等统一许可证的 LICENSE，不要替项目宣布许可证。community ports 的来源／许可／评价／人工接纳则已按上述固定证据完成并通过 release gate；这不反向推导整个仓库的发行许可证。
