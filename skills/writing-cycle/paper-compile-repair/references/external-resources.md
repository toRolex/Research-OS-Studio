# 必需 sibling 资源与缺失处理

`paper-compile-repair` 与 `paper-compile` 是两个独立发行的 Skill 包。完整编译修复须把 `paper-compile` 安装到同一 Skills 根目录；它是必需 sibling，而非要求先运行的另一个流程。源码树与 Skills CLI 的扁平安装都以包 slug 和相对链接定位，不依赖 `writing-cycle` 等类别目录。完整安装会把两包置于同一安装根；单独安装本包时不得假定 sibling 存在。

四个目标资源的唯一权威副本及其许可证均保留在 `paper-compile` 包；本包的轻量指针不复制内容或另立维护版本。以下是本包指向 sibling 的七条引用边（其中 diagnostics 被多个阶段复用）：

| 本包引用位置 | 相对目标 | 依赖分支 |
| --- | --- | --- |
| `SKILL.md` 的诊断步骤 | `../paper-compile/references/diagnostics.md` | 诊断分类、孤立 `.tex` 检查与据此形成修复方案 |
| `SKILL.md` 的后续轮次 | `../paper-compile/references/diagnostics.md` | 新错误的重新分类与修复决策 |
| `references/bounded-repair.md` | `../../paper-compile/references/diagnostics.md` | 有界修复的诊断顺序 |
| `references/build.md` | `../../paper-compile/references/build.md` | 路径/dirty 基线、输入闭合、安全分级、临时写域及预算门、构建 |
| `references/diagnostics.md` | `../../paper-compile/references/diagnostics.md` | 诊断分类与孤立 `.tex` 检查 |
| `references/pdf-checks.md` | `../../paper-compile/references/pdf-checks.md` | 新 PDF 与投稿规则核验 |
| `templates/compilation.md` | `../../paper-compile/templates/compilation.md` | 规范化编译/修复报告字段 |

## 缺失时只阻塞对应分支

若对应链接不可解析，不要虚构内容、跳过引用或减弱安全条件；报告缺失的 sibling/resource，并停止该资源所需的分支：

- 缺 `diagnostics.md`：可继续只读盘点并记录已有日志原文，但不能声称完成八类诊断/孤立 `.tex` 检查，不能据此形成或应用修复方案。
- 缺 `build.md`：阻塞任何基线构建、重编译，以及需要重编译验证的源稿修复。TeX 输入闭合性、完整审阅、分级安全门和现有可验证 sandbox 条件仍必须满足；禁止以宿主默认安全、空目录、权限设置或 `-no-shell-escape` 替代 sandbox。
- 缺 `pdf-checks.md`：不声称新 PDF 已核验、投稿就绪或修复闭环；需该核验才能完成的任务保持未完成/blocked。
- 缺 `templates/compilation.md`：不能声称已按规范模板交付完整编译报告；可返回明确标注缺失的简要事实状态，不伪装为模板报告。

缺失 sibling 不妨碍有效范围内的只读授权核对、路径清点或已有材料收集；但完整编译修复不能因只读前置仍可执行而被描述为单包可用。任何修复都不得在缺失必需诊断/构建资源时越过上述阻塞继续写源。
