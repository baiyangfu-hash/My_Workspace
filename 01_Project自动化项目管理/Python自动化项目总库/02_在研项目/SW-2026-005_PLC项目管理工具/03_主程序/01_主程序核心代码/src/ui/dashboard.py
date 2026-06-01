# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from src.ui.ui_scale import current_ui_profile
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DashboardPage(QWidget):
    action_triggered = pyqtSignal(str)

    def __init__(self, parent=None, ui_profile=None):
        super().__init__(parent)
        self._ui_profile = ui_profile or current_ui_profile(parent)
        self._quick_actions = {}
        self._stat_card_labels = {}
        self._init_ui()

    def _init_ui(self):
        profile = self._ui_profile
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(
            profile.spacing_xl,
            profile.spacing_md,
            profile.spacing_xl,
            profile.spacing_md,
        )
        main_layout.setSpacing(profile.spacing_lg)

        self._build_hero_section(main_layout)
        self._build_stat_cards_section(main_layout)
        self._build_bottom_section(main_layout)

        main_layout.addStretch()

    def _build_hero_section(self, parent_layout: QVBoxLayout):
        profile = self._ui_profile
        hero_layout = QVBoxLayout()
        hero_layout.setSpacing(6)
        hero_layout.setContentsMargins(0, 0, 0, 20)

        title_label = QLabel("PLC项目管理工具")
        title_font = QFont("Microsoft YaHei UI", 28)
        title_font.setWeight(QFont.Light)
        title_label.setFont(title_font)
        title_label.setProperty("DashboardHeroTitle", True)
        hero_layout.addWidget(title_label)

        subtitle_label = QLabel(
            "Trae伴生式工作空间治理 \u2014 规范检查\u00B7文档生成\u00B7变更管理"
        )
        subtitle_label.setProperty("DashboardHeroSubtitle", True)
        hero_layout.addWidget(subtitle_label)

        parent_layout.addLayout(hero_layout)

    def _build_stat_card(self, icon_text, icon_color_prop, title, value, description):
        card = QFrame()
        card.setProperty("StatCard", "true")
        card.setFixedHeight(96)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 18, 20, 18)

        icon_frame = QFrame()
        icon_frame.setFixedSize(40, 40)
        icon_frame.setProperty("StatCardIcon", icon_color_prop)
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel(icon_text)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 18px; background: transparent;")
        icon_layout.addWidget(icon_label)
        layout.addWidget(icon_frame)

        layout.addSpacing(14)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        title_lbl = QLabel(title)
        title_lbl.setProperty("StatCardTitle", True)
        value_lbl = QLabel(value)
        value_lbl.setProperty("StatCardValue", True)
        desc_lbl = QLabel(description)
        desc_lbl.setProperty("StatCardDesc", True)
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(value_lbl)
        text_layout.addWidget(desc_lbl)
        layout.addLayout(text_layout, 1)

        return card

    def _build_stat_cards_section(self, parent_layout: QVBoxLayout):
        profile = self._ui_profile
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(14)

        self._card_workspace = self._build_stat_card(
            "\U0001F4C1", "orange",
            "工作空间项目", "3", "2 DJ + 1 SW 项目"
        )
        self._card_templates = self._build_stat_card(
            "\U0001F4DD", "blue",
            "文档模板", "10", "7种工程文档 + 3种管理文档"
        )
        self._card_compliance = self._build_stat_card(
            "\u2705", "green",
            "规范检查通过率", "92%", "5/7检查器启用 \u00B7 上次: 2分钟前"
        )
        self._card_changes = self._build_stat_card(
            "\U0001F504", "yellow",
            "待处理变更", "5", "3 Draft \u00B7 2 In Progress"
        )

        self._stat_card_labels = {
            "workspace": self._card_workspace.findChild(QLabel, "", Qt.FindChildrenRecursively),
            "templates": self._card_templates.findChild(QLabel, "", Qt.FindChildrenRecursively),
            "compliance": self._card_compliance.findChild(QLabel, "", Qt.FindChildrenRecursively),
            "changes": self._card_changes.findChild(QLabel, "", Qt.FindChildrenRecursively),
        }

        for card in [self._card_workspace, self._card_templates,
                      self._card_compliance, self._card_changes]:
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            cards_layout.addWidget(card)

        parent_layout.addLayout(cards_layout)

    def _build_quick_action_btn(self, icon, text, action_id):
        btn = QPushButton(f"{icon} {text}")
        btn.setProperty("QuickActionBtn", "true")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(36)
        btn.clicked.connect(
            lambda checked, a=action_id: self.action_triggered.emit(a)
        )
        return btn

    def _build_recent_item(self, name, path):
        item = QWidget()
        item.setProperty("RecentProjectItem", "true")
        item.setCursor(Qt.PointingHandCursor)
        layout = QHBoxLayout(item)
        layout.setContentsMargins(8, 8, 8, 8)

        icon = QLabel("\U0001F4C1")
        name_lbl = QLabel(name)
        name_lbl.setProperty("RecentName", True)
        path_lbl = QLabel(path)
        path_lbl.setProperty("RecentPath", True)

        layout.addWidget(icon)
        layout.addSpacing(6)
        text_vbox = QVBoxLayout()
        text_vbox.setSpacing(1)
        text_vbox.addWidget(name_lbl)
        text_vbox.addWidget(path_lbl)
        layout.addLayout(text_vbox, 1)

        return item

    def _build_bottom_section(self, parent_layout: QVBoxLayout):
        profile = self._ui_profile
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(profile.spacing_lg)

        quick_widget = QWidget()
        quick_layout = QVBoxLayout(quick_widget)
        quick_layout.setContentsMargins(0, 0, 0, 0)
        quick_layout.setSpacing(profile.spacing_sm)

        quick_title = QLabel("\u26A1 快速操作")
        quick_title.setProperty("SectionTitle", True)
        quick_layout.addWidget(quick_title)

        quick_btns_row = QHBoxLayout()
        quick_btns_row.setSpacing(8)

        actions = [
            ("\U0001F4DD", "新建文档", "new_document"),
            ("\U0001F50D", "运行规范检查", "spec_check"),
            ("\U0001F4C1", "新建项目", "new_project"),
            ("\U0001F504", "版本同步", "version_sync"),
            ("\U0001F4DD", "ST编辑器", "st_editor"),
            ("\U0001F527", "自动修复", "auto_fix"),
        ]

        for icon, text, action_id in actions:
            btn = self._build_quick_action_btn(icon, text, action_id)
            self._quick_actions[action_id] = btn
            quick_btns_row.addWidget(btn)

        quick_layout.addLayout(quick_btns_row, 1)
        bottom_layout.addWidget(quick_widget, 1)

        recent_widget = QWidget()
        recent_widget.setFixedWidth(400)
        recent_layout = QVBoxLayout(recent_widget)
        recent_layout.setContentsMargins(0, 0, 0, 0)
        recent_layout.setSpacing(profile.spacing_sm)

        recent_header = QHBoxLayout()
        recent_title = QLabel("\U0001F552 最近项目")
        recent_title.setProperty("SectionTitle", True)
        recent_header.addWidget(recent_title)
        recent_header.addStretch()
        view_all_btn = QLabel('<a href="#" style="color:#4FC3F7;text-decoration:none;">打开全部</a>')
        view_all_btn.setCursor(Qt.PointingHandCursor)
        view_all_btn.setProperty("ViewAllLink", True)
        recent_header.addWidget(view_all_btn)
        recent_layout.addLayout(recent_header)

        self._recent_content = QWidget()
        self._recent_layout = QVBoxLayout(self._recent_content)
        self._recent_layout.setContentsMargins(0, 0, 0, 0)
        self._recent_layout.setSpacing(4)

        default_projects = [
            ("DJ-2026-005 边框缓存机", "0100_PLC自动化/DJ-2026-005"),
            ("SW-2026-007 输送机控制", "0100_PLC自动化/SW-2026-007"),
            ("SW-2026-008 打胶机送料", "0100_PLC自动化/SW-2026-008"),
        ]

        for name, path in default_projects:
            item = self._build_recent_item(name, path)
            self._recent_layout.addWidget(item)

        self._recent_layout.addStretch()
        recent_layout.addWidget(self._recent_content, 1)

        bottom_layout.addWidget(recent_widget)
        parent_layout.addLayout(bottom_layout)

    def refresh_dashboard_data(self):
        try:
            from src.services.project_service import ProjectService
            from src.core.settings import SettingsManager

            projects = ProjectService.get_all_projects() or []
            total = len(projects)
            active = sum(
                1 for p in projects
                if getattr(getattr(p, 'status', None), 'value', '') == 'active'
            )
            completed = sum(
                1 for p in projects
                if getattr(getattr(p, 'status', None), 'value', '') == 'completed'
            )
            archived = total - active - completed

            self.update_stats({
                "total": total,
                "active": active,
                "completed": completed,
                "archived": archived,
            })

            recent = SettingsManager.get_recent_projects() or []
            self.refresh_recent_projects(recent)

        except Exception as e:
            logger.warning(f"刷新Dashboard数据失败: {e}")

    def update_stats(self, data: dict):
        try:
            total = data.get("total", 0)
            active = data.get("active", 0)
            completed = data.get("completed", 0)
            archived = data.get("archived", 0)

            self._update_stat_card_value(self._card_workspace, str(total))
            self._update_stat_card_value(self._card_compliance,
                                          f"{min(92, max(0, 100 - archived * 5))}%")

            pending = total - completed
            self._update_stat_card_value(self._card_changes, str(max(0, pending)))

        except Exception as e:
            logger.error(f"更新统计指标失败: {e}")

    def refresh_statistics(self, total: int, active: int, completed: int, archived: int):
        self.update_stats({
            "total": total,
            "active": active,
            "completed": completed,
            "archived": archived,
        })

    def refresh_recent_projects(self, recent_projects: list):
        while self._recent_layout.count():
            item = self._recent_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not recent_projects:
            empty_label = QLabel("\U0001F4C1 暂无最近项目")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setProperty("EmptyState", True)
            self._recent_layout.addWidget(empty_label)
            self._recent_layout.addStretch()
            return

        for proj in recent_projects[:5]:
            name = proj.get("name", "-") if isinstance(proj, dict) else str(proj)
            path = proj.get("path", "") if isinstance(proj, dict) else ""
            item = self._build_recent_item(name, path)
            self._recent_layout.addWidget(item)

        self._recent_layout.addStretch()

    def _update_stat_card_value(self, card: QFrame, value: str):
        if not card:
            return
        for child in card.findChildren(QLabel):
            if child.property("StatCardValue"):
                child.setText(value)
                break

    def update_health_metrics(
        self,
        compliance: float,
        issues: float,
        libraries: float,
        structure: float,
        overall: float,
    ):
        try:
            self._update_stat_card_value(self._card_compliance, f"{compliance:.0f}%")
            logger.info(f"健康度指标已更新: 综合 {overall:.1f} 分")
        except Exception as e:
            logger.error(f"更新健康度指标失败: {e}")
