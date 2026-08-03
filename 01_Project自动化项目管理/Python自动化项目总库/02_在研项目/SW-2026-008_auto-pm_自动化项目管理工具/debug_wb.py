import ast
import re


def has_future_annotations(content):
    return bool(re.search(r"from\s+__future__\s+import\s+annotations", content))

def add_future_annotations(content):
    if has_future_annotations(content):
        return content, False
    lines = content.split("\n")
    insert_idx = 0
    if lines and lines[0].startswith("#!"):
        insert_idx = 1
    if insert_idx < len(lines) and "coding" in lines[insert_idx]:
        insert_idx += 1
    if insert_idx < len(lines) and (
        lines[insert_idx].strip().startswith('"""') or lines[insert_idx].strip().startswith("'''")
    ):
        docstring_delim = lines[insert_idx].strip()[:3]
        insert_idx += 1
        while insert_idx < len(lines):
            if docstring_delim in lines[insert_idx]:
                insert_idx += 1
                break
            insert_idx += 1
    while insert_idx < len(lines) and lines[insert_idx].strip() == "":
        insert_idx += 1
    lines.insert(insert_idx, "from __future__ import annotations")
    if insert_idx + 1 < len(lines) and lines[insert_idx + 1].strip() != "":
        lines.insert(insert_idx + 1, "")
    return "\n".join(lines), True

with open(r"tests\application\test_workbench_facade.py", encoding="utf-8") as f:
    content = f.read()

new_content, changed = add_future_annotations(content)
print(f"Changed: {changed}")
print("First 10 lines of new content:")
for i, line in enumerate(new_content.split("\n")[:10]):
    print(f"{i}: {repr(line)}")

try:
    ast.parse(new_content)
    print("AST parsed OK")
except SyntaxError as e:
    print(f"SyntaxError: {e}")
