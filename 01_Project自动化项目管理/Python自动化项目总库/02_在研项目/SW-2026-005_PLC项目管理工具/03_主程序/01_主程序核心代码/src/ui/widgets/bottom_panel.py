from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QStackedWidget, QPlainTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QTextCursor


class BottomPanel(QWidget):

    panel_toggled = pyqtSignal(bool)
    tab_switched = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BottomPanel")
        self._expanded = True
        self._default_height = 200
        self._minimum_height = 100
        self._init_ui()

    def _init_ui(self):
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self._init_header()
        self._init_content()
        self._main_layout.addWidget(self._header)
        self._main_layout.addWidget(self._content_stack)
        self.setMinimumHeight(self._minimum_height)
        self.setMaximumHeight(16777215)
        self.resize(self.width(), self._default_height)

    def _init_header(self):
        self._header = QWidget()
        self._header.setObjectName("BottomPanelHeader")
        self._header.setFixedHeight(32)
        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(4, 0, 4, 0)
        header_layout.setSpacing(2)

        self._toggle_btn = QPushButton("▼")
        self._toggle_btn.setFixedSize(24, 24)
        self._toggle_btn.clicked.connect(self.toggle)

        self._title_label = QLabel("输出")

        header_layout.addWidget(self._toggle_btn)
        header_layout.addWidget(self._title_label)

        header_layout.addStretch()

        self._sub_tab_names = ["output", "problems", "terminal"]
        self._sub_tab_buttons = {}
        sub_tab_labels = {"output": "输出", "problems": "问题", "terminal": "终端"}

        for tab_name in self._sub_tab_names:
            btn = QPushButton(sub_tab_labels[tab_name])
            btn.setProperty("BottomPanelTab", True)
            btn.setProperty("Active", False)
            btn.setCheckable(False)
            btn.clicked.connect(lambda checked, name=tab_name: self._on_sub_tab_clicked(name))
            header_layout.addWidget(btn)
            self._sub_tab_buttons[tab_name] = btn

        self._close_btn = QPushButton("✕")
        self._close_btn.setFixedSize(24, 24)
        self._close_btn.setProperty("SidebarCollapseBtn", True)
        self._close_btn.clicked.connect(self.collapse)

        header_layout.addWidget(self._close_btn)

        self._sub_tab_buttons["output"].setProperty("Active", True)

    def _init_content(self):
        self._content_stack = QStackedWidget()
        self._content_stack.setObjectName("BottomPanelContent")

        self._output_edit = QPlainTextEdit()
        self._output_edit.setProperty("OutputText", True)
        self._output_edit.setReadOnly(True)
        self._output_edit.setMaximumBlockCount(10000)

        self._problems_table = QTableWidget()
        self._problems_table.setProperty("ResultTable", True)
        self._problems_table.setColumnCount(5)
        self._problems_table.setHorizontalHeaderLabels(["严重度", "文件", "行号", "规则", "描述"])
        header = self._problems_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.resizeSection(0, 70)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.resizeSection(2, 60)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        self._problems_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._problems_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._problems_table.setAlternatingRowColors(True)
        self._problems_table.verticalHeader().setVisible(False)

        self._terminal_edit = QPlainTextEdit()
        self._terminal_edit.setProperty("OutputText", True)
        self._terminal_edit.setReadOnly(True)
        self._terminal_edit.setMaximumBlockCount(10000)

        self._content_stack.addWidget(self._output_edit)
        self._content_stack.addWidget(self._problems_table)
        self._content_stack.addWidget(self._terminal_edit)

    def _on_sub_tab_clicked(self, tab_name):
        index_map = {name: idx for idx, name in enumerate(self._sub_tab_names)}
        self._content_stack.setCurrentIndex(index_map[tab_name])
        for name, btn in self._sub_tab_buttons.items():
            btn.setProperty("Active", name == tab_name)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._title_label.setText({"output": "输出", "problems": "问题", "terminal": "终端"}[tab_name])
        self.tab_switched.emit(tab_name)

    def append_output(self, text, level="info"):
        color_map = {
            "info": "#4FC1FF",
            "success": "#6BCF7C",
            "warning": "#FFD700",
            "error": "#FF6B6B",
        }
        color = color_map.get(level, "#D4D4D4")
        html = f'<span style="color:{color};">{text}</span>'
        self._output_edit.appendHtml(html)
        self._scroll_to_bottom(self._output_edit)

    def set_problems(self, problems_list):
        self._problems_table.setRowCount(0)
        for problem in problems_list:
            row = self._problems_table.rowCount()
            self._problems_table.insertRow(row)
            severity_item = QTableWidgetItem(problem.get("severity", ""))
            if problem.get("severity", "").lower() == "error":
                severity_item.setForeground(QColor("#FF6B6B"))
            elif problem.get("severity", "").lower() == "warning":
                severity_item.setForeground(QColor("#FFD700"))
            else:
                severity_item.setForeground(QColor("#4FC1FF"))
            self._problems_table.setItem(row, 0, severity_item)
            self._problems_table.setItem(row, 1, QTableWidgetItem(problem.get("file", "")))
            self._problems_table.setItem(row, 2, QTableWidgetItem(str(problem.get("line", ""))))
            self._problems_table.setItem(row, 3, QTableWidgetItem(problem.get("rule", "")))
            self._problems_table.setItem(row, 4, QTableWidgetItem(problem.get("description", "")))

    def clear_problems(self):
        self._problems_table.setRowCount(0)

    def append_terminal(self, text):
        self._terminal_edit.appendPlainText(text)
        self._scroll_to_bottom(self._terminal_edit)

    def _scroll_to_bottom(self, edit):
        cursor = edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        edit.setTextCursor(cursor)

    def toggle(self):
        if self._expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        if self._expanded:
            return
        self._expanded = True
        self._toggle_btn.setText("▼")
        self._content_stack.setVisible(True)
        self.setMinimumHeight(self._minimum_height)
        self.setMaximumHeight(16777215)
        self.resize(self.width(), self._default_height)
        self.panel_toggled.emit(True)

    def collapse(self):
        if not self._expanded:
            return
        self._expanded = False
        self._toggle_btn.setText("▶")
        self._content_stack.setVisible(False)
        self.setFixedHeight(0)
        self.panel_toggled.emit(False)

    def is_expanded(self):
        return self._expanded

    def switch_tab(self, tab_name):
        if tab_name in self._sub_tab_names:
            self._on_sub_tab_clicked(tab_name)