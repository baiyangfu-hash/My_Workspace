"""测试 ModbusDebuggerView.qml 的 QML 渲染与数据绑定"""

from __future__ import annotations

import os
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent

from auto_pm.modbus.modbus_bridge import ModbusBridge
from auto_pm.modbus.modbus_service import ModbusService


def test_modbus_gui_render() -> None:
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    
    bridge = ModbusBridge()
    
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("modbusBridge", bridge)
    
    qml_file = repo_root / "auto_pm" / "ui" / "qml" / "views" / "ModbusDebuggerView.qml"
    
    component = QQmlComponent(engine, QUrl.fromLocalFile(str(qml_file)))
    if not component.isReady():
        print("❌ ModbusDebuggerView.qml 加载失败:")
        for err in component.errors():
            print("  -", err.toString())
        sys.exit(1)
        
    view = component.create()
    if view is None:
        print("❌ 视图对象实例化失败")
        sys.exit(1)
        
    print("✅ ModbusDebuggerView.qml QML 视图实例化成功！")
    print("✅ ContextProperty 'modbusBridge' 绑定正常！")

if __name__ == "__main__":
    test_modbus_gui_render()
