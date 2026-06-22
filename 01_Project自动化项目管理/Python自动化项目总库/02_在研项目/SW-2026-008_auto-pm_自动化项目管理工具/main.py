"""auto-pm 统一主入口

智能路由：
    python main.py                  # 无参数 → 启动 GUI 桌面应用
    python main.py gui              # 显式启动 GUI
    python main.py project list     # CLI 子命令
    python main.py --help           # 查看所有命令

等价于已安装的 `auto-pm` 命令（pyproject.toml: [project.scripts]）。
"""

from __future__ import annotations

import sys

from auto_pm.cli.__main__ import cli


def main() -> None:
    """统一入口：无参数时默认启动 GUI，否则走 CLI"""
    # sys.argv[0] 是脚本自身，长度为 1 说明没有传入任何参数
    if len(sys.argv) == 1:
        sys.argv.append("gui")

    cli()


if __name__ == "__main__":
    main()
