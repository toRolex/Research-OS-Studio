# Gates: Research OS P0

Scope: 完整实现 Issue #24，交付可安装、可组合、用户掌握推进权的计算研究与数学研究 skills 系统，并产出论文与可追溯 Publication。

- [x] G1: Issue #24 的 canonical workflow 与 discipline inventory 全部存在，catalog、目录和 frontmatter 一致，workflow 仅用户调用、discipline 仅模型调用。
  CHECK: uv run --frozen research-os validate-repository --root .
  EXPECT: /"status"\s*:\s*"pass"/
  EVIDENCE: 2026-09-06 实测 PASS/0；15 workflows、8 disciplines，catalog 与 raw digests 无漂移。Claude projection 完整区分 user/model invocation；Codex 因不支持 discipline 私有性，普通 setup 显式安装 workflow-only scope 并固定 8 项 excluded/BLOCKED，完整 projection 请求仍 exit 3、零输出。

- [x] G2: typed Artifact、target、relation、Assessment、Publication、external reference、migration 和 port manifest 均由统一 deterministic validators 覆盖，稳定退出码为 0/1/2/3。
  CHECK: uv run --frozen python -m unittest discover -s tests/contracts -t . -v
  EXPECT: OK
  EVIDENCE: 2026-09-06 主线程复验 63 tests / OK；最终全量 408 项及 CLI/Claude/Codex parity 覆盖 Manuscript、Publication、external reference、数学 typed projections 与显式 validation context。Port release 缺失是 G7，不是 validator 缺失。

- [x] G3: 干净普通科研项目可显式安装与 setup；不会自动启动 workflow；更新及旧 commit replay 不覆盖旧 run、fixed Artifact 或 Publication。
  CHECK: uv run --frozen python -m unittest discover -s tests/install -t . -v && uv run --frozen python -m unittest discover -s tests/history -t . -v
  EXPECT: OK
  EVIDENCE: 2026-09-06 主线程复验 install 27、history 13；另 wheel/sdist/installed-history 11 项通过。Packaged RECORD、竞态不覆盖、显式 update、legacy read-only restore 与迁移回滚均覆盖。

- [x] G4: empirical-computational reference project 在本地 CPU 上逐项显式执行外循环与五个实验 workflow，经 pinned handoff、预算硬停止、失败保留、论文/PDF生成和用户确认后冻结 Publication。
  CHECK: uv run --frozen python -m unittest tests.e2e.test_e2e_computational -v
  EXPECT: OK
  EVIDENCE: 2026-09-06 最终 wheel E2E PASS；真实 CPU MSE=1.25，普通失败、预算停止、进程树清理、Claim/Evidence、PDF、digest freeze、update/history 完整闭环。

- [x] G5: mathematical-theoretical reference project 逐项显式执行 statement、普通证明、独立 review、可选 Lean、论文/PDF和 Publication；固定 Lean 工具链可用时真实 replay，不可用时结构化 BLOCKED。
  CHECK: uv run --frozen python -m unittest tests.e2e.test_e2e_mathematical -v
  EXPECT: OK
  EVIDENCE: 2026-09-06 普通数学 typed E2E PASS；另以项目外临时官方 elan 固定 `leanprover/lean4:v4.19.0`，Lean 4.19.0 commit `6caaee842e94`、Lake `5.0.0-6caaee8`；真实 `lake build`、axiom audit、statement comparator、isolated kernel replay 全部 PASS。release reference 3/3，数学 55/55；详见 `gates/leaf-lean419-reference.md`。

- [x] G6: Publication 固定唯一主要文本、封闭成员、Claim/Evidence、六轴 Assessment 与 external receipts；冻结后不可覆盖，替代/撤回只包外追加。
  CHECK: uv run --frozen python -m unittest discover -s tests/publication -t . -v
  EXPECT: OK
  EVIDENCE: 2026-09-06 主线程复验 25 tests / OK；真实 PDF、统一 registry、final digest confirmation、作者/人类接受独立门、漂移、事件原子性与第二 Publication 覆盖。

- [x] G7: 至少一项计算研究能力和一项数学研究能力以 port-first/minimal-adaptation 方式接纳，具备冻结来源、完整 commit、许可、baseline hashes、adaptation ledger、baseline/adapted eval 和人工接纳证据；无证据源码 hard block。
  CHECK: uv run --frozen research-os validate-ports --root .
  EXPECT: /"status"\s*:\s*"pass"/
  EVIDENCE: 2026-09-06 用户以 `ACCEPT PORTS person:rolex 50874399aeb2c943938f3f34acc67c81eda21e2ab0083d10072ead2e5e44f70e` 接受固定 request；8 个最终 admission/product digest 逐项重验后写入 decision receipts。`validate-ports` 实测 PASS/0、release_authorized=true、8/8 external ports accepted；`validate-repository` PASS/0。来源/许可/snapshot/ledger/detail/产品/人工决定均 digest 绑定，上游代码未执行。

- [x] G8: Claude Code 与 Codex projection 可从 canonical Core 重建；同一 fixture 的语义、报告、停止状态和退出码一致；平台能力不足时 fail-closed BLOCKED。
  CHECK: uv run --frozen python -m unittest discover -s tests/adapters -t . -v
  EXPECT: OK
  EVIDENCE: 2026-09-06 最终 wheel E2E 与独立实物安装 PASS；安装包强制验证 `core/port-release-attestation.json`，缺失或 canonical discipline 漂移拒绝。真实 Claude/Codex host execution 仍因 isolation profile 未验证而 BLOCKED，故完整文字中的 live-host 条件不勾选。

- [x] G9: SSH/SLURM 未配置时明确 BLOCKED；远端状态未知时禁止盲目重提；已配置环境的条件验收入口和证据格式完整。
  CHECK: uv run --frozen python -m unittest discover -s tests/remote -t . -v
  EXPECT: OK
  EVIDENCE: 2026-09-06 主线程复验 44 tests / OK；缺配置、unknown latch、submit/status/cancel/log/artifact receipts 与安全回收完整。真实 SSH/SLURM 环境仍 NOT_EVALUATED。

- [x] G10: 冻结 UV 环境中的完整测试、provider-neutrality、negative fixtures、catalog/projection golden 与两条 E2E 全部通过。
  CHECK: uv lock --check && uv sync --frozen && uv run --frozen python tests/e2e/run_suite.py --output /tmp/research-os-all-tests
  EXPECT: OK
  EVIDENCE: 2026-09-06 最终 Lean-enabled 完整套件 416/416 PASS、0 skip/failure/error，179.231s，exit 0；包含两个 wheel E2E、真实 Lean reference、39 个 port tests、安装 port-release attestation 与 projection inventory 负例。`uv lock --check`、`git diff --check` 均 exit 0。
- [x] G11: 文档准确覆盖安装/更新、workflow、Artifact/Assurance、Publication、migration、porting/license、Adapter 支持矩阵及两个 reference project 的复现步骤。
  EVIDENCE: README、PRODUCT、CONTEXT、五份 `docs/guides/` 与 truthful CI 已更新；过时 manuscript CLI 缺口、旧 378 计数和 canonical notes 状态已修正。

- [x] G12: 独立 harsh review 对照 Issue #24 原文未发现 blocker/critical 缺口，且所有实施偏差均记录。
  EVIDENCE: 多轮 hostile review 的 blocker 已闭环：8 disciplines/ports、真实 Lean、decision/detail binding、许可证打包、Codex inventory、bundle snapshot 投影、安装时 port-release attestation。最终 validators 与完整套件均 PASS。条件环境保持准确：Claude/Codex live host 为 BLOCKED，SSH/SLURM 为 NOT_EVALUATED，不冒充真实环境通过。