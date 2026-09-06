# Gates: Unified integration
Scope: CLI/catalog/repository validation/projection/package 单一真源。

- [x] G1: repository validation passes
  CHECK: uv run --frozen research-os validate-repository --root .
  EXPECT: /"status"\s*:\s*"pass"/
  EVIDENCE: 2026-09-06 最终实测 PASS/0；15 workflows、8 disciplines，catalog 无漂移；8 accepted ports 与 canonical products digest 绑定。

- [x] G2: 全部 unit/integration/E2E tests pass
  CHECK: uv run --frozen python tests/e2e/run_suite.py --output /tmp/research-os-all-tests
  EXPECT: OK
  EVIDENCE: 最终 Lean-enabled 416/416 PASS，0 skip/failure/error，179.231s。

- [x] G3: 独立 wheel 安装、sdist 重建与历史回归
  EVIDENCE: wheel build PASS；独立 UV venv 的真实 wheel setup PASS；安装包含 port-release attestation、第三方许可证与 Claude/Codex projections。旧安装、update、history、legacy read-only tests 均在完整套件通过。

- [x] G4: port release 与安装绑定
  CHECK: uv run --frozen research-os validate-ports --root .
  EXPECT: /"release_authorized"\s*:\s*true/
  EVIDENCE: 8/8 external ports accepted。安装入口机械验证 bundled `core/port-release-attestation.json`；缺 attestation 或 canonical discipline 漂移均拒绝，不能用 RECORD 自洽绕过人工接纳。

## 最终边界

- Claude Code：完整 workflow/discipline projection；live execution 无 verified isolation 时 BLOCKED。
- Codex：workflow-only，8 disciplines 明确 excluded/BLOCKED；额外或改名 skill 注入触发 projection inventory failure。
- 未执行上游社区代码；未自动启动 workflow；未 commit/push。
