"""Bulk-fix mypy no-untyped-def errors in test files.

This script adds type annotations to:
1. Test functions (def test_xxx) -> None
2. Top-level helper functions (def _xxx) -> Any
3. Fixture functions (def xxx) -> Generator[..., None, None] or appropriate type
4. from __future__ import annotations if missing

Usage:
    python fix_mypy_annotations.py --dry-run   # preview changes
    python fix_mypy_annotations.py             # apply changes
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent / "tests"


def has_future_annotations(content: str) -> bool:
    return bool(re.search(r"from\s+__future__\s+import\s+annotations", content))


def add_future_annotations(content: str) -> tuple[str, bool]:
    """Add from __future__ import annotations if missing. Returns (content, changed)."""
    if has_future_annotations(content):
        return content, False

    # Insert after the docstring if present, or at the top
    lines = content.split("\n")
    insert_idx = 0

    # Check for shebang
    if lines and lines[0].startswith("#!"):
        insert_idx = 1

    # Check for encoding declaration
    if insert_idx < len(lines) and "coding" in lines[insert_idx]:
        insert_idx += 1

    # Check for module docstring
    if insert_idx < len(lines) and (
        lines[insert_idx].strip().startswith('"""') or lines[insert_idx].strip().startswith("'''")
    ):
        # Find end of docstring
        docstring_delim = lines[insert_idx].strip()[:3]
        insert_idx += 1
        while insert_idx < len(lines):
            if docstring_delim in lines[insert_idx]:
                insert_idx += 1
                break
            insert_idx += 1

    # Insert after any blank lines following the docstring
    while insert_idx < len(lines) and lines[insert_idx].strip() == "":
        insert_idx += 1

    # Insert the future import
    lines.insert(insert_idx, "from __future__ import annotations")
    # Add blank line after if not already
    if insert_idx + 1 < len(lines) and lines[insert_idx + 1].strip() != "":
        lines.insert(insert_idx + 1, "")

    return "\n".join(lines), True


def fix_file(filepath: Path, dry_run: bool = False) -> int:
    """Fix a single test file. Returns number of changes made."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  SKIP: Cannot read {filepath}: {e}")
        return 0

    original = content
    changes = 0

    # Add from __future__ import annotations
    content, changed = add_future_annotations(content)
    if changed:
        changes += 1

    # Parse the AST to find functions without return annotations
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"  SKIP: Syntax error in {filepath}: {e}")
        return 0

    # Collect functions that need fixes (in reverse line order to avoid offset issues)
    fixes: list[tuple[int, int, str]] = []  # (lineno, col_offset, replacement_suffix)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip if already has return annotation
            if node.returns is not None:
                continue

            func_name = node.name
            func_line = node.lineno

            # Determine the right annotation
            if func_name.startswith("test_"):
                annotation = " -> None"
            elif func_name.startswith("_"):
                # Helper function
                # Check if it's a generator (has yield)
                has_yield = any(
                    isinstance(n, (ast.Yield, ast.YieldFrom)) for n in ast.walk(node)
                )
                if has_yield:
                    annotation = " -> Generator[Any, None, None]"
                else:
                    annotation = " -> Any"
            elif func_name == "setup_method" or func_name == "teardown_method":
                annotation = " -> None"
            else:
                # Fixtures or other functions - skip, they might need specific types
                # But check if it's a top-level fixture
                continue

            # Find the position to insert the annotation
            # The annotation goes after the closing paren of the parameter list
            # We need to find the closing paren line
            source_lines = content.split("\n")
            def_line = source_lines[func_line - 1]

            # Find the closing paren
            # Simple case: all on one line
            close_paren_line_idx = func_line - 1
            close_paren_col = def_line.rfind(")")

            if close_paren_col == -1 or ":" not in def_line[close_paren_col:]:
                # Multi-line signature - search for the closing paren
                for i in range(func_line - 1, len(source_lines)):
                    line = source_lines[i]
                    if ")" in line:
                        # Check if this line has a colon after the closing paren
                        close_idx = line.rfind(")")
                        rest = line[close_idx + 1:].strip()
                        if rest == ":" or rest == "":
                            close_paren_line_idx = i
                            close_paren_col = close_idx
                            break
                else:
                    continue  # Can't find closing paren

            # The annotation goes right after the closing paren, before the colon
            line = source_lines[close_paren_line_idx]
            before = line[:close_paren_col + 1]
            after = line[close_paren_col + 1:]

            if after.strip().startswith(":"):
                colon_idx = after.index(":")
                new_line = before + annotation + after[colon_idx:]
            else:
                new_line = before + annotation + after

            source_lines[close_paren_line_idx] = new_line
            fixes.append((close_paren_line_idx, new_line))

    if fixes:
        # Apply fixes (deduplicate by line)
        lines = content.split("\n")
        seen_lines = set()
        for line_idx, new_line in fixes:
            if line_idx not in seen_lines:
                lines[line_idx] = new_line
                seen_lines.add(line_idx)
                changes += 1

        content = "\n".join(lines)

    if content != original:
        if not dry_run:
            filepath.write_text(content, encoding="utf-8")
        return changes

    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("files", nargs="*", help="Specific files to fix")
    args = parser.parse_args()

    if args.files:
        files = [Path(f) for f in args.files]
    else:
        files = sorted(TEST_DIR.rglob("test_*.py"))

    total_changes = 0
    fixed_files = 0

    for filepath in files:
        if not filepath.is_file():
            continue
        changes = fix_file(filepath, dry_run=args.dry_run)
        if changes > 0:
            print(f"  {'[DRY RUN] ' if args.dry_run else ''}{filepath.relative_to(TEST_DIR.parent)}: {changes} changes")
            total_changes += changes
            fixed_files += 1

    print(f"\nTotal: {total_changes} changes in {fixed_files} files")
    if args.dry_run:
        print("DRY RUN - no files were modified. Remove --dry-run to apply.")


if __name__ == "__main__":
    main()