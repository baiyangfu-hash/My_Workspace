"""变更中心模块

提供变更中心全局页（ChangeCenterView）及其子组件：
    - ChangeCenterView: 左右分栏全局页（列表 + 详情）
    - ChangeListPanel: 变更单列表面板（状态 Tab 筛选）
    - ChangeDetailPanel: 变更单详情面板（含状态流转按钮）
"""

from auto_pm.ui.change_center.center_view import ChangeCenterView
from auto_pm.ui.change_center.change_detail_panel import ChangeDetailPanel
from auto_pm.ui.change_center.change_list_panel import ChangeListPanel

__all__ = ["ChangeCenterView", "ChangeListPanel", "ChangeDetailPanel"]
