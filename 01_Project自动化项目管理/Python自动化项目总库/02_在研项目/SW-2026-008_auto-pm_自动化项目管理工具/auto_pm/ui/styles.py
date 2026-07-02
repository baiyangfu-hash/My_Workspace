"""共享 UI 样式表

提供 BASE_WIDGET_STYLE，覆盖所有常见控件的显式颜色，
防止 Windows dark mode 下控件继承系统暗色主题导致文字不可读/背景不协调。

使用方式：
    from auto_pm.ui.styles import BASE_WIDGET_STYLE

    _DIALOG_STYLE = BASE_WIDGET_STYLE + "\\n" + \"\"\"
    QDialog { background: #fafafa; }
    ...
    \"\"\"
"""

from __future__ import annotations

# 基础控件样式 — 显式设置颜色，防止 dark mode 继承
BASE_WIDGET_STYLE = """
/* ── 文字颜色 ────────────────────────────────── */
QLabel { color: #333; }
QCheckBox { color: #333; }
QRadioButton { color: #333; }
QGroupBox { color: #333; font-weight: bold; }

/* ── 输入控件 ────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
    background: #ffffff;
    color: #333;
    border: 1px solid #ccc;
    border-radius: 3px;
    padding: 4px 6px;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
    border-color: #4a90d9;
}
QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled,
QComboBox:disabled, QSpinBox:disabled, QDateEdit:disabled {
    background: #f0f0f0;
    color: #999;
}

/* ── 下拉框弹出列表 ──────────────────────────── */
QComboBox QAbstractItemView {
    background: #ffffff;
    color: #333;
    selection-background-color: #4a90d9;
    selection-color: #ffffff;
}

/* ── 表格 ────────────────────────────────────── */
QTableWidget, QTableView {
    background: #ffffff;
    color: #333;
    gridline-color: #e0e0e0;
}
QTableWidget::item, QTableView::item { color: #333; }
QHeaderView::section {
    background: #f0f0f0;
    color: #333;
    border: 1px solid #e0e0e0;
    padding: 4px;
}

/* ── 列表 ────────────────────────────────────── */
QListWidget {
    background: #ffffff;
    color: #333;
    border: 1px solid #ccc;
}

/* ── 滚动条 ──────────────────────────────────── */
QScrollBar:vertical {
    background: #f0f0f0;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #c0c0c0;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #f0f0f0;
    height: 10px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #c0c0c0;
    border-radius: 5px;
    min-width: 20px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── 滚动区域 + 容器 ────────────────────────── */
QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; border: none; }
QStackedWidget, QSplitter { background: transparent; }
QFrame { background: transparent; }

/* ── 按钮 ────────────────────────────────────── */
QPushButton {
    background: #f5f5f5;
    color: #333;
    border: 1px solid #ccc;
    border-radius: 3px;
    padding: 5px 12px;
}
QPushButton:hover { background: #e8e8e8; }
QPushButton:pressed { background: #d0d0d0; }
QPushButton:disabled { color: #999; background: #f0f0f0; }

/* ── Tab ─────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #e0e0e0;
    background: #ffffff;
}
QTabBar::tab {
    background: #f0f0f0;
    color: #555;
    padding: 6px 12px;
    border: 1px solid #e0e0e0;
    border-bottom: none;
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
}
QTabBar::tab:selected {
    background: #ffffff;
    color: #333;
}

/* ── 工具提示 ────────────────────────────────── */
QToolTip {
    background: #ffffe0;
    color: #333;
    border: 1px solid #ccc;
}

/* ── 进度条 ──────────────────────────────────── */
QProgressBar {
    background: #f0f0f0;
    border: 1px solid #e0e0e0;
    border-radius: 3px;
    text-align: center;
    color: #333;
}
QProgressBar::chunk {
    background: #4a90d9;
    border-radius: 3px;
}
"""
