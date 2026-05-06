# -*- coding: utf-8 -*-
"""
FB功能块文档生成对话框

用于根据ST代码中的Function Block定义自动生成标准化文档。
（预留接口，待后续迭代实现）
"""
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class FBDocumentDialog(QDialog):
    """
    FB功能块文档生成对话框 (预留)

    功能规划:
    - 解析ST源码中的FUNCTION_BLOCK定义
    - 自动提取变量列表和注释
    - 生成标准化的FB文档模板
    - 支持导出为Markdown/PDF格式
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FB功能块文档生成")
        self.setMinimumSize(500, 350)
        self.setModal(True)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        info_label = QLabel(
            "\u2699\uFE0F FB功能块文档生成器\n\n"
            "此功能正在开发中，将支持:\n"
            "- 从ST源码解析FUNCTION_BLOCK定义\n"
            "- 自动提取输入/输出/局部变量\n"
            "- 生成标准FB文档(Markdown格式)\n"
            "- 变量类型和描述的表格化展示\n\n"
            "敬请期待后续版本..."
        )
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close)
