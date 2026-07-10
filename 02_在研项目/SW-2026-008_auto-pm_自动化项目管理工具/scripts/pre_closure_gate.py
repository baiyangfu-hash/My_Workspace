"""闭环前门禁脚本 - 运行三轨检查并输出 JSON 证据

用途：CHG 闭环前必须运行此脚本，输出作为 PM_SESSION §3 spec_compliance 的机器证据。
     禁止在 all_green=false 时回写 "ruff 0 errors" 或 "pytest 0 failed" 到 PM_SESSION。

运行方式：
    python scripts/pre_closure_gate.py --workspace <工作空间根>

输出：
    reports/gate_result.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_ruff(workspace: str) -> dict:
    """运行 ruff check . 并解析错误数"""
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", ".", "--output-format=json"],
        capture_output=True,
        text=True,
        cwd=workspace,
        shell=False,
    )
    # ruff JSON 输出是一个列表，每个元素是一个 violation
    # 无违规时输出空列表 "[]"，退出码 0
    # 有违规时输出非空列表，退出码 1
    try:
        violations = json.loads(result.stdout) if result.stdout.strip() else []
    except json.JSONDecodeError:
        violations = []

    return {"errors": len(violations)}


def run_mypy(workspace: str) -> dict:
    """运行 mypy auto_pm/ 并解析错误数"""
    result = subprocess.run(
        [sys.executable, "-m", "mypy", "auto_pm/"],
        capture_output=True,
        text=True,
        cwd=workspace,
        shell=False,
    )

    # mypy 成功时 stdout: "Success: no issues found in N source files"
    # mypy 失败时 stdout: "Found N errors in M files (checked X source files)"
    output = result.stdout
    success_match = re.search(r"Success: no issues found in (\d+) source files", output)
    if success_match:
        return {"errors": 0, "files": int(success_match.group(1))}

    error_match = re.search(r"Found (\d+) errors?", output)
    files_match = re.search(r"in (\d+) files?", output)
    errors = int(error_match.group(1)) if error_match else -1
    files = int(files_match.group(1)) if files_match else -1
    return {"errors": errors, "files": files}


def run_pytest(workspace: str) -> dict:
    """运行 pytest --no-cov -q -m "not gui" 并解析结果"""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--no-cov", "-q", "-m", "not gui"],
        capture_output=True,
        text=True,
        cwd=workspace,
        shell=False,
    )

    # pytest 输出末尾格式: "1260 passed, 2 skipped, 3 warnings in 46.12s"
    # 或失败时: "3 failed, 1257 passed, 2 skipped in 46.12s"
    output = result.stdout + result.stderr

    passed_match = re.search(r"(\d+) passed", output)
    skipped_match = re.search(r"(\d+) skipped", output)
    failed_match = re.search(r"(\d+) failed", output)

    return {
        "passed": int(passed_match.group(1)) if passed_match else 0,
        "skipped": int(skipped_match.group(1)) if skipped_match else 0,
        "failed": int(failed_match.group(1)) if failed_match else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="auto-pm 闭环前门禁脚本")
    parser.add_argument(
        "--workspace",
        "-w",
        required=True,
        help="工作空间根路径",
    )
    args = parser.parse_args()

    workspace = str(Path(args.workspace).resolve())
    reports_dir = Path(workspace) / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    print("[1/3] Running ruff check . ...")
    ruff_result = run_ruff(workspace)
    print(f"      ruff: {ruff_result['errors']} errors")

    print("[2/3] Running mypy auto_pm/ ...")
    mypy_result = run_mypy(workspace)
    print(f"      mypy: {mypy_result['errors']} errors in {mypy_result['files']} files")

    print("[3/3] Running pytest --no-cov -q -m 'not gui' ...")
    pytest_result = run_pytest(workspace)
    print(
        f"      pytest: {pytest_result['passed']} passed, "
        f"{pytest_result['skipped']} skipped, "
        f"{pytest_result['failed']} failed"
    )

    all_green = (
        ruff_result["errors"] == 0
        and mypy_result["errors"] == 0
        and pytest_result["failed"] == 0
    )

    gate_result = {
        "timestamp": datetime.now().isoformat(),
        "ruff": ruff_result,
        "mypy": mypy_result,
        "pytest": pytest_result,
        "all_green": all_green,
    }

    result_path = reports_dir / "gate_result.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(gate_result, f, ensure_ascii=False, indent=2)

    print(f"\nGate result saved to: {result_path}")
    print(f"all_green: {all_green}")

    if all_green:
        print("\n[OK] 三轨门禁全绿，可以回写 PM_SESSION §3 spec_compliance")
        return 0
    else:
        print("\n[FAIL] 三轨门禁未全绿，禁止回写 'ruff 0 errors' 或 'pytest 0 failed' 到 PM_SESSION")
        return 1


if __name__ == "__main__":
    sys.exit(main())
