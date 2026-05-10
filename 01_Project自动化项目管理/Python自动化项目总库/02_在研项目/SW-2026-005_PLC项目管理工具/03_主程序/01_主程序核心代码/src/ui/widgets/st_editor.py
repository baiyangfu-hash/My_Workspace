# -*- coding: utf-8 -*-
"""
ST代码编辑器组件 (预留接口)

基于QScintilla构建的结构化文本(ST)代码编辑器，
提供IEC 61131-3 ST语言的语法高亮、代码补全、错误检测等功能。

注意: 此模块为预留接口，完整实现依赖QScintilla安装。
当QScintilla不可用时，会回退到基础文本编辑模式。
"""
import logging
import importlib
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPlainTextEdit,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

logger = logging.getLogger(__name__)


class STEditor(QWidget):
    """
    ST代码编辑器 (预留)

    规划功能:
    - IEC 61131-3 ST语言语法高亮
    - 关键字自动补全 (VAR/FUNCTION_BLOCK/IF/CASE等)
    - 括号匹配和高亮
    - 行号显示
    - 代码折叠 (FUNCTION_BLOCK级别)
    - 编译错误位置标记
    - 代码片段(snippet)快速插入
    """

    _missing_notice_shown = False

    def __init__(self, parent=None, show_dependency_notice: bool = True):
        super().__init__(parent)
        self._has_qscintilla = False
        self._editor_widget = None
        self._show_dependency_notice = show_dependency_notice
        self._init_editor()

    def _init_editor(self):
        """初始化编辑器组件 (尝试使用QScintilla，否则回退)"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        qsci_classes, import_error = self._import_qscintilla_classes()
        if qsci_classes is not None:
            qsci_scintilla_cls, qsci_lexer_st_cls = qsci_classes
            self._setup_qscintilla_editor(
                layout, qsci_scintilla_cls, qsci_lexer_st_cls
            )
            self._has_qscintilla = True
            logger.debug("ST编辑器: 使用QScintilla引擎")
            return

        if import_error:
            logger.info(
                f"ST编辑器: 回退到基础文本编辑模式 (QScintilla不可用: {import_error})"
            )

        self._fallback_editor(layout)
        self._has_qscintilla = False
        if self._show_dependency_notice:
            self._schedule_missing_qscintilla_notice()
    @staticmethod
    def _import_qscintilla_classes():
        try:
            qsci_module = importlib.import_module("PyQt5.Qsci")
            qsci_scintilla_cls = getattr(qsci_module, "QsciScintilla")
            qsci_lexer_st_cls = getattr(qsci_module, "QsciLexerST")
            return (qsci_scintilla_cls, qsci_lexer_st_cls), None
        except Exception as e:
            try:
                qsci_module = importlib.import_module("Qsci")
                qsci_scintilla_cls = getattr(qsci_module, "QsciScintilla")
                qsci_lexer_st_cls = getattr(qsci_module, "QsciLexerST")
                return (qsci_scintilla_cls, qsci_lexer_st_cls), None
            except Exception:
                return None, str(e)

    def _setup_qscintilla_editor(
        self,
        parent_layout: QVBoxLayout,
        qsci_scintilla_cls,
        qsci_lexer_st_cls,
    ):
        """配置QScintilla ST编辑器"""
        editor = qsci_scintilla_cls(self)

        # 基本配置
        editor.setFont(QFont("Consolas", 11))
        editor.setMarginLineNumbers(1, True)
        editor.setMarginWidth(1, 50)
        editor.setIndentationWidth(4)
        editor.setTabWidth(4)
        editor.setIndentationsUseTabs(False)
        editor.setAutoIndent(True)
        editor.setBraceMatching(qsci_scintilla_cls.SloppyBraceMatch)
        editor.setCaretLineVisible(True)
        editor.setCaretLineBackgroundColor(Qt.yellow.lighter(160))

        # 设置ST词法分析器
        lexer = qsci_lexer_st_cls(editor)
        lexer.setFont(QFont("Consolas", 11))
        editor.setLexer(lexer)

        # 默认示例代码
        default_code = self._get_default_st_code()
        editor.setText(default_code)

        parent_layout.addWidget(editor)
        self._editor_widget = editor

    def _fallback_editor(self, parent_layout: QVBoxLayout):
        """回退到基础QPlainTextEdit"""
        info_label = QLabel(
            "\u26A1 ST代码编辑器\n\n"
            "(预留功能 - 完整版需安装 QScintilla)\n\n"
            "当前使用基础文本编辑模式。\n"
            "安装命令: python -m pip install QScintilla\n\n"
            "完整版将支持:\n"
            "- IEC 61131-3 ST语法高亮\n"
            "- 关键字自动补全\n"
            "- 代码折叠与括号匹配\n"
            "- 编译错误定位\n"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet(
            "color: #757575; font-size: 10pt; padding: 20px;"
        )
        parent_layout.addWidget(info_label)

        editor = QPlainTextEdit()
        editor.setFont(QFont("Consolas", 11))
        editor.setPlaceholderText("在此编写ST代码...")
        editor.setPlainText(self._get_default_st_code())
        parent_layout.addWidget(editor)
        self._editor_widget = editor

    def _schedule_missing_qscintilla_notice(self):
        if STEditor._missing_notice_shown:
            return
        STEditor._missing_notice_shown = True

        def _show_notice():
            QMessageBox.information(
                self,
                "ST编辑器功能受限",
                "未检测到 QScintilla，ST编辑器已回退到基础文本模式。\n\n"
                "如需语法高亮/补全等功能，请安装：\n"
                "python -m pip install QScintilla\n\n"
                "安装后重启程序即可生效。",
                QMessageBox.Ok,
            )

        QTimer.singleShot(0, _show_notice)

    @staticmethod
    def _get_default_st_code() -> str:
        """获取默认的ST示例代码模板"""
        return (
            "(* ============================================ *)\n"
            "(* Function Block: FB_MotorControl             *)\n"
            "(* Description: 电机控制功能块                  *)\n"
            "(* Author: SW-2026-005                         *)\n"
            "(* ============================================ *)\n\n"
            "FUNCTION_BLOCK FB_MotorControl\n"
            "VAR_INPUT\n"
            "    bEnable     : BOOL;      (* 使能信号 *)\n"
            "    bStart      : BOOL;      (* 启动信号 *)\n"
            "    bStop       : BOOL;      (* 停止信号 *)\n"
            "    rSpeedRef   : REAL;      (* 速度设定值 [rpm] *)\n"
            "END_VAR\n\n"
            "VAR_OUTPUT\n"
            "    bRunning    : BOOL;      (* 运行状态 *)\n"
            "    bFault      : BOOL;      (* 故障标志 *)\n"
            "    rActualSpeed : REAL;     (* 实际速度 [rpm] *)\n"
            "END_VAR\n\n"
            "VAR\n"
            "    tonDelay    : TON;       (* 启动延时定时器 *)\n"
            "    fbState     : INT := 0;  (* 状态机变量 *)\n"
            "END_VAR\n\n"
            "(* 主逻辑 - 状态机实现 *)\n"
            "CASE fbState OF\n"
            "    0:  (* 待机状态 *)\n"
            "        bRunning := FALSE;\n"
            "        IF bEnable AND bStart THEN\n"
            "            fbState := 1;\n"
            "        END_IF;\n\n"
            "    1:  (* 启动中 *)\n"
            "        tonDelay(IN:=TRUE, PT:=T#2S);\n"
            "        IF tonDelay.Q THEN\n"
            "            fbState := 2;\n"
            "            tonDelay(IN:=FALSE);\n"
            "        END_IF;\n\n"
            "    2:  (* 运行中 *)\n"
            "        bRunning := TRUE;\n"
            "        rActualSpeed := rSpeedRef;\n"
            "        IF bStop OR NOT bEnable THEN\n"
            "            fbState := 3;\n"
            "        END_IF;\n\n"
            "    3:  (* 停止中 *)\n"
            "        bRunning := FALSE;\n"
            "        rActualSpeed := 0.0;\n"
            "        fbState := 0;\n\n"
            "ELSE\n"
            "    bFault := TRUE;\n"
            "END_CASE;\n"
            "\n"
            "END_FUNCTION_BLOCK\n"
        )

    # ========== 公共API ==========

    def get_text(self) -> str:
        """获取编辑器中的代码文本"""
        if self._editor_widget is None:
            return ""
        if self._has_qscintilla:
            return self._editor_widget.text()
        return self._editor_widget.toPlainText()

    def set_text(self, code: str):
        """设置编辑器中的代码文本"""
        if self._editor_widget is None:
            return
        if self._has_qscintilla:
            self._editor_widget.setText(code)
        else:
            self._editor_widget.setPlainText(code)

    @property
    def has_full_features(self) -> bool:
        """检查是否具备完整的QScintilla功能"""
        return self._has_qscintilla
