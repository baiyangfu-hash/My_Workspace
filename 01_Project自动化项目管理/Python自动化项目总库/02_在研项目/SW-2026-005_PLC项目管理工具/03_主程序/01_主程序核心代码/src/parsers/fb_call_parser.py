# -*- coding: utf-8 -*-
"""
FB调用语句解析器

从OB1等主程序SCL源码中解析出每个FB实例的调用参数列表。
核心能力:
- 识别 InstanceName( ... ); 形式的FB调用块
- 正确处理嵌套括号(数组索引、函数调用)、多行参数、行内注释
- 区分输入参数(:=)和输出参数(=>)
- 支持VAR_IN_OUT参数的识别
"""
import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class FBCallArgument:
    """单个FB调用参数"""

    param_name: str
    direction: str
    value_expression: str
    line_number: int
    fb_instance_name: str = ""


@dataclass
class FBCallSite:
    """单个FB调用点（一个完整的 InstanceName(...); 块）"""

    fb_instance_name: str
    fb_type_name: str = ""
    file_path: str = ""
    line_number: int = 0
    end_line_number: int = 0
    input_args: List[FBCallArgument] = field(default_factory=list)
    output_args: List[FBCallArgument] = field(default_factory=list)
    inout_args: List[FBCallArgument] = field(default_factory=list)

    @property
    def all_args(self) -> List[FBCallArgument]:
        return self.input_args + self.inout_args + self.output_args

    def get_arg_by_name(self, name: str) -> Optional[FBCallArgument]:
        lower = name.lower()
        for arg in self.all_args:
            if arg.param_name.lower() == lower:
                return arg
        return None

    def get_called_param_names(self) -> List[str]:
        return [a.param_name for a in self.all_args]


class FBCallParser:
    """
    OB1 FB调用语句解析器

    解析模式:
        GlobalVars.fbPickPlace(
            i_bAutoMode := expr,
            q_bOutput  => target
        );

    关键技术点:
    - 用括号深度追踪分割顶层逗号（避免数组索引/函数调用的内部逗号干扰）
    - 支持 (* ... *) 行内注释剥离
    - 支持跨多行的长调用块
    """

    RE_FB_CALL_START = re.compile(
        r"(?P<instance>(?:\w+\.)+\w+|\w+)\s*\(",
    )
    RE_ARG_ASSIGN = re.compile(
        r"(?P<name>\w+)\s*(?P<op>:=|=>)\s*(?P<value>.+)",
    )

    @classmethod
    def parse_ob1_calls(cls, ob1_source: str, file_path: str = "") -> List[FBCallSite]:
        """
        解析OB1中的所有FB调用

        Args:
            ob1_source: OB1.scl完整源码文本
            file_path: 源文件路径(用于记录)

        Returns:
            List[FBCallSite]: 所有FB调用点的列表
        """
        calls: List[FBCallSite] = []
        lines = ob1_source.splitlines()

        for idx, line in enumerate(lines):
            stripped = line.strip()

            if not stripped:
                continue

            match = cls.RE_FB_CALL_START.match(stripped)
            if not match:
                continue

            instance_name = match.group("instance").strip()
            start_pos_in_line = match.start()

            call_site = cls._parse_fb_call_block(
                lines, idx, start_pos_in_line, instance_name, file_path,
            )
            if call_site:
                calls.append(call_site)

        logger.info(f"FB调用解析完成: 共发现{len(calls)}个调用点")
        return calls

    @classmethod
    def _parse_fb_call_block(
        cls,
        lines: List[str],
        start_line_idx: int,
        start_col: int,
        instance_name: str,
        file_path: str,
    ) -> Optional[FBCallSite]:
        """
        从起始行开始解析一个完整的 FB_Instance(...); 调用块

        策略: 从 '(' 开始逐字符追踪括号深度，找到匹配的 ')'，
             再确认后面跟着 ';'
        """
        start_line_num = start_line_idx + 1

        first_line = lines[start_line_idx]
        open_paren_pos = first_line.index("(", start_col) if "(" in first_line[start_col:] else -1
        if open_paren_pos == -1:
            return None

        depth = 1
        current_line_idx = start_line_idx
        char_pos = open_paren_pos + 1
        block_chars: List[str] = []

        while depth > 0 and current_line_idx < len(lines):
            line = lines[current_line_idx]

            while char_pos < len(line):
                ch = line[char_pos]

                if ch == "(":
                    depth += 1
                    block_chars.append(ch)
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        end_line_num = current_line_idx + 1
                        inner_text = "".join(block_chars).strip()
                        return cls._build_call_site(
                            inner_text, instance_name, file_path,
                            start_line_num, end_line_num,
                        )
                    block_chars.append(ch)
                elif ch == "'" or ch == '"':
                    block_chars.append(ch)
                    char_pos += 1
                    while char_pos < len(line) and line[char_pos] != ch:
                        if line[char_pos] == "\\":
                            block_chars.append(line[char_pos])
                            char_pos += 1
                        block_chars.append(line[char_pos])
                        char_pos += 1
                    if char_pos < len(line):
                        block_chars.append(line[ch])
                else:
                    block_chars.append(ch)

                char_pos += 1

            current_line_idx += 1
            char_pos = 0

        return None

    @classmethod
    def _build_call_site(
        cls,
        inner_text: str,
        instance_name: str,
        file_path: str,
        start_line: int,
        end_line: int,
    ) -> FBCallSite:
        """从括号内文本构建FBCallSite"""
        site = FBCallSite(
            fb_instance_name=instance_name,
            file_path=file_path,
            line_number=start_line,
            end_line_number=end_line,
        )

        raw_args = cls._split_top_level_commas(inner_text)
        base_line = start_line

        for arg_text in raw_args:
            arg_text_clean = cls._strip_inline_comment(arg_text.strip())
            if not arg_text_clean:
                continue

            arg = cls._extract_argument(arg_text_clean, instance_name, base_line)
            if arg is None:
                continue

            if arg.direction == "output":
                site.output_args.append(arg)
            elif arg.direction == "inout":
                site.inout_args.append(arg)
            else:
                site.input_args.append(arg)

            base_line += arg_text.count("\n") + (1 if "\n" not in arg_text else 0)

        return site

    @classmethod
    def _split_top_level_commas(cls, text: str) -> List[str]:
        """
        按顶层逗号分割参数文本，忽略括号内的逗号

        例如: "a := fn(x,y), b => z" → ["a := fn(x,y)", " b => z"]
        """
        parts: List[str] = []
        current: List[str] = []
        depth = 0
        in_string = False
        string_char = ""

        for ch in text:
            if ch in ("'", '"') and not in_string:
                in_string = True
                string_char = ch
                current.append(ch)
            elif ch == string_char and in_string:
                in_string = False
                string_char = ""
                current.append(ch)
            elif in_string:
                current.append(ch)
            elif ch == "(":
                depth += 1
                current.append(ch)
            elif ch == ")":
                depth -= 1
                current.append(ch)
            elif ch == "," and depth == 0:
                parts.append("".join(current))
                current = []
            else:
                current.append(ch)

        if current:
            parts.append("".join(current))

        return parts

    @classmethod
    def _strip_inline_comment(cls, text: str) -> str:
        """剥离行内 (* ... *) 注释"""
        result = text
        while True:
            start = result.find("(*")
            if start == -1:
                break
            end = result.find("*)", start)
            if end == -1:
                result = result[:start]
                break
            result = result[:start] + result[end + 2:]
        return result.strip()

    @classmethod
    def _extract_argument(
        cls,
        arg_text: str,
        fb_instance_name: str,
        base_line: int,
    ) -> Optional[FBCallArgument]:
        """
        解析单个参数: paramName := value 或 paramName => value

        Returns:
            FBCallArgument 或 None(解析失败时)
        """
        clean = arg_text.strip()
        if not clean:
            return None

        match = cls.RE_ARG_ASSIGN.match(clean)
        if not match:
            return None

        param_name = match.group("name").strip()
        op = match.group("op").strip()
        value_expr = match.group("value").strip()

        if op == "=>":
            direction = "output"
        elif param_name.lower().startswith("io_"):
            direction = "inout"
        else:
            direction = "input"

        line_offset = clean.count("\n")
        actual_line = base_line + line_offset

        return FBCallArgument(
            param_name=param_name,
            direction=direction,
            value_expression=value_expr,
            line_number=actual_line,
            fb_instance_name=fb_instance_name,
        )
