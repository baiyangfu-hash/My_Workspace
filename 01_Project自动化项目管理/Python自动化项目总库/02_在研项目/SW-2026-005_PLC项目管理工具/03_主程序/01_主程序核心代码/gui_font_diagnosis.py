# -*- coding: utf-8 -*-
"""
GUI 字体诊断脚本 - 精确定位 ToolBox 乱码根因

诊断项目：
  1. QApplication vs QWidget 级别字体是否一致
  2. QSS 加载前后字体变化
  3. ToolBox 及其子组件的实际字体
  4. QSS 中 * 选择器的实际效果
  5. 编码检查：源文件中的中文字符串
"""
import sys
import os
from pathlib import Path

base_dir = Path(__file__).parent
src_dir = base_dir / "src"
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(base_dir))

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QGuiApplication, QFont, QFontDatabase, QPainter, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QToolBox, QLabel, QPushButton

QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

app = QApplication(sys.argv)

print("=" * 70)
print("🔬 GUI 字体深度诊断 - SW-2026-005")
print("=" * 70)

# ========== 1. 系统字体数据库 ==========
print("\n[1] 系统字体数据库扫描")
db = QFontDatabase()
families = db.families()
target_fonts = ["Microsoft YaHei UI", "Microsoft YaHei", "SimHei", "SimSun", "Segoe UI"]
for f in target_fonts:
    status = "✅" if f in families else "❌"
    print(f"   {status} {f}")

# ========== 2. QApplication 字体 ==========
print("\n[2] QApplication 级别字体（未修改前）")
app_font = app.font()
print(f"   字体族: {app_font.family()}")
print(f"   字号: {app_font.pointSize()}pt")
print(f"   像素大小: {app_font.pixelSize()}px")
print(f"   粗细: {app_font.weight()}")
print(f"   样式策略: {app_font.styleStrategy()}")

# ========== 3. 测试 StyleBuilder 字体解析 ==========
print("\n[3] StyleBuilder._resolve_chinese_font() 测试")
from src.ui.builders.style_builder import StyleBuilder

resolved = StyleBuilder._resolve_chinese_font(12)
print(f"   解析结果: {resolved.family()}")
print(f"   解析字号: {resolved.pointSize()}pt")
print(f"   是否精确匹配: {'✅' if resolved.family() == 'Microsoft YaHei UI' else '❌'}")

# ========== 4. 创建测试组件并检查字体继承 ==========
print("\n[4] 组件字体继承测试")

test_widget = QWidget()
test_widget.setFont(resolved)
print(f"\n   [4.1] QWidget.setFont() 后:")
print(f"        widget.font(): {test_widget.font().family()}")

tool_box = QToolBox(test_widget)
print(f"\n   [4.2] 子组件 QToolBox（未显式设置字体）:")
print(f"        tool_box.font(): {tool_box.font().family()}")
print(f"        是否继承父级: {'✅' if tool_box.font().family() == resolved.family() else '❌ 未继承!'}")

label = QLabel("测试中文", tool_box)
print(f"\n   [4.3] QLabel（ToolBox的子组件）:")
print(f"        label.font(): {label.font().family()}")

btn = QPushButton("按钮中文", tool_box)
print(f"\n   [4.4] QPushButton（ToolBox的子组件）:")
print(f"        btn.font(): {btn.font().family()}")

# ========== 5. QSS 影响测试 ==========
print("\n[5] QSS 对字体的影响测试")

qss_test = """
* {
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
}
"""
print(f"\n   [5.1] 应用 QSS 前:")
print(f"        widget.font(): {test_widget.font().family()}")

test_widget.setStyleSheet(qss_test)
print(f"\n   [5.2] 应用 QSS 后 (* {{ font-family: 'Microsoft YaHei UI', ... }}):")
print(f"        widget.font(): {test_widget.font().family()}")
print(f"        tool_box.font(): {tool_box.font().family()}")
print(f"        label.font(): {label.font().family()}")
print(f"        btn.font(): {btn.font().family()}")

# ========== 6. 实际加载项目的 QSS ==========
print("\n[6] 项目实际 QSS 加载测试")

from src.core.settings import SettingsManager
from src.ui.ui_scale import current_ui_profile, build_runtime_stylesheet

SettingsManager.initialize()
theme = SettingsManager.get("theme", "dark")
profile = current_ui_profile()

qss_base_path = Path(__file__).resolve()
for _ in range(8):
    qss_base_path = qss_base_path.parent
    if (qss_base_path / "resources").exists():
        break

qss_path = qss_base_path / "resources" / "styles" / f"material_{theme}.qss"
if qss_path.exists():
    with open(qss_path, 'r', encoding='utf-8') as f:
        qss_content = f.read()

    full_qss = qss_content + "\n" + build_runtime_stylesheet(profile)

    test_widget2 = QWidget()
    test_widget2.setFont(resolved)

    tool_box2 = QToolBox(test_widget2)
    label2 = QLabel("仪表盘", tool_box2)

    print(f"\n   [6.1] 应用项目 QSS 前:")
    print(f"        widget.font(): {test_widget2.font().family()}")
    print(f"        tool_box.font(): {tool_box2.font().family()}")
    print(f"        label.text+font: '{label2.text()}' @ {label2.font().family()}")

    test_widget2.setStyleSheet(full_qss)

    print(f"\n   [6.2] 应用项目 QSS 后:")
    print(f"        widget.font(): {test_widget2.font().family()}")
    print(f"        tool_box.font(): {tool_box2.font().family()}")
    print(f"        label.text+font: '{label2.text()}' @ {label2.font().family()}")

    import re
    font_decls = re.findall(r'font-family\s*:\s*[^;}{]+', full_qss)
    print(f"\n   [6.3] QSS 中所有 font-family 声明 ({len(font_decls)} 处):")
    for i, fd in enumerate(font_decls[:10], 1):
        print(f"        [{i}] {fd.strip()}")

# ========== 7. 渲染测试 ==========
print("\n[7] 中文渲染像素级测试")

test_texts = [
    ("项目管理", resolved),
    ("文档管理", resolved),
    ("仪表盘", app_font),
]

for text, font_obj in test_texts:
    img = QImage(200, 40, QImage.Format_ARGB32)
    img.fill(0xFFFFFFFF)
    painter = QPainter(img)
    painter.setFont(font_obj)
    painter.drawText(5, 25, text)
    painter.end()

    has_content = False
    for y in range(img.height()):
        for x in range(img.width()):
            if img.pixelColor(x, y).alpha() > 0:
                has_content = True
                break
        if has_content:
            break

    status = "✅ 可渲染" if has_content else "❌ 空白!"
    print(f"   {status} \"{text}\" @ {font_obj.family()}({font_obj.pointSize()}pt)")

# ========== 8. 源文件编码检查 ==========
print("\n[8] 关键源文件编码检查")

files_to_check = [
    base_dir / "src" / "ui" / "builders" / "left_panel_builder.py",
    base_dir / "src" / "ui" / "dashboard.py",
]

for fp in files_to_check:
    if not fp.exists():
        continue
    raw = fp.read_bytes()
    bom = raw[:3]
    encoding = "unknown"

    if raw.startswith(b'\xef\xbb\xbf'):
        encoding = "UTF-8 BOM"
    elif raw.startswith(b'\xff\xfe'):
        encoding = "UTF-16 LE"
    elif raw.startswith(b'\xfe\xff'):
        encoding = "UTF-16 BE"
    else:
        try:
            raw.decode('utf-8')
            encoding = "UTF-8 (no BOM)"
        except:
            try:
                raw.decode('gbk')
                encoding = "GBK/GB2312"
            except:
                encoding = "BINARY?"

    chinese_count = raw.decode('utf-8', errors='ignore').count('\u4e00') + \
                    sum(1 for c in raw.decode('utf-8', errors='ignore') if '\u4e00' <= c <= '\u9fff')

    print(f"   {fp.name}: {encoding}, 大小={len(raw)}B, 中文字符≈{chinese_count}")

print("\n" + "=" * 70)
print("🏁 诊断完成")
print("=" * 70)

app.quit()
