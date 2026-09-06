# Gates: Install history projections
Scope: 普通项目安装/更新/历史恢复及 Claude/Codex 薄投影。
- [x] G1: install/history/adapter tests pass
  CHECK: uv run python -m unittest discover -s tests/install -v && uv run python -m unittest discover -s tests/history -v && uv run python -m unittest discover -s tests/adapters -v
  EXPECT: OK
  EVIDENCE: 2026-09-06 macOS arm64 / UV Python 3.14.4 最终竞态与 packaged-artifact rerun：install 27、history 13、adapters 11，合计 51 tests；三组均 OK。Linux renameat2 分支尚未实机验证，不记 Linux PASS。
- [x] G2: 安装不引入专用全局 runtime/lockfile；旧记录不覆盖；平台不足 fail-closed
  EVIDENCE: `tests/install/test_install.py` 覆盖 runtime/lock/environment 文件拒绝、显式环境更新、旧文件保留；`tests/history/test_history.py` 固定 commit 恢复并保留 failed run；`tests/adapters/test_projections.py` 证明 Codex 缺 discipline private visibility 时 exit 3、outputs/next_steps 为空。未运行真实 Claude Code/Codex host；不得据此记 host PASS。
- [x] G3: source pin、逐文件原子发布、保留路径与 provider 边界均有真实负面测试
  EVIDENCE: hostile review 先复现并修复：mutable checkout 冒充 pin、source ancestor symlink、install parent swap/concurrent destination、history output-parent symlink/final publish clobber、Codex 未定义 visibility 冒充 private。独立回归位于 `tests/install/test_install.py`、`tests/history/test_history.py`、`tests/adapters/test_projections.py`；canonical setup 仅陈述 host-neutral controls，provider 配置保留在 adapters/projector。
- [x] G4: deterministic TOCTOU hooks，文件/目录发布不覆盖并发拥有者，错误为 fail/1
  EVIDENCE: RED→GREEN 实际复现：最终文件出现前 bytes 已完整写入并 fsync；link 发布时抢占目标；dirfd 遍历/最终发布点换 symlink；预检 open 前删除/换 symlink/FIFO；第二文件失败时首文件被同 bytes/异 inode 替换；history 发布前空目录抢占与 staging 名称替换。均无 sleep/概率循环；保留原 symlink、gitlink、legacy/history tests。macOS 实跑 renameatx_np(RENAME_EXCL)；原语不可用测试 fail/1，无 os.replace fallback。归档已含 `.research-os/history-restore.json` 的 RED→GREEN 回归证明预检 fail/1，目标与新增父目录均不创建。UV compileall（install/history 源码及测试）与 git diff --check 均 exit 0。
  BOUNDARY: 防非协作公共名称竞态；不声称抵御恶意同 UID 篡改私有 0700 staging，亦不声称目录 fd 可阻止持有目录被第三方移出原树。所有写入/发布相对已持有 no-follow directory fd，换 symlink 不重定向写入；父目录身份异常 fail。
  CLEANUP: 无 inode+bytes 原子条件 unlink，公共已发布名称一律不自动回滚删除。失败可能保留完整已发布文件及私有 staging，返回 cleanup_required 与检查路径；不是整次安装事务原子性。仅成功路径私有 staging 在 fd/inode/bytes 匹配后清理；身份异常停止清理。history 失败 staging 亦保留，绝不 rmtree 他人替换物。
- [x] G5: packaged-artifact 来源机械校验，不冒充 exact Git
  EVIDENCE: `PackagedBundleTests` 正向覆盖 RECORD wheel 布局、真实 `uv pip install --target` wheel、真实 `uv venv` 后 `uv pip install --python` wheel；标准 `../../../bin/fixture-research-os` hash/size 验证通过但不复制/执行，外部脚本篡改拒绝。完整 RECORD raw digest 与 logical resource inventory digest 写入 provenance；name/version 来自已校验 METADATA，`source_revision=null`，`baseline_revision` 仅 informational。install/verify manifest roundtrip 通过，Git profile 历史测试仍通过。
  NEGATIVE: tampered resource/code、missing、weak hash、wrong size、editable、no RECORD、额外/未映射关键资源、symlink、hardlink、重复/别名 RECORD、mapping 逃逸/别名、调用方自报 source_verified 均拒绝。顾问指出的任意外部 RECORD、关键根普通文件/子树 FIFO 已 RED→GREEN 修复。`source_verified` 为 init=False，仅验证 constructors 设真。
  BOUNDARY: 包内 critical roots `_core/_adapters/_templates/_reference_projects` 必须目录且全部常规资源明确映射；hash 证明安装 artifact 与 RECORD 一致，不证明发行者真实性或 Git exact commit。跨 site-packages RECORD 仅支持可验证 pyvenv 布局的 `../../../bin/<name>`，其他/system 布局 fail-closed。本次只交付 constructor/manifest seam，L10 facade 接入验收另记，不借此声明 wheel CLI E2E PASS。
