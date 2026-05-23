# -*- coding: utf-8 -*-
"""
工具栏管理器 - 负责构建和管理主工具栏

从main_window.py的_init_tool_bar()方法提取，
实现工具栏创建逻辑的独立封装。

职责:
- 构建主工具栏 (新建/打开/保存/检查等快捷按钮)
- 管理工具栏按钮状态
- 通过EventBus发射工具栏事件
- 支持图标和提示文本
"""
from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow,
    QToolBar,
    QAction,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from src.core.event_bus import EventBus
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ToolBarManager:
    """
    工具栏管理器

    使用方式:
        toolbar_manager = ToolBarManager(main_window, event_bus)
        toolbar = toolbar_manager.build()

    设计原则:
        - 单一职责: 只负责工具栏的创建和管理
        - 事件驱动: 通过EventBus发射信号
        - 可配置: 支持自定义图标、大小和布局
    """

    def __init__(self, parent: QMainWindow, event_bus: EventBus):
        """
        初始化工具栏管理器

        Args:
            parent: 主窗口实例 (QMainWindow)
            event_bus: 全局事件总线实例
        """
        self._parent = parent
        self._event_bus = event_bus
        self._toolbar: Optional[QToolBar] = None
        self._icon_size = QSize(22, 22)  # 默认图标大小

    def build(self) -> QToolBar:
        """
        构建工具栏并添加到主窗口

        工具栏按钮顺序:
        1. 新建项目
        2. 打开项目
        ---
        3. 保存
        ---
        4. 规范检查

        Returns:
            QToolBar: 构建完成的工具栏对象
        """
        self._toolbar = QToolBar("主工具栏", self._parent)
        self._toolbar.setMovable(False)
        self._toolbar.setIconSize(self._icon_size)

        # 新建项目按钮
        new_action = QAction("新建项目", self._parent)
        new_action.setStatusTip("创建新的PLC项目 (Ctrl+N)")
        new_action.triggered.connect(self._on_new_project)
        self._toolbar.addAction(new_action)

        self._toolbar.addSeparator()

        # 打开项目按钮
        open_action = QAction("打开项目", self._parent)
        open_action.setStatusTip("打开已有项目 (Ctrl+O)")
        open_action.triggered.connect(self._on_open_project)
        self._toolbar.addAction(open_action)

        self._toolbar.addSeparator()

        # 保存按钮
        save_action = QAction("保存", self._parent)
        save_action.setStatusTip("保存当前工作 (Ctrl+S)")
        save_action.triggered.connect(self._on_save)
        self._toolbar.addAction(save_action)

        self._toolbar.addSeparator()

        # 规范检查按钮
        check_action = QAction("规范检查", self._parent)
        check_action.setStatusTip("运行规范检查 (F5)")
        check_action.triggered.connect(self._on_run_check)
        self._toolbar.addAction(check_action)

        # 将工具栏添加到主窗口
        self._parent.addToolBar(Qt.TopToolBarArea, self._toolbar)

        logger.debug("工具栏构建完成")
        return self._toolbar

    def set_icon_size(self, size: QSize):
        """
        设置工具栏图标大小

        Args:
            size: 图标尺寸 (宽, 高)
        """
        self._icon_size = size
        if self._toolbar:
            self._toolbar.setIconSize(size)

    # ===== 事件处理方法 =====

    def _on_new_project(self):
        self._event_bus.project_created.emit("")

    def _on_open_project(self):
        from PyQt5.QtWidgets import QFileDialog
        from pathlib import Path

        project_dir = QFileDialog.getExistingDirectory(
            self._parent, "选择项目目录", "./Projects"
        )
        if project_dir:
            from src.core.settings import SettingsManager
            SettingsManager.add_recent_project(
                project_dir, Path(project_dir).name
            )
            self._event_bus.project_opened.emit(project_dir)

    def _on_save(self):
        """保存 - 更新状态栏"""
        self._parent.statusBar().showMessage("\U0001F4BE 已保存")
        logger.debug("执行保存操作 (来自工具栏)")

    def _on_run_check(self):
        """规范检查 - 发射事件到EventBus"""
        self._event_bus.spec_check_request.emit({})
