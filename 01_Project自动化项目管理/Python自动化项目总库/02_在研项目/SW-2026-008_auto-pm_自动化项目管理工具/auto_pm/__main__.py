"""auto-pm 包入口 - 支持 python -m auto_pm 执行

Windows GBK 环境下，site 模块加载含中文路径的 .pth 文件时会触发
UnicodeDecodeError 崩溃。设置 PYTHONUTF8=1 可防止此问题。
对于 Rich 输出的终端编码适配，在 cli/__main__.py 中处理。
"""

from __future__ import annotations

import os

# 强制 UTF-8 模式，防止 Windows GBK 环境下 site 模块崩溃
# 此设置影响子进程和后续的 Python I/O 操作
os.environ.setdefault("PYTHONUTF8", "1")

from auto_pm.cli.__main__ import cli  # noqa: E402

if __name__ == "__main__":
    cli()
