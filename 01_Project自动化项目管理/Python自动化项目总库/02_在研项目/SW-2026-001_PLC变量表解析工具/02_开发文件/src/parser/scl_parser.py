#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCL解析器

用于解析Siemens SCL源文件，提取变量声明信息
"""

import re
from typing import List, Dict, Optional
from parser.base_parser import BaseParser
from utils.error_handler import ErrorHandler


COMPLEX_TYPE_MEMBERS: Dict[str, List[Dict[str, str]]] = {
    "FB_TONR": [
        {"name": "IN", "type": "BOOL", "default": "OFF", "comment": "计时执行"},
        {"name": "PT", "type": "DINT", "default": "0", "comment": "预设定时"},
        {"name": "R", "type": "BOOL", "default": "OFF", "comment": "计时器复位"},
        {"name": "Q", "type": "BOOL", "default": "OFF", "comment": "时间到达"},
        {"name": "ET", "type": "DINT", "default": "0", "comment": "经过时间"},
    ],
    "FB_TON": [
        {"name": "IN", "type": "BOOL", "default": "OFF", "comment": "计时执行"},
        {"name": "PT", "type": "DINT", "default": "0", "comment": "预设定时"},
        {"name": "Q", "type": "BOOL", "default": "OFF", "comment": "时间到达"},
        {"name": "ET", "type": "DINT", "default": "0", "comment": "经过时间"},
    ],
}

SCOPE_MAP = {
    "VAR_INPUT": "IN",
    "VAR_OUTPUT": "OUT",
    "VAR_IN_OUT": "VAR_IN_OUT",
    "VAR": "VAR",
    "VAR_TEMP": "VAR",
}

BOOL_DEFAULT = "OFF"
NUMERIC_DEFAULTS = {
    "INT": "0",
    "DINT": "0",
    "REAL": "0.0",
    "WORD": "0",
    "DWORD": "0",
    "BYTE": "0",
}


def _is_complex_type(type_name: str) -> bool:
    return type_name.startswith("FB_") or type_name.startswith("ST_")


def _get_default_for_type(type_name: str) -> str:
    if type_name == "BOOL":
        return BOOL_DEFAULT
    return NUMERIC_DEFAULTS.get(type_name, "")


def _get_members_for_type(type_name: str) -> List[Dict[str, str]]:
    if type_name in COMPLEX_TYPE_MEMBERS:
        return COMPLEX_TYPE_MEMBERS[type_name]
    return []


def _clean_default(value: str) -> str:
    return value.rstrip(";").strip()


class SclParser(BaseParser):
    """
    SCL解析器

    解析Siemens SCL源文件，提取FUNCTION_BLOCK中的变量声明
    支持加载外部ST文件来展开复杂类型(如ST_Cylinder)
    """

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.fb_name: str = ""
        self._struct_defs: Dict[str, List[Dict[str, str]]] = {}

    def load_type_files(self, type_file_paths: List[str]) -> None:
        for path in type_file_paths:
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                self._extract_struct_definitions(content)
            except Exception as e:
                print(f"加载类型文件失败 {path}: {str(e)}")

    def parse(self) -> List[Dict]:
        self.variables = []
        error_handler = ErrorHandler()

        try:
            with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            error_info = error_handler.handle_exception(e, f"读取SCL文件: {self.file_path}")
            raise Exception(error_handler.format_error_message(error_info))

        self._extract_struct_definitions(content)
        self._extract_fb_name(content)
        self._extract_variables(content)

        return self.variables

    def _extract_struct_definitions(self, content: str) -> None:
        struct_pattern = re.compile(
            r"TYPE\s+(\w+)\s*:\s*STRUCT\s*(.*?)\s*END_STRUCT\s*END_TYPE",
            re.DOTALL | re.IGNORECASE,
        )
        for match in struct_pattern.finditer(content):
            type_name = match.group(1)
            body = match.group(2)
            members = self._parse_struct_body(body)
            if members:
                self._struct_defs[type_name] = members
                COMPLEX_TYPE_MEMBERS[type_name] = members

    def _parse_struct_body(self, body: str) -> List[Dict[str, str]]:
        members: List[Dict[str, str]] = []
        for line in body.split("\n"):
            line = line.strip()
            if not line or line.startswith("//"):
                continue

            comment = ""
            comment_match = re.search(r"//\s*(.*)", line)
            if comment_match:
                comment = comment_match.group(1).strip()
                line = line[:comment_match.start()].strip()

            line = line.rstrip(";").strip()
            if not line:
                continue

            var_match = re.match(
                r"(\w+)\s*:\s*(BOOL|INT|DINT|REAL|WORD|DWORD|BYTE)\s*(?::=\s*(.+))?",
                line,
            )
            if var_match:
                name = var_match.group(1)
                vtype = var_match.group(2)
                default = _clean_default(var_match.group(3)) if var_match.group(3) else _get_default_for_type(vtype)
                members.append({"name": name, "type": vtype, "default": default, "comment": comment})
        return members

    def _extract_fb_name(self, content: str) -> None:
        fb_match = re.search(r"FUNCTION_BLOCK\s+(\w+)", content)
        if fb_match:
            self.fb_name = fb_match.group(1)

    def _extract_variables(self, content: str) -> None:
        scope_pattern = re.compile(
            r"(VAR_INPUT|VAR_OUTPUT|VAR_IN_OUT|VAR|VAR_TEMP)\s*(.*?)\s*END_VAR",
            re.DOTALL | re.IGNORECASE,
        )

        seq = 1
        for match in scope_pattern.finditer(content):
            scope_keyword = match.group(1).upper()
            body = match.group(2)
            autoshop_scope = SCOPE_MAP.get(scope_keyword, "VAR")

            for line in body.split("\n"):
                line = line.strip()
                if not line or line.startswith("//"):
                    continue

                var_info = self._parse_var_line(line)
                if not var_info:
                    continue

                var_name = var_info["name"]
                var_type = var_info["type"]
                var_comment = var_info["comment"]
                var_default = var_info["default"]

                if _is_complex_type(var_type):
                    members = _get_members_for_type(var_type)
                    self.variables.append({
                        "seq": seq,
                        "scope": autoshop_scope,
                        "name": var_name,
                        "type": var_type,
                        "hidden_default": "",
                        "default": "",
                        "retain": "不保持",
                        "comment": var_comment,
                        "is_sub": False,
                    })
                    seq += 1

                    for member in members:
                        self.variables.append({
                            "seq": "",
                            "scope": "",
                            "name": f"{var_name}.{member['name']}",
                            "type": member["type"],
                            "hidden_default": "",
                            "default": member.get("default", ""),
                            "retain": "不保持",
                            "comment": member.get("comment", ""),
                            "is_sub": True,
                        })
                else:
                    self.variables.append({
                        "seq": seq,
                        "scope": autoshop_scope,
                        "name": var_name,
                        "type": var_type,
                        "hidden_default": "",
                        "default": var_default,
                        "retain": "不保持",
                        "comment": var_comment,
                        "is_sub": False,
                    })
                    seq += 1

    def _parse_var_line(self, line: str) -> Optional[Dict[str, str]]:
        comment = ""
        comment_match = re.search(r"\(\*\s*(.*?)\s*\*\)", line)
        if comment_match:
            comment = comment_match.group(1).strip()
            line = line[:comment_match.start()] + line[comment_match.end():]
        else:
            comment_match = re.search(r"//\s*(.*)", line)
            if comment_match:
                comment = comment_match.group(1).strip()
                line = line[:comment_match.start()]

        line = line.strip().rstrip(";").strip()
        if not line:
            return None

        match = re.match(r"(\w+)\s*:\s*(\w+)(?:\s*:=\s*(\S+))?", line)
        if not match:
            return None

        name = match.group(1)
        vtype = match.group(2)
        default = _clean_default(match.group(3)) if match.group(3) else _get_default_for_type(vtype)

        return {"name": name, "type": vtype, "default": default, "comment": comment}

    def export_to_autoshop_csv(self, output_path: str, encoding: str = "gbk") -> bool:
        try:
            with open(output_path, "wb") as f:
                header = "序号,类别,名称,数据类型,隐藏初始值,初始值,掉电保持,注释,\n"
                f.write(header.encode(encoding))
                for var in self.variables:
                    seq = str(var["seq"]) if var["seq"] != "" else ""
                    scope = var["scope"] if not var["is_sub"] else ""
                    row = (
                        f"{seq},{scope},{var['name']},{var['type']},"
                        f"{var['hidden_default']},{var['default']},{var['retain']},"
                        f"{var['comment']},\n"
                    )
                    f.write(row.encode(encoding))
            return True
        except Exception as e:
            print(f"导出Autoshop CSV失败: {str(e)}")
            return False
