"""auto-pm 项目根入口 - 支持直接运行 python main.py 启动 GUI

当直接运行此文件时（如 VS Code "Run Python File"），Python 会将项目根目录加入 sys.path，
而非 auto_pm/ 目录，从而避免 auto_pm/logging/ 与标准库 logging 的命名冲突。

Windows GBK 环境下，site 模块加载含中文路径的 .pth 文件时会触发 UnicodeDecodeError，
设置 PYTHONUTF8=1 可防止此问题。对于 Rich 输出的终端编码适配，在 cli/__main__.py 中处理。
"""

from __future__ import annotations

import os
import sys

os.environ.setdefault("PYTHONUTF8", "1")

if len(sys.argv) == 1:
    sys.argv.append("gui")

from auto_pm.cli.__main__ import _fix_windows_encoding, cli  # noqa: E402

_fix_windows_encoding()
cli()
