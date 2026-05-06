# -*- coding: utf-8 -*-
"""
新建文档对话框

提供基于模板创建新文档的界面，支持选择文档类型、填写元数据等。
"""
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QTextEdit,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtCore import Qt

from src.core.constants import DocumentType, DOCUMENT_TYPE_NAMES
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class NewDocumentDialog(QDialog):
    """
    新建文档对话框

    支持从预定义模板创建各类工程文档，
    包括需求规格、设计文档、接口文档等。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("\U0001F4DD 新建文档")
        self.setMinimumSize(480, 450)
        self.setModal(True)

        self._doc_data = {}
        self._init_ui()

    def _init_ui(self):
        """初始化对话框UI布局"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 文档类型选择
        form = QFormLayout()
        form.setSpacing(10)

        self._combo_doc_type = QComboBox()
        for doc_type in DocumentType:
            display_name = DOCUMENT_TYPE_NAMES.get(doc_type, doc_type.name)
            self._combo_doc_type.addItem(f"[{doc_type.value}] {display_name}", doc_type)
        form.addRow("文档类型 *:", self._combo_doc_type)

        self._edit_doc_name = QLineEdit()
        self._edit_doc_name.setPlaceholderText("自动生成或自定义文件名")
        form.addRow("文档名称:", self._edit_doc_name)

        self._edit_version = QLineEdit()
        self._edit_version.setText("V1.0.0")
        form.addRow("版本号:", self._edit_version)

        self._edit_author = QLineEdit()
        self._edit_author.setPlaceholderText("文档作者")
        form.addRow("作者:", self._edit_author)

        self._edit_remarks = QTextEdit()
        self._edit_remarks.setMaximumHeight(80)
        self._edit_remarks.setPlaceholderText("备注说明...")
        form.addRow("备注:", self._edit_remarks)

        layout.addLayout(form)
        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_ok = QPushButton("\u27A4 创建")
        btn_ok.setMinimumHeight(34)
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self._on_create)

        btn_cancel = QPushButton("取消")
        btn_cancel.setMinimumHeight(34)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addLayout(btn_layout)

        # 文档类型变化时更新默认名称
        self._combo_doc_type.currentIndexChanged.connect(self._update_default_name)

    def _update_default_name(self, index: int):
        """根据文档类型更新默认文档名称"""
        doc_type = self._combo_doc_type.itemData(index)
        type_name = DOCUMENT_TYPE_NAMES.get(doc_type, doc_type.name)
        self._edit_doc_name.setText(type_name)

    def _on_create(self):
        """确认创建文档"""
        doc_type = self._combo_doc_type.currentData()
        if not doc_type:
            QMessageBox.warning(self, "提示", "请选择文档类型!")
            return

        self._doc_data = {
            "doc_type": doc_type,
            "doc_name": self._edit_doc_name.text().strip() or DOCUMENT_TYPE_NAMES.get(doc_type),
            "version": self._edit_version.text().strip() or "V1.0.0",
            "author": self._edit_author.text().strip(),
            "remarks": self._edit_remarks.toPlainText().strip(),
        }

        logger.info(f"准备创建文档: {self._doc_data['doc_name']}")
        self.accept()

    def get_document_data(self) -> dict:
        """获取用户填写的文档数据"""
        return self._doc_data.copy()
