# integration/research-os-v2 notes（#38 + #39）

## 范围

只合 `v2/ticket-38`（`7f4d99f`）和 `v2/ticket-39`（`9923d7d`）到 `integration/research-os-v2`。`--no-ff`，不 squash。不改原 main 工作区，不 push，不开 PR，不关票。不实现 #40 的 setup 翻转。

## Decisions

- 顺序：先 merge #38（与基线干净），再 merge #39。冲突只在 `README.md`、`skills/README.md`、`scripts/check-skills.py`。`paper-compile-repair` 自动合并：#38 的相对路径修正 + #39 的两道门。
- 清单：入口换成 `research-os`（ask-research-os 已删除），调用方式按 #39 全部标「显式」。setup 行写明仍是显式、模型主动建议由 #40 翻转，不把当前树说成已翻转。
- 英文 `docs/README-en.md` 没有冲突，但 #38 仍写 User 17 / Model 22。与中文清单不一致会把「除 setup 外全部显式」说成假话，所以同步改成 Explicit，setup 行注明尚未翻转。
- 单一 `scripts/check-skills.py`：#39 的叶门路径基线整表并入；`research-os → Gates: none` 仍走 #38 的 `EXPECTED_GATES` / `gate_problems`。setup 不进叶基线。除 setup 外缺 `disable-model-invocation: true` 或缺 `allow_implicit_invocation: false` 失败。setup 保持「当前显式 + yaml false 合法；半翻转失败」。
- 成功输出必须含「调用策略」和「门声明」，否则 #39 正例读不到合同字样。
- #38 notes 已在其分支 `git add -f`。#39 notes 原只留在票 worktree（gitignore），本合并同样 `git add -f` 拷入，避免集成后丢失叶门盘点。

## 真实行为待验

- 静态 checker 与双方单测只证明声明、链接、基线和损坏副本。不证明宿主真的停在 Gate，不证明 route-only 零副作用，不证明三宿主已登录或可委派。
- 12 条逻辑路线里，本分支路由表只有 route-only 与 custom。其余 playbook 未交付，checker 不要求它们。
- setup 仍是 `disable-model-invocation: true`。README 写「当前未全量 v2 / 尚未翻转」，不能当成 #40 已完成。

## Deviations

- 英文清单不在冲突文件里，但仍改了 User/Model 计数。不改的话中英 README 对同一 39 个 skill 给出两套调用方式。
- #39 测试仍点名已删除的 `skills/general/ask-research-os/SKILL.md`，只断言它不在叶基线常量里，不读文件。未改该测试。
- 叶正文里的「model-invoked」角色句是历史描述，不是 frontmatter。清单不再写 model-invoked；不改科研步骤正文。
