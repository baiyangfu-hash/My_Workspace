"""Old project retrofit: inject hooks + handoffs without restructuring."""

from __future__ import annotations

import shutil
from pathlib import Path


def retrofit_project(
    project_root: str | Path,
    workspace_root: str | Path,
    force: bool = False,
) -> list[str]:
    """Inject continuity mechanisms into an existing project.

    Only ADDS files, never modifies existing content (except Spec Snapshot in PM_SESSION).

    Returns list of created file paths.
    """
    root = Path(project_root).resolve()
    ws_root = Path(workspace_root).resolve()

    if not root.is_dir():
        raise ValueError(f"目录不存在: {root}")

    from .detect import detect_project_type
    project_type = detect_project_type(root)
    if not project_type:
        raise ValueError(f"无法检测项目类型: {root}")

    created: list[str] = []

    # 1. Read PM_SESSION and check lifecycle
    pm_sessions = list(root.glob("PM_SESSION*.md"))
    if not pm_sessions:
        raise FileNotFoundError(f"未找到 PM_SESSION 文件: {root}")

    pm_path = pm_sessions[0]
    pm_content = pm_path.read_text(encoding="utf-8")

    # Check lifecycle
    if not force:
        if "lifecycle: archived" in pm_content.lower():
            print(f"  项目已归档 (lifecycle: archived)，跳过")
            print(f"  使用 --force 强制执行")
            return []

    template_root = ws_root / ".trae" / "project-bootstrap" / project_type

    # 2. Inject hooks
    hooks_dst = root / ".github" / "hooks"
    if not hooks_dst.exists():
        hooks_src = template_root / "hooks"
        if hooks_src.is_dir():
            shutil.copytree(hooks_src, hooks_dst)
            created.append(str(hooks_dst))
            print(f"  + hooks: {hooks_dst.relative_to(root)}")
    else:
        print(f"  (skip) hooks 已存在")

    # 3. Create handoffs
    handoffs_dir = root / ".trae" / "handoffs"
    if not handoffs_dir.exists():
        handoffs_dir.mkdir(parents=True, exist_ok=True)
        created.append(str(handoffs_dir))
        print(f"  + handoffs: {handoffs_dir.relative_to(root)}")
    else:
        print(f"  (skip) handoffs 已存在")

    # 4. Add Spec Snapshot if missing
    from .snapshot import has_spec_snapshot, fill_snapshot_in_content
    if not has_spec_snapshot(pm_content):
        new_content = fill_snapshot_in_content(pm_content, project_type, ws_root)
        if new_content != pm_content:
            pm_path.write_text(new_content, encoding="utf-8")
            created.append(str(pm_path))
            print(f"  + Spec Snapshot 已补全")
    else:
        print(f"  (skip) Spec Snapshot 已存在")

    return created
