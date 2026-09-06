# Gates: Foundation contracts harsh re-review
Scope: Issue #24 / PLAN.md 下的 Artifact envelope、type registry、SemVer、P0 Git/URI target、schema/runtime parity、动态 Validation Report builder。

- [x] G1: leaf foundation tests 真实执行且全部通过
  CHECK: uv run --project . --directory . python -m unittest discover -s tests/contracts/foundation -v
  EXPECT: OK
  EVIDENCE: 2026-09-06 实际执行；29 tests，Ran 29 tests in 0.008s，OK。
- [x] G2: JSON fixtures 被实际加载并断言正负结果，不是仅检查文件名
  EVIDENCE: `tests/contracts/foundation/test_schema_parity.py::test_fixture_inventory_exercises_positive_and_negative_targets` 逐个 `json.loads` 四个 fixture，并同时断言 schema/runtime：fixed-uri PASS、floating-git FAIL、live-git PASS、query-uri FAIL；已随 29-test suite 通过。
- [x] G3: schema/runtime 对完整 foundation contract 矩阵保持 pass/fail parity
  EVIDENCE: Artifact 1.0.0/1.1.0 覆盖 live/fixed/cross-repo/URI、非法 path/query/version/field/spec、三类数组非法 item；Validation Report 覆盖合法、未知 verdict、BLOCKED 空 issues；所有 parity 断言通过。另验证所有 6 个 foundation/artifact schema 无 blocked/unsupported definition。
- [x] G4: pinned target 严格拒绝 branch/tag/缩写；跨仓库必须 commit；URI 必须固定 digest
  EVIDENCE: `test_targets.py` 覆盖 main/latest/7-char/大写/非 hex commit、cross-repo 无 commit/HTTP/credential/query、URI 缺失或非法 digest；host/percent/path canonical hostile cases通过。Foundation target 仅定义结构化 locator；真实 Git object/file 与 TOCTOU 解析属于 lifecycle/integration seam，未在本 leaf 冒充已验证。
- [x] G5: BLOCKED/usage/fail/pass 语义不互相冒充，报告 verdict 与 observations 一致且退出码可机械映射
  EVIDENCE: 非 PASS report 必须至少一条 issue；PASS+issues 拒绝；URI subject digest mismatch 拒绝；`exit_code_for_verdict` 实测映射 pass=0/fail=1/usage_error=2/blocked=3，未知 verdict 抛 ValueError；schema/runtime parity 通过。
- [x] G6: SemVer 与 registry 构造、排序、哈希和 snapshot deterministic
  EVIDENCE: SemVer 正负与官方 precedence 序列测试通过；registry registration-order hostile test通过；三种注册顺序 snapshot SHA-256 均为 `e7fe95b5ac5dccc02285c7e13c5c8b59409199928ead30f6bbf5619536326c10`。
- [x] G7: canonical foundation 无 provider 泄漏、自动推进或网络获取
  EVIDENCE: 对 `core/contracts/foundation/**`、`src/research_os/validation/foundation/**`、`tests/contracts/foundation/**` 执行 rg 扫描 Claude/Codex/Anthropic/OpenAI/MCP/hook/model/provider/workflow/auto-advance/requests/httpx/socket/urlopen，零命中；实现仅 `urllib.parse`，LocalSchemaValidator 明确禁止 remote `$ref`。
- [x] G8: 修改范围仅为用户允许路径；未 commit/push
  EVIDENCE: 本 reviewer 仅编辑 `core/contracts/foundation/**`、`src/research_os/validation/foundation/**`、`tests/contracts/foundation/**`、本 gate；工作树中其他并发 agent 改动保持未触碰。当前 branch `research-skills-system`；未执行 commit/push。
- [x] G9: compileall、AST、JSON parse、diff-check 通过；gate evidence 重写为真实结果
  EVIDENCE: `python -m compileall -q`、全 foundation Python `ast.parse`、foundation/artifact/fixture JSON `json.loads` 输出 `JSON_OK AST_OK COMPILE_OK`；允许范围 `git diff --check` 零输出；范围内 `find -type l` 零输出。

## Hostile findings fixed

1. HIGH：Artifact runtime 接受 `provenance/relations/assurance` 非 object item，而 schema 拒绝。独立复现加入 parity 矩阵；修复 runtime item validation。
2. HIGH：Validation Report 可输出 `blocked|usage_error|fail` 且 issues 为空，BLOCKED 可冒充有根据的外部阻塞；URI subject 外层 digest 可与 target digest 冲突。独立复现加入 `test_report.py`；修复 builder/runtime/schema parity。
3. HIGH：URI canonical profile 接受 percent-encoded dot/slash/backslash、percent-encoded host、Unicode/非法 DNS host，存在路径解释差异与 canonical ambiguity。独立复现加入 `test_targets.py`；修复 host/path normalization rejection。
4. MEDIUM：TypeRegistry 对 SemVer build metadata precedence 相等，排序退化为注册顺序，snapshot/hash 非 deterministic。独立复现加入 `test_registry_artifact.py`；增加字符串 tie-break。
5. MEDIUM：LocalSchemaValidator 对畸形 keyword 值可崩溃或空绿，且不支持报告 schema 所需条件约束。独立复现加入 `test_schema_parity.py`；增加 schema-definition fail-closed、`allOf/if/then/minItems` 支持与 symlink escape 测试。

## Hostile evidence / limits

- 测试不再空绿：fixture 内容实际加载；每个确认 finding 均先红后绿。
- 用户 workflow 推进不属于 foundation leaf；canonical foundation 扫描无 workflow/自动推进逻辑，未声称 E2E workflow PASS。
- Git target 的“pinned”在 foundation 层只机械要求 40 lowercase hex；commit object、regular blob、symlink/TOCTOU 的仓库实体验证需要 lifecycle/integration seam。本 leaf 未运行该外部 seam，未写成 PASS。
- 无外部网络、SSH/SLURM、Lean 或 provider 环境验收；均未写成 PASS。
