# resubmit

已有投稿要换 venue。新目录承接适配稿，旧投稿目录保持原样。范围确认和改动确认是 `resubmit-pipeline` 的自带门。

## 适用

用户给出旧投稿目录、目标 venue 和另一个新目录。只回复审稿走 rebuttal；只做演讲走 paper-talk。

## 阶段角色

Role: orchestrator

范围与改动确认。

Role: writer

获准适配。

Role: reviewer

只读编译／引用检查；无 fresh 时标自查。

## 步骤

1. 读 `skills/writing-cycle/resubmit-pipeline/SKILL.md` 全文。停在 adaptation-scope：用户批准新目录之前不创建、不复制、不覆盖。目标已存在、非空或指向旧稿时停止。
2. 按 `skills/writing-cycle/resubmit-pipeline/references/adaptation-methods.md` 锁定旧稿并在新目录适配模板。旧稿只读。规则缺失时保留未核实项。
3. 只读检查读 `skills/writing-cycle/paper-compile/SKILL.md`，引用检测读 `skills/writing-cycle/citation-audit/SKILL.md`。两份正文的自带门照旧生效。本步不改研究材料。
4. 停在 change-confirm。用户逐项决定之前零研究材料写入。编译修复与引用改写只记下待转交入口名 paper-compile-repair、apply-citation-fixes。本路线不打开它们的正文，也不执行它们；用户要做时另行点名。
5. 对已批准的本路线正文改动应用后，重做只读检查。报告格式用 `skills/writing-cycle/resubmit-pipeline/templates/adaptation-report.md`。
6. 交付新目录候选与报告。不向投稿系统提交、不上传、不发布。

## 停止

旧稿零变更。新目录只含本次批准的复制、适配和报告。全部拒绝时零写入。
