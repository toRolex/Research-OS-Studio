# Ticket #41 implementation notes

## 范围

#41 只加 idea-discovery 路由行与 `playbooks/idea-discovery.md`，并改本路线 README / PRODUCT-MAP / 验收场景。不实现其他路线，不改 `composition-notes.md`，不改叶 skill 正文。

## 共享合同

沿用 `.agents/notes/ticket-38-implementation-notes.md` 与 `/tmp/research-os-v2-notes/shared-contract-approved.md`。分支 `v2/ticket-41` 从 `integration/research-os-v2` 的 `50ae6aa` 起，当时与 tip 相同。

## Decisions

- 阶段审批留在叶 skill（`stage-checkpoint`、`write-path`、`scope-clarify`、`anchor-clarify`）。playbook 写 `Gates: none`，不把叶门再声明一遍。
- 「一次走完」只在用户本次调用写明并给出预算时连续执行；默认每阶段停。
- 级联用仓库根反引号路径 `skills/idea-cycle/.../SKILL.md`，并带上各叶要求再读的 references。`composition-notes.md` 只在 playbook 里点名，不把表抄进 playbook。
- 直接点名 `/idea-discovery` 仍是叶入口。`/research-os` 命中本路线才按 playbook 编排。
- 粘性：匹配后保持；用户说 new task 回到入口重匹配。

## Deviations

- 真实 arXiv 两次 `SSL_ERROR_SYSCALL`，完整候选到 Proposal 未跑通。记为 AC 待验，不补造论文或评审。
- pi 轨迹用 `--no-extensions --no-context-files`，避免改用户全局配置和本仓 AGENTS；工具未用 `--no-tools` 限制。skill 用 `--skill` 显式加载。
- 集成 tip 在实现期间从 `50ae6aa` 进到 `f94fc10`（#40 setup）。先提交本票再 merge，然后重跑静态检查。
