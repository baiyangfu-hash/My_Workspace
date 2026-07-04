"""全局功能页模块（V0.8.0 Phase 4 / CHG-092 起仅保留 GlobalView）

V0.8.0 Phase 4 已将 4 个 QWidget 页面（ReportPage/SettingsPage/SpecCenterView/
TemplatePage）及 spec_center_tabs/ 子目录全部迁移到 QML 并删除：
- 新版页面位于 ``auto_pm/ui/qml/views/``
- 旧版 ``main_window.py`` 仍可用 try/except 占位回退（deprecated，V0.9 移除）

保留：
- ``global_view.py``：GlobalView 仍被 main_window.py 使用
- ``spec_center_dto.py``：SpecCenterAdapter + DTOs，由 QML SpecCenterView 通过
  QmlBridge 使用
"""

__all__: list[str] = []
