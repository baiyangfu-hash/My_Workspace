# -*- coding: utf-8 -*-
"""
ST (Structured Text) 代码解析器

基于IEC 61131-3标准解析ST源代码，
提取变量声明、POU定义、函数调用等关键信息。
支持多品牌PLC方言的兼容处理。
"""
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class POUType(Enum):
    """POU类型枚举"""
    PROGRAM = "PROGRAM"
    FUNCTION = "FUNCTION"
    FUNCTION_BLOCK = "FUNCTION_BLOCK"
    METHOD = "METHOD"
    ACTION = "ACTION"


class VarCategory(Enum):
    """变量类别枚举"""
    VAR = "VAR"                    # 局部变量
    VAR_INPUT = "VAR_INPUT"        # 输入变量
    VAR_OUTPUT = "VAR_OUTPUT"      # 输出变量
    VAR_IN_OUT = "VAR_IN_OUT"      # 输入输出变量
    VAR_GLOBAL = "VAR_GLOBAL"      # 全局变量
    VAR_TEMP = "VAR_TEMP"          # 临时变量 (CODESYS)
    VAR_STATIC = "VAR_STATIC"      # 静态变量
    VAR_CONSTANT = "VAR_CONSTANT"  # 常量
    VAR_EXTERNAL = "VAR_EXTERNAL"  # 外部变量
    VAR_ACCESS = "VAR_ACCESS"      # 访问变量


@dataclass
class VariableInfo:
    """变量信息数据类"""
    name: str
    data_type: str
    category: VarCategory
    initial_value: Optional[str] = None
    comment: str = ""
    line_number: int = 0
    pou_name: str = ""


@dataclass
class POUInfo:
    """POU (Program Organization Unit) 信息数据类"""
    name: str
    pou_type: POUType
    return_type: Optional[str] = None       # 仅FUNCTION有返回值
    variables: List[VariableInfo] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0
    source_file: str = ""


class STParser:
    """
    ST源码解析器

    功能:
    - 提取所有POU定义 (PROGRAM/FUNCTION/FUNCTION_BLOCK)
    - 解析各类型的变量声明段
    - 支持结构体(STRUCT)和数组(ARRAY)类型解析
    - 基础的语法验证
    """

    # 正则表达式模式
    RE_POU_DECLARATION = re.compile(
        r"(PROGRAM|FUNCTION_BLOCK|FUNCTION)\s+"
        r"(?P<name>\w+)"
        r"(?:\s*:\s*(?P<return_type>\w+(?:\s*\([^)]*\))?))?"
        r"\s*",
        re.IGNORECASE,
    )
    RE_VAR_BLOCK_START = re.compile(
        r"VAR(?:_(?:INPUT|OUTPUT|IN_OUT|GLOBAL|TEMP|STATIC|CONSTANT|EXTERNAL|ACCESS))?"
        r"(?:\s+(?:RETAIN|NON_RETAIN|PERSISTENT))*",
        re.IGNORECASE,
    )
    RE_VAR_DECLARATION = re.compile(
        r"(?P<names>[\w\s,]+?)\s*:\s*(?P<type>\w+(?:\s*\([^)]*\))?(?:\s*ARRAY\s+\[.*?\])?(?:\s*OF\s+\w+)?)"
        r"(?:\s*:=\s*(?P<init>[^;]*?))?"
        r"\s*(?:\(\*\s*(?P<comment>(?:[^*]|\*(?!))*)\*\))?"
        r"\s*;",
        re.IGNORECASE,
    )

    def __init__(self):
        self._pous: List[POUInfo] = []
        self._global_vars: List[VariableInfo] = []
        self._source_lines: List[str] = []
        self._source_text: str = ""

    def parse(self, source_code: str) -> Tuple[List[POUInfo], List[VariableInfo]]:
        """
        解析ST源代码

        Args:
            source_code: ST源码文本

        Returns:
            Tuple[List[POUInfo], List[VariableInfo]]: (POU列表, 全局变量列表)
        """
        self._source_text = source_code
        self._source_lines = source_code.splitlines()
        self._pous = []
        self._global_vars = []

        try:
            self._extract_pous()
            logger.info(f"ST解析完成: {len(self._pous)} 个POU, "
                        f"{len(self._global_vars)} 个全局变量")
        except Exception as e:
            logger.exception(f"ST解析过程出错: {e}")

        return self._pous, self._global_vars

    def _extract_pous(self):
        """提取所有POU定义"""
        for match in self.RE_POU_DECLARATION.finditer(self._source_text):
            pou_type_str = match.group(1).upper()
            pou_type = POUType(pou_type_str)
            pou_name = match.group("name").strip()
            return_type = match.group("return_type")

            start_line = (
                self._source_text[:match.start()].count("\n") + 1
            )

            pou_info = POUInfo(
                name=pou_name,
                pou_type=pou_type,
                return_type=return_type,
                start_line=start_line,
            )

            # 提取该POU内的变量声明
            pou_end = self._find_pou_end(match.start())
            pou_block = self._source_text[match.start():pou_end]
            pou_info.end_line = (
                self._source_text[:pou_end].count("\n") + 1
            )
            pou_info.variables = self._extract_variables_from_block(
                pou_block, pou_name
            )

            self._pous.append(pou_info)

    def _find_pou_end(self, start_pos: int) -> int:
        """查找POU结束位置 (匹配END_PROGRAM/END_FUNCTION_BLOCK等)"""
        depth = 1
        pos = start_pos
        text = self._source_text

        while pos < len(text) and depth > 0:
            # 检查是否遇到END_*
            end_match = re.search(
                r"END_(?:PROGRAM|FUNCTION_BLOCK|FUNCTION|ACTION|METHOD)",
                text[pos:], re.IGNORECASE,
            )
            if end_match:
                depth -= 1
                pos += end_match.end()
            else:
                pos += 1

        return min(pos, len(text))

    def _extract_variables_from_block(
        self, block_text: str, pou_name: str
    ) -> List[VariableInfo]:
        """从代码块中提取变量声明"""
        variables = []

        # 查找每个VAR...END_VAR块
        var_pattern = re.compile(
            r"(VAR(?:_\w+)?)"
            r"(?:\s+(?:RETAIN|NON_RETAIN|PERSISTENT))*\s*"
            r"(.*?)"
            r"END_VAR",
            re.IGNORECASE | re.DOTALL,
        )

        for var_match in var_pattern.finditer(block_text):
            category_str = var_match.group(1).upper()

            try:
                category = VarCategory(category_str)
            except ValueError:
                category = VarCategory.VAR

            var_content = var_match.group(2)
            line_offset = (
                block_text[:var_match.start()].count("\n") + 1
            )

            # 处理全局变量单独存储
            if category == VarCategory.VAR_GLOBAL:
                vars_in_block = self._parse_var_declarations(
                    var_content, category, pou_name, line_offset
                )
                self._global_vars.extend(vars_in_block)
            else:
                vars_in_block = self._parse_var_declarations(
                    var_content, category, pou_name, line_offset
                )
                variables.extend(vars_in_block)

        return variables

    def _parse_var_declarations(
        self,
        content: str,
        category: VarCategory,
        pou_name: str,
        line_offset: int,
    ) -> List[VariableInfo]:
        """解析变量声明行"""
        variables = []

        for decl_match in self.RE_VAR_DECLARATION.finditer(content):
            names_str = decl_match.group("names").strip()
            data_type = decl_match.group("type") or "UNKNOWN"
            init_value = decl_match.group("init")
            comment = decl_match.group("comment") or ""
            line_num = line_offset + content[:decl_match.start()].count("\n")

            # 处理逗号分隔的多变量名
            for name in [n.strip() for n in names_str.split(",")]:
                if name and not name.startswith((*"(*",)):
                    variables.append(VariableInfo(
                        name=name.strip(),
                        data_type=data_type.strip(),
                        category=category,
                        initial_value=(
                            init_value.strip() if init_value else None
                        ),
                        comment=comment.strip(),
                        line_number=line_num,
                        pou_name=pou_name,
                    ))

        return variables

    def get_variable_by_name(
        self, name: str
    ) -> Optional[VariableInfo]:
        """按名称查找变量"""
        for pou in self._pous:
            for var in pou.variables:
                if var.name.lower() == name.lower():
                    return var
        for var in self._global_vars:
            if var.name.lower() == name.lower():
                return var
        return None

    def get_pou_by_name(self, name: str) -> Optional[POUInfo]:
        """按名称查找POU"""
        for pou in self._pous:
            if pou.name.lower() == name.lower():
                return pou
        return None

    @property
    def pous(self) -> List[POUInfo]:
        """获取解析出的所有POU"""
        return self._pous

    @property
    def global_variables(self) -> List[VariableInfo]:
        """获取解析出的所有全局变量"""
        return self._global_vars
