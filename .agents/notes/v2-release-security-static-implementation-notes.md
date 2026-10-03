# v2 release security/static 独立复验 notes

## 范围

- 执行基线：`5efd2daffc68612def5e4660defb68db5a7780e3`。只写独立报告与本 notes；不 commit/gh/修改共用 report；不碰 main/全局。
- 新 scratch：`/tmp/ros-v2-release-security`。Python 一律 `uv run`；无项目 runtime/validator 新增。
- 安全扫描只输出路径、行、类别与计数，候选值不输出；真敏感先通知主 agent，协调前不清洗。公开论文作者邮箱不归凭据。

## 决策

- 先核 tar 路径、重复成员、链接/特殊类型，再只手工抽出常规文件到 scratch，避免 tar 路径逃逸。验收侧一次性扫描程序只存 scratch，不进入产品。

## 执行结果与复核决策

- 5efd2da 基线 checker39/U38/M1、tests23、scripts43 全 exit0；收到主 agent 的 README/checker TDD 修复通知后在 ecdddab 再全跑：23+45=68 与 checker 全 exit0。末核 HEAD 已因主 agent 文档提交前进，报告不偷换执行 tip；skills tree 不变。
- 新整改包899常规文件（898 payload+manifest）逐字扫描，manifest898/898全匹配，archive SHA与来源报告一致。其余旧包同时扫描；合计5753常规文件545918107原字节、28PDF文本。
- validation有1同root软链接：首轮保守拒绝解包；核目标为包内AGENTS.md常规文件后，仅逐常规文件读取和抽出，软链接不创建。避免安全验收为了方便而跟随symlink。
- 148规则候选按唯一来源/匹配形态复核，全为科学授权文案/路径/状态、regex与环境变量模板、已REDACTED signed URL、安全无值元数据。真敏感0，不改归档。
- 给主 agent 的中间说明曾过早将hosts4Bearer猜成token字段/脱敏值；随后局部无值语境精确核为CLI help JWT bearer自然语言说明，已发送更正。报告采用精确结论。
- 补scan1211 JSON/JSONL、78004转义string，无新增高置信度private key/provider key/JWT/userinfo/Basic候选。扫描程序仅scratch一次性审查，不进入仓库或产品。
- 最终报告：docs/acceptance/v2-release-security-static.md；不commit/gh/动共用report/清洗。

## Deviations

- `astral-sh/uv` skill 不在当前可用列表；没有改全局或安装，继续用已有 UV。
- 一次递归逐JSON string补核耗时超过60秒被终止（已完成所有原字节扫描不受影响）；改用一次有界转义string补核高置信度类别，120秒内完成，未无限重试。日志不输出候选值。
