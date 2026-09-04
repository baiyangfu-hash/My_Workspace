"""GUI 冒烟测试脚本 — 启动 PyWebView 窗口并截图保存"""

from __future__ import annotations

import os
import sys
import time
import threading

from PIL import ImageGrab

# 确保项目根目录在 sys.path
sys.path.insert(0, os.path.dirname(__file__))

try:
    import webview
except ImportError:
    print("ERROR: pywebview 未安装")
    sys.exit(1)

from src.bridge.webview_bridge import WebViewBridge

WORKSPACE_ROOT = r"C:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化"
UI_DIR = os.path.join(os.path.dirname(__file__), "ui")
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "test_screenshots")

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

bridge = WebViewBridge(WORKSPACE_ROOT)
html_path = os.path.join(UI_DIR, "index.html")

window = webview.create_window(
    title="PLC 项目管理工具 — 冒烟测试",
    url=html_path,
    js_api=bridge,
    width=1280,
    height=860,
    min_size=(960, 640),
)

bridge.set_window(window)

# 截图计数
_screenshot_done = threading.Event()
_dashboard_pushed = threading.Event()


def on_loaded():
    """页面加载完成后推送 Dashboard 数据"""
    try:
        bridge.push_dashboard_data()
        print("[SMOKE] Dashboard 数据推送完成")
        _dashboard_pushed.set()
    except Exception as e:
        print(f"[SMOKE] Dashboard 数据推送失败: {e}")


window.events.loaded += on_loaded


def take_screenshots():
    """延迟截图线程：等待页面渲染完成后截图"""
    # 等待 Dashboard 数据推送
    _dashboard_pushed.wait(timeout=15)

    # 额外等待渲染
    time.sleep(3)

    # 截图 1: Dashboard 总览页
    try:
        path1 = os.path.join(SCREENSHOT_DIR, "01_dashboard.png")
        img = ImageGrab.grab()
        img.save(path1)
        print(f"[SMOKE] 截图1 (Dashboard): {path1} — size={os.path.getsize(path1):,} bytes")
    except Exception as e:
        print(f"[SMOKE] 截图1失败: {e}")

    time.sleep(1)

    # 导航到项目详情页
    try:
        window.evaluate_js("location.hash = '#/detail/DJ-2026-005';")
        print("[SMOKE] 导航到项目详情页")
    except Exception as e:
        print(f"[SMOKE] 导航失败: {e}")

    time.sleep(3)

    # 截图 2: 项目详情页
    try:
        path2 = os.path.join(SCREENSHOT_DIR, "02_detail.png")
        img = ImageGrab.grab()
        img.save(path2)
        print(f"[SMOKE] 截图2 (Detail): {path2} — size={os.path.getsize(path2):,} bytes")
    except Exception as e:
        print(f"[SMOKE] 截图2失败: {e}")

    time.sleep(1)

    # 导航到变更管理页
    try:
        window.evaluate_js("location.hash = '#/change';")
        print("[SMOKE] 导航到变更管理页")
    except Exception as e:
        print(f"[SMOKE] 导航失败: {e}")

    time.sleep(3)

    # 截图 3: 变更管理页
    try:
        path3 = os.path.join(SCREENSHOT_DIR, "03_change.png")
        img = ImageGrab.grab()
        img.save(path3)
        print(f"[SMOKE] 截图3 (Change): {path3} — size={os.path.getsize(path3):,} bytes")
    except Exception as e:
        print(f"[SMOKE] 截图3失败: {e}")

    _screenshot_done.set()
    # 截图完成后关闭窗口
    time.sleep(1)
    print("[SMOKE] 所有截图完成，关闭窗口")
    window.destroy()


# 预热缓存
bridge.preload_cache()
print("[SMOKE] 缓存预热完成")

# 在独立线程中延迟截图
threading.Thread(target=take_screenshots, daemon=True).start()

print("[SMOKE] 启动 PyWebView 窗口...")
webview.start(debug=False)

# 等待截图完成
if _screenshot_done.wait(timeout=30):
    print("[SMOKE] 冒烟测试完成 — 截图已保存到:", SCREENSHOT_DIR)
else:
    print("[SMOKE] 冒烟测试超时")

# 列出截图文件
for f in sorted(os.listdir(SCREENSHOT_DIR)):
    fpath = os.path.join(SCREENSHOT_DIR, f)
    size = os.path.getsize(fpath)
    print(f"  {f} ({size:,} bytes)")
