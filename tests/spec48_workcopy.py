"""Copy only Git-tracked working files for Spec48 checker counterexamples."""
import os
import shutil
import subprocess
from pathlib import Path


def copy_tracked_tree(source: Path, dest: Path) -> None:
    """Keep current tracked contents, including force-tracked notes, not local evidence."""
    paths = subprocess.run(
        ["git", "ls-files", "-z"], cwd=source,
        check=True, capture_output=True, timeout=30,
    ).stdout.split(b"\0")
    # Some callers pass the already-created, empty TemporaryDirectory itself.
    dest.mkdir(exist_ok=True)
    for entry in paths:
        if not entry:
            continue
        relative = Path(os.fsdecode(entry))
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, target, follow_symlinks=False)
