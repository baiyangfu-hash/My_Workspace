# -*- coding: utf-8 -*-
"""
Markdown文档编辑器组件

基于QPlainTextEdit构建的轻量级Markdown编辑器，
支持语法高亮预览、实时渲染和导出功能。
（当前为基础实现，后续迭代可集成QWebEngineView实现实时预览）
"""
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
    QLabel,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCursor, QColor

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DocumentEditor(QWidget):
    """
    Markdown文档编辑器

    功能规划:
    - Markdown源码编辑区
    - 实时HTML预览区 (可选)
    - 工具栏快捷按钮 (加粗/斜体/标题/列表等)
    - 文件保存与导出
    - 自动保存机制
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_file_path = None
        self._modified = False
        self._init_ui()

    def _init_ui(self):
        """初始化编辑器UI布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)

        # ===== 工具栏 =====
        toolbar = QHBoxLayout()
        toolbar.setSpacing(4)

        tools = [
            ("B", "粗体 (Ctrl+B)", self._insert_bold),
            ("I", "斜体 (Ctrl+I)", self._insert_italic),
            ("H1", "一级标题", lambda: self._insert_heading(1)),
            ("H2", "二级标题", lambda: self._insert_heading(2)),
            ("--", "无序列表", self._insert_ulist),
            ("1.", "有序列表", self._insert_olist),
            ("``", "代码块", self._insert_code),
            (">", "引用", self._insert_quote),
            ("链接", "插入链接", self._insert_link),
        ]

        for tooltip, text, callback in tools:
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.setMaximumWidth(40)
            btn.clicked.connect(callback)
            toolbar.addWidget(btn)

        toolbar.addStretch()

        # 预览切换按钮
        self._btn_preview = QPushButton("\u2630 预览")
        self._btn_preview.setCheckable(True)
        self._btn_preview.setMaximumWidth(70)
        toolbar.addWidget(self._btn_preview)

        main_layout.addLayout(toolbar)

        # ===== 编辑/预览区域 =====
        self._splitter = QSplitter(Qt.Horizontal)

        # 源码编辑区
        self._editor = QPlainTextEdit()
        editor_font = QFont("Consolas", 12)
        self._editor.setFont(editor_font)
        self._editor.setPlaceholderText(
            "# 在此编写Markdown文档...\n\n"
            "支持标准Markdown语法:\n"
            "- 标题 (# ## ###)\n"
            "- **粗体** / *斜体*\n"
            "- [链接](url)\n"
            "- `代码`\n"
            "- 列表、表格等\n"
        )
        self._editor.textChanged.connect(self._on_text_changed)
        self._splitter.addWidget(self._editor)

        # HTML预览区 (默认隐藏)
        self._preview = QTextBrowser()
        self._preview.setOpenExternalLinks(True)
        self._preview.setMinimumWidth(300)
        self._preview.hide()
        self._splitter.addWidget(self._preview)

        self._splitter.setSizes([700, 400])
        main_layout.addWidget(self._splitter)

        # ===== 底部状态栏 =====
        status_bar = QHBoxLayout()
        self._status_label = QLabel("就绪")
        self._status_label.setStyleSheet(
            "font-size: 9pt; color: #757575;"
        )
        self._line_col_label = QLabel("行 1, 列 1")
        self._line_col_label.setStyleSheet(
            "font-size: 9pt; color: #9E9E9E;"
        )

        status_bar.addWidget(self._status_label)
        status_bar.addStretch()
        status_bar.addWidget(self._line_col_label)
        main_layout.addLayout(status_bar)

        # 预览切换
        self._btn_preview.toggled.connect(self._toggle_preview)

        # 光标位置更新
        self._editor.cursorPositionChanged.connect(self._update_cursor_position)

    def _on_text_changed(self):
        """文本变化处理"""
        self._modified = True
        self._update_status()

        # 如果预览模式开启，自动刷新预览
        if self._btn_preview.isChecked():
            self._refresh_preview()

    def _update_cursor_position(self):
        """更新光标位置显示"""
        cursor = self._editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self._line_col_label.setText(f"\u884C {line}, \u5217 {col}")

    def _update_status(self):
        """更新状态标签"""
        text = self._editor.toPlainText()
        char_count = len(text)
        word_count = len(text.split()) if text.strip() else 0
        modified_mark = " *" if self._modified else ""
        file_name = (
            self._current_file_path.name
            if self._current_file_path else
            "\u65B0\u5EFA\u6587\u6863"
        )
        self._status_label.setText(
            f"{file_name}{modified_mark} | "
            f"{char_count} \u5B57 | {word_count} \u8BCD"
        )

    def _toggle_preview(self, checked: bool):
        """切换预览面板可见性"""
        if checked:
            self._preview.show()
            self._refresh_preview()
        else:
            self._preview.hide()
        self._btn_preview.setText(
            "\u2630 \u7F16\u8F91" if checked else "\u2630 \u9884\u89C8"
        )

    def _refresh_preview(self):
        """刷新HTML预览"""
        try:
            import markdown
            md_text = self._editor.toPlainText()
            html_content = markdown.markdown(
                md_text, extensions=["tables", "fenced_code"]
            )
            wrapped_html = f"<body style='padding:16px; "
            f"font-family:\"Microsoft YaHei\",sans-serif;'>{html_content}</body>"
            self._preview.setHtml(wrapped_html)
        except ImportError:
            self._preview.setPlainText(
                "[预览需要安装 markdown 库: pip install Markdown]"
            )
        except Exception as e:
            logger.warning(f"预览渲染失败: {e}")

    # ========== Markdown快捷插入方法 ==========

    def _insert_bold(self):
        """插入粗体标记"""
        self._wrap_selection("**", "**")

    def _insert_italic(self):
        """插入斜体标记"""
        self._wrap_selection("*", "*")

    def _insert_heading(self, level: int):
        """插入标题标记"""
        prefix = "#" * level + " "
        cursor = self._editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfBlock)
        cursor.insertText(prefix)

    def _insert_ulist(self):
        """插入无序列表"""
        self._insert_at_line_start("- ")

    def _insert_olist(self):
        """插入有序列表"""
        self._insert_at_line_start("1. ")

    def _insert_code(self):
        """插入代码块"""
        cursor = self._editor.textCursor()
        cursor.insertText("```\n\n```")
        cursor.movePosition(QTextCursor.PreviousBlock)
        self._editor.setTextCursor(cursor)

    def _insert_quote(self):
        """插入引用"""
        self._insert_at_line_start("> ")

    def _insert_link(self):
        """插入链接"""
        self._wrap_selection("[", "](url)")

    def _wrap_selection(self, before: str, after: str):
        """将选中文本用前后缀包裹"""
        cursor = self._editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"{before}{text}{after}")
        else:
            cursor.insertText(f"{before}{after}")
            cursor.movePosition(QTextCursor.Left, n=len(after))
            self._editor.setTextCursor(cursor)

    def _insert_at_line_start(self, prefix: str):
        """在行首插入前缀"""
        cursor = self._editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfBlock)
        cursor.insertText(prefix)

    # ========== 公共API ==========

    def open_file(self, file_path: str):
        """打开文件进行编辑"""
        from pathlib import Path
        path = Path(file_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self._editor.setPlainText(content)
            self._current_file_path = path
            self._modified = False
            self._update_status()
            logger.info(f"已打开文件: {path.name}")

    def save_file(self) -> bool:
        """保存当前文件"""
        if not self._current_file_path:
            return False
        try:
            with open(self._current_file_path, "w", encoding="utf-8") as f:
                f.write(self._editor.toPlainText())
            self._modified = False
            self._update_status()
            logger.info(f"文件已保存: {self._current_file_path.name}")
            return True
        except IOError as e:
            logger.error(f"文件保存失败: {e}")
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
            return False

    def get_content(self) -> str:
        """获取编辑器中的文本内容"""
        return self._editor.toPlainText()

    def set_content(self, text: str):
        """设置编辑器文本内容"""
        self._editor.setPlainText(text)
        self._modified = False
        self._update_status()

    @property
    def is_modified(self) -> bool:
        """检查是否有未保存的修改"""
        return self._modified
