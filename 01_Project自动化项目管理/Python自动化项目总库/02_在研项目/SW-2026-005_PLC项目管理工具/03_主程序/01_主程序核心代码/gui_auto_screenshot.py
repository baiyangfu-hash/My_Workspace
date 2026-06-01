# -*- coding: utf-8 -*-
"""
GUI 自动化截图工具 - SW-2026-005 PLC项目管理工具

功能：
  1. 启动 main.py 作为子进程
  2. 等待 GUI 窗口出现并完全渲染
  3. 截取窗口截图保存为 PNG
  4. 输出诊断信息（窗口标题/尺寸/DPI/字体等）

用法：
  python gui_auto_screenshot.py [--wait N] [--output DIR] [--mode light|dark]
"""
import sys
import os
import time
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


def check_dependencies():
    """检查依赖库是否可用"""
    missing = []
    try:
        import win32gui
        import win32ui
        import win32con
    except ImportError:
        missing.append("pywin32 (pip install pywin32)")
    
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow (pip install Pillow)")
    
    if missing:
        print(f"❌ 缺少依赖: {', '.join(missing)}")
        print("正在自动安装...")
        for dep in missing:
            pkg = dep.split("(")[0].strip()
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])
        print("✅ 依赖安装完成，请重新运行")
        return False
    return True


def find_window(title_pattern="PLC项目管理工具", timeout=15, interval=0.5):
    """
    查找目标窗口
    
    Args:
        title_pattern: 窗口标题关键字
        timeout: 超时时间(秒)
        interval: 轮询间隔(秒)
    
    Returns:
        (hwnd, title) 或 (None, None)
    """
    import win32gui
    
    start = time.time()
    while time.time() - start < timeout:
        def callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title_pattern in title:
                    results.append((hwnd, title))
                    return False
            return True
        
        results = []
        win32gui.EnumWindows(callback, results)
        if results:
            return results[0]
        time.sleep(interval)
    
    return None, None


def capture_window(hwnd, output_path):
    """
    截取指定窗口并保存为 PNG
    
    Args:
        hwnd: 窗口句柄
        output_path: 输出文件路径
    
    Returns:
        dict: 截图元数据
    """
    import win32gui
    import win32ui
    import win32con
    from PIL import Image
    
    # 获取窗口尺寸
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top
    
    # 创建设备上下文
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    
    # 创建位图对象
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    
    # 截图
    saveDC.SelectObject(saveBitMap)
    result = saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
    
    # 转换为 PIL Image
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1
    )
    
    # 保存
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(str(output_path), 'PNG')
    
    # 清理资源
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    
    return {
        "path": str(output_path),
        "size": (width, height),
        "file_size": output_path.stat().st_size if output_path.exists() else 0,
    }


def get_process_info():
    """获取当前系统进程信息（用于查找 python 进程）"""
    import psutil
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            info = proc.info
            if info['name'] and 'python' in info['name'].lower():
                cmdline = info.get('cmdline') or []
                if any('main.py' in str(c) for c in cmdline):
                    processes.append({
                        "pid": info['pid'],
                        "name": info['name'],
                        "cmdline": " ".join(cmdline[:3]),
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return processes


def main():
    parser = argparse.ArgumentParser(description='GUI 自动截图工具')
    parser.add_argument('--wait', type=int, default=5, help='等待GUI渲染时间(秒)')
    parser.add_argument('--output', type=str, default=None, help='输出目录')
    parser.add_argument('--mode', type=str, default=None, help='主题模式(light/dark)')
    parser.add_argument('--timeout', type=int, default=20, help='查找窗口超时时间(秒)')
    args = parser.parse_args()
    
    # 设置路径
    base_dir = Path(__file__).parent
    src_dir = base_dir / "src"
    sys.path.insert(0, str(src_dir))
    sys.path.insert(0, str(base_dir))
    
    # 输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_dir = Path(args.output) if args.output else base_dir / "data" / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    output_path = screenshot_dir / f"gui_{timestamp}.png"
    
    print("=" * 60)
    print("📸 GUI 自动截图工具 - SW-2026-005")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return 1
    
    # 启动应用
    main_py = base_dir / "main.py"
    if not main_py.exists():
        print(f"❌ 找不到 main.py: {main_py}")
        return 1
    
    print(f"\n[1/4] 🚀 启动应用: {main_py.name}")
    print(f"     等待时间: {args.wait}秒 | 超时: {args.timeout}秒")
    
    env = os.environ.copy()
    if args.mode:
        # 临时修改设置来强制指定主题
        settings_path = base_dir / "data" / "settings.json"
        import json
        settings = {}
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        settings['theme'] = args.mode
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        print(f"     主题模式: {args.mode}")
    
    proc = subprocess.Popen(
        [sys.executable, str(main_py)],
        cwd=str(base_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print(f"     进程 PID: {proc.pid}")
    
    # 等待 GUI 渲染
    print(f"\n[2/4] ⏳ 等待 GUI 完全渲染...")
    time.sleep(args.wait)
    
    # 查找窗口
    print(f"\n[3/4] 🔍 查找目标窗口...")
    hwnd, title = find_window(timeout=args.timeout)
    
    if not hwnd:
        print(f"     ❌ 在 {args.timeout}秒内未找到窗口!")
        proc.terminate()
        return 1
    
    print(f"     ✅ 找到窗口!")
    print(f"     标题: {title}")
    print(f"     句柄: {hwnd}")
    
    # 获取窗口信息
    import win32gui
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    w, h = right - left, bottom - top
    print(f"     尺寸: {w}x{h}")
    print(f"     位置: ({left}, {top})")
    
    # 截图
    print(f"\n[4/4] 📷 截图中...")
    meta = capture_window(hwnd, output_path)
    
    print(f"\n{'=' * 60}")
    print("✅ 截图完成!")
    print(f"{'=' * 60}")
    print(f"  文件路径: {meta['path']}")
    print(f"  图片尺寸: {meta['size'][0]}x{meta['size'][1]}")
    print(f"  文件大小: {meta['file_size'] / 1024:.1f} KB")
    print(f"  时间戳: {timestamp}")
    
    # 额外信息：尝试获取字体和DPI信息
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtGui import QGuiApplication
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        screen = QGuiApplication.primaryScreen()
        if screen:
            geo = screen.geometry()
            dpr = screen.devicePixelRatio()
            dpi = screen.logicalDotsPerInch()
            print(f"\n  屏幕信息:")
            print(f"    分辨率: {geo.width()}x{geo.height()}")
            print(f"    DPI缩放: {dpr:.2f}x")
            print(f"    逻辑DPI: {dpi:.0f}")
        
        font = app.font()
        print(f"  应用字体:")
        print(f"    字体族: {font.family()}")
        print(f"    字号: {font.pointSize()}pt")
        print(f"    像素大小: {font.pixelSize()}px")
    except Exception as e:
        print(f"  ⚠️ 无法获取Qt信息: {e}")
    
    # 保持进程运行以便查看
    print(f"\n💡 应用仍在运行(PID:{proc.pid})，可手动查看效果")
    print(f"   按 Ctrl+C 终止进程")
    
    try:
        proc.wait(timeout=300)  # 最多等待5分钟
    except subprocess.TimeoutExpired:
        proc.terminate()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
