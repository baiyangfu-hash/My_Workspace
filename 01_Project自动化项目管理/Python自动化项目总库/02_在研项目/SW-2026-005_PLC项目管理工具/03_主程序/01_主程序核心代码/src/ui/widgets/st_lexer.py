# -*- coding: utf-8 -*-
"""
IEC 61131-3 ST/SCL 自定义词法分析器

基于 Dynamic Siemens Language Support (VS Code) 的 TextMate 语法规则转换而来:
  - 来源: BjAlvestad/vscode-simatic-scl (基于 Gunders89/vscode-scl)
  - 原始文件: syntaxes/scl.tmLanguage.json
  - 转换目标: PyQt5.Qsci.QsciLexerCustom

支持的语言特性:
- 块注释 (* *) 和行注释 //
- 控制流关键字 (IF/FOR/WHILE/CASE 等)
- 声明关键字 (VAR/FUNCTION_BLOCK/DATA_BLOCK 等)
- 数据类型 (BOOL/INT/REAL/TIME/STRING 等)
- 内置函数 (ABS/SQRT/TON/TOF/MUX 等)
- 运算符 (AND/OR/XOR/NOT/MOD/DIV/:= 等)
- 布尔常量 (TRUE/FALSE/NULL)
- 数字字面量 (十进制/十六进制/二进制/时间字面量)
- 字符串字面量 ('单引号字符串')
- S7 系统属性 (S7_*, ExternalAccessible 等)
"""
import re
from PyQt5.QtGui import QColor, QFont
from PyQt5.Qsci import QsciLexerCustom, QsciScintillaBase

logger = __import__("logging").getLogger(__name__)


class QsciLexerST(QsciLexerCustom):
    """
    IEC 61131-3 Structured Text / Siemens SCL 词法分析器
    
    样式索引定义:
        Default     = 0   默认文本
        CommentBlock = 1  (* 块注释 *)
        CommentLine  = 2  // 行注释
        KeywordCtrl  = 3  控制流关键字 (IF/FOR/WHILE/CASE...)
        KeywordDecl  = 4  声明关键字 (VAR/FUNCTION_BLOCK/DATA_BLOCK...)
        DataType     = 5  数据类型 (BOOL/INT/REAL/TIME/STRING...)
        BuiltinFunc  = 6  内置函数 (ABS/SQRT/TON/TOF/SEL/MUX...)
        Operator     = 7  运算符 (AND/OR/XOR/NOT/MOD/DIV/:=...)
        Constant     = 8  布尔常量 (TRUE/FALSE/NULL)
        Number       = 9  数字字面量
        String       = 10 字符串字面量 ('...')
        Attribute    = 11 S7系统属性 (S7_*/ExternalAccessible...)
        Punctuation  = 12 分号等标点
    """

    STYLE_DEFAULT = 0
    STYLE_COMMENT_BLOCK = 1
    STYLE_COMMENT_LINE = 2
    STYLE_KEYWORD_CTRL = 3
    STYLE_KEYWORD_DECL = 4
    STYLE_DATA_TYPE = 5
    STYLE_BUILTIN_FUNC = 6
    STYLE_OPERATOR = 7
    STYLE_CONSTANT = 8
    STYLE_NUMBER = 9
    STYLE_STRING = 10
    STYLE_ATTRIBUTE = 11
    STYLE_PUNCTUATION = 12

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_styles()
        self._compile_patterns()

    def _init_styles(self):
        """初始化所有样式（颜色+字体）"""
        default_font = QFont("Consolas", 10)

        self.setColor(QColor("#D4D4D4"), self.STYLE_DEFAULT)
        self.setFont(default_font, self.STYLE_DEFAULT)
        self.setPaper(QColor("#1E1E1E"), self.STYLE_DEFAULT)

        self.setColor(QColor("#6A9955"), self.STYLE_COMMENT_BLOCK)
        self.setFont(default_font, self.STYLE_COMMENT_BLOCK)

        self.setColor(QColor("#6A9955"), self.STYLE_COMMENT_LINE)
        self.setFont(default_font, self.STYLE_COMMENT_LINE)

        self.setColor(QColor("#C586C0"), self.STYLE_KEYWORD_CTRL)
        self.setFont(QFont("Consolas", 10, QFont.Bold), self.STYLE_KEYWORD_CTRL)

        self.setColor(QColor("#569CD6"), self.STYLE_KEYWORD_DECL)
        self.setFont(QFont("Consolas", 10, QFont.Bold), self.STYLE_KEYWORD_DECL)

        self.setColor(QColor("#4EC9B0"), self.STYLE_DATA_TYPE)
        self.setFont(default_font, self.STYLE_DATA_TYPE)

        self.setColor(QColor("#DCDCAA"), self.STYLE_BUILTIN_FUNC)
        self.setFont(default_font, self.STYLE_BUILTIN_FUNC)

        self.setColor(QColor("#D4D4D4"), self.STYLE_OPERATOR)
        self.setFont(QFont("Consolas", 10, QFont.Bold), self.STYLE_OPERATOR)

        self.setColor(QColor("#CE9178"), self.STYLE_CONSTANT)
        self.setFont(QFont("Consolas", 10, QFont.Bold), self.STYLE_CONSTANT)

        self.setColor(QColor("#B5CEA8"), self.STYLE_NUMBER)
        self.setFont(default_font, self.STYLE_NUMBER)

        self.setColor(QColor("#CE9178"), self.STYLE_STRING)
        self.setFont(default_font, self.STYLE_STRING)

        self.setColor(QColor("#9CDCFE"), self.STYLE_ATTRIBUTE)
        self.setFont(default_font, self.STYLE_ATTRIBUTE)

        self.setColor(QColor("#D4D4D4"), self.STYLE_PUNCTUATION)
        self.setFont(default_font, self.STYLE_PUNCTUATION)

    def _compile_patterns(self):
        """预编译所有正则表达式模式"""

        ctrl_keywords = (
            r"\b(?:break|case|end_case|continue|do|to|else|elsif|AT|"
            r"for|end_for|goto|if|end_if|return|of|while|end_while|"
            r"then|repeat|until|end_repeat|exit|label|end_label|"
            r"REGION|END_REGION)\b"
        )
        self._re_ctrl_kw = re.compile(ctrl_keywords, re.IGNORECASE)

        decl_keywords = (
            r"\b(?:var\s+constant|var|var_input|var_output|var_in_out|"
            r"var_temp|end_var|begin|const|end_const|type|end_type)\b"
        )
        self._re_decl_kw = re.compile(decl_keywords, re.IGNORECASE)

        storage_types = (
            r"\b(?:FUNCTION|END_FUNCTION|FUNCTION_BLOCK|END_FUNCTION_BLOCK|"
            r"DATA_BLOCK|END_DATA_BLOCK|STRUCT|END_STRUCT|METHOD|END_METHOD|"
            r"PROGRAM|END_PROGRAM|INTERFACE|END_INTERFACE|ACTION|END_ACTION|"
            r"STEP|END_STEP|TRANSITION|END_TRANSITION)\b"
        )
        self._re_storage = re.compile(storage_types, re.IGNORECASE)

        data_types = (
            r"\b(?:ANY|ARRAY|BOOL|BYTE|CHAR|COUNTER|DATE|DATE_AND_TIME|"
            r"SINT|INT|DINT|LINT|DTL|DT|DWORD|POINTER|REAL|LREAL|"
            r"S5TIME|STRING|TIME|TIMER|TIME_OF_DAY|TOD|USINT|UINT|"
            r"UDINT|ULINT|VOID|WORD|WSTRING|TON_TIME|TOF_TIME|TP_TIME|"
            r"IEC_TIMER|ENO|TCONNECTION_ID|TADDR|VERSION)\b"
        )
        self._re_data_type = re.compile(data_types, re.IGNORECASE)

        builtin_funcs = (
            r"\b(?:ABS|SQR|SQRT|EXP|EXPD|LN|LOG|ACOS|ASIN|ATAN|"
            r"COS|SIN|TAN|ROL|ROR|SHL|SHR|SEL|MAX|MIN|LIMIT|MUX|"
            r"ROUND|TRUNC|LEN|LEFT|RIGHT|MID|INSERT|DELETE|REPLACE|"
            r"CONCAT|FIND|EQ|GE|GT|LE|LT|NE|MOVE|BLKMOV|WORD_TO_INT|"
            r"INT_TO_WORD|CHAR_TO_INT|INT_TO_CHAR|TRUNC|ROUND|"
            r"TON|TOF|TP|CTU|CTUD|CTC|R_TRIG|F_TRIG|SR|RS|SEL|"
            r"MAX|MIN|MUX|LIMIT|MOVE|BLKMOV|SCATTER|GATHER|"
            r"ATTACH|DETACH|ENABLE|DISABLE|ABORT|GET|PUT|SEND_RECV|"
            r"T_ADD|T_SUB|T_DIFF|DATE_AND_TIME_TO_DT|DT_TO_DATE_AND_TIME|"
            r"BCD_TO_INT|INT_TO_BCD)\b"
        )
        self._re_builtin_func = re.compile(builtin_funcs, re.IGNORECASE)

        operators = (
            r"(?<!\w)(?:AND|OR|XOR|NOT|MOD|DIV)(?!\w)|"
            r":=|<>|>=|<=|\*\*|=="
        )
        self._re_operator = re.compile(operators, re.IGNORECASE)

        s7_attrs = (
            r"\b(?:S7_\w+|ExternalAccessible|ExternalVisible|"
            r"ExternalWritable|LibVersion|InstructionName|"
            r"'SetPin'|'GetPin')\b"
        )
        self._re_attribute = re.compile(s7_attrs, re.IGNORECASE)

        self._re_constant = re.compile(r"\b(?:TRUE|FALSE|NULL)\b", re.IGNORECASE)

        time_literal = (
            r"\b[Tt]#(?:(?:\d+d)?(?:\d+h)?(?:\d+m)?(?:\d+s)?(?:\d+ms)?)?\b|"
            r"\b[Dd]#\d{4}-\d{2}-\d{2}(?:-\d{2}:\d{2}:\d{2})?\b|"
            r"\b[Tt][Oo][Dd]#\d{2}:\d{2}:\d{2}\b"
        )
        hex_literal = r"\b16#[0-9A-Fa-f_]+\b"
        bin_literal = r"\b2#[01_]+\b"
        num_literal = r"(?:\b0[xX][0-9a-fA-F]+\b|\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b)"
        self._re_number = re.compile(
            f"(?:{time_literal}|{hex_literal}|{bin_literal}|{num_literal})"
        )

        self._re_string_start = re.compile(r"'")
        self._re_comment_block_start = re.compile(r"\(\*")
        self._re_comment_line_start = re.compile(r"//")

    def language(self):
        return "IEC 61131-3 ST / SCL"

    def description(self, style):
        descriptions = {
            self.STYLE_DEFAULT: "Default",
            self.STYLE_COMMENT_BLOCK: "Block Comment",
            self.STYLE_COMMENT_LINE: "Line Comment",
            self.STYLE_KEYWORD_CTRL: "Control Keyword",
            self.STYLE_KEYWORD_DECL: "Declaration Keyword",
            self.STYLE_DATA_TYPE: "Data Type",
            self.STYLE_BUILTIN_FUNC: "Built-in Function",
            self.STYLE_OPERATOR: "Operator",
            self.STYLE_CONSTANT: "Constant",
            self.STYLE_NUMBER: "Number Literal",
            self.STYLE_STRING: "String Literal",
            self.STYLE_ATTRIBUTE: "System Attribute",
            self.STYLE_PUNCTUATION: "Punctuation",
        }
        return descriptions.get(style, "")

    STATE_DEFAULT = 0
    STATE_IN_BLOCK_COMMENT = 1
    STATE_IN_STRING = 2

    def _get_previous_line_style(self, position: int) -> int:
        """获取指定位置前一行的样式（兼容QScintilla各版本）

        QScintilla 2.14+ 提供 previousLineStyle()，
        旧版本需手动从 Scintilla 内部获取。
        """
        if hasattr(super(), 'previousLineStyle'):
            try:
                return super().previousLineStyle(position)
            except Exception:
                pass

        editor = self.editor()
        if not editor:
            return self.STYLE_DEFAULT

        try:
            line = editor.lineIndexFromPosition(position)[0]
            if line > 0:
                prev_line_end = editor.positionFromLineIndex(line, 0) - 1
                if prev_line_end >= 0:
                    byte_pos = editor.SendScintilla(
                        editor.SCI_POSITIONBEFORE, prev_line_end + 1
                    )
                    style = editor.SendScintilla(
                        editor.SCI_GETSTYLEAT, byte_pos
                    )
                    return style
        except Exception:
            pass

        return self.STYLE_DEFAULT

    def styleText(self, start, end):
        """主着色入口 — 由 QScintilla 在文本变化时调用

        使用状态跟踪机制处理跨段的多行结构（块注释/字符串）。
        通过 previousLineStyle 恢复上一段末尾的解析状态，
        确保跨行块注释和字符串正确高亮。
        """
        editor = self.editor()
        if not editor:
            return

        text = editor.text()
        if end > len(text):
            end = len(text)

        segment = text[start:end]
        if not segment:
            return

        prev_style = self._get_previous_line_style(start)
        if prev_style == self.STYLE_COMMENT_BLOCK:
            initial_state = self.STATE_IN_BLOCK_COMMENT
        elif prev_style == self.STYLE_STRING:
            initial_state = self.STATE_IN_STRING
        else:
            initial_state = self.STATE_DEFAULT

        self.startStyling(start)
        pos = 0
        length = len(segment)
        state = initial_state

        if state == self.STATE_IN_BLOCK_COMMENT:
            pos = self._resume_block_comment(segment, pos, length)
            state = self.STATE_DEFAULT
        elif state == self.STATE_IN_STRING:
            pos = self._resume_string(segment, pos, length)
            state = self.STATE_DEFAULT

        while pos < length:
            ch = segment[pos]

            if ch == '(' and pos + 1 < length and segment[pos + 1] == '*':
                pos = self._style_comment_block(segment, pos, length)
            elif ch == '/' and pos + 1 < length and segment[pos + 1] == '/':
                pos = self._style_comment_line(segment, pos, length)
            elif ch == "'":
                pos = self._style_string(segment, pos, length)
            elif ch.isalpha() or ch == '_':
                pos = self._style_word(segment, pos, length)
            elif ch.isdigit() or (ch == '#' and pos > 0 and segment[pos - 1].isalpha()):
                pos = self._style_number(segment, pos, length)
            else:
                styled = False
                for op_match in self._re_operator.finditer(segment[pos:]):
                    if op_match.start() == 0:
                        op_len = len(op_match.group())
                        self.setStyling(op_len, self.STYLE_OPERATOR)
                        pos += op_len
                        styled = True
                        break
                if not styled:
                    if ch == ';':
                        self.setStyling(1, self.STYLE_PUNCTUATION)
                    else:
                        self.setStyling(1, self.STYLE_DEFAULT)
                    pos += 1

    def _resume_block_comment(self, text, pos, length):
        """从段中间恢复块注释样式（跨段续接）"""
        start_pos = pos
        depth = 1
        while pos < length and depth > 0:
            if text[pos] == '(' and pos + 1 < length and text[pos + 1] == '*':
                depth += 1
                pos += 2
            elif text[pos] == '*' and pos + 1 < length and text[pos + 1] == ')':
                depth -= 1
                pos += 2
            else:
                pos += 1
        self.setStyling(pos - start_pos, self.STYLE_COMMENT_BLOCK)
        return pos

    def _resume_string(self, text, pos, length):
        """从段中间恢复字符串样式（跨段续接）"""
        start_pos = pos
        while pos < length:
            ch = text[pos]
            if ch == "'":
                pos += 1
                break
            elif ch == '\\' or ch == '$':
                pos += 2 if pos + 1 < length else 1
            else:
                pos += 1
        self.setStyling(pos - start_pos, self.STYLE_STRING)
        return pos

    def _style_comment_block(self, text, pos, length):
        """样式化块注释 (* ... *) 支持嵌套"""
        depth = 1
        start_pos = pos
        pos += 2
        while pos < length and depth > 0:
            if text[pos] == '(' and pos + 1 < length and text[pos + 1] == '*':
                depth += 1
                pos += 2
            elif text[pos] == '*' and pos + 1 < length and text[pos + 1] == ')':
                depth -= 1
                pos += 2
            else:
                pos += 1
        self.setStyling(pos - start_pos, self.STYLE_COMMENT_BLOCK)
        return pos

    def _style_comment_line(self, text, pos, length):
        """样式化行注释 // ... """
        start_pos = pos
        pos += 2
        while pos < length and text[pos] != '\n' and text[pos] != '\r':
            pos += 1
        self.setStyling(pos - start_pos, self.STYLE_COMMENT_LINE)
        return pos

    def _style_string(self, text, pos, length):
        """样式化字符串 '...' """
        start_pos = pos
        pos += 1
        while pos < length:
            ch = text[pos]
            if ch == "'":
                pos += 1
                break
            elif ch == '\\' or ch == '$':
                pos += 2 if pos + 1 < length else 1
            else:
                pos += 1
        self.setStyling(pos - start_pos, self.STYLE_STRING)
        return pos

    def _style_word(self, text, pos, length):
        """样式化标识符/关键字 — 按优先级匹配"""
        start_pos = pos
        while pos < length and (text[pos].isalnum() or text[pos] == '_'):
            pos += 1
        word = text[start_pos:pos]

        if self._re_attribute.match(word):
            style = self.STYLE_ATTRIBUTE
        elif self._re_constant.match(word):
            style = self.STYLE_CONSTANT
        elif self._re_ctrl_kw.match(word):
            style = self.STYLE_KEYWORD_CTRL
        elif self._re_decl_kw.match(word) or self._re_storage.match(word):
            style = self.STYLE_KEYWORD_DECL
        elif self._re_data_type.match(word):
            style = self.STYLE_DATA_TYPE
        elif self._re_builtin_func.match(word):
            style = self.STYLE_BUILTIN_FUNC
        elif self._re_operator.match(word):
            style = self.STYLE_OPERATOR
        else:
            style = self.STYLE_DEFAULT

        self.setStyling(pos - start_pos, style)
        return pos

    def _style_number(self, text, pos, length):
        """样式化数字字面量"""
        start_pos = pos
        while pos < length:
            remaining = text[start_pos:pos + 1]
            if self._re_number.fullmatch(remaining) is not None:
                pos += 1
            else:
                break
        if pos == start_pos:
            pos += 1
        self.setStyling(pos - start_pos, self.STYLE_NUMBER)
        return pos
