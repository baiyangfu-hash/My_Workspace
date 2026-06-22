"""GUI 入口（已迁移到 PySide6）

保留此包以兼容旧的 ``from auto_pm.gui import ...`` 导入。
实际入口在 auto_pm.ui.main_window.MainWindow。
"""

from auto_pm.ui.main_window import MainWindow

__all__ = ["MainWindow"]
