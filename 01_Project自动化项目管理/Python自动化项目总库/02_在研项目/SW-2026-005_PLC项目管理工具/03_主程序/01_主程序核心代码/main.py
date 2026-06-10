"""PLC 项目管理工具 — 主入口

启动 PyWebView 窗口，加载 Bridge 验证页面。

环境变量:
    PLC_WORKSPACE_ROOT  工作空间根目录（默认弹出选择对话框）
    PLC_DEBUG           调试模式开关（true/false，默认 false）
"""

from __future__ import annotations

import logging
import os
import sys

try:
    import webview
except ImportError:
    print("=" * 60)
    print("错误: 缺少 pywebview 依赖")
    print()
    print("请运行以下命令安装:")
    print("  pip install pywebview>=5.0")
    print()
    print("如果已安装但仍报错，请确认当前 Python 环境:")
    print(f"  当前解释器: {sys.executable}")
    print(f"  Python 版本: {sys.version}")
    print("=" * 60)
    sys.exit(1)

from src.bridge.webview_bridge import WebViewBridge
from src.utils.logger import get_logger

# UI 资源目录
UI_DIR = os.path.join(os.path.dirname(__file__), "ui")

# 调试模式：从环境变量读取（默认 false，打包后即为生产模式）
_DEBUG = os.environ.get("PLC_DEBUG", "false").lower() in ("true", "1", "yes")


def main() -> None:
    log = get_logger(__name__)

    # 工作空间：优先环境变量，否则留空（前端会提示用户选择）
    initial_workspace = ""
    env_root = os.environ.get("PLC_WORKSPACE_ROOT")
    if env_root and os.path.isdir(env_root):
        initial_workspace = env_root

    bridge = WebViewBridge(initial_workspace)
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

    # pywebview 6.x 使用事件绑定替代 create_window 的 loaded 参数
    def on_loaded():
        """页面加载完成后推送 Dashboard 数据（evaluate_js 推送模式）"""
        if initial_workspace:
            try:
                bridge.push_dashboard_data()
                log.info("Dashboard 数据推送完成")
            except Exception as e:
                log.warning("首次 Dashboard 数据推送失败: %s", e)

    window.events.loaded += on_loaded

    # 预热项目列表缓存，确保 Dashboard 首次加载时无需等待扫描
    if initial_workspace:
        log.info("预热项目列表缓存...")
        try:
            bridge.preload_cache()
            log.info("项目列表缓存预热完成")
        except Exception as e:
            log.warning("项目列表缓存预热失败（不影响启动）: %s", e)

    log.info("PLC 项目管理工具启动, workspace=%s, debug=%s", initial_workspace or "(待选择)", _DEBUG)
    webview.start(debug=_DEBUG)


if __name__ == "__main__":
    main()
