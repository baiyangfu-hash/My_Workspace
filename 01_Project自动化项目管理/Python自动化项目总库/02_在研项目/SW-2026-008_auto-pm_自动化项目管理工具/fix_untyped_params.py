"""Fix untyped function parameters in test files using AST.

Handles:
- tmp_path without Path type
- monkeypatch without MonkeyPatch type
- Other common untyped parameters
"""

from __future__ import annotations

import ast
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent / "tests"

# Common parameter name -> type mapping
KNOWN_TYPES: dict[str, str] = {
    "tmp_path": "Path",
    "tmpdir": "Path",
    "monkeypatch": "MonkeyPatch",
    "cli_runner": "CliRunner",
    "caplog": "LogCaptureFixture",
    "capsys": "CaptureFixture[str]",
    "capsysbinary": "CaptureFixture[bytes]",
    "capfd": "CaptureFixture[str]",
    "capfdbinary": "CaptureFixture[bytes]",
    "request": "FixtureRequest",
    "record_property": "Callable[[str, object], None]",
    "record_testsuite_property": "Callable[[str, object], None]",
    "pytestconfig": "Config",
    "recwarn": "WarningsRecorder",
}


def fix_file(filepath: Path) -> int:
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return 0

    original = content

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return 0

    # Collect all fixes: (lineno, col_offset, old_text, new_text)
    fixes: list[tuple[int, int, str, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
                if arg.annotation is None and arg.arg in KNOWN_TYPES:
                    type_name = KNOWN_TYPES[arg.arg]
                    # Find the exact position of the argument name in the source
                    arg_line = arg.lineno
                    arg_col = arg.col_offset

                    # Get the source line
                    try:
                        source_line = content.split("\n")[arg_line - 1]
                    except IndexError:
                        continue

                    # Find the argument name in the line
                    # The arg name should be at position arg_col (0-based in AST)
                    # But AST col_offset is byte offset, so we need to be careful
                    name_in_line = source_line[arg_col:arg_col + len(arg.arg)]
                    if name_in_line != arg.arg:
                        # Try to find it
                        idx = source_line.find(arg.arg, arg_col - 5)
                        if idx == -1:
                            continue
                        arg_col = idx

                    old_text = arg.arg
                    new_text = f"{arg.arg}: {type_name}"

                    fixes.append((arg_line, arg_col, old_text, new_text))

            # Handle *args and **kwargs
            if node.args.vararg and node.args.vararg.annotation is None:
                arg = node.args.vararg
                arg_line = arg.lineno
                arg_col = arg.col_offset
                try:
                    source_line = content.split("\n")[arg_line - 1]
                except IndexError:
                    pass
                else:
                    old_text = f"*{arg.arg}"
                    new_text = f"*{arg.arg}: Any"
                    fixes.append((arg_line, arg_col, old_text, new_text))

            if node.args.kwarg and node.args.kwarg.annotation is None:
                arg = node.args.kwarg
                arg_line = arg.lineno
                arg_col = arg.col_offset
                try:
                    source_line = content.split("\n")[arg_line - 1]
                except IndexError:
                    pass
                else:
                    old_text = f"**{arg.arg}"
                    new_text = f"**{arg.arg}: Any"
                    fixes.append((arg_line, arg_col, old_text, new_text))

    if not fixes:
        return 0

    # Sort fixes by line (descending) and then by column (descending) to apply from end
    fixes.sort(key=lambda x: (x[0], x[1]), reverse=True)

    lines = content.split("\n")
    changes = 0

    for line_no, col, old_text, new_text in fixes:
        line_idx = line_no - 1
        if line_idx >= len(lines):
            continue
        line = lines[line_idx]
        # Verify the text at the position
        if line[col:col + len(old_text)] == old_text:
            new_line = line[:col] + new_text + line[col + len(old_text):]
            lines[line_idx] = new_line
            changes += 1

    if changes > 0:
        new_content = "\n".join(lines)
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