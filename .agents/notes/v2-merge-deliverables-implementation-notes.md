# 合并 v2/accept-deliverables 到 integration

## 范围

- 基线 `e4de7a0`。`merge --no-ff v2/accept-deliverables` tip `e473842`。未改 main，未 tag/push/PR，未关 #37。
- 先完整读报告、notes 与非归档 diff，再扫归档。rate-limit 预检后读 #37 最近评论与 #41/#43/#44/#46 标题状态。两次 GraphQL 各 cost 1；结束 core remaining 5000，graphql remaining 4965，resetAt 2026-10-03T08:55:29Z。
- Python 用 `uv run`。pre-implement 已读；本文件是合并任务 notes，不覆盖来源 notes。

## Decisions

- merge-base 就是 `e4de7a0`：来源分支已含 integration tip，只多 8 路径（报告、notes、归档、两个 source-verification 叶副本、两处链接、一个测试）。`--no-commit` 合并无冲突。
- 两份 `references/source-verification.md` 与仓库仍在的 `skills/idea-cycle/source-verification.md` 逐字相同（`cmp`）。共有文件保留。只改叶内链接，不改科研逻辑。
- 归档原 SHA `03b7925abbd4d0cb7ce57c071373be3b3d194d5f1dc76d7216a96885d3b9928e` 与报告一致。解包 2211 文件 / 197 目录；其中 1204 个是 macOS AppleDouble `._*`，真文件 1007。`evidence-hashes.json` 1005 条，不含自身与 `trace-index.json`。无 `__pycache__`、`.git`、`node_modules`、vendor。project/.pi 约 1.1MiB（安装副本）；LaTeX aux/fls/fdb 与 PNG 约 3.3MiB，是编译失败现场，不删。
- 扫描不打印值。PEM / AKIA / ghp / github_pat / Bearer / env 密钥赋值为 0。两处“URL userinfo”是 bibtex 被截断后误拼的 `github.io` 页面，host 无冒号，不是凭证。两份 Gibbs–Candès PDF 里 `sk-` 各 2 次，不满足 `sk-`+20 字母数字，是论文正文。
- 唯一清洗：`evidence/idea-sources/aci-or2.json` 的 OpenReview 抓取夹带出版商签名链接。1 条 Elsevier `X-Amz-Security-Token`/`Credential`/`Signature`，2 条 Silverchair `?token=`。值换成 `REDACTED`，算法/日期/过期/SignedHeaders 保留。只改 `evidence-hashes.json` 该条（bytes 3024983，sha256 `d5b321397defea826e26a6922e6e08219a37c6a97622467cf5f388d40ec5afe4`），缩进原格式，其余条目字节不变。作者邮箱是论文公开元数据，保留。`/Users/...` 是验收路径，保留。
- 重打包排除 AppleDouble，未删失败 trace、旧 PDF、无效 diagnostic。新 SHA-256 `4dde9d353a92057b29a7dd5f2ee10f63e356234cabb553b929cac9a0e95f6ef0`。报告末尾已改为这个 hash，并写明原 hash。
- 票不关。报告自己写明：#41 部分过（handoff 中性、逐字 todolist、UV、模型身份）；#43 产物过但 ML 编译次数越界；#44 产物过但 talk 修订门/预算失败、最终版无第三 fresh。这些不是环境阻碍。#46 仍开。
- 合并工作树 UV：`check-skills.py` OK 39（U 38 / M 1）；`unittest discover -s tests` 19；`discover -s scripts -p 'test*.py'` 43；合计 62。`git diff --check` 通过。

## 失败指针（下一个 bugfix 用，不在本次修）

1. ML 编译次数：初 3 次用尽后又第 4、5 次。证据 `evidence/writing-ml-*`，第 6 个 fresh 抓到陈旧 PDF。报告「#43 AC」表与「限制」节。
2. talk 门：初 fresh 发现 α 方向反了之后，未另确认就做 v2/第 4 次编译。总计 6 次（初 3 + 未批 interim 1 + 补救 2）。`evidence/talk-review.report.md`、`talk-review-v2.report.md`、`talk-final-review-version-check.json`。最终 PDF/script hash 与 fresh 所审不同。
3. resubmit：显式 repair 之前，scratch 诊断改了 abstract 并用 awk 丢段落，已标 INVALID。有效的只有后续 `build/repair1/paper.pdf`。
4. Idea handoff：`idea-review1` prompt 夹带“leading candidates / final proposal likely combine”。不是中性交接。
5. 逐字 todolist、idea-once 的 python3（非 UV）、idea-fixed-default 误报主模型 gpt（session 实为 glm）。trace 保留。

## Deviations

- 清洗改了归档字节，所以不能保留来源分支上的原 SHA。原值只存在未合并的 `e473842` 树里；合并提交里的包是清洗后的。
- 重打包掉了 AppleDouble。这些不是科研证据；若保留会让文件数从 1005 变成 2209 且 hash 索引对不上。
