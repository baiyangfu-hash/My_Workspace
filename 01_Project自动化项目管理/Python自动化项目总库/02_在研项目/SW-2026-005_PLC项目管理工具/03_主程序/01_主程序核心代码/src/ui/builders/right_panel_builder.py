# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QLabel,
    QGroupBox,
    QFormLayout,
    QTextEdit,
    QPushButton,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal

from ..dashboard import DashboardPage
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class RightPanelBuilder:

    @staticmethod
    def build(parent, jump_handler=None) -> dict:
        tab_widget = QTabWidget(parent)
        tab_widget.setTabPosition(QTabWidget.North)
        tab_widget.setTabShape(QTabWidget.Rounded)
        tab_widget.setElideMode(Qt.ElideRight)

        dashboard_page = DashboardPage()
        tab_widget.addTab(dashboard_page, "\u2630 仪表盘")

        project_info_widget, project_info_labels = RightPanelBuilder._create_project_info_widget()
        tab_widget.addTab(project_info_widget, "\U0001F4C1 项目")

        document_editor = RightPanelBuilder._create_document_tab()
        tab_widget.addTab(document_editor, "\U0001F4DD 文档")

        change_mgmt_panel = RightPanelBuilder._create_change_management_tab()
        tab_widget.addTab(change_mgmt_panel, "\U0001F504 变更管理")

        plc_tools_tabs, st_editor = RightPanelBuilder._create_plc_tools_tab()
        tab_widget.addTab(plc_tools_tabs, "\u26A1 PLC工具")

        spec_check_tab_panel = RightPanelBuilder._create_spec_check_tab(jump_handler)
        tab_widget.addTab(spec_check_tab_panel, "\u2705 规范检查")

        return {
            "tab_widget": tab_widget,
            "dashboard_page": dashboard_page,
            "project_info_widget": project_info_widget,
            "document_editor": document_editor,
            "change_mgmt_panel": change_mgmt_panel,
            "plc_tools_tabs": plc_tools_tabs,
            "st_editor": st_editor,
            "spec_check_tab_panel": spec_check_tab_panel,
            "project_info_labels": project_info_labels,
        }

    @staticmethod
    def _create_project_info_widget():
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        title = QLabel("\U0001F4C1 项目详情")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title.setStyleSheet("color: #212121;")
        layout.addWidget(title)

        info_group = QGroupBox("基本信息")
        info_form = QFormLayout(info_group)
        info_form.setSpacing(8)

        lbl_project_name = QLabel("-")
        lbl_project_id = QLabel("-")
        lbl_project_type = QLabel("-")
        lbl_project_path = QLabel("-")
        lbl_project_path.setWordWrap(True)
        lbl_project_stage = QLabel("-")

        info_form.addRow("项目名称:", lbl_project_name)
        info_form.addRow("项目编号:", lbl_project_id)
        info_form.addRow("项目类型:", lbl_project_type)
        info_form.addRow("当前阶段:", lbl_project_stage)
        info_form.addRow("项目路径:", lbl_project_path)
        layout.addWidget(info_group)

        desc_group = QGroupBox("项目描述")
        desc_layout = QVBoxLayout(desc_group)
        txt_project_desc = QTextEdit()
        txt_project_desc.setReadOnly(True)
        txt_project_desc.setMaximumHeight(200)
        txt_project_desc.setPlaceholderText("选择项目后显示详细信息...")
        desc_layout.addWidget(txt_project_desc)
        layout.addWidget(desc_group)

        layout.addStretch()

        labels = {
            "name": lbl_project_name,
            "id": lbl_project_id,
            "type": lbl_project_type,
            "stage": lbl_project_stage,
            "path": lbl_project_path,
            "desc": txt_project_desc,
        }

        return widget, labels

    @staticmethod
    def _create_document_tab():
        try:
            from ..widgets.document_editor import DocumentEditor
            return DocumentEditor()
        except ImportError as e:
            logger.warning(f"DocumentEditor加载失败: {e}")
            return RightPanelBuilder._create_fallback_widget("文档编辑器加载失败")

    @staticmethod
    def _create_change_management_tab():
        try:
            from ..widgets.change_management_panel import ChangeManagementPanel
            return ChangeManagementPanel()
        except ImportError as e:
            logger.warning(f"ChangeManagementPanel加载失败: {e}")
            return RightPanelBuilder._create_fallback_widget("变更管理面板加载失败")

    @staticmethod
    def _create_plc_tools_tab():
        from PyQt5.QtWidgets import QTabWidget as InnerTabWidget

        container = InnerTabWidget()
        container.setTabPosition(InnerTabWidget.North)
        container.setDocumentMode(True)

        st_editor = None
        try:
            from ..widgets.st_editor import STEditor
            st_editor = STEditor(show_dependency_notice=True)
        except ImportError as e:
            logger.warning(f"STEditor加载失败: {e}")
            st_editor = RightPanelBuilder._create_fallback_widget("ST编辑器加载失败")
        container.addTab(st_editor, "\U0001F4DD ST编辑器")

        return container, st_editor

    @staticmethod
    def _create_spec_check_tab(jump_handler=None):
        guide = QWidget()
        layout = QVBoxLayout(guide)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.addStretch()

        icon = QLabel("\U0001F50D")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 48pt; color: #BDBDBD;")
        layout.addWidget(icon)

        title = QLabel("\u89C4\u8303\u68C0\u67E5\u9762\u677F")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 16pt; font-weight: bold; color: #424242; padding: 12px 0; "
            "font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', SimHei, sans-serif;"
        )
        layout.addWidget(title)

        desc = QLabel(
            "\u89C4\u8303\u68C0\u67E5\u529F\u80FD\u5DF2\u79FB\u81F3\u5E95\u90E8 Dock \u9762\u677F\uFF0C"
            "\u70B9\u51FB\u4E0B\u65B9\u6309\u94AE\u6253\u5F00\u3002"
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet(
            "color: #757575; font-size: 10pt; padding: 8px 0; "
            "font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', SimHei, sans-serif;"
        )
        layout.addWidget(desc)

        btn = QPushButton("  \u6253\u5F00\u89C4\u8303\u68C0\u67E5\u9762\u677F")
        btn.setFixedHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton { background-color: #1976D2; color: white; "
            "border: none; border-radius: 6px; padding: 8px 24px; "
            "font-size: 11pt; font-weight: bold; }"
            "QPushButton:hover { background-color: #1565C0; }"
        )
        layout.addWidget(btn, alignment=Qt.AlignCenter)

        layout.addStretch()

        guide._open_spec_check_btn = btn
        return guide

    @staticmethod
    def _create_fallback_widget(message: str):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addStretch()
        label = QLabel(f"\u26A0\uFE0F {message}")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #757575; font-size: 11pt; padding: 40px;")
        layout.addWidget(label)
        layout.addStretch()
        return widget

    @staticmethod
    def _create_placeholder_widget(title: str, description: str):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addStretch()

        icon_label = QLabel("\U0001F6E0\uFE0F")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 36pt; color: #BDBDBD;")
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 14pt; font-weight: bold; color: #616161; padding: 8px 0; "
            "font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', SimHei, sans-serif;"
        )
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(
            "color: #9E9E9E; font-size: 10pt; padding: 8px 40px; "
            "font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', SimHei, sans-serif;"
        )
        layout.addWidget(desc_label)

        layout.addStretch()
        return widget
