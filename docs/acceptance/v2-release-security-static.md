# v2 release：安全与 UV 静态独立复验

## 结论与执行版本

- **本次扫描未发现真实凭据；无需清洗。** 新整改包完整扫描、898 条逐文件 SHA 全匹配；四个已有验收归档均复核常规文件。结论限定本次规则/文件内容，不是不存在任何形式秘密的形式化保证。
- 初始执行 tip：`5efd2daffc68612def5e4660defb68db5a7780e3`。checker 39 Skill（U38/M1）、`tests/` 23、`scripts/` 43，全部 exit0。
- README/checker 两条旧承诺修复后，最终全 suite 执行 tip：`ecdddab828ef027590d1b49eb3870435bf995a71`。checker **39（U38/M1）**、`tests/` **23**、`scripts/` **45**，合计 **68 tests，全部 exit0**；`git diff --check` exit0。
- 末核时 HEAD 随主 agent 文档提交推进（先 `dc9d0de`，再 `464b272`）；相对 ecdddab 仅 acceptance/report/notes，未把 68 tests 冒充这些后续提交的重新执行。5efd2da 与末核当前 `skills` Git tree 均为 `f673b96dbf7656b091d7d15b2a7364fb6b411ec5`。本任务不重演宿主/科研行为，不据静态绿改写旧失败或科研 REVISE/WARN。

## 安全解包与扫描

先完整读 tar member metadata：拒绝绝对路径、`..`、反斜杠逃逸、重复 member、设备等特殊类型；不调用通用 tar 解压、不恢复成员权限。仅常规文件手工写入新的 `/tmp/ros-v2-release-security/extracted/`，目录/文件权限受控，不创建归档 symlink/hardlink。

| 包（`docs/acceptance/evidence/`） | archive bytes | 常规文件 / 扫描原字节 | 路径与链接 |
|---|---:|---:|---|
| `v2-accept-remediation.tar.gz` | 47,077,162 | 899 / 70,273,550 | 路径/重复/特殊/软硬链接均 0 |
| `v2-accept-deliverables.tar.gz` | 82,958,572 | 1,007 / 329,309,408 | 同上均 0 |
| `v2-accept-hosts.tar.gz` | 8,148,719 | 844 / 34,291,122 | 同上均 0 |
| `v2-accept-validation.tar.gz` | 22,334,163 | 3,003 / 112,044,027 | 无逃逸/重复/特殊/硬链接；1 contained symlink，不创建 |

validation symlink 为 `ros-v2-validation/source/CLAUDE.md` → `AGENTS.md`：解析后确在同包 root，target 是归档中的常规文件。首遍保守拒绝整个包解压，随后只读链接边界并逐常规文件读取/扫描；没有跟随真实文件系统链接。四包合计 **5,753 常规文件、545,918,107 原字节**。另用 `pdftotext` 检查 28 PDF 文本（整改11、deliverables17），以及 1,211 JSON/JSONL 文件中的 78,004 转义字符串补核高置信度凭据形式，无新增强候选。

扫描类别：私钥 PEM/OpenSSH、Bearer/Basic、provider API key、JWT、URL userinfo、API-key/password/secret/token/authorization 赋值、签名 URL 与 X-Amz/X-Goog 查询参数。**输出仅类别/路径/行/计数与无值形态；未输出候选值，未清洗任何材料。** 公开论文作者邮箱不是凭据，不因论文标题页联系邮箱改变原文。

### 候选分类（不是发现真实秘密）

| 包 | 初筛候选 | 复核结果 |
|---|---:|---|
| remediation | 16 credential-assignment | 11 是同一批准 prompt 文件路径的重复原轨迹；1 是科学授权叙述；3 是 formula-derivation 正文写入授权后的动词；1 是 archive-evidence.py 扫描正则源码。全部 false positive |
| deliverables | 13 credential-assignment；9 signed-url-query | 13 为写入/compute 科学许可正文与重复原轨迹；9 为旧 publisher URL：token/Security-Token/Credential/Signature 共5处已 REDACTED，另4处仅算法、日期、signed headers、期限。无可用签名/凭据 |
| hosts | 2 credential-assignment；4 bearer | 2 为用户写入许可原话；4 均 `setup-native/codex/stdout.jsonl:29` CLI help 的 JWT bearer 自然语言说明，非认证值 |
| validation | 104 credential-assignment | 批次授权 ID、授权文档定位、许可/到期状态、正文流程动词及其 trace 重复；另1是 release.yml 引用宿主 secrets 的环境变量模板，非展开值 |

共148初筛命中；按唯一匹配形态、原来源语境及重复 trace 分组复核，**真敏感0**。原始候选 metadata 在 scratch，报告不搬运值或整条 session。

## 新整改包 SHA 与 manifest

- archive SHA-256：`ffc305f4c1a94bd9ae6ea31f344de3736f47800b5f8593beb6091077b45e329a`，与原验收报告声明一致。
- root：`ros-v2-remediation/`；manifest：`evidence/SHA256SUMS.json`。解析898项，每个相对路径先核 containment，再读实际内容计算 SHA-256：**898/898 匹配**，missing/mismatch/unsafe/unlisted 全0。899常规文件中唯一不自列者就是 manifest 本身。
- 其余 archive 本次计算 SHA-256（本页记录，不宣称已重验其所有历史 manifest）：
  - deliverables：`4dde9d353a92057b29a7dd5f2ee10f63e356234cabb553b929cac9a0e95f6ef0`
  - hosts：`cab141490a54d13564d27723a6f8cfcff726d555698da26668111d0eb3cefa9e`
  - validation：`dc4ae3ef5f4d012cfefe908abe69f0c4818a8dbc6ad8634c7bd4268a1e065f91`

## 可复验命令与日志

环境：UV **0.12.22**、`uv run python` **3.14.4**。所有 Python（包含验收侧一次性扫描）都由 UV 执行；不新建产品 runtime/validator、不改 main/全局。

```sh
uv run python scripts/check-skills.py
uv run python -m unittest discover -s tests -p 'test*.py' -v
uv run python -m unittest discover -s scripts -p 'test*.py' -v
git diff --check
```

scratch：`/tmp/ros-v2-release-security/`。基线日志 `checker.txt`、`tests.txt`、`scripts-tests.txt`；最终 `checker-final.txt`、`tests-final.txt`、`scripts-tests-final.txt`、`final-tip.txt`；安全侧 `archive-summary.json`、`validation-supplement.json`、`manifest-result.json`、`candidates-all.json`、`decoded-scan-summary.json`。这些是验收侧本地证据，不是产品协议。独立因果 notes：`.agents/notes/v2-release-security-static-implementation-notes.md`。

本 agent 只写本报告与独立 notes；未 commit、未 gh、未改共用 report，未执行清洗/发布/关票。后续新包或代码变更需由主 agent 再做有界末验。

## 新组合包末验：gate（独立追加）

收到主 agent 的最终 hash 稳定通知后，执行 tip `eaa76f07f9488e26a11af58894c65c80e4e88041`，只在新 `/tmp/ros-v2-release-security/new-packs/` 检查，不覆盖旧提取。

- `evidence/v2-release-gate-combinations.tar.gz`：**12,544,022 bytes**；SHA-256 **`2291c39cbe506db6fa90c11e684e5047d9300ebd813d35496d5942e6cbb3efc1`**，扫描前后相同。
- 577常规文件、35,203,600原字节全scan；4PDF文本、104JSON/JSONL内110,656解码字符串按全部凭据规则scan。成员路径、重复、特殊类型、软硬链接均0。
- `ros-v2-release-gates/evidence/SHA256SUMS.json` 为576项字典，每项包含SHA与bytes；逐payload路径containment后实际核**576/576 SHA+bytes双匹配**。payload共35,108,790bytes；missing/mismatch/unlisted均0，唯一自列豁免manifest本身。初次扫描器不支持这一manifest形态，随后实际核并扩展scratch脚本；没有把unsupported算通过。
- 5规则候选均false positive：`evidence/issue-37.cached.json` 原字节1处与解码1处为旧auth存在性探测说明；formula-derivation正文144–146行3处为写入许可后的动作动词。**真实敏感0，无清洗。** 未输出候选值。
- 日志：`new-gate-scan.txt`、`new-packs/gate-manifest-result.json` 与无值候选metadata。此追加不重跑tests；最后产品全suite由主 agent 执行。

## 新宿主包末验：host（独立追加）

主 agent 授权开始并随后确认包已最终稳定；执行 tip仍 `eaa76f07f9488e26a11af58894c65c80e4e88041`。新提取以archive hash命名，不覆盖gate或旧归档。

- `evidence/v2-release-host-regression.tar.gz`：**15,807,902 bytes**；SHA-256 **`d80e120694d7623533e253798550a43d8b61b6eea78592a5df388a2063a4cadc`**，开始/完成/晚核三次相同。
- 928常规文件、**57,045,065原字节**全scan；456JSON/JSONL内**341,503解码字符串**按全部规则scan，无PDF。成员路径、重复、特殊类型、软硬链接均0。
- `ros-v2-release-hosts/evidence/SHA256SUMS.json`：927条payload SHA+bytes实际双核**927/927匹配**；missing/mismatch/unlisted全0，manifest本身是唯一自列豁免。
- 11 credential-assignment候选全部false positive：archive.py:17两处扫描正则；experiment-plan/claude/stdout.jsonl及对应host-session两份相同科研预算授权叙述，各raw+decoded合4处；input-37.json旧auth存在性说明raw+decoded共2处；formula正文144–146行3处动作动词。**真实敏感0，不清洗，不打印值。**
- 日志：`new-host-scan.txt`、`new-packs/v2-release-host-regression-summary.json`、`new-packs/v2-release-host-regression-candidates.json`。独立安全末验不把归档完整性转成所有45次CLI行为都成功；空斜杠调用与timeout等行为失败仍由宿主报告原样记录。

两新包共1,505常规文件、92,248,665原字节；新manifest合计1,503 payload全部SHA+bytes匹配。追加仅报告/notes，无新tests/runtime/validator；最终全suite/提交由主 agent处理。
