"""PLC 项目管理工具 — 主入口

启动 PyWebView 窗口，加载 Bridge 验证页面。
"""

from __future__ import annotations

import logging
import os
import sys

import webview

from src.bridge.webview_bridge import WebViewBridge
from src.utils.logger import get_logger

# 工作空间根目录（0100_PLC自动化）
WORKSPACE_ROOT = r"C:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化"

# UI 资源目录
UI_DIR = os.path.join(os.path.dirname(__file__), "ui")


def main() -> None:
    log = get_logger(__name__)
    log.info("PLC 项目管理工具启动")

    bridge = WebViewBridge(WORKSPACE_ROOT)
    html_path = os.path.join(UI_DIR, "index.html")

    window = webview.create_window(
        title="PLC 项目管理工具",
        url=html_path,
        js_api=bridge,
        width=1280,
        height=860,
        min_size=(960, 640),
    )
    bridge.set_window(window)

    log.info("加载页面: %s", html_path)
    webview.start(debug=True)


if __name__ == "__main__":
    main()
