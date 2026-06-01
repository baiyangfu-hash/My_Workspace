# -*- coding: utf-8 -*-
"""
同步结果对话框 - CHG/IFC文档生成后的审核与回写界面

功能:
- 显示生成文件路径
- 文件内容只读预览
- "打开所在目录"按钮
- "回写到项目"按钮 (将文档复制到项目标准目录)
- "仅保存到输出目录"按钮

设计原则:
- 独立于MainWindow，可单独使用
- 返回用户操作选择供调用方处理
- 同名文件回写时自动备份(.bak)
"""
import os
from pathlib import Path

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QFileDialog,
)
from PyQt5.QtCore import Qt

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SyncResultDialog(QDialog):
    """
    同步结果对话框

    使用方式:
        dialog = SyncResultDialog(parent, file_path, "CHG文档生成结果", doc_type="chg")
        dialog.exec_()
        action = dialog.get_action()
        if action == "writeback":
            ...
    """

    ACTION_OPEN_DIR = "open_dir"
    ACTION_WRITEBACK = "writeback"
    ACTION_SAVE_ONLY = "save_only"

    def __init__(self, parent, file_path: str, title: str, doc_type: str = "chg"):
        """
        初始化同步结果对话框

        Args:
            parent: 父窗口
            file_path: 生成的文件路径
            title: 对话框标题
            doc_type: 文档类型 "chg" | "ifc"
        """
        super().__init__(parent)
        self._file_path = file_path
        self._doc_type = doc_type
        self._action = self.ACTION_SAVE_ONLY

        self.setWindowTitle(title)
        self.setMinimumSize(650, 480)
        self.resize(720, 520)

        self._setup_ui()
        self._load_file_content()

        logger.debug(f"SyncResultDialog初始化: {file_path}")

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        file_label = QLabel(f"\U0001F4C4 生成文件:")
        file_label.setProperty("sectionTitle", True)
        layout.addWidget(file_label)

        path_label = QLabel(str(self._file_path))
        path_label.setWordWrap(True)
        path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        path_label.setProperty("valueLabel", True)
        layout.addWidget(path_label)

        preview_label = QLabel("\U0001F4D6 内容预览:")
        preview_label.setProperty("sectionTitle", True)
        layout.addWidget(preview_label)

        self._preview = QTextEdit()
        self._preview.setReadOnly(True)

        layout.addWidget(self._preview, stretch=1)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self._btn_open_dir = QPushButton(" \U0001F4C2 打开所在目录")
        self._btn_open_dir.setFixedHeight(36)
        self._btn_open_dir.setCursor(Qt.PointingHandCursor)
        self._btn_open_dir.setProperty("ToolBtn", True)
        self._btn_open_dir.clicked.connect(self._on_open_dir)

        self._btn_writeback = QPushButton(" \U0001F4BE 回写到项目")
        self._btn_writeback.setFixedHeight(36)
        self._btn_writeback.setCursor(Qt.PointingHandCursor)
        self._btn_writeback.setProperty("PrimaryBtn", True)
        self._btn_writeback.clicked.connect(self._on_writeback)

        self._btn_save_only = QPushButton(" 仅保存到输出目录")
        self._btn_save_only.setFixedHeight(36)
        self._btn_save_only.setCursor(Qt.PointingHandCursor)
        self._btn_save_only.setProperty("ToolBtn", True)
        self._btn_save_only.clicked.connect(self._on_save_only)

        btn_layout.addWidget(self._btn_open_dir)
        btn_layout.addWidget(self._btn_writeback)
        btn_layout.addStretch()
        btn_layout.addWidget(self._btn_save_only)
        layout.addLayout(btn_layout)

    def _load_file_content(self):
        try:
            p = Path(self._file_path)
            if p.is_file():
                content = p.read_text(encoding="utf-8", errors="replace")
                self._preview.setPlainText(content)
            else:
                self._preview.setPlainText(f"(文件不存在: {self._file_path})")
        except Exception as e:
            self._preview.setPlainText(f"(读取文件失败: {e})")
            logger.warning(f"预览文件失败: {e}")

    def _on_open_dir(self):
        dir_path = os.path.dirname(self._file_path)
        if os.path.isdir(dir_path):
            os.startfile(dir_path)
            logger.info(f"已打开目录: {dir_path}")
        else:
            logger.warning(f"目录不存在: {dir_path}")

    def _on_writeback(self):
        self._action = self.ACTION_WRITEBACK
        self.accept()

    def _on_save_only(self):
        self._action = self.ACTION_SAVE_ONLY
        self.accept()

    def get_action(self) -> str:
        return self._action

    def get_file_path(self) -> str:
        return self._file_path

    def get_doc_type(self) -> str:
        return self._doc_type
