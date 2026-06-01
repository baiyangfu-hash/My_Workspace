# -*- coding: utf-8 -*-
"""
ST代码编辑器组件

基于QScintilla构建的结构化文本(ST)代码编辑器，
提供IEC 61131-3 ST语言的语法高亮、代码补全、错误检测等功能。

语法高亮规则来源: Dynamic Siemens Language Support (VS Code)
  - 原始TextMate语法: BjAlvestad/vscode-simatic-scl
  - 转换为: src/ui/widgets/st_lexer.py (QsciLexerCustom)

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
from PyQt5.QtGui import QFont, QColor

logger = logging.getLogger(__name__)


class STEditor(QWidget):
    """
    ST代码编辑器

    功能:
    - IEC 61131-3 ST语言语法高亮 (13种样式)
    - 行号显示
    - 括号匹配和高亮
    - 代码折叠
    - 当前行高亮
    - 自动缩进

    语法着色覆盖:
    - 控制流关键字: IF/FOR/WHILE/CASE/REPEAT (紫色粗体)
    - 声明关键字: VAR/FUNCTION_BLOCK/DATA_BLOCK (蓝色粗体)
    - 数据类型: BOOL/INT/REAL/TIME/STRING (青色)
    - 内置函数: ABS/SQRT/TON/TOF/MUX (浅黄)
    - 运算符: AND/OR/XOR/NOT/:= (白色粗体)
    - 布尔常量: TRUE/FALSE (橙色粗体)
    - 数字字面量: 十进制/十六进制/二进制/时间 (浅绿)
    - 字符串: '...' (橙色)
    - 注释: (* *) 和 // (绿色)
    - S7属性: S7_* / ExternalAccessible (浅蓝)
    """

    _missing_notice_shown = False

    def __init__(self, parent=None, show_dependency_notice: bool = True):
        super().__init__(parent)
        self._has_qscintilla = False
        self._has_st_lexer = False
        self._editor_widget = None
        self._show_dependency_notice = show_dependency_notice
        self._init_editor()

    def _init_editor(self):
        """初始化编辑器组件 (尝试使用QScintilla+自定义Lexer，否则回退)"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        qsci_cls = self._try_import_qscintilla()
        if qsci_cls is not None:
            self._setup_qscintilla_editor(layout, qsci_cls)
            return

        self._fallback_editor(layout)
        self._has_qscintilla = False
        self._has_st_lexer = False
        if self._show_dependency_notice:
            self._schedule_missing_qscintilla_notice()

    @staticmethod
    def _try_import_qscintilla():
        try:
            qsci_module = importlib.import_module("PyQt5.Qsci")
            return getattr(qsci_module, "QsciScintilla")
        except Exception:
            try:
                qsci_module = importlib.import_module("Qsci")
                return getattr(qsci_module, "QsciScintilla")
            except Exception:
                return None

    def _setup_qscintilla_editor(self, parent_layout: QVBoxLayout, qsci_scintilla_cls):
        """配置QScintilla ST编辑器 + 自定义ST Lexer"""
        from .st_lexer import QsciLexerST

        editor = qsci_scintilla_cls(self)

        editor.setFont(QFont("Consolas", 11))
        editor.setMarginLineNumbers(1, True)
        editor.setMarginWidth(1, 50)
        editor.setIndentationWidth(4)
        editor.setTabWidth(4)
        editor.setIndentationsUseTabs(False)
        editor.setAutoIndent(True)
        editor.setBraceMatching(qsci_scintilla_cls.SloppyBraceMatch)
        editor.setCaretLineVisible(True)
        editor.setCaretLineBackgroundColor(QColor(40, 42, 54))
        editor.setFolding(qsci_scintilla_cls.BoxedTreeFoldStyle)
        editor.setAutoCompletionSource(
            qsci_scintilla_cls.AcsAll | qsci_scintilla_cls.AcsAPIs
        )
        editor.setIndentationGuides(True)

        lexer = QsciLexerST(editor)
        editor.setLexer(lexer)

        default_code = self._get_default_st_code()
        editor.setText(default_code)

        parent_layout.addWidget(editor)
        self._editor_widget = editor
        self._has_qscintilla = True
        self._has_st_lexer = True
        logger.info("ST编辑器: QScintilla引擎 + IEC 61131-3 ST语法高亮已启用")

    def _fallback_editor(self, parent_layout: QVBoxLayout):
        """回退到基础QPlainTextEdit"""
        info_label = QLabel(
            "\u26A1 ST代码编辑器\n\n"
            "(完整版需安装 QScintilla)\n\n"
            "当前使用基础文本编辑模式。\n"
            "安装命令: python -m pip install QScintilla\n\n"
            "完整版将支持:\n"
            "- IEC 61131-3 ST语法高亮 (13种样式)\n"
            "- 行号、括号匹配、代码折叠\n"
            "- 关键字自动补全\n"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setProperty("treeStatus", True)
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
            "// ============================================================================\n"
            "// Function Block: FB_ValveControl\n"
            "// Description: 阀门控制功能块\n"
            "// Author: SW-2026-005\n"
            "// ============================================================================\n\n"
            "FUNCTION_BLOCK FB_ValveControl\n"
            "VAR_INPUT\n"
            "    // 第一部分：模式控制\n"
            "    AutoManual   : BOOL := FALSE;  // [输入] 自动/手动模式切换\n\n"
            "    // 第二部分：操作命令\n"
            "    OpenCmd      : BOOL := FALSE;  // [输入] 开阀命令\n"
            "    CloseCmd     : BOOL := FALSE;  // [输入] 关阀命令\n\n"
            "    // 第三部分：传感器信号\n"
            "    OverCurrent  : BOOL := FALSE;  // [输入] 过流检测信号\n"
            "    OpenLimit    : BOOL := FALSE;  // [输入] 开到位限位开关\n"
            "    CloseLimit   : BOOL := FALSE;  // [输入] 关到位限位开关\n\n"
            "    // 第四部分：故障管理\n"
            "    FaultReset   : BOOL := FALSE;  // [输入] 故障复位\n"
            "END_VAR\n\n"
            "VAR_OUTPUT\n"
            "    bOpen        : BOOL;          // [输出] 开阀执行\n"
            "    bClose       : BOOL;          // [输出] 关阀执行\n"
            "    bFault       : BOOL;          // [输出] 故障标志\n"
            "    bOpened      : BOOL;          // [输出] 已开到位\n"
            "    bClosed     : BOOL;          // [输出] 已关到位\n"
            "END_VAR\n\n"
            "VAR\n"
            "    fbState      : INT := 0;      // 状态机变量\n"
            "    tonOpenDelay : TON;           // 开阀延时定时器\n"
            "    tonCloseDelay: TON;           // 关阀延时定时器\n"
            "END_VAR\n\n"
            "(* 主逻辑 - 状态机实现 *)\n"
            "CASE fbState OF\n"
            "    0:  (* 待机状态 *)\n"
            "        bOpen := FALSE;\n"
            "        bClose := FALSE;\n"
            "        IF AutoManual AND OpenCmd THEN\n"
            "            fbState := 10;\n"
            "        ELSIF NOT AutoManual AND OpenCmd THEN\n"
            "            fbState := 20;\n"
        )

    def open_file(self, file_path: str, line_number: int = None):
        """打开指定文件并定位到行号"""
        if not self._editor_widget or not self._has_qscintilla:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self._editor_widget.setText(content)
            if line_number and line_number > 0:
                self._editor_widget.ensureLineVisible(line_number - 1)
                line_start_pos = self._editor_widget.positionFromLine(line_number - 1)
                self._editor_widget.setSelection(line_start_pos, 0)
        except Exception as e:
            logger.warning(f"打开文件失败 [{file_path}]: {e}")

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
        """检查是否具备完整的QScintilla+ST语法高亮功能"""
        return self._has_qscintilla and self._has_st_lexer
