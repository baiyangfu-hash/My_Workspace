"""auto_pm.ui 包

V0.9.0 起 QML 为唯一 UI 入口，旧 QWidget 模块已全部移除。

架构分层：
- qml/: QML 视图 + 组件 + 主题 + 模型 + 对话框
- qml_bridge.py: Python↔QML 数据桥（暴露 Service 层）
- qml_main_window.py: QML GUI 入口
- global_pages/spec_center_dto.py: SpecCenterAdapter + DTOs（QML SpecCenterView 使用）
- models/: Qt 模型适配器（ProjectModel 等，QML/QWidget 共用）

UI 层通过 Service 层访问数据，不直接访问文件系统/DB。
"""

__all__: list[str] = []
