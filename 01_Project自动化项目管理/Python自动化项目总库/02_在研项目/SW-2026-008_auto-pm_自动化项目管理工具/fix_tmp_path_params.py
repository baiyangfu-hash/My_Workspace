"""Fix tmp_path without type annotation in function signatures (def lines only)."""

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

    lines = content.split("\n")
    new_lines = []

    for line in lines:
        stripped = line.strip()
        # Only process def lines
        if stripped.startswith("def "):
            # Fix: tmp_path without type annotation in function signatures
            # Pattern: (tmp_path) or (tmp_path, ...) or (..., tmp_path) or (..., tmp_path, ...)
            # But NOT tmp_path: Path (already annotated)
            new_line = re.sub(r'\btmp_path\b(?!\s*:)', 'tmp_path: Path', line)
            if new_line != line:
                new_lines.append(new_line)
                changes += 1
            else:
                new_lines.append(line)
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