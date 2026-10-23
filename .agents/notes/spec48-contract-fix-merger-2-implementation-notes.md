# Spec48 #60 contract-fix merger slice 2 notes

## 状态

- 候选/来源合并：done；`64278eb1969b897079ef1716770541c6cf30757` 已快进合入，C 源 `b8ca00f38ff085ab923adf528ba75e7a3a80c135` 已 no-ff 合入；无文件冲突、无重叠路径。
- 适用串行验证：done；C 安装态 7/7、Discovery 2/2、W3 3/3、#45/#55/M/policy 29/29、全包 diff-check 通过；checker 仍为原 9 条且与基线逐字节相同。完整命令、真实 rc 与日志见 `/tmp/spec48-contract-fix-merger-2/REPORT.md`。
- notes 小提交与完整候选报告：done；最终 merge 候选 `405838e54d06e4125807b82ad8697b592a26df60`（双亲为候选 `64278...` 与 C 源 `b8ca00...`），报告 `/tmp/spec48-contract-fix-merger-2/REPORT.md`。

## 入口判定与边界

直接执行：用户明确指定本 merger 小片并禁止继续派发；只在独立 T3 worktree 串行合并已验候选与 C 源，不触碰 integration/主目录，不 push、不操作 tracker，不提前纳入 A/B 或安装路径局部 SKILL 冲突修复，不做 promotion。

## 实施决策

- 合并前 HEAD 为 `14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e` 且 clean。候选 `64278...` 是 HEAD 的后代，因此按指令以 `--ff-only` 保留其既有候选历史；其上再对 C 源 `b8ca00...` 执行 `--no-ff`，明确记录来源边界。
- C 的七个 Skill 正文及安装态测试均与实现源 `e7fcb080db6dbc3c0e505581edd89086b6835bbc` 的七个包树逐一相同；与候选变化路径无交集，合并无冲突，因此没有需要额外手工修补的交叉差异。安全门由安装态 7-test 回归及现有 D/#45 回归验证。
- C 安装态检查覆盖：只读职责、有效 batch/额度/并发、目标/假设替换确认、用户停止不可自行恢复，以及已授权调用者转交和普通中断在重新核验后按剩余额度恢复；没有把普通重试等同于新授权。
- 七个 C 包 payload 完全匹配固定源，故该源已有 Skills CLI 实测可复用；本轮又重新运行 C 的真实安装态测试。`skills/general/research-os` 与 D 已验包树对象相同（`7578ab8bb1dcab878c2dbf1235c62f7d7f920e5a`），Discovery CLI 证据亦有本轮安装态回归复验。
- #45 腐坏副本正/负 fixture 在组合测试中通过；C 源报告提及的旧 #45 脚本失败未复现，因为此轮先合入的 `64278...` 已含对应 fixture 修复。
- 完整串行验证日志存于 `/tmp/spec48-contract-fix-merger-2/logs/`；本范围不要求重跑全仓 suite，也未将 C 报告里的既有全套失败再次当成本候选失败。

## Deviations

- 无（截至首次实施记录）。
