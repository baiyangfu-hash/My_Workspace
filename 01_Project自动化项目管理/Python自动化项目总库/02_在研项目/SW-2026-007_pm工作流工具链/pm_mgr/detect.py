"""Project type detection via multi-signal heuristics."""

from __future__ import annotations

import json
import os
from pathlib import Path


def detect_project_type(project_root: str | Path) -> str | None:
    """Detect project type from directory signals.

    Priority:
    1. .plc.json  -> plc
    2. pyproject.toml -> software
    3. *.scl / *.db -> plc
    4. main.py / package.json -> software
    5. PM_SESSION context

    Returns 'software', 'plc', or None if undetermined.
    """
    root = Path(project_root).resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")

    # Signal 1: .plc.json (search up to 3 levels deep)
    if list(root.rglob(".plc.json")):
        return "plc"

    # Signal 2: pyproject.toml (search up to 3 levels deep)
    if list(root.rglob("pyproject.toml")):
        return "software"

    # Signal 3: .scl / .db files (recursive search, limited depth)
    scl_files = list(root.rglob("*.scl"))
    db_files = list(root.rglob("*.db"))
    if scl_files or db_files:
        return "plc"

    # Signal 4: main.py / package.json
    if (root / "main.py").is_file() or (root / "package.json").is_file():
        return "software"

    # Signal 5: PM_SESSION context
    for f in root.glob("PM_SESSION*.md"):
        content = f.read_text(encoding="utf-8")
        # Heuristic: if project_root path contains PLC automation keywords
        if "0100_PLC" in content or ".plc.json" in content:
            return "plc"
        if "pyproject.toml" in content or "python" in content.lower():
            return "software"

    return None


def is_empty_dir(path: str | Path, ignore_patterns: list[str] | None = None) -> bool:
    """Check if directory is empty, respecting ignore patterns.

    Patterns are glob-style (e.g., '.plc-out', '.git', '__pycache__').
    """
    root = Path(path).resolve()
    if not root.is_dir():
        return False

    if ignore_patterns is None:
        ignore_patterns = [".plc-out", ".git", "__pycache__", ".pytest_cache"]

    entries = list(root.iterdir())
    visible = [
        e for e in entries
        if not any(e.match(p) for p in ignore_patterns)
    ]
    return len(visible) == 0
