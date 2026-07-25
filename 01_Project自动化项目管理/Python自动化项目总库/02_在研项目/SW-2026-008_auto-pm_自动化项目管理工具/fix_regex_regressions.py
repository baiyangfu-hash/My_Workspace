"""Fix regex regressions: remove type annotations from function calls."""

from __future__ import annotations

import re
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent / "tests"


def fix_file(filepath: Path) -> int:
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return 0

    original = content
    changes = 0

    # Fix: tmp_path: Path in function calls (not in def lines)
    # Pattern: (tmp_path: Path, ...) or (tmp_path: Path) that is NOT preceded by 'def '
    # We do this by removing ': Path' from function calls

    # Strategy: find lines that are NOT def lines but contain 'tmp_path: Path'
    lines = content.split("\n")
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("def ") or stripped.startswith("class ") or stripped.startswith("@") or stripped.startswith("lambda"):
            new_lines.append(line)
            continue
        # Check if this is a function call with tmp_path: Path
        if "tmp_path: Path" in line:
            # Remove the type annotation from function call arguments
            new_line = line.replace("tmp_path: Path", "tmp_path")
            new_lines.append(new_line)
            if new_line != line:
                changes += 1
        else:
            new_lines.append(line)

    if changes > 0:
        new_content = "\n".join(new_lines)
        filepath.write_text(new_content, encoding="utf-8")

    return changes


def main():
    files = sorted(TEST_DIR.rglob("*.py"))
    total = 0
    for fp in files:
        c = fix_file(fp)
        if c > 0:
            print(f"  {fp.relative_to(TEST_DIR.parent)}: {c} changes")
            total += c
    print(f"\nTotal: {total} changes")


if __name__ == "__main__":
    main()