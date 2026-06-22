"""auto_pm.ui 包

PySide6 原生桌面 UI 层（V2.0）。

架构分层：
- main_window: QMainWindow 主窗口（侧边栏 + 工具栏 + 状态栏 + QStackedWidget）
- views: 视图层（项目列表页 / 项目工作区 / 全局功能页）
- widgets: 复用组件（项目卡片 / 统计栏 / 筛选栏）
- models: Qt 模型适配器（ProjectModel）

UI 层通过 Service 层访问数据，不直接访问文件系统/DB。
"""

from auto_pm.ui.main_window import MainWindow

__all__ = ["MainWindow"]
