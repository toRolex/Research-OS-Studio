# Gates: Publication and paper
Scope: 双 profile manuscript/PDF 与不可覆盖、可追溯 Publication；仅 L08 文件。

- [x] G1: publication tests pass
  CHECK: `uv run --frozen python -m unittest discover -s tests/publication -v`
  EXPECT: OK
  EVIDENCE: 2026-09-06，25 tests / 18.552s / OK，无 skip。先观察 renderer、Publication API、schemas 缺失失败；再实现。独立复核三项缺陷均补测试观察 red 后修至 green。
- [x] G2: 唯一主文本、封闭成员、Claim/Evidence closure、Assessments、external receipts、final digest confirmation 与包外事件完整
  EVIDENCE:
  - `test_publication.py`: 两 profile；实际 bytes digest；canonical manifest digest 与 receipt；新 Publication 不改变旧包；精确确认、用户身份、漂移拒绝；离线 external 内容/license/log receipts；notice/retract/stale-audit 包外追加。
  - `test_negative.py`: 冲突不能隐藏；缺失/错误 scope/过期/不确定/not_applicable/失败 gate；假 commit、越界/别名/符号链接/目录；原子无覆盖（含空目录）；篡改 receipt/额外成员；真实第二 Publication supersede；缺失上游 stale；错误 JSON fail-closed。
  - 顾问发现并已修复：失败 cleanup 路径重解析越界；事件写失败占用最终名；伪 receipt 掩盖 Manuscript 作者自审。新增目录交换/fsync 故障注入与作者反例全部通过。
  - 追加 hostile P2 修复：opaque material/PDF 的 independent review 不解析 JSON；固定 typed Manuscript 才比较真实作者。回归先复现失败再修通过。事件另注入 exclusive link 已可见之后的 parent fsync 失败，证明最终路径清理且可重试。
  - `test_renderer.py`: 真实 `%PDF-1.4`、正确 xref/页数、确定性、安全 literal escaping；本机 Poppler `pdftotext` 独立解析恢复原文本，实际执行未 skip。最小 renderer 明确拒绝非 ASCII 字形，不静默损失。
  - `test_reference_handoff.py`: 临时目录实际运行 computational CPU reference；数学现有 statement/proof/review/Lean sources 按实际 file bytes 冻结。语义/run digest 不混同 SHA-256。此证据不是完整安装/CLI/Lean E2E。
  - `test_schemas.py`: 两 typed schema 离线校验及未知字段拒绝；两 profile 模板不伪造接受。

## 交付边界

- Public seam: `research_os.publication`；stage/preflight/freeze/verify/append_event/stale_audit、Manuscript validator/文本投影/PDF renderer。
- Profile 必需 gates 为 whole-Manuscript 的 structural、independent、human，加 empirical 或 mathematical；这是 profile 1.0.0 保守最低发布策略，不是六轴评分。自定义 gates 只能增加。所有六轴 refs 均显式保留；`[]`=未纳入 Assessment，显式 `not_applicable`=作者记录的不适用结论，不能代替必需 pass。API 不合成任何 Assessment；测试 pass fixtures 不代表默认接受。
- 上游 computational candidate Evidence 与数学 review record 不直接视为规范 Evidence/Assessment。原 bytes 按 material 保留，用户另行提供规范 Artifact 与真实完整 Git commit。禁止自动人类接受、伪造 commit、联网补源。
- 原子不覆盖目录发布支持 Darwin/Linux；其他平台 fail-closed。文件权限不是防恶意手工修改的承诺；`verify_publication` 检测封闭包漂移。
- shared CLI/core 由集成 leaf 接线，本 leaf 未修改；旧单成员 freeze 不能冒充新 staged profile。

## 非本 leaf 验证结果

- 2026-09-06：当前并行修改下 `tests/test_walking_skeleton.py` 为 13/14；`test_output_race_preserves_concurrent_file` 得 2、期望 1。超出 Owns，已通知主会话，未改。
- Ruff 未执行：`uvx ruff` 获取未声明外部包被权限门拒绝；未绕过或修改依赖/配置。
- 未 commit/push。验收不声称整个 P0、shared CLI 或真实 Lean E2E 已通过。
