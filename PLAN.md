# Plan: Research OS P0

Depth: tree 5   Mode: orchestrated
Budget note: 完整产品级实现；强验证优先，禁止以 walking skeleton、空 inventory 或 BLOCKED 替代发布验收。

## Contract

- Interfaces: canonical Core 由 `core/catalog.json`、`core/contracts/**`、`core/skills/**`、`templates/**` 构成；Python 仅提供 deterministic validators、workflow execution seam、安装投影、远端适配和 Publication freeze。
- Artifact: `contract{name,version}`、`target`、`type{name,version}`、`spec`；可选仅 `title/provenance/relations/assurance`。所有领域对象均为版本化 type。
- Targets: Git 使用安全仓库相对文件路径；固定 Git 使用完整 40 字符 commit。P0 URI profile 仅规范化无 userinfo/query/fragment 的 HTTPS，并要求 SHA-256。
- Relations: 唯一规范 relation 为 Evidence 内嵌 `supports`；固定 Claim target、JSON Pointer scope、method、conditions。
- Assurance: 六轴不可线性化；scope 为 `whole_subject` 或 JSON Pointer 集；同固定 subject、同维度且 scope 前缀相交的有效冲突阻塞 gate。
- Identity: Project principals 绑定 role；`human_acceptance` 只接受 `user` role。Independent review 机械验证不同 principal、固定输入和 isolation receipt。
- Workflows: 15 个 user-invoked workflow；只读用户指定 pinned Artifact，输出 candidate + report + 可选 next steps 后停止，不调用下一 workflow。
- Disciplines: 8 个 model-invoked discipline；只能在当前 workflow 内工作，不能改语义、预算、statement、gate 或正式接受。
- Reports: Validation Report 动态记录实际 validator 名称/版本/subject/evidence，稳定退出码 `0 pass / 1 fail / 2 usage / 3 blocked external prerequisite`。
- Publication: staged manifest → deterministic preflight → final content-digest confirmation → immutable write + freeze receipt；替代、撤回、stale audit 为包外追加事件。
- Data ownership: 每个 leaf 只修改 Owns；共享 facade 仅 L10 修改。所有 Python 操作使用 UV。
- Naming: skill 目录、frontmatter name、catalog ID 完全一致；workflow 使用 `disable-model-invocation` 平台投影，discipline 不作为用户入口。

## Tree

- 1 Research OS P0 .................................... GATES.md
  - 1.1 Core and capability system .................... GATES.md
    - 1.1.1 Foundation contracts ...................... gates/leaf-foundation.md
    - 1.1.2 Domain graph contracts .................... gates/leaf-semantics.md
    - 1.1.3 Port + disciplines ........................ gates/leaf-ports.md
  - 1.2 Research workflows ............................ GATES.md
    - 1.2.1 Outer-loop workflows ...................... gates/leaf-outer.md
    - 1.2.2 Computational slice ....................... gates/leaf-computational.md
    - 1.2.3 Remote adapters ........................... gates/leaf-remote.md
    - 1.2.4 Mathematical + Lean slice ................. gates/leaf-mathematical.md
  - 1.3 Delivery boundary ............................. GATES.md
    - 1.3.1 Publication + paper/PDF ................... gates/leaf-publication.md
    - 1.3.2 Install/update/history/projections ......... gates/leaf-install.md
    - 1.3.3 Unified integration facade ................ gates/leaf-integration.md
  - 1.4 Release truth ................................. GATES.md
    - 1.4.1 Release acceptance and documentation ...... gates/leaf-release.md

## Leaves

| Leaf | Owns | Needs | Tier |
|---|---|---|---|
| L01 Foundation | `core/contracts/foundation/**`, existing artifact schemas, `src/research_os/validation/foundation/**`, `tests/contracts/foundation/**` | — | strong |
| L02 Semantics | `core/contracts/semantics/**`, `src/research_os/validation/semantics/**`, `tests/contracts/semantics/**` | L01 API | strong |
| L03 Ports | `ports/**`, 8 discipline skill dirs, `src/research_os/validation/ports/**`, `tests/ports/**` | — | strong |
| L04 Outer | outer workflow skill dirs, `src/research_os/workflows/outer/**`, `templates/outer/**`, `tests/workflows/outer/**` | L01/L02 API | strong |
| L05 Computational | 5 experiment skill dirs, `src/research_os/workflows/computational/**`, `templates/computational/**`, `reference-projects/computational/**`, `tests/workflows/computational/**` | L01/L02 API, L03 interface | strong |
| L06 Remote | `src/research_os/remote/**`, `adapters/ssh/**`, `adapters/slurm/**`, `tests/remote/**` | L05 protocol | strong |
| L07 Mathematical | math/Lean skill dirs, `src/research_os/workflows/mathematical/**`, `templates/mathematical/**`, `reference-projects/mathematical/**`, `tests/mathematical/**` | L01/L02 API, L03 interface | strong |
| L08 Publication | freeze skill, `core/contracts/publication/**`, `src/research_os/publication/**`, `templates/publication/**`, `tests/publication/**` | L01/L02 API; L05/L07 output contract | strong |
| L09 Install | setup skill, `src/research_os/install/**`, `src/research_os/history/**`, root adapter JSON, `tests/install/**`, `tests/history/**`, `tests/adapters/**` | resource manifest contract | strong |
| L10 Integration | root Python facade files, `core/catalog.json`, script, pyproject/lock, existing top-level tests, `tests/integration/**` | L01–L09 | max |
| L11 Release | `.github/**`, `tests/e2e/**`, `docs/guides/**`, README/PRODUCT/CONTEXT/ADR | L10 | max |

## Dispatch schedule

- Ready now: L01, L02（按已固定 contract 协同但文件互斥）, L03, L04, L05, L07, L09。
- Waiting: L06 needs L05；L08 needs L05/L07；L10 needs L01–L09；L11 needs L10。
- Integration policy: 叶子返回后先独立执行 gate，再进入下一叶。共享 facade 在 L10 前冻结不动。

## Status log

- 2026-09-06：创建 worktree，读取 Issue #24/#1，基线 40/40 tests pass。
- 2026-09-06：建立 GATES.md、实施 notes 与进度页。
- 2026-09-06：八维 gap audit 完成；15 个 agents 返回、1 个初审流中断但对应 hostile verification 成功。判定当前是 FAIL/NOT IMPLEMENTED。
- 2026-09-06：固定十项机械语义，写入本 Contract；本机未发现 `lean`/`lake`，但固定 Lean fixture 的真实发布验收不得以 BLOCKED 替代。
