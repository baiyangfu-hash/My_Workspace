"""Bulk-fix remaining mypy no-untyped-def errors in test files - Phase 2.

Handles:
1. Untyped *args and **kwargs parameters
2. Untyped function parameters (tmp_path, monkeypatch, etc.)
3. dict without type arguments -> dict[str, Any]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent / "tests"


def fix_file(filepath: Path, dry_run: bool = False) -> int:
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return 0

    original = content
    changes = 0

    # Fix 1: *_args -> *args: Any, **_kwargs -> **kwargs: Any
    # Pattern: def _fn(*_args, **_kwargs) -> ...:
    new_content = re.sub(
        r'(\*_args)(\s*,?\s*)',
        r'*args: Any\2',
        content
    )
    new_content = re.sub(
        r'(\*\*_kwargs)(\s*\))',
        r'**kwargs: Any\2',
        new_content
    )
    if new_content != content:
        changes += 1
        content = new_content

    # Fix 2: tmp_path without type annotation in test function signatures
    # Pattern: def test_xxx(tmp_path) -> None:
    new_content = re.sub(
        r'(def\s+test_\w+)\((\s*tmp_path\s*)\)(\s*->)',
        r'\1(tmp_path: Path)\3',
        content
    )
    # Also handle multi-param: def test_xxx(self, tmp_path) -> None:
    new_content = re.sub(
        r'(def\s+test_\w+)\((\s*self\s*,\s*tmp_path\s*)\)(\s*->)',
        r'\1(self, tmp_path: Path)\3',
        new_content
    )
    # Handle tmp_path as part of multi-param: def test_xxx(self, tmp_path, other) -> None:
    new_content = re.sub(
        r'(\btmp_path\b)(\s*,)(?!\s*:)' ,
        r'tmp_path: Path\2',
        new_content
    )
    # Handle tmp_path as last param: , tmp_path) -> None:
    new_content = re.sub(
        r'(,\s*tmp_path)(\s*\)\s*->)',
        r', tmp_path: Path\2',
        new_content
    )
    # Handle (tmp_path,) -> None:
    new_content = re.sub(
        r'(\(\s*tmp_path)(\s*,)(?!\s*:)',
        r'(tmp_path: Path\2',
        new_content
    )
    if new_content != content:
        changes += 1
        content = new_content

    # Fix 3: monkeypatch without type annotation
    # Pattern: def test_xxx(..., monkeypatch) -> None:
    new_content = re.sub(
        r'(\bmonkeypatch\b)(\s*[,\)])(?!\s*:)',
        r'monkeypatch: MonkeyPatch\2',
        content
    )
    if new_content != content:
        changes += 1
        content = new_content

    # Fix 4: dict without type arguments -> dict[str, Any]
    # Pattern: captured: dict = {} or : dict = or -> dict:
    new_content = re.sub(
        r':\s*dict\s*=\s*\{',
        ': dict[str, Any] = {',
        content
    )
    new_content = re.sub(
        r'->\s*dict\s*:',
        '-> dict[str, Any]:',
        new_content
    )
    if new_content != content:
        changes += 1
        content = new_content

    # Fix 5: Untyped inner function parameters like filter_domain=None
    # Pattern: def _xxx(param=None) -> Any:
    # This is harder to fix automatically, so we'll handle it with a simple approach
    # for common patterns
    new_content = re.sub(
        r'(def\s+_\w+)\((\s*filter_domain\s*=\s*None\s*)\)(\s*->)',
        r'\1(filter_domain: str | None = None)\3',
        content
    )
    if new_content != content:
        changes += 1
        content = new_content

    # Fix 6: proj without type in fixtures
    new_content = re.sub(
        r'(def\s+proj\()(\s*tmp_path)(\s*[,\)])(?!\s*:)',
        r'\1tmp_path: Path\3',
        content
    )
    if new_content != content:
        changes += 1
        content = new_content

    if content != original and not dry_run:
        filepath.write_text(content, encoding="utf-8")

    return changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    if args.files:
        files = [Path(f) for f in args.files]
    else:
        files = sorted(TEST_DIR.rglob("test_*.py"))

    total_changes = 0
    for filepath in files:
        if not filepath.is_file():
            continue
        changes = fix_file(filepath, dry_run=args.dry_run)
        if changes > 0:
            print(f"  {'[DRY RUN] ' if args.dry_run else ''}{filepath.relative_to(TEST_DIR.parent)}: {changes} changes")
            total_changes += changes

    print(f"\nTotal: {total_changes} changes")
    if args.dry_run:
        print("DRY RUN - no files were modified.")


if __name__ == "__main__":
    main()