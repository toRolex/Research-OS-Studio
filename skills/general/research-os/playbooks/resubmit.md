# resubmit

已有投稿要换 venue。新目录承接适配稿，旧投稿目录保持原样；新建目录与既有文件的写入边界仍服从当前委托。

## 适用

用户给出旧投稿目录、目标 venue 和另一个新目录。只回复审稿走 rebuttal；只做演讲走 paper-talk。

## 阶段角色

Role: orchestrator

核对委托范围与保留待决冲突。

Role: writer

获准适配。

Role: reviewer

只读编译／引用检查；无 fresh 时标自查。

## 步骤

1. 读 `skills/writing-cycle/resubmit-pipeline/SKILL.md` 全文。写入路径继承委托；范围缺失时只展示计划。目标已存在、非空或指向旧稿时停止，不覆盖旧稿。
2. 按 `skills/writing-cycle/resubmit-pipeline/references/adaptation-methods.md` 锁定旧稿并在新目录适配模板。旧稿只读。规则缺失时保留未核实项。
3. 只读检查读 `skills/writing-cycle/paper-compile/SKILL.md`，引用检测读 `skills/writing-cycle/citation-audit/SKILL.md`。保持检查只读；当前委托已授权的编译与引用修复由对应能力按精确 diff 合同承接，不要求再次点名。
4. 按委托核对拟议改动及授权范围。独立调用按 Skill 合同确认改动；级联调用在当前委托允许范围内继续，不重复确认。超出授权的改动保留为建议并停该分支。
5. 对委托授权范围内的本路线正文改动应用后，重做只读检查。报告格式用 `skills/writing-cycle/resubmit-pipeline/templates/adaptation-report.md`。
6. 交付新目录候选与报告。不向投稿系统提交、不上传、不发布。

## 停止

旧稿始终只读；新目录只包含委托授权的复制、适配和报告。越权或预算到限时停对应动作。交付后不投稿、不上传、不发布。
