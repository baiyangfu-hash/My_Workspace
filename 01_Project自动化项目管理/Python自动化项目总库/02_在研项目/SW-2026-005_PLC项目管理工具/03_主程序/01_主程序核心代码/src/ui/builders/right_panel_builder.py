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
from src.ui.ui_scale import current_ui_profile
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class RightPanelBuilder:

    @staticmethod
    def build(parent, jump_handler=None, ui_profile=None) -> dict:
        profile = ui_profile or current_ui_profile(parent)
        tab_widget = QTabWidget(parent)
        tab_widget.setTabPosition(QTabWidget.North)
        tab_widget.setTabShape(QTabWidget.Triangular)
        tab_widget.setElideMode(Qt.ElideRight)
        tab_widget.setDocumentMode(True)

        dashboard_page = DashboardPage(ui_profile=profile)
        tab_widget.addTab(dashboard_page, "仪表盘")

        project_info_widget, project_info_labels = RightPanelBuilder._create_project_info_widget(profile)
        tab_widget.addTab(project_info_widget, "项目")

        document_editor = RightPanelBuilder._create_document_tab()
        tab_widget.addTab(document_editor, "文档")

        change_mgmt_panel = RightPanelBuilder._create_change_management_tab()
        tab_widget.addTab(change_mgmt_panel, "变更管理")

        plc_tools_tabs, st_editor = RightPanelBuilder._create_plc_tools_tab()
        tab_widget.addTab(plc_tools_tabs, "PLC工具")

        spec_check_tab_panel = RightPanelBuilder._create_spec_check_tab(jump_handler, profile)
        tab_widget.addTab(spec_check_tab_panel, "规范中心")

        auto_fix_panel = RightPanelBuilder._create_auto_fix_tab()
        excel_export_panel = RightPanelBuilder._create_excel_export_tab()

        return {
            "tab_widget": tab_widget,
            "dashboard_page": dashboard_page,
            "project_info_widget": project_info_widget,
            "document_editor": document_editor,
            "change_mgmt_panel": change_mgmt_panel,
            "plc_tools_tabs": plc_tools_tabs,
            "st_editor": st_editor,
            "spec_check_tab_panel": spec_check_tab_panel,
            "auto_fix_panel": auto_fix_panel,
            "excel_export_panel": excel_export_panel,
            "project_info_labels": project_info_labels,
        }

    @staticmethod
    def _create_project_info_widget(profile):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(
            profile.spacing_lg,
            profile.spacing_lg,
            profile.spacing_lg,
            profile.spacing_lg,
        )
        layout.setSpacing(profile.spacing_lg)

        title = QLabel("项目详情")
        title.setFont(QFont("Microsoft YaHei UI", profile.font_pt(16), QFont.Bold))
        title.setProperty("panelTitle", True)
        layout.addWidget(title)

        info_group = QGroupBox("基本信息")
        info_group.setProperty("IndustrialGroup", True)
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
        desc_group.setProperty("IndustrialGroup", True)
        desc_layout = QVBoxLayout(desc_group)
        txt_project_desc = QTextEdit()
        txt_project_desc.setReadOnly(True)
        txt_project_desc.setMaximumHeight(profile.description_max_height)
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
        container.addTab(st_editor, "ST编辑器")

        return container, st_editor

    @staticmethod
    def _create_spec_check_tab(jump_handler=None, profile=None):
        profile = profile or current_ui_profile()
        guide = QWidget()
        layout = QVBoxLayout(guide)
        layout.setContentsMargins(
            profile.guide_padding,
            profile.guide_padding,
            profile.guide_padding,
            profile.guide_padding,
        )
        layout.setSpacing(profile.spacing_lg)
        layout.addStretch()

        icon = QLabel("\U0001F50D")
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)

        title = QLabel("规范检查面板")
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("sectionTitle", True)
        layout.addWidget(title)

        desc = QLabel(
            "规范检查功能已移至底部 Dock 面板，"
            "点击下方按钮打开。"
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setProperty("welcomeText", True)
        layout.addWidget(desc)

        btn = QPushButton("  打开规范检查面板")
        btn.setFixedHeight(profile.guide_button_height)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("PrimaryBtn", True)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

        layout.addStretch()

        guide._open_spec_check_btn = btn
        return guide

    @staticmethod
    def _create_auto_fix_tab():
        try:
            from ..widgets.auto_fix_panel import AutoFixPanel
            return AutoFixPanel()
        except ImportError as e:
            logger.warning(f"AutoFixPanel加载失败: {e}")
            return RightPanelBuilder._create_fallback_widget("自动修复面板加载失败")

    @staticmethod
    def _create_excel_export_tab():
        try:
            from ..widgets.excel_export_panel import ExcelExportPanel
            return ExcelExportPanel()
        except ImportError as e:
            logger.warning(f"ExcelExportPanel加载失败: {e}")
            return RightPanelBuilder._create_fallback_widget("Excel导出面板加载失败")

    @staticmethod
    def _create_fallback_widget(message: str):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addStretch()
        label = QLabel(f"\u26A0\uFE0F {message}")
        label.setAlignment(Qt.AlignCenter)
        label.setProperty("emptyState", True)
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
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setProperty("sectionTitle", True)
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setProperty("welcomeText", True)
        layout.addWidget(desc_label)

        layout.addStretch()
        return widget
