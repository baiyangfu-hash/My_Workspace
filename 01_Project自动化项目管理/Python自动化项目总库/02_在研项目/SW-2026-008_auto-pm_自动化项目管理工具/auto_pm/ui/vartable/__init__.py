"""变量表 GUI 组件包（V2.3 Week4）

提供基于 PySide6 的变量表编辑器与项目工作区 Tab：
- VariableTableModel：QAbstractTableModel，持有可变行数据
- VariableTableEditor：QTableView + 工具栏 + 右键菜单，支持增删改查/导入/导出
- VartableTab：项目工作区变量表 Tab，扫描文件 + 解析 + 编辑器集成
"""

from auto_pm.ui.vartable.variable_table_editor import (
    VariableTableEditor,
    VariableTableModel,
)
from auto_pm.ui.vartable.vartable_tab import VartableTab

__all__ = [
    "VariableTableEditor",
    "VariableTableModel",
    "VartableTab",
]
