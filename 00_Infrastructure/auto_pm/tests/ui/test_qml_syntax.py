"""QML 静态语法与组件加载回归测试门禁 (DEV-216 / DEV-300)

自动扫描 auto_pm/ui/qml 目录下的所有 .qml 文件，
在 offscreen 模式下通过 QQmlComponent 校验语法、类型绑定和信号定义的正确性，
确保 QML 解析错误 100% 在 CI/pytest 阶段被拦截。
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication, QUrl
from PySide6.QtQml import QQmlComponent, QQmlEngine

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="module")
def qml_engine() -> QQmlEngine:
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    engine = QQmlEngine()
    qml_dir = Path(__file__).parent.parent.parent / "auto_pm" / "ui" / "qml"
    engine.addImportPath(str(qml_dir))
    engine.addImportPath(str(qml_dir / "components"))
    engine.addImportPath(str(qml_dir / "views"))
    engine.addImportPath(str(qml_dir / "views" / "workspace"))
    engine.addImportPath(str(qml_dir / "dialogs"))
    engine.addImportPath(str(qml_dir / "theme"))
    return engine


def _get_all_qml_files() -> list[Path]:
    qml_dir = Path(__file__).parent.parent.parent / "auto_pm" / "ui" / "qml"
    return sorted(qml_dir.rglob("*.qml"))


@pytest.mark.parametrize("qml_path", _get_all_qml_files(), ids=lambda p: p.name)
def test_qml_file_syntax_and_component_loading(qml_engine: QQmlEngine, qml_path: Path) -> None:
    """每个 QML 文件必须能被 QQmlComponent 成功解析无语法错误"""
    component = QQmlComponent(qml_engine, QUrl.fromLocalFile(str(qml_path)))
    if component.isError():
        errors = [e.toString() for e in component.errors()]
        pytest.fail(f"QML 语法解析错误 [{qml_path.name}]:\n" + "\n".join(errors))
