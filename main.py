"""Workspace root entry routed to the stdlib stable launcher only.

The parent intentionally does not import ``auto_pm``.  The launcher resolves
and exact-verifies a release before a separate ``-B -I`` child imports it.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    launcher = Path(__file__).resolve().parent / "00_Infrastructure" / "auto_pm" / "launcher" / "launch.py"
    if not launcher.is_file():
        print(f"root entry: stable launcher missing: {launcher}", file=sys.stderr)
        return 2
    return subprocess.run([sys.executable, "-B", str(launcher), *sys.argv[1:]], check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())