# Gates: Release acceptance

Scope: Research OS P0 本地产品构建、发行实物与 truthful conditional boundaries。

## 验收账本（2026-09-06）

- [x] R1: 完整测试收集并执行
  CHECK: uv run --frozen python tests/e2e/run_suite.py --output /tmp/research-os-all-tests
  EVIDENCE: 38 test files，416/416 PASS，0 skip/failure/error，179.231s。

- [x] R2: 计算 CPU 产物闭环
  EVIDENCE: wheel→setup→六外循环→五实验 workflow→MSE=1.25→失败/预算硬停→Claim/Evidence→稿件/PDF→digest freeze→update/history。

- [x] R3: 普通数学与固定 Lean 闭环
  EVIDENCE: statement revision、ordinary proof、独立 review、Publication；官方隔离 elan 的 Lean 4.19/Lake 真实 build、axiom audit、statement comparator、kernel replay PASS；数学 55/55。

- [x] R4: Community ports 与许可证
  CHECK: uv run --frozen research-os validate-ports --root .
  EVIDENCE: 用户确认 acceptance request `50874399aeb2c943938f3f34acc67c81eda21e2ab0083d10072ead2e5e44f70e`；8/8 external ports accepted，release_authorized=true。MIT/Apache-2.0 与修改归属随 wheel 发行资源。

- [x] R5: Repository 与安装发布门
  CHECK: uv run --frozen research-os validate-repository --root .
  EVIDENCE: PASS/0。wheel 强制验证 bundled port-release attestation；缺失或 discipline 漂移拒绝。独立 UV venv wheel setup PASS。

- [x] R6: Adapter 与 provider-neutrality
  EVIDENCE: Claude 完整投影；Codex workflow-only，disciplines 明确 BLOCKED；projection inventory 拒绝额外/改名 skill。Core 无 provider policy 泄漏。

- [x] R7: Publication 与历史
  EVIDENCE: typed Manuscript、真实 deterministic PDF、六轴 Assurance、final digest confirmation、不可覆盖 Publication、包外追加事件、显式 update 与完整 commit restore。

- [x] R8: 冻结依赖与构建实物
  EVIDENCE: `uv lock --check`、`git diff --check`、wheel build 均 PASS。wheel SHA-256 `b7ebe3854aaa8119731b13f1267bc8a56919e819da0914187258bd0c30088f6e`。

## 条件环境，不冒充 PASS

- Claude Code／Codex live model execution：缺 verified isolation profile，结构化 BLOCKED。
- SSH／SLURM 真实环境：NOT_EVALUATED；协议实现与 44 tests PASS，未配置凭据、未提交作业。
- Linux CI：workflow 已固定，当前实测平台为 macOS arm64；不声称本会话已运行 GitHub Linux runner。

本地 P0 产品构建完成。未 commit、未 push、未 merge。
