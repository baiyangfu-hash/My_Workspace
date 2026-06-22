"""导航树节点数据模型

定义 NavigationTree 使用的节点数据结构，存储于 QTreeWidgetItem.UserRole。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NavNode:
    """导航树节点数据模型

    Attributes:
        node_type: 节点类型 'stack' | 'phase' | 'function' | 'root'
        label: 节点显示文本（不含计数徽标）
        filter_stack: 技术栈筛选 'plc' | 'python' | None
        filter_phase: 阶段筛选 'developing' | 'commissioning'
            | 'production' | 'archived' | None
        page_id: 功能页ID 'all_projects' | 'change_center' | 'spec_center'
            | 'template' | 'report' | 'settings' | None
        badge_count: 计数徽标值
        children: 子节点列表（预留）
    """

    node_type: str
    label: str
    filter_stack: Optional[str] = None
    filter_phase: Optional[str] = None
    page_id: Optional[str] = None
    badge_count: int = 0
    children: list = field(default_factory=list)
