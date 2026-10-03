---
name: setup-research-os
description: "科研项目还没有项目级角色表、默认算力政策或研究工作区导航时建议一次 setup：确认当时可用模型、八个角色、零授权默认政策和缺失种子。用户也可显式调用。"
---

# Setup Research OS

这是 prompt-driven Workflow。用户显式要求初始化，或项目还没有项目级角色表、默认算力政策、研究导航时，模型可以建议运行它。建议不是写入授权。本 Skill 不调用任何研究 Workflow。

输入是当前科研项目、用户在对话中的选择，以及当时宿主列出的可用模型。位置不明时先问清楚。输出是经确认的 `.agents/research-os-models.md`、默认 `compute-policy.md`、缺失的工作区种子，以及一个 Agent 指令文件中的 Research OS 区块。

写入范围只限最后获批草稿列出的项目内文件和必要父目录。使用宿主现有读取、提问与精确编辑能力。能力不足时报告缺口并停止。不读取凭据，不配置 Python、Lean、LaTeX、GPU、SSH，不安装 Skills，不运行实验，不联网检索，不做 Git 写操作。

`~/.agents/pstack-models.md` 只可在用户要求对照时只读，禁止编辑、移动或覆盖。已存在的 `research-log.md` 整文件保留，一个字节都不改。

## 1. Explore

只读检查当前项目：

- 确认项目根目录，读取适用的项目指令和 README。
- 检查根目录 `CLAUDE.md`、`AGENTS.md`，以及已有 `## Research OS` 区块。
- 查找 `.agents/research-os-models.md`、工作区里的 `compute-policy.md`、`README.md`、`project.md`、`findings.md`、`research-log.md`。已有非空工作区优先沿用，例如 `research/`、`notes/`、`docs/research/`。
- 记录这些文件是否存在，以及角色表、政策、研究日志的当前字节。全局 `~/.agents/pstack-models.md` 只记录路径和修改时间，用来事后核对它没变。
- 区分文件、目录、符号链接与不可读对象。指令文件链接指向项目外、链接失效或访问被拒时，停止该写入。

完成条件：能列出项目根、已有导航、角色表、政策、日志、指令文件候选，以及未知项。此时没有任何写入。

## 2. 列出可用模型

向当前宿主查询本 session 真正可用的模型。Pi 用 `pi --list-models`，读出 provider、model id，以及该行 thinking 是 yes 还是 no。其他宿主用它自己的模型列表命令；命令失败或结果不含模型 id 时，说明清单未知并停止，不编造 slug。

每条候选记成 `provider/model-id`。thinking 为 no 的模型只允许 `off`。thinking 为 yes 的模型只在 `off`、`minimal`、`low`、`medium`、`high`、`xhigh`、`max` 中选择该模型实际支持的档位；清单没写具体档位时，向用户标出“档位未在清单中分开列出”，由用户选定其中一档。

完成条件：后续推荐的每个模型都能在这次命令输出里逐字找到。

## 确认模型

八个角色固定为 orchestrator、literature、ideator、implementer、analyst、prover、writer、reviewer。一次只确认一个角色，推荐放在前面：一个清单内的 `provider/model-id`，加一个该模型支持的 thinking。

Gate: model-confirm | before=role-table-write | approval=explicit-user | source=SKILL.md#确认模型

用户给出的 slug 不在本轮清单中时，停下并重新询问。未确认的模型不进入草稿，也不写入文件。八个角色都确认后，才展示整份角色表：每行 `角色: provider/model-id | thinking`，不多行、不缺行。

完成条件：八个角色各自有一条用户确认过的、且模型属于本轮清单的角色行。

## 4. Present

简述哪些文件复用、哪些缺失、哪些需要决定。推荐可见的 `research/`；已有工作区沿用。材料留在原处。

默认政策按 [compute-policy.md](templates/compute-policy.md) 整文件起草。它的额度是 0，范围和有效期是未指定。向用户说明：默认政策不是本批运行许可，不能据此启动实验或付费调用。

完成条件：用户已看到事实、建议和预计写入范围。

## 5. Ask

一次只问一个尚未决定的问题：

1. 工作区有歧义时，问沿用哪一个。没有工作区时，问是否采用 `research/`。同名文件不能当目录。
2. 项目名称或说明无法从材料确定时，只问缺失项，或允许跳过。
3. 指令文件优先已有 `CLAUDE.md`，否则已有 `AGENTS.md`。两者都有时只改前者。都没有时询问创建哪一个，也允许暂不创建。
4. 内容冲突按 [冲突与重复执行规则](references/conflicts.md) 逐项选择。角色表和政策文件若与确认稿不同，选择保留现状或整文件替换，不做半文件拼接。

完成条件：每个拟写入项的路径和冲突处理已确定。用户拒绝时零写入并停止。

## 6. Draft

读取 [基础文档种子](templates/workspace.md)、[角色表形状](templates/research-os-models.md)、[默认算力政策](templates/compute-policy.md) 和 [研究日志字段](templates/research-log.md)。只用所需部分。

向用户展示完整草稿：

- `.agents/research-os-models.md` 的全文，八行都是已确认模型。
- 工作区 `compute-policy.md` 的全文。用户没有另给一批真实授权时，使用默认模板原文。
- 缺失的导航、项目说明、findings、研究日志。日志只在文件不存在时创建。
- 指令文件中拟写入的 `## Research OS` 区块，以及保留不动的其余内容。

导航只链接已经存在或本批会创建的文件。

完成条件：每一处拟写入内容都已展示，没有隐藏文件。

## 确认写入

Gate: write-confirm | before=workspace-write | approval=explicit-user | source=SKILL.md#确认写入

询问是否按这份完整草稿写入。沉默、推荐答案、单个路径选择和“已安装”都不算同意。用户改草稿后，重新展示受影响全文再确认。用户拒绝则零写入。

若确认稿与目标文件字节相同，报告“无需写入”并停止。

完成条件：当前全文获得明确写入同意，或已停止。

## 8. Write

写入前重新读取全部目的文件。内容与 Draft 所见不一致、新建路径已经出现，或指令文件候选的优先级变了，就停止整批，回到 Ask。

按获批全文写入：

- 角色表和政策文件整文件替换。确认稿与现状字节相同时跳过。不在文件末尾追加第二套角色或第二套额度。
- 只创建缺失的导航、项目说明、findings、研究日志。研究日志已存在时不打开它来改写。
- `## Research OS` 区块原位更新一次；没有时追加一次。其他区块逐字保留。

不创建、不修改 `~/.agents/pstack-models.md`。遇到写入错误立即停止，报告已成功和未完成的文件。

完成条件：获批内容已写入且没有额外文件；或失败已报告并停止。

## 9. Verify

重新读取每个获批文件，对照确认稿的字节、角色行数、政策字段和链接目标。核对：

- `.agents/research-os-models.md` 恰好八个角色，每个模型都属于写入前那份清单。
- `compute-policy.md` 仍写明不是运行授权。
- 既有 `research-log.md` 的字节与 Explore 时相同。
- `~/.agents/pstack-models.md` 的修改时间与 Explore 时相同；本来不存在则仍然不存在。
- Research OS 区块只有一份，没有多余空目录或研究产物。

完成条件：全部获批变更已逐项核对，结果和局限已告诉用户。

## 10. Stop

告知角色表、政策和工作区导航的实际路径。重复运行只补缺失项；角色表和政策在用户确认新全文后整文件替换。到此停止，不启动研究流程。
