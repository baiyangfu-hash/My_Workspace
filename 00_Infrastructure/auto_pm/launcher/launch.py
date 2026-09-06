#!/usr/bin/env python3
"""Fail-closed stable launcher: verify first, then isolate release execution."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bootstrap import BootstrapError, resolve_with_fallback

_RELEASE_CHILD = (
    "import runpy, sys; release_dir = sys.argv[1]; "
    "sys.path.insert(0, release_dir); runpy.run_module('auto_pm', run_name='__main__')"
)
_UNSAFE_PYTHON_ENV = ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "PYTHONUSERBASE")


def _child_environment() -> dict[str, str]:
    env = dict(os.environ)
    for name in _UNSAFE_PYTHON_ENV:
        env.pop(name, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONNOUSERSITE"] = "1"
    return env


def main(argv: list[str] | None = None, *, container: Path | None = None) -> int:
    """Resolve and execute a release, or only resolve for isolation testing."""
    resolved_container = container or Path(__file__).resolve().parent.parent
    try:
        release_dir, slot = resolve_with_fallback(resolved_container)
    except BootstrapError as exc:
        print(f"launcher: {exc}", file=sys.stderr)
        return exc.exit_code
    print(f"launcher: release verified via {slot}: {release_dir}")
    if os.environ.get("AUTO_PM_ENTRY_RESOLVE_ONLY") == "1":
        return 0
    command = [sys.executable, "-B", "-I", "-c", _RELEASE_CHILD, str(release_dir)]
    command.extend(sys.argv[1:] if argv is None else argv)
    return subprocess.run(command, cwd=release_dir, env=_child_environment(), check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
