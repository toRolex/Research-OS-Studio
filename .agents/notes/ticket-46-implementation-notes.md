# Ticket #46 implementation notes

## 祖先

开工时 `v2/ticket-46` 与 `integration/research-os-v2` 都是 `97f185e`。报告前 tip 未前进，没有可 merge 的新提交。

## Decisions

- Seam A 仍只有 `scripts/check-skills.py`。本票只加三个公开函数：`release_route_problems`、`stale_promise_problems`、`host_fallback_problems`，由仓库扫描直接调用。
- 测试期望值是 14 行路由字面量和两句旧承诺，不从实现再推导。
- 旧承诺 sweep 只改产品入口：根 README、英文 README、验收指南 experiment-bridge 第 6 条。叶 skill description 里的「产出后停止」留在叶合同，不在本票改写。
- 许可证、原子切换清单、历史审计里的 `ask-research-os` 继续按 #38 的迁移例外保留。
- 验收事实写 `docs/v2-release-acceptance.md`。因果写本文件。外部轨迹留在 `/tmp/ros46-install-k0vn`。
- 三宿主安装用临时项目 `--copy`。`file:` URL 被 `127.0.0.1:7890` 断开后，改 `git clone --local`。不用 `--global`。
- 行为只跑低消耗只读。pi 用 `cliproxy/glm-5.3-flash` thinking off。Codex 显式 `deepseek-v4.1-flash` 且 reasoning low。Claude 请求 haiku，JSON 用量却是 `gpt-6-luna` 与 `glm-5.3-flash`，按 JSON 记录。

## Deviations

- 不把前票 `/tmp` 轨迹算进本票通过格。#41、#43 本来就缺完整交付；#42、#44、#45 的轨迹没有在 `97f185e` 上重跑。
- Codex 在只读夹带执行词时推荐了 experiment-plan。正文已写只读优先。一次失败不改 playbook 去追这个样本。
- pi 串行降级只读了入口和 experiment-plan playbook，没有读叶 skill。记为未走完，不补造已读。
- 因此不打 `v2.0.0`，不关 #37–#46，不 push，不开 PR。
