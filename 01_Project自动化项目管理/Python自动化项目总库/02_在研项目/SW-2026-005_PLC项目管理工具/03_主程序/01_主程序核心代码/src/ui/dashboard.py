# -*- coding: utf-8 -*-
"""
仪表盘页面组件

提供项目概览、快速操作入口、最近项目列表和系统状态信息展示。
作为用户启动应用后的首页，帮助用户快速了解工作状态。
"""
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class StatCard(QFrame):
    """统计卡片组件 - 用于展示关键指标"""

    def __init__(
        self,
        title: str,
        value: str,
        color: str = "#1976D2",
        icon: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.setProperty("StatCard", True)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)

        layout = self.layout() if self.layout() else QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        title_row = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 18pt; color: {color};")
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 10pt; color: #757575;")
        title_row.addWidget(icon_label)
        title_row.addWidget(title_label)
        title_row.addStretch()
        layout.addLayout(title_row)

        self._value_label = QLabel(value)
        self._value_label.setAlignment(Qt.AlignCenter)
        self._value_label.setStyleSheet(
            f"font-size: 22pt; font-weight: bold; color: {color};"
        )
        layout.addWidget(self._value_label)

    def set_value(self, value: str):
        self._value_label.setText(value)


class QuickActionButton(QPushButton):
    """快捷操作按钮"""

    def __init__(self, text: str, icon: str = "", color: str = "#1976D2", parent=None):
        super().__init__(text, parent)
        self.icon_text = icon
        self.btn_color = color
        self.setProperty("QuickAction", True)
        self.setCursor(Qt.PointingHandCursor)


class DashboardPage(QWidget):
    """
    仪表盘页面

    展示内容包括:
    - 项目统计卡片 (总数/进行中/已完成/已归档)
    - 快捷操作按钮区
    - 最近打开的项目列表
    - 系统状态信息

    Signals:
        action_triggered(str): 快捷操作被触发
            - "new_project" / "open_project" / "new_document"
            - "spec_check" / "variable_check" / "generate_report"
    """

    action_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """初始化仪表盘UI布局"""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        content = QWidget()
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(16)

        # ===== 标题区域 =====
        header_layout = QHBoxLayout()
        title_label = QLabel("\u2630 仪表盘")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title_label.setStyleSheet("color: #212121;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        welcome_label = QLabel(
            "欢迎使用 SW-2026-005 PLC项目管理工具"
        )
        welcome_label.setStyleSheet(
            "font-size: 11pt; color: #757575;"
        )
        header_layout.addWidget(welcome_label)
        main_layout.addLayout(header_layout)

        # ===== 统计卡片区域 =====
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        self.card_total = StatCard(
            "项目总数", "0", "#1976D2", "\U0001F4CB"
        )
        self.card_active = StatCard(
            "进行中", "0", "#4CAF50", "\u25B6"
        )
        self.card_completed = StatCard(
            "已完成", "0", "#2196F3", "\u2705"
        )
        self.card_archived = StatCard(
            "已归档", "0", "#9E9E9E", "\U0001F4C1"
        )

        cards_layout.addWidget(self.card_total)
        cards_layout.addWidget(self.card_active)
        cards_layout.addWidget(self.card_completed)
        cards_layout.addWidget(self.card_archived)
        main_layout.addLayout(cards_layout)

        # ===== 快捷操作区域 =====
        quick_section_title = QLabel("\u26A1 快捷操作")
        quick_section_title.setFont(
            QFont("Microsoft YaHei", 12, QFont.Bold)
        )
        quick_section_title.setStyleSheet("color: #424242;")
        main_layout.addWidget(quick_section_title)

        quick_grid = QGridLayout()
        quick_grid.setSpacing(10)

        actions = [
            ("\u002B 新建项目", "#1976D2", "new_project"),
            ("\U0001F4C2 打开项目", "#FF5722", "open_project"),
            ("\U0001F4DD 新建文档", "#4CAF50", "new_document"),
            ("\u2705 规范检查", "#9C27B0", "spec_check"),
            ("\U0001F9EA 变量检查", "#009688", "variable_check"),
            ("\U0001F4CB 生成报告", "#FF9800", "generate_report"),
        ]

        for idx, (text, color, action_id) in enumerate(actions):
            row = idx // 3
            col = idx % 3
            btn = QuickActionButton(text, color=color)
            btn.clicked.connect(
                lambda checked, a=action_id: self.action_triggered.emit(a)
            )
            quick_grid.addWidget(btn, row, col)

        main_layout.addLayout(quick_grid)

        # ===== 最近项目区域 =====
        recent_section_title = QLabel(
            "\U0001F552 最近打开的项目"
        )
        recent_section_title.setFont(
            QFont("Microsoft YaHei", 12, QFont.Bold)
        )
        recent_section_title.setStyleSheet("color: #424242;")
        main_layout.addWidget(recent_section_title)

        recent_scroll = QScrollArea()
        recent_scroll.setWidgetResizable(True)
        recent_scroll.setMaximumHeight(180)
        recent_scroll.setStyleSheet(
            "QScrollArea { border: 1px solid #E0E0E0; border-radius: 6px; }"
        )

        self._recent_content = QWidget()
        self._recent_layout = QVBoxLayout(self._recent_content)
        self._recent_layout.setContentsMargins(8, 8, 8, 8)

        self._recent_empty_label = QLabel(
            "\U0001F4C1 暂无最近打开的项目\n\n"
            "点击上方 \"打开项目\" 或使用 Ctrl+O 快捷键打开一个项目"
        )
        self._recent_empty_label.setAlignment(Qt.AlignCenter)
        self._recent_empty_label.setStyleSheet(
            "color: #9E9E9E; font-size: 10pt; padding: 20px;"
        )
        self._recent_layout.addWidget(self._recent_empty_label)
        self._recent_layout.addStretch()

        recent_scroll.setWidget(self._recent_content)
        main_layout.addWidget(recent_scroll)

        self._recent_scroll = recent_scroll

        # 底部弹性空间
        main_layout.addStretch()

        # ===== 健康度指标区域（新增） =====
        self._init_health_section(main_layout)

    def _init_health_section(self, parent_layout: QVBoxLayout):
        """
        初始化健康度指标展示区域（新增功能）

        显示项目的四维健康度评分：
        - 规范符合度
        - 问题严重程度
        - 库引用状态
        - 结构合规性

        Args:
            parent_layout: 父布局对象
        """
        # 健康度区域标题
        health_title = QLabel("\U0001F4CA \u9879\u76EE\u5065\u5EB7\u5EA6")
        health_title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        health_title.setStyleSheet("color: #424242;")
        parent_layout.addWidget(health_title)

        # 健康度卡片容器
        health_container = QWidget()
        health_layout = QHBoxLayout(health_container)
        health_layout.setContentsMargins(0, 0, 0, 0)
        health_layout.setSpacing(12)

        # 创建四个健康度指标卡片
        self._health_compliance = StatCard(
            "\u89C4\u8303\u7B26\u5408\u5EA6", "--", "#1976D2", "\u2705"
        )
        self._health_issues = StatCard(
            "\u95EE\u9898\u4E25\u91CD\u7A0B", "--", "#F44336", "\u26A0\uFE0F"
        )
        self._health_libraries = StatCard(
            "\u5E93\u5F15\u7528\u72B6\u6001", "--", "#FF9800", "\U0001F4E6"
        )
        self._health_structure = StatCard(
            "\u7ED3\u6784\u5408\u89C4\u6027", "--", "#4CAF50", "\U0001F3CB\uFE0F"
        )

        # 综合健康分卡片
        self._health_overall = StatCard(
            "\u7EFC\u5408\u5065\u5EB7\u5206", "--", "#9C27B0", "\U0001F31F"
        )

        # 添加到布局
        health_layout.addWidget(self._health_compliance)
        health_layout.addWidget(self._health_issues)
        health_layout.addWidget(self._health_libraries)
        health_layout.addWidget(self._health_structure)
        health_layout.addWidget(self._health_overall)

        parent_layout.addWidget(health_container)

        # 默认隐藏（等待数据）
        health_container.hide()
        self._health_container = health_container

        logger.debug("健康度指标展示区域已初始化")

    def update_health_metrics(
        self,
        compliance: float,
        issues: float,
        libraries: float,
        structure: float,
        overall: float,
    ):
        """
        更新健康度指标显示

        Args:
            compliance: 规范符合度得分 (0-100)
            issues: 问题严重程度得分 (0-100，越高越好)
            libraries: 库引用状态得分 (0-100)
            structure: 结构合规性得分 (0-100)
            overall: 综合健康分 (0-100)
        """
        try:
            # 显示容器
            if self._health_container:
                self._health_container.show()

            # 更新各维度分数
            self._update_stat_card_value(
                self._health_compliance, f"{compliance:.1f}"
            )
            self._update_stat_card_value(
                self._health_issues, f"{issues:.1f}"
            )
            self._update_stat_card_value(
                self._health_libraries, f"{libraries:.1f}"
            )
            self._update_stat_card_value(
                self._health_structure, f"{structure:.1f}"
            )
            self._update_stat_card_value(
                self._health_overall, f"{overall:.1f}"
            )

            logger.info(f"健康度指标已更新: 综合 {overall:.1f} 分")

        except Exception as e:
            logger.error(f"更新健康度指标失败: {e}")

    def _update_stat_card_value(self, card: StatCard, value: str):
        if card and hasattr(card, 'set_value'):
            card.set_value(value)

    def refresh_statistics(self, total: int, active: int, completed: int, archived: int):
        for card, value in [
            (self.card_total, total),
            (self.card_active, active),
            (self.card_completed, completed),
            (self.card_archived, archived),
        ]:
            if card and hasattr(card, 'set_value'):
                card.set_value(str(value))

    def refresh_recent_projects(self, recent_projects: list):
        """刷新最近项目列表"""
        while self._recent_layout.count():
            item = self._recent_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not recent_projects:
            self._recent_empty_label = QLabel(
                "\U0001F4C1 暂无最近打开的项目\n\n"
                "点击上方 \"打开项目\" 或使用 Ctrl+O 快捷键打开一个项目"
            )
            self._recent_empty_label.setAlignment(Qt.AlignCenter)
            self._recent_empty_label.setStyleSheet(
                "color: #9E9E9E; font-size: 10pt; padding: 20px;"
            )
            self._recent_layout.addWidget(self._recent_empty_label)
            self._recent_layout.addStretch()
            return

        for proj in recent_projects[:10]:
            name = proj.get("name", "-")
            path = proj.get("path", "-")
            label = QLabel(f"  \U0001F4C2 {name}")
            label.setToolTip(path)
            label.setStyleSheet(
                "font-size: 10pt; color: #424242; padding: 4px 8px;"
            )
            self._recent_layout.addWidget(label)

        self._recent_layout.addStretch()
