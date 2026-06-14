"""Run QA/test scripts collected in `06_交付物/03_测试文件`.

该脚本统一在受控子进程中执行交付物目录下的测试脚本，避免乱放多个执行入口。
"""
import subprocess
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[3]
TEST_DIR = BASE / '06_交付物' / '03_测试文件'

def main():
    if not TEST_DIR.exists():
        print(f"测试目录不存在: {TEST_DIR}")
        return 1

    py_files = sorted([p for p in TEST_DIR.glob('*.py') if p.name != 'run_tests.py'])
    if not py_files:
        print("未找到可执行的测试脚本")
        return 0

    for p in py_files:
        print(f"运行: {p.name}")
        res = subprocess.run([sys.executable, str(p)])
        if res.returncode != 0:
            print(f"脚本失败: {p} (exit {res.returncode})")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
