# Research OS Studio

Research OS Studio 是一套安装到现有科研项目中的 Agent Skills：把研究拆成可追踪的步骤，让 AI 生成候选结果，但把输入、验收和是否继续的决定留给用户。

## 安装

需要 Git 和 [uv](https://docs.astral.sh/uv/)。

```bash
git clone https://github.com/toRolex/Research-OS-Studio.git
cd Research-OS-Studio
uv tool install .
```

然后安装到你的科研项目：

```bash
research-os setup-research-os --project /你的/科研项目/绝对路径
```

该命令会把 Core、模板以及 Claude Code／Codex 可用的 Skills 写入项目，不会修改项目原有依赖。

## 使用

Research OS Studio 按**外循环、内循环、发布循环**组织研究。它们是三个由用户控制的工作阶段，不是自动运行的流水线：每个 workflow 完成后都会停止，只有你确认结果并显式调用下一步，研究才会继续。

### 1. 准备固定输入

安装后的 `templates/` 提供各类 Artifact 模板。以研究问题为例：

```bash
cd /你的/科研项目/绝对路径
mkdir -p inputs requests reports
cp templates/outer/research-charter.input.json inputs/research-question.json
```

编辑 `inputs/research-question.json`，写入研究问题、边界、成功标准和预算，并确保 `target.path` 与文件实际路径一致：

```json
{
  "contract": {"name": "research-os/artifact", "version": "1.1.0"},
  "target": {"kind": "git", "path": "inputs/research-question.json"},
  "type": {"name": "research-question", "version": "1.0.0"},
  "spec": {
    "question": "要研究的问题",
    "boundaries": ["明确的研究边界"],
    "success_criteria": [],
    "budget": {},
    "invariants": []
  }
}
```

计算文件的 SHA-256，并把路径与摘要写入 `requests/charter.json`：

```bash
shasum -a 256 inputs/research-question.json
```

```json
{
  "inputs": [
    {
      "path": "inputs/research-question.json",
      "sha256": "替换为实际的 64 位 SHA-256"
    }
  ],
  "output_path": "charter.json",
  "report_path": "reports/charter.json"
}
```

输入一旦固定就不要原地修改；内容变化时重新计算摘要并创建新的 request。

### 2. 外循环：确定研究方向

外循环把问题逐步收敛成可执行的研究方向：

```text
research-charter
    ↓
research-literature
    ↓
research-gap
    ↓
research-idea
    ↓
research-novelty
    ↓
research-reflect
```

- `research-charter`：固定问题、边界、成功标准和预算。
- `research-literature`：整理用户提供并固定的文献与引用；不会自行搜索互联网。
- `research-gap`：从现有证据中识别研究空白，证据不足时明确标记 unsupported。
- `research-idea`：围绕选定 gap 生成假设、方案和验证方法。
- `research-novelty`：把 idea 与已有文献进行有边界的比较，不直接宣称创新成立。
- `research-reflect`：汇总失败、不确定性与下一步选项，由用户决定继续、回退或停止。

在 Claude Code 中可显式调用：

```text
/research-charter
```

也可直接使用 CLI：

```bash
research-os workflow research-charter \
  --project "$PWD" \
  --request requests/charter.json
```

后续 workflow 使用同一命令形态，只需更换 workflow 名称和 request。前一步输出只是下一步的候选输入，不会被自动接受。

### 3. 内循环：执行和评估实验

用户从外循环选定研究方向后，可进入计算实验内循环：

```text
design-experiment
    ↓
prepare-experiment
    ↓
run-experiment
    ↓
analyze-experiment
    ↓
assess-result-to-claim
    └──────────────→ 根据结果重新设计下一轮实验
```

- `design-experiment`：固定假设、数据、controls、metrics、判据和预算。
- `prepare-experiment`：检查环境与命令，建立 attempt ledger，保留准备失败记录。
- `run-experiment`：按固定设计执行实验，记录实际结果、资源使用和失败现场。
- `analyze-experiment`：分析固定的 run 与结果文件，不隐式补跑实验。
- `assess-result-to-claim`：判断结果是否支持指定 Claim，并明确适用范围与条件。

每一轮都产生新的 Artifact。是否修改假设、扩大预算或开始下一轮，必须由用户重新确认；系统不会因结果不理想而自动重试。

数学研究可在外循环后走并列路径：先用 `math-proof` 记录普通证明与 proof gap，需要形式化验证时再显式调用 `lean-formalize`。数学路径不是第三个循环。

### 4. 发布循环：冻结可复验成果

发布循环把用户选定的研究材料整理为不可覆盖的 Publication：

```text
准备 Manuscript、PDF、Evidence 与 Assessments
    ↓
stage：固定完整成员集合
    ↓
preflight：检查文件摘要、依赖闭合与必需 gates
    ↓
用户核对最终 manifest 和 digest
    ↓
freeze-publication
    ↓
验证冻结包并停止
```

发布前应保留研究问题、实验设计、运行、分析、Claim／Evidence、评审记录和稿件等实际使用材料。调用：

```text
/freeze-publication
```

workflow 会展示最终 manifest、检查结果和形如以下内容的确认串：

```text
FREEZE <publication> SHA256 <final-manifest-sha256>
```

只有项目中具有 `user` role 的 principal 精确确认本次 digest 后才能冻结。任何文件变化都必须重新 stage、preflight 和确认。冻结只在项目中创建不可覆盖的成果包，不会自动投稿或发布到外部平台。

### 5. 检查结果

每个 workflow 通常写入一个结果 Artifact 和一个 workflow report。运行后检查：

1. 输出是否仍为 `candidate`，内容和边界是否符合预期。
2. report 的停止原因、预算使用、失败记录和建议是否准确。
3. 下一步 request 是否引用了正确路径与实际 SHA-256。
4. 需要 Git 身份的计算 handoff 是否固定了完整 40 位 commit。

可以单独验证 Artifact：

```bash
research-os validate --project "$PWD" charter.json
```

验证通过只表示结构、引用和固定关系满足契约，不代表研究结论正确；是否接受并继续始终由用户决定。

## 运行原理

1. `setup-research-os` 将 provider-neutral Skills 投影到当前 Agent 工具可识别的目录。
2. 每个 workflow 只读取用户明确指定并用 SHA-256 固定的 JSON Artifact。
3. Agent 负责研究推理，确定性 validator 负责检查结构、引用、预算和文件一致性。
4. 每个 workflow 按契约产出结果与报告，然后停止；用户验收后才能进入下一步。
5. Artifact、运行记录和最终 Publication 保存在项目中，可由 Git 追踪和恢复。
