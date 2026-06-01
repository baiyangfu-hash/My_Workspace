# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QAbstractItemView,
    QLabel,
    QTextEdit,
    QSplitter,
    QMessageBox,
    QInputDialog,
    QComboBox,
    QGroupBox,
    QLineEdit,
    QFrame,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPalette

from src.core.constants import ChangeCategory, ChangeStatus
from src.services.change_service import ChangeService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ChangeManagementPanel(QWidget):

    change_request_selected = pyqtSignal(str, str)
    status_changed = pyqtSignal()

    STATUS_COLORS = {
        ChangeStatus.DRAFT.value: "#9E9E9E",
        ChangeStatus.REVIEW.value: "#2196F3",
        ChangeStatus.APPROVED.value: "#4CAF50",
        ChangeStatus.ANALYZING.value: "#FF9800",
        ChangeStatus.IN_PROGRESS.value: "#00BCD4",
        ChangeStatus.IMPLEMENTED.value: "#8BC34A",
        ChangeStatus.VERIFYING.value: "#7C4DFF",
        ChangeStatus.COMPLETED.value: "#3F51B5",
        ChangeStatus.CANCELLED.value: "#F44336",
    }

    STATUS_DISPLAY = {
        ChangeStatus.DRAFT.value: "草稿",
        ChangeStatus.REVIEW.value: "审核中",
        ChangeStatus.APPROVED.value: "已批准",
        ChangeStatus.ANALYZING.value: "分析中",
        ChangeStatus.IN_PROGRESS.value: "进行中",
        ChangeStatus.IMPLEMENTED.value: "已实施",
        ChangeStatus.VERIFYING.value: "验证中",
        ChangeStatus.COMPLETED.value: "已完成",
        ChangeStatus.CANCELLED.value: "已取消",
    }

    BADGE_STYLES = {
        "draft": ("Draft", "#6B6B6B", "#E0E0E0"),
        "in-progress": ("In-Progress", "#2196F3", "#E3F2FD"),
        "approved": ("Approved", "#4CAF50", "#E8F5E9"),
        "rejected": ("Rejected", "#F44336", "#FFEBEE"),
    }

    COL_ID = 0
    COL_TITLE = 1
    COL_PROJECT = 2
    COL_STATUS = 3
    COL_CREATED_DATE = 4
    COL_ACTIONS = 5
    COL_COUNT = 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self._project_path = None
        self._current_change_id = None
        self._all_requests = []
        self._search_text = ""
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        toolbar = self._build_toolbar()
        main_layout.addWidget(toolbar)

        splitter = QSplitter(Qt.Vertical)

        self._table = QTableWidget(0, self.COL_COUNT)
        self._table.setHorizontalHeaderLabels(
            ["编号", "标题", "项目", "状态", "创建日期", "操作"]
        )
        self._apply_table_style()
        self._table.horizontalHeader().setSectionResizeMode(
            self.COL_ID, QHeaderView.ResizeToContents
        )
        self._table.horizontalHeader().setSectionResizeMode(
            self.COL_TITLE, QHeaderView.Stretch
        )
        self._table.horizontalHeader().setSectionResizeMode(
            self.COL_PROJECT, QHeaderView.ResizeToContents
        )
        self._table.horizontalHeader().setSectionResizeMode(
            self.COL_STATUS, QHeaderView.Fixed
        )
        self._table.setColumnWidth(self.COL_STATUS, 100)
        self._table.horizontalHeader().setSectionResizeMode(
            self.COL_CREATED_DATE, QHeaderView.ResizeToContents
        )
        self._table.horizontalHeader().setSectionResizeMode(
            self.COL_ACTIONS, QHeaderView.Fixed
        )
        self._table.setColumnWidth(self.COL_ACTIONS, 120)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(False)
        self._table.verticalHeader().setVisible(False)
        self._table.cellClicked.connect(lambda row, col: self._on_row_selected(row))
        splitter.addWidget(self._table)

        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(4, 4, 4, 4)
        detail_layout.setSpacing(6)

        self._detail_title = QLabel("选择变更单查看详情")
        self._detail_title.setProperty("panelTitle", True)
        self._detail_title.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        detail_layout.addWidget(self._detail_title)

        self._detail_content = QTextEdit()
        self._detail_content.setReadOnly(True)
        self._detail_content.setMaximumHeight(180)
        self._detail_content.setPlaceholderText("变更单内容将在此显示...")
        detail_layout.addWidget(self._detail_content)

        action_group = QGroupBox("状态操作")
        action_group.setProperty("IndustrialGroup", True)
        action_layout = QHBoxLayout(action_group)
        action_layout.setSpacing(6)

        self._btn_approve = QPushButton("✅ 批准")
        self._btn_approve.setProperty("SuccessBtn", True)
        self._btn_approve.setFixedHeight(30)
        self._btn_approve.clicked.connect(self._on_approve)
        action_layout.addWidget(self._btn_approve)

        self._btn_advance = QPushButton("⏩ 推进")
        self._btn_advance.setProperty("PrimaryBtn", True)
        self._btn_advance.setFixedHeight(30)
        self._btn_advance.clicked.connect(self._on_advance)
        action_layout.addWidget(self._btn_advance)

        self._btn_cancel = QPushButton("❌ 取消")
        self._btn_cancel.setProperty("DangerBtn", True)
        self._btn_cancel.setFixedHeight(30)
        self._btn_cancel.clicked.connect(self._on_cancel)
        action_layout.addWidget(self._btn_cancel)

        action_layout.addStretch()
        detail_layout.addWidget(action_group)

        splitter.addWidget(detail_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter)

        self._update_action_buttons(None)

    def _build_toolbar(self) -> QWidget:
        toolbar_container = QFrame()
        toolbar_container.setObjectName("toolbarContainer")
        toolbar_container.setStyleSheet("""
            QFrame#toolbarContainer {
                background-color: #2D2D30;
                border-radius: 4px;
                padding: 4px;
            }
        """)

        toolbar = QHBoxLayout(toolbar_container)
        toolbar.setContentsMargins(8, 6, 8, 6)
        toolbar.setSpacing(8)

        self._btn_create = QPushButton("➕ 新建变更单")
        self._btn_create.setObjectName("primaryButton")
        self._btn_create.setStyleSheet("""
            QPushButton#primaryButton {
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton#primaryButton:hover {
                background-color: #1084D8;
            }
            QPushButton#primaryButton:pressed {
                background-color: #005A9E;
            }
        """)
        self._btn_create.setFixedHeight(32)
        self._btn_create.setCursor(Qt.PointingHandCursor)
        self._btn_create.clicked.connect(self._on_create)
        toolbar.addWidget(self._btn_create)

        self._btn_refresh = QPushButton("🔄 刷新列表")
        self._btn_refresh.setObjectName("secondaryButton")
        self._btn_refresh.setStyleSheet("""
            QPushButton#secondaryButton {
                background-color: #3C3C3C;
                color: #CCCCCC;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton#secondaryButton:hover {
                background-color: #4A4A4A;
                color: white;
            }
            QPushButton#secondaryButton:pressed {
                background-color: #333333;
            }
        """)
        self._btn_refresh.setFixedHeight(32)
        self._btn_refresh.setCursor(Qt.PointingHandCursor)
        self._btn_refresh.clicked.connect(self.refresh)
        toolbar.addWidget(self._btn_refresh)

        self._btn_sync_check = QPushButton("🔍 版本同步检查")
        self._btn_sync_check.setObjectName("secondaryButton")
        self._btn_sync_check.setStyleSheet("""
            QPushButton#secondaryButton {
                background-color: #3C3C3C;
                color: #CCCCCC;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton#secondaryButton:hover {
                background-color: #4A4A4A;
                color: white;
            }
            QPushButton#secondaryButton:pressed {
                background-color: #333333;
            }
        """)
        self._btn_sync_check.setFixedHeight(32)
        self._btn_sync_check.setCursor(Qt.PointingHandCursor)
        toolbar.addWidget(self._btn_sync_check)

        toolbar.addStretch()

        self._search_input = QLineEdit()
        self._search_input.setObjectName("searchInput")
        self._search_input.setPlaceholderText("搜索变更单...")
        self._search_input.setFixedWidth(200)
        self._search_input.setFixedHeight(32)
        self._search_input.setStyleSheet("""
            QLineEdit#searchInput {
                background-color: #3C3C3C;
                color: #CCCCCC;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 13px;
            }
            QLineEdit#searchInput:focus {
                border: 1px solid #007ACC;
            }
            QLineEdit#searchInput::placeholder {
                color: #888888;
            }
        """)
        self._search_input.textChanged.connect(self._on_search_text_changed)
        toolbar.addWidget(self._search_input)

        return toolbar_container

    def _create_status_badge(self, status: str) -> QLabel:
        badge = QLabel()
        badge.setText(status)

        badge_key = "draft"
        if status in ("In-Progress", "进行中", "审核中", "分析中", "实施中"):
            badge_key = "in-progress"
        elif status in ("Approved", "已批准", "已完成"):
            badge_key = "approved"
        elif status in ("Rejected", "已取消"):
            badge_key = "rejected"

        display_text, text_color, bg_color = self.BADGE_STYLES.get(badge_key, (status, "#9E9E9E", "#E0E0E0"))

        badge.setText(display_text)
        badge.setAlignment(Qt.AlignCenter)
        badge.setProperty("StatusBadge", badge_key)
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 10px;
                padding: 3px 12px;
                font-size: 11px;
                font-weight: bold;
            }}
        """)
        badge.setFixedHeight(24)
        return badge

    def _apply_table_style(self):
        self._table.setStyleSheet("""
            QTableWidget {
                gridline-color: #3E3E42;
                background-color: #252526;
                alternate-background-color: #2D2D30;
                color: #CCCCCC;
                border: 1px solid #3E3E42;
                border-radius: 4px;
            }

            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #3E3E42;
            }

            QTableWidget::item:selected {
                background-color: #094771;
                color: white;
            }

            QTableWidget::item:hover {
                background-color: #2A2D2E;
            }

            QHeaderView::section {
                background-color: #2D2D30;
                color: #CCCCCC;
                border-bottom: 2px solid #E86100;
                padding: 8px 6px;
                font-weight: bold;
                font-size: 12px;
                border-right: 1px solid #3E3E42;
            }

            QTableWidget QTableCornerButton::section {
                background-color: #2D2D30;
                border: none;
            }
        """)

    def _on_search_text_changed(self, text: str):
        self._search_text = text.strip().lower()
        self._apply_filter()

    def _apply_filter(self):
        if not hasattr(self, '_all_requests'):
            return

        self._table.setRowCount(0)

        filtered_requests = []
        if not self._search_text:
            filtered_requests = self._all_requests
        else:
            for req in self._all_requests:
                if (self._search_text in req.change_id.lower() or
                    self._search_text in req.title.lower()):
                    filtered_requests.append(req)

        for row, req in enumerate(filtered_requests):
            self._populate_row(row, req)

        self._detail_title.setText(f"共 {len(filtered_requests)} 个变更单")

    def _populate_row(self, row: int, req):
        self._table.insertRow(row)

        id_item = QTableWidgetItem(req.change_id)
        id_item.setForeground(QColor("#4FC1FF"))
        font = id_item.font()
        font.setUnderline(True)
        id_item.setFont(font)
        id_item.setData(Qt.UserRole, req.change_id)
        self._table.setItem(row, self.COL_ID, id_item)

        title_item = QTableWidgetItem(req.title)
        self._table.setItem(row, self.COL_TITLE, title_item)

        project_name = getattr(req, 'project', '') or ''
        project_item = QTableWidgetItem(project_name)
        self._table.setItem(row, self.COL_PROJECT, project_item)

        status_display = self.STATUS_DISPLAY.get(req.status, req.status)
        badge_label = self._create_status_badge(status_display)
        self._table.setCellWidget(row, self.COL_STATUS, badge_label)

        created_date = getattr(req, 'created_date', '') or ''
        date_item = QTableWidgetItem(created_date)
        self._table.setItem(row, self.COL_CREATED_DATE, date_item)

        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(4, 2, 4, 2)
        actions_layout.setSpacing(4)

        btn_view = QPushButton("查看")
        btn_view.setObjectName("actionMiniBtn")
        btn_view.setStyleSheet("""
            QPushButton#actionMiniBtn {
                background-color: transparent;
                color: #4FC1FF;
                border: 1px solid #4FC1FF;
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 11px;
            }
            QPushButton#actionMiniBtn:hover {
                background-color: #4FC1FF;
                color: white;
            }
        """)
        btn_view.setFixedHeight(22)
        btn_view.setCursor(Qt.PointingHandCursor)
        btn_view.clicked.connect(lambda checked, r=row: self._on_view_detail(r))
        actions_layout.addWidget(btn_view)

        btn_review = QPushButton("审核")
        btn_review.setObjectName("actionMiniBtn")
        btn_review.setStyleSheet("""
            QPushButton#actionMiniBtn {
                background-color: transparent;
                color: #4CAF50;
                border: 1px solid #4CAF50;
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 11px;
            }
            QPushButton#actionMiniBtn:hover {
                background-color: #4CAF50;
                color: white;
            }
        """)
        btn_review.setFixedHeight(22)
        btn_review.setCursor(Qt.PointingHandCursor)
        btn_review.clicked.connect(lambda checked, r=row: self._on_review(r))
        actions_layout.addWidget(btn_review)

        actions_layout.addStretch()
        self._table.setCellWidget(row, self.COL_ACTIONS, actions_widget)

    def _on_view_detail(self, row: int):
        self._on_row_selected(row)

    def _on_review(self, row: int):
        self._on_row_selected(row)
        if self._current_change_id:
            self._on_approve()

    def set_project_path(self, project_path: str):
        self._project_path = project_path
        self.refresh()

    def refresh(self):
        self._table.setRowCount(0)
        self._all_requests = []

        if not self._project_path:
            self._detail_title.setText("请先打开项目")
            return

        try:
            requests = ChangeService.list_change_requests(self._project_path)
            self._all_requests = requests
        except Exception as e:
            logger.exception(f"加载变更单列表失败: {e}")
            self._detail_title.setText("加载失败")
            return

        self._apply_filter()

    def _on_row_selected(self, row: int):
        if row < 0:
            self._current_change_id = None
            self._detail_content.clear()
            self._update_action_buttons(None)
            return

        id_item = self._table.item(row, self.COL_ID)
        if not id_item:
            return

        change_id = id_item.data(Qt.UserRole) or id_item.text()
        self._current_change_id = change_id
        self.change_request_selected.emit(change_id, self._project_path or "")

        status_cell = self._table.cellWidget(row, self.COL_STATUS)
        current_status = None
        if status_cell and isinstance(status_cell, QLabel):
            status_text = status_cell.text()
            for val, display in self.STATUS_DISPLAY.items():
                if display == status_text or val == status_text:
                    current_status = val
                    break

        self._update_action_buttons(current_status)
        self._load_change_detail(change_id)

    def _load_change_detail(self, change_id: str):
        if not self._project_path:
            return

        file_path = ChangeService._find_change_file(self._project_path, change_id)
        if not file_path:
            self._detail_content.setHtml("<p style='color:#9E9E9E'>文件未找到</p>")
            return

        try:
            content = file_path.read_text(encoding="utf-8")
            self._detail_content.setPlainText(content)
        except Exception as e:
            self._detail_content.setHtml(
                f"<p style='color:#F44336'>读取失败: {e}</p>"
            )

    def _update_action_buttons(self, current_status: str):
        if current_status is None:
            self._btn_approve.setEnabled(False)
            self._btn_advance.setEnabled(False)
            self._btn_cancel.setEnabled(False)
            return

        try:
            status_enum = None
            for s in ChangeStatus:
                if s.value == current_status:
                    status_enum = s
                    break

            if status_enum is None:
                self._btn_approve.setEnabled(False)
                self._btn_advance.setEnabled(False)
                self._btn_cancel.setEnabled(False)
                return

            valid_next = ChangeStatus.valid_transitions(status_enum)
            self._btn_approve.setEnabled(ChangeStatus.APPROVED in valid_next)
            self._btn_advance.setEnabled(
                any(s in valid_next for s in [
                    ChangeStatus.REVIEW,
                    ChangeStatus.ANALYZING,
                    ChangeStatus.IN_PROGRESS,
                    ChangeStatus.IMPLEMENTED,
                    ChangeStatus.VERIFYING,
                    ChangeStatus.COMPLETED,
                ])
            )
            self._btn_cancel.setEnabled(ChangeStatus.CANCELLED in valid_next)
        except Exception:
            self._btn_approve.setEnabled(False)
            self._btn_advance.setEnabled(False)
            self._btn_cancel.setEnabled(False)

    def _on_create(self):
        if not self._project_path:
            QMessageBox.warning(self, "⚠️ 提示", "请先打开项目")
            return

        categories = [c.value for c in ChangeCategory]
        category, ok = QInputDialog.getItem(
            self, "新建变更单", "选择变更分类:", categories, 0, False
        )
        if not ok:
            return

        title, ok = QInputDialog.getText(
            self, "新建变更单", "变更标题:"
        )
        if not ok or not title.strip():
            return

        description, ok = QInputDialog.getText(
            self, "新建变更单", "变更描述(可选):"
        )

        try:
            category_enum = ChangeCategory(category)
            req, error = ChangeService.create_change_request(
                self._project_path, category_enum, title.strip(),
                description.strip() if ok else ""
            )
            if error:
                QMessageBox.warning(self, "⚠️ 创建失败", error)
                return
            self.refresh()
            self.status_changed.emit()
            QMessageBox.information(
                self, "✅ 成功", f"变更单 {req.change_id} 已创建"
            )
        except Exception as e:
            QMessageBox.critical(self, "❌ 错误", f"创建变更单失败: {e}")

    def _on_approve(self):
        if not self._current_change_id or not self._project_path:
            return

        approver, ok = QInputDialog.getText(
            self, "审核通过", "审核人姓名:"
        )
        if not ok:
            return

        try:
            success = ChangeService.approve_change_request(
                self._project_path, self._current_change_id,
                approver.strip() if approver else ""
            )
            if success:
                self.refresh()
                self.status_changed.emit()
                QMessageBox.information(self, "✅ 成功", "变更单已审核通过")
            else:
                QMessageBox.warning(self, "⚠️ 失败", "审核操作未成功，请检查变更单状态")
        except Exception as e:
            QMessageBox.critical(self, "❌ 错误", f"审核操作失败: {e}")

    def _on_advance(self):
        if not self._current_change_id or not self._project_path:
            return

        file_path = ChangeService._find_change_file(
            self._project_path, self._current_change_id
        )
        if not file_path:
            return

        current_status = ChangeService._read_status(file_path)
        current_enum = ChangeService._status_from_value(current_status)
        if not current_enum:
            return

        valid_next = ChangeStatus.valid_transitions(current_enum)
        advance_options = [
            s for s in valid_next
            if s not in (ChangeStatus.CANCELLED, ChangeStatus.APPROVED)
        ]
        if not advance_options:
            QMessageBox.information(self, "ℹ️ 提示", "当前状态无可推进的目标状态")
            return

        options = [
            f"{self.STATUS_DISPLAY.get(s.value, s.value)} ({s.value})"
            for s in advance_options
        ]
        choice, ok = QInputDialog.getItem(
            self, "推进状态", "选择目标状态:", options, 0, False
        )
        if not ok:
            return

        target_value = choice.split("(")[-1].rstrip(")")
        target_enum = ChangeService._status_from_value(target_value)
        if not target_enum:
            return

        try:
            success = ChangeService.update_status(
                self._project_path, self._current_change_id, target_enum
            )
            if success:
                self.refresh()
                self.status_changed.emit()
                QMessageBox.information(self, "✅ 成功", "状态已更新")
            else:
                QMessageBox.warning(self, "⚠️ 失败", "状态更新未成功")
        except Exception as e:
            QMessageBox.critical(self, "❌ 错误", f"状态更新失败: {e}")

    def _on_cancel(self):
        if not self._current_change_id or not self._project_path:
            return

        reply = QMessageBox.question(
            self, "❓ 确认取消",
            f"确定要取消变更单 {self._current_change_id} 吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            success = ChangeService.update_status(
                self._project_path, self._current_change_id,
                ChangeStatus.CANCELLED
            )
            if success:
                self.refresh()
                self.status_changed.emit()
                QMessageBox.information(self, "✅ 成功", "变更单已取消")
            else:
                QMessageBox.warning(self, "⚠️ 失败", "取消操作未成功")
        except Exception as e:
            QMessageBox.critical(self, "❌ 错误", f"取消操作失败: {e}")

    def cleanup(self):
        pass
