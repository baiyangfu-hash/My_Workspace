# -*- coding: utf-8 -*-
"""
GUI 根因定位脚本 v2 - 聚焦 QToolBox 高 DPI 渲染问题

新诊断方向：
  1. 测试禁用高 DPI 缩放后是否正常
  2. 检查 QFontDatabase.addApplicationFont() 是否有帮助
  3. 对比 QToolBox vs 其他组件的字体解析差异
  4. 测试使用 QFont.setFamilies() 显式设置
"""
import sys
import os
from pathlib import Path

base_dir = Path(__file__).parent
src_dir = base_dir / "src"
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(base_dir))

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import (
    QGuiApplication, QFont, QFontDatabase, QFontInfo,
    QPainter, QImage
)
from PyQt5.QtWidgets import (
    QApplication, QWidget, QToolBox, QLabel,
    QPushButton, QVBoxLayout, QMainWindow
)

print("=" * 70)
print("🔬 根因定位 v2 - QToolBox 高 DPI 渲染")
print("=" * 70)

# ========== 测试 1: QFontInfo 实际解析结果 ==========
print("\n[测试1] QFontInfo - 查看字体实际被解析成什么")

app = QApplication(sys.argv)
db = QFontDatabase()

test_font = QFont("Microsoft YaHei UI", 12)
font_info = QFontInfo(test_font)
print(f"   请求字体: Microsoft YaHei UI 12pt")
print(f"   QFontInfo.family(): {font_info.family()}")
print(f"   QFontInfo.pointSize(): {font_info.pointSize()}")
print(f"   QFontInfo.exactMatch(): {font_info.exactMatch()}")
print(f"   是否精确匹配: {'✅' if font_info.exactMatch() else '❌ Qt做了替换!'}")

# 如果不是精确匹配，看看实际用了什么
if not font_info.exactMatch():
    print(f"   ⚠️ Qt 将 '{test_font.family()}' 替换为 '{font_info.family()}'")

# ========== 测试 2: addApplicationFont 预加载 ==========
print("\n[测试2] 尝试预加载字体到 Qt 数据库")

font_files = [
    r"C:\Windows\Fonts\msyh.ttc",      # 微软雅黑
    r"C:\Windows\Fonts\msyhl.ttc",     # 微软雅黑 Light
    r"C:\Windows\Fonts\simsun.ttc",    # 宋体
]

for ff in font_files:
    if os.path.exists(ff):
        id = db.addApplicationFont(ff)
        if id < 0:
            print(f"   ❌ 加载失败: {ff}")
        else:
            families = db.applicationFontFamilies(id)
            print(f"   ✅ 加载成功: {Path(ff).name} → {families}")

# ========== 测试 3: 创建完整窗口并截图对比 ==========
print("\n[测试3] 创建测试窗口对比不同组件")

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("字体测试窗口")
        self.setGeometry(100, 100, 800, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        font = QFont("Microsoft YaHei UI", 12)
        font.setStyleStrategy(font.PreferAntialias | font.PreferMatch)
        self.setFont(font)

        tool_box = QToolBox()
        tool_box.addItem(QLabel("测试标签1"), "▶ 页面标题1")
        tool_box.addItem(QLabel("测试标签2"), "▶ 页面标题2")
        layout.addWidget(tool_box)

        label = QLabel("普通 QLabel 中文测试")
        layout.addWidget(label)

        btn = QPushButton("普通 QPushButton 中文测试")
        layout.addWidget(btn)

window = TestWindow()
window.show()

app.processEvents()
time.sleep(0.5)

import time

print(f"\n   窗口字体: {window.font().family()} ({window.font().pointSize()}pt)")
print(f"   ToolBox字体: {tool_box.font().family()}")
print(f"   QLabel字体: {label.font().family()}")
print(f"   QPushButton字体: {btn.font().family()}")

# ========== 测试 4: 禁用高 DPI ==========
print("\n[测试4] 当前高 DPI 设置状态")
screen = QGuiApplication.primaryScreen()
if screen:
    dpr = screen.devicePixelRatio()
    logical_dpi = screen.logicalDotsPerInch()
    physical_dpi = screen.physicalDotsPerInch()
    print(f"   DPR (devicePixelRatio): {dpr}")
    print(f"   Logical DPI: {logical_dpi}")
    print(f"   Physical DPI: {physical_dpi}")
    print(f"   AA_EnableHighDpiScaling: {QCoreApplication.testAttribute(Qt.AA_EnableHighDpiScaling)}")
    print(f"   AA_UseHighDpiPixmaps: {QCoreApplication.testAttribute(Qt.AA_UseHighDpiPixmaps)}")

# ========== 测试 5: 检查所有可用中文字体 ==========
print("\n[测试5] 系统中所有可能支持中文的字体")
all_families = db.families()
chinese_capable = []
for f in sorted(all_families):
    fl = f.lower()
    if any(k in fl for k in [
        'yahei', 'hei', 'song', 'ming', 'sim',
        'fang', 'kai', 'yuan', 'noto', 'cjk',
        'wenquan', 'droid', 'source han'
    ]):
        chinese_capable.append(f)

print(f"   找到 {len(chinese_capable)} 个可能支持中文的字体:")
for f in chinese_capable[:20]:
    print(f"      - {f}")

# ========== 测试 6: 尝试 setFamilies() 而非构造函数 ==========
print("\n[测试6] 使用 setFamilies() 设置字体族列表")

font2 = QFont()
font2.setPointSize(12)
font2.setFamilies(["Microsoft YaHei UI", "Segoe UI", "Arial"])
font2.setStyleStrategy(font2.PreferAntialias | font2.PreferMatch)

info2 = QFontInfo(font2)
print(f"   设置 families: ['Microsoft YaHei UI', 'Segoe UI', 'Arial']")
print(f"   实际解析为: {info2.family()}")
print(f"   精确匹配: {info2.exactMatch()}")

print("\n" + "=" * 70)
print("🏁 诊断完成")
print("=" * 70)

window.close()
app.quit()
