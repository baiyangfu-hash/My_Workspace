# -*- coding: utf-8 -*-
"""
系统设置对话框 - 从main_window.py提取的独立设置界面

提供用户偏好设置的管理界面，包括:
- 常规设置: 默认项目路径、自动保存、日志级别
- 编辑器设置: 字体、字号、制表符宽度

设计原则:
- 独立于MainWindow，可单独使用
- 使用SettingsManager读写配置
- 支持Tab分组管理不同类别的设置
- 保存时验证数据有效性
"""
from typing import Optional
from pathlib import Path

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QTabWidget,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QLabel,
)
from PyQt5.QtCore import Qt

from src.core.settings import SettingsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SettingsDialog(QDialog):
    """
    系统设置对话框

    使用方式:
        from src.ui.dialogs.settings_dialog import SettingsDialog
        
        dialog = SettingsDialog(parent)
        if dialog.exec_() == dialog.Accepted:
            # 设置已保存
            pass

    设置分类:
        Tab 1 - 常规设置: 项目路径、自动保存、日志级别
        Tab 2 - 编辑器设置: 字体、字号、制表符宽度
    """

    def __init__(self, parent=None):
        """
        初始化设置对话框

        Args:
            parent: 父窗口 (QWidget或QMainWindow)
        """
        super().__init__(parent)
        self.setWindowTitle("\u2699\uFE0F 系统设置")
        self.setMinimumSize(550, 420)
        self.resize(600, 450)

        # 初始化UI
        self._setup_ui()
        
        logger.debug("设置对话框初始化完成")

    def _setup_ui(self):
        """构建对话框UI布局"""
        # 主布局
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Tab控件 - 分组显示不同类别设置
        tabs = QTabWidget()
        self._create_general_tab(tabs)
        self._create_editor_tab(tabs)
        layout.addWidget(tabs)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        apply_btn = QPushButton("应用")
        apply_btn.setFixedWidth(70)
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1976D2;
                border: 1px solid #1976D2;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #E3F2FD; }
        """)
        apply_btn.clicked.connect(self._on_apply)

        reset_btn = QPushButton("重置")
        reset_btn.setFixedWidth(70)
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #757575;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #F5F5F5; color: #424242; }
        """)
        reset_btn.clicked.connect(self._on_reset)

        ok_btn = QPushButton("保存")
        ok_btn.setFixedWidth(80)
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1565C0; }
            QPushButton:pressed { background-color: #0D47A1; }
        """)
        ok_btn.clicked.connect(self._on_save)

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedWidth(80)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #757575;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
            }
            QPushButton:hover { 
                background-color: #F5F5F5; 
                color: #424242; 
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(apply_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

    def _create_general_tab(self, tabs: QTabWidget):
        """
        创建常规设置标签页

        包含设置项:
        - 默认项目路径 (QLineEdit)
        - 自动保存 (QCheckBox)
        - 日志级别 (QComboBox)

        Args:
            tabs: 父级TabWidget
        """
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        # 默认项目路径
        self._setting_default_path = QLineEdit(
            SettingsManager.get("default_project_root", "./Projects") or ""
        )
        self._setting_default_path.setPlaceholderText("例如: ./Projects 或 D:/Projects")
        form.addRow("默认项目路径:", self._setting_default_path)

        self._path_status = QLabel("")
        self._path_status.setStyleSheet("font-size: 8pt; padding: 2px 0;")
        form.addRow("", self._path_status)
        self._setting_default_path.textChanged.connect(self._validate_path_live)

        self._setting_auto_save = QCheckBox("启用自动保存")
        self._setting_auto_save.setChecked(SettingsManager.get("auto_backup", True))
        form.addRow("", self._setting_auto_save)

        # 日志级别
        self._setting_log_level = QComboBox()
        self._setting_log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        current_level = SettingsManager.get("log_level", "INFO")
        idx = self._setting_log_level.findText(current_level)
        if idx >= 0:
            self._setting_log_level.setCurrentIndex(idx)
        form.addRow("日志级别:", self._setting_log_level)

        tabs.addTab(tab, "常规设置")

    def _create_editor_tab(self, tabs: QTabWidget):
        """
        创建编辑器设置标签页

        包含设置项:
        - 字体 (QLineEdit)
        - 字号 (QSpinBox)
        - 制表符宽度 (QSpinBox)

        Args:
            tabs: 父级TabWidget
        """
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        # 编辑器字体
        self._editor_font = QLineEdit(
            SettingsManager.get("editor_font_family", "Consolas")
        )
        self._editor_font.setPlaceholderText("例如: Consolas, Microsoft YaHei Mono")
        form.addRow("字体:", self._editor_font)

        # 字号
        self._editor_font_size = QSpinBox()
        self._editor_font_size.setRange(8, 32)
        self._editor_font_size.setValue(
            SettingsManager.get("editor_font_size", 12)
        )
        form.addRow("字号:", self._editor_font_size)

        # 制表符宽度
        self._editor_tab_width = QSpinBox()
        self._editor_tab_width.setRange(2, 8)
        self._editor_tab_width.setValue(
            SettingsManager.get("editor_tab_width", 4)
        )
        form.addRow("制表符宽度:", self._editor_tab_width)

        tabs.addTab(tab, "编辑器设置")

    def _on_save(self):
        try:
            validation_errors = self._validate_settings()
            if validation_errors:
                QMessageBox.warning(
                    self,
                    "\u26A0\uFE0F 输入错误",
                    f"以下设置项有误:\n\n" + "\n".join(validation_errors),
                    QMessageBox.Ok,
                )
                return

            self._save_settings()

            logger.info("系统设置已保存")

            QMessageBox.information(
                self,
                "\u2705 成功",
                "设置已保存，部分设置需要重启应用后生效。",
                QMessageBox.Ok,
            )
            self.accept()

        except Exception as e:
            logger.exception(f"保存设置失败: {e}")
            QMessageBox.critical(
                self,
                "\u274C 错误",
                f"保存设置失败:\n\n{str(e)}",
                QMessageBox.Ok,
            )

    def _validate_settings(self) -> list:
        errors = []

        default_path = self._setting_default_path.text().strip()
        if default_path and len(default_path) > 260:
            errors.append("- 默认项目路径过长 (最大260字符)")
        if default_path and not Path(default_path).exists():
            errors.append("- 默认项目路径不存在 (将自动创建)")

        font_name = self._editor_font.text().strip()
        if font_name and not all(c.isprintable() for c in font_name):
            errors.append("- 字体名称包含非法字符")

        font_size = self._editor_font_size.value()
        if font_size < 8 or font_size > 32:
            errors.append("- 字号必须在 8-32 之间")

        tab_width = self._editor_tab_width.value()
        if tab_width < 2 or tab_width > 8:
            errors.append("- 制表符宽度必须在 2-8 之间")

        return errors

    def _validate_path_live(self, text: str):
        path = text.strip()
        if not path:
            self._path_status.setText("")
            self._path_status.setStyleSheet("font-size: 8pt; padding: 2px 0;")
            return
        p = Path(path)
        if p.exists() and p.is_dir():
            self._path_status.setText("\u2705 路径有效")
            self._path_status.setStyleSheet("color: #4CAF50; font-size: 8pt; padding: 2px 0;")
        else:
            self._path_status.setText("\u26A0\uFE0F 路径不存在")
            self._path_status.setStyleSheet("color: #FF9800; font-size: 8pt; padding: 2px 0;")

    def _on_apply(self):
        validation_errors = self._validate_settings()
        if validation_errors:
            QMessageBox.warning(
                self, "\u26A0\uFE0F 输入错误",
                f"以下设置项有误:\n\n" + "\n".join(validation_errors),
                QMessageBox.Ok,
            )
            return
        self._save_settings()
        logger.info("设置已应用 (未关闭对话框)")

    def _on_reset(self):
        self._setting_default_path.setText(
            SettingsManager.get("default_project_root", "./Projects") or ""
        )
        self._setting_auto_save.setChecked(SettingsManager.get("auto_backup", True))
        current_level = SettingsManager.get("log_level", "INFO")
        idx = self._setting_log_level.findText(current_level)
        if idx >= 0:
            self._setting_log_level.setCurrentIndex(idx)
        self._editor_font.setText(
            SettingsManager.get("editor_font_family", "Consolas")
        )
        self._editor_font_size.setValue(
            SettingsManager.get("editor_font_size", 12)
        )
        self._editor_tab_width.setValue(
            SettingsManager.get("editor_tab_width", 4)
        )
        logger.info("设置已重置为当前保存值")

    def _save_settings(self):
        SettingsManager.set(
            "default_project_root",
            self._setting_default_path.text().strip(),
        )
        SettingsManager.set(
            "auto_backup",
            self._setting_auto_save.isChecked(),
        )
        SettingsManager.set(
            "log_level",
            self._setting_log_level.currentText(),
        )
        SettingsManager.set(
            "editor_font_family",
            self._editor_font.text().strip() or "Consolas",
        )
        SettingsManager.set(
            "editor_font_size",
            self._editor_font_size.value(),
        )
        SettingsManager.set(
            "editor_tab_width",
            self._editor_tab_width.value(),
        )
        SettingsManager.save()
