# Research OS Studio

可安装到普通科研项目的 provider-neutral Agent Skills、typed Artifact 契约、确定性 validators 与薄 Adapter。用户逐个调用 workflow；输出 candidate／报告／下一步选项后停止，无中央 planner、自动科研循环或隐式接受。

**当前是已通过本地 P0 构建与发布门的候选实现。** 实测 catalog 为 **15 workflows、8 disciplines**；八项 community ports 已由用户对固定 acceptance request 作最终 digest 接纳，`validate-repository` 与 `validate-ports` 均 PASS。固定 Lean 4.19 reference 已真实 PASS。Claude/Codex live host 与 SSH／SLURM 真实环境仍是条件性 NOT_EVALUATED，不影响本地 Core/skills 构建完成，但不能据此声称真实宿主或集群验收。

## 安装与开始

需要 Git、[uv](https://docs.astral.sh/uv/)、Python 3.12+。开发／验收环境使用已有锁文件。

```bash
git clone https://github.com/toRolex/Research-OS-Studio.git
cd Research-OS-Studio
uv lock --check
uv sync --frozen
uv build --wheel --out-dir /tmp/research-os-dist
uv venv /tmp/research-os-tooling
uv pip install --python /tmp/research-os-tooling/bin/python /tmp/research-os-dist/research_os-0.1.0-py3-none-any.whl
uv run --no-project /tmp/research-os-tooling/bin/research-os setup-research-os --project /absolute/research-project
```

这里 wheel 安装使用 UV 的独立环境接口，不修改科研项目依赖。setup 从已安装 wheel 校验资源来源，复制 Core／templates／references 并生成项目级 Claude Code／Codex projection；不启动研究、不自动更新，不安装全局专用 runtime。不要把 dirty checkout 当成已验证安装来源。通用 Skills 复制入口、更新和历史恢复见[安装指南](docs/guides/installation.md)。

每一步 request 由用户指定和固定，不能把前一步的建议当作授权。

```bash
# request 文件的完整可运行实例由 reference 验收保存，见下方指南。
uv run --no-project /tmp/research-os-tooling/bin/research-os workflow research-charter \
  --project /absolute/research-project --request requests/charter.json
uv run --no-project /tmp/research-os-tooling/bin/research-os validate \
  --project /absolute/research-project charter.json
```

退出码：`0 pass`、`1 validation failure`、`2 usage/configuration error`、`3 blocked external prerequisite`。结构通过不是研究正确或 human acceptance。

## 文档

- [安装、显式更新、历史恢复](docs/guides/installation.md)
- [15 workflows 与准确 CLI](docs/guides/workflows.md)
- [Artifact／target／relation／Assurance、Publication、migration、ports 与 license](docs/guides/contracts-publication.md)
- [Adapter capability／support matrix](docs/guides/support-matrix.md)
- [计算与数学 reference 复现、证据边界](docs/guides/references.md)
- [领域词汇](CONTEXT.md)、[产品范围](PRODUCT.md)、[发布验收记录](gates/leaf-release.md)

## 验收

在仓库根运行。收集 runner 检查所有测试文件均已进入 suite，输出逐项 ID 与真实计数，拒绝零测试、重复 ID、import errors 和漏收集。

```bash
uv sync --frozen
uv run --frozen python tests/e2e/run_suite.py --collect-only --output /tmp/research-os-counts
uv run --frozen python tests/e2e/run_suite.py --e2e --output /tmp/research-os-e2e
uv run --frozen python tests/e2e/run_suite.py --output /tmp/research-os-all-tests
# 综合环境发布门当前预期返回非零：本地 Core／ports／Lean 为 PASS，但真实 SSH／SLURM 为 NOT_EVALUATED、live host execution 为 BLOCKED；不能忽略后声称完整环境发布获准。
uv run --frozen python tests/e2e/check_release.py --output /tmp/research-os-release-gates
```

两 reference 的产物线从真实 wheel/setup 经显式 CLI、固定输入、稿件／真实 PDF，到最终 digest 确认和不可覆盖 Publication，再显式更新与旧 commit 恢复。固定研究／review／acceptance 输入仅为 fixture，不代表真实模型评审或学术接受。Manuscript、Publication、external reference 与数学 typed projections 已接入统一 `validate` registry，并由直接 CLI 与两 Adapter 共用。

CI 固定 UV／Python／Action revision、使用冻结锁安装并保存计数和证据。固定 Lean 4.19 reference 已用项目外临时官方 elan 完成真实 build/audit/comparator/replay。第三方许可证与修改归属随 `core/licenses/ports/` 进入发行资源；community ports 已由用户对 `ports/acceptance-request.json` 的固定 digest 作最终接纳，并由安装时 bundled release attestation 强制绑定 canonical disciplines。
