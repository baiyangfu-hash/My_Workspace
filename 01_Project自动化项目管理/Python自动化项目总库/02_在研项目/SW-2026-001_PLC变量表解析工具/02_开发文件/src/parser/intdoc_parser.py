#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
接口文档解析器

解析Markdown格式的PLC接口文档（接口文档_INT.md），
提取VAR_INPUT/VAR_OUTPUT/VAR区段的顶层变量及结构体字段定义。
"""

import re
from typing import List, Dict, Optional

from .base_parser import BaseParser
from utils.encoding_detector import EncodingDetector


class IntDocParser(BaseParser):
    """
    接口文档解析器

    解析Markdown格式的接口文档，提取：
    - 顶层变量（VAR_INPUT / VAR_OUTPUT / VAR 区段）
    - 结构体字段定义（ST_xxx 字段定义 子表）
    """

    # 识别 VAR 区段标题的正则：### 2.1 VAR_INPUT / ### 2.2 VAR_OUTPUT / ### 2.3 VAR
    _SECTION_RE = re.compile(
        r"^#{2,4}\s*[\d.]*\s*(VAR_INPUT|VAR_OUTPUT|VAR(?:\s+CONSTANT)?)\b",
        re.IGNORECASE,
    )

    # 识别结构体字段定义子表标题：**ST_CylinderCmd 字段定义** 或 **ST_xxx 字段定义 (Vx.x.x)**
    _STRUCT_DEF_RE = re.compile(
        r"\*\*(ST_\w+)\s+字段定义\*\*\s*(?:\(V[\d.]+\))?",
        re.IGNORECASE,
    )

    # 识别结构体类型引用：ST_CylinderCmd / ST_CylinderSts
    _STRUCT_TYPE_RE = re.compile(r"^(ST_\w+)$")

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.struct_fields: List[Dict] = []

    def parse(self) -> List[Dict]:
        """
        解析接口文档

        返回:
            List[Dict]: 顶层变量列表，每个变量包含:
                - name: 变量名
                - type: 数据类型
                - scope: 声明区（VAR_INPUT/VAR_OUTPUT/VAR）
                - description: 说明
                - default_value: 默认值（如有）
                - value_range: 有效值域（如有）

        结构体字段存储在 self.struct_fields，每个字段包含:
                - struct_name: 结构体名
                - field: 字段名
                - type: 数据类型
                - default_value: 默认值
                - value_range: 有效值域
                - description: 说明
        """
        encoding_detector = EncodingDetector()
        encoding = encoding_detector.detect_encoding(self.file_path)

        with open(self.file_path, "r", encoding=encoding) as f:
            lines = f.readlines()

        self._parse_sections(lines)
        return self.variables

    def get_struct_fields(self) -> List[Dict]:
        """
        获取解析后的结构体字段列表

        返回:
            List[Dict]: 结构体字段列表
        """
        return self.struct_fields

    def _parse_sections(self, lines: List[str]) -> None:
        """
        逐行扫描，识别区段标题和结构体定义标题，解析对应的Markdown表格
        """
        current_scope: Optional[str] = None
        current_struct: Optional[str] = None
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # 检测 VAR 区段标题
            scope_match = self._SECTION_RE.match(line)
            if scope_match:
                current_scope = self._normalize_scope(scope_match.group(1))
                current_struct = None
                i += 1
                continue

            # 检测结构体字段定义标题
            struct_match = self._STRUCT_DEF_RE.search(line)
            if struct_match:
                current_struct = struct_match.group(1)
                current_scope = None
                i += 1
                continue

            # 检测Markdown表格起始（以 | 开头）
            if line.startswith("|") and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if self._is_table_separator(next_line):
                    table_rows = self._extract_table(lines, i)
                    if table_rows:
                        if current_struct:
                            self._parse_struct_table(table_rows, current_struct)
                        elif current_scope:
                            self._parse_variable_table(table_rows, current_scope)
                    i += len(table_rows) + 1
                    continue

            i += 1

    def _normalize_scope(self, raw: str) -> str:
        """规范化声明区名称"""
        raw = raw.upper().strip()
        if raw.startswith("VAR_INPUT"):
            return "VAR_INPUT"
        if raw.startswith("VAR_OUTPUT"):
            return "VAR_OUTPUT"
        return "VAR"

    def _is_table_separator(self, line: str) -> bool:
        """判断是否为Markdown表格分隔行（如 |---|---|）"""
        return bool(re.match(r"^\|[\s\-:|]+\|?\s*$", line))

    def _extract_table(self, lines: List[str], start_idx: int) -> List[str]:
        """
        从start_idx开始提取连续的表格行（含表头和分隔行）

        返回:
            表格行列表（不含分隔行）
        """
        table_lines = []
        i = start_idx
        while i < len(lines):
            line = lines[i].strip()
            if not line.startswith("|"):
                break
            table_lines.append(line)
            i += 1
        # 移除分隔行（第2行）
        if len(table_lines) >= 2 and self._is_table_separator(table_lines[1]):
            table_lines.pop(1)
        return table_lines

    def _parse_table_row(self, row: str) -> List[str]:
        """将Markdown表格行拆分为单元格列表"""
        cells = row.split("|")
        # 去掉首尾空元素（行首|和行尾|产生的空串）
        cells = [c.strip() for c in cells[1:-1]] if len(cells) > 2 else [c.strip() for c in cells]
        return cells

    def _parse_variable_table(self, table_lines: List[str], scope: str) -> None:
        """
        解析顶层变量表

        表头可能包含：名称/字段/类型/默认值/有效值域/说明/来源/去向 等
        """
        if not table_lines:
            return

        headers = [h.strip() for h in self._parse_table_row(table_lines[0])]

        # 列名匹配（容错不同INT.md的列名差异）
        col_map = self._map_variable_columns(headers)

        for row_line in table_lines[1:]:
            cells = self._parse_table_row(row_line)
            if len(cells) < 2:
                continue

            var = {
                "name": self._get_cell(cells, col_map.get("name"), "").strip(),
                "type": self._get_cell(cells, col_map.get("type"), "").strip(),
                "scope": scope,
                "description": self._get_cell(cells, col_map.get("description"), "").strip(),
                "default_value": self._get_cell(cells, col_map.get("default_value"), "").strip(),
                "value_range": self._get_cell(cells, col_map.get("value_range"), "").strip(),
            }

            # 跳过空行或分隔说明行
            if not var["name"] or var["name"].startswith("---"):
                continue
            # 跳过注释行（如 > 注释）
            if var["name"].startswith(">"):
                continue

            self.variables.append(var)

    def _parse_struct_table(self, table_lines: List[str], struct_name: str) -> None:
        """
        解析结构体字段定义表

        表头通常包含：字段/类型/默认值/有效值域/说明
        """
        if not table_lines:
            return

        headers = [h.strip() for h in self._parse_table_row(table_lines[0])]
        col_map = self._map_struct_columns(headers)

        for row_line in table_lines[1:]:
            cells = self._parse_table_row(row_line)
            if len(cells) < 2:
                continue

            field = {
                "struct_name": struct_name,
                "field": self._get_cell(cells, col_map.get("field"), "").strip(),
                "type": self._get_cell(cells, col_map.get("type"), "").strip(),
                "default_value": self._get_cell(cells, col_map.get("default_value"), "").strip(),
                "value_range": self._get_cell(cells, col_map.get("value_range"), "").strip(),
                "description": self._get_cell(cells, col_map.get("description"), "").strip(),
            }

            if not field["field"] or field["field"].startswith("---"):
                continue
            if field["field"].startswith(">"):
                continue

            self.struct_fields.append(field)

    def _map_variable_columns(self, headers: List[str]) -> Dict[str, Optional[int]]:
        """
        将表头名映射到标准字段名（容错不同列名写法）

        支持的列名变体：
            name: 名称/字段/变量名/Name
            type: 类型/数据类型/Type
            description: 说明/注释/描述/去向/来源
            default_value: 默认值/初始值
            value_range: 有效值域/值域/范围
        """
        col_map: Dict[str, Optional[int]] = {
            "name": None,
            "type": None,
            "description": None,
            "default_value": None,
            "value_range": None,
        }

        for idx, h in enumerate(headers):
            h_lower = h.lower().strip()
            if col_map["name"] is None and h_lower in ("名称", "字段", "变量名", "name"):
                col_map["name"] = idx
            elif col_map["type"] is None and h_lower in ("类型", "数据类型", "type", "datatype"):
                col_map["type"] = idx
            elif col_map["default_value"] is None and h_lower in ("默认值", "初始值", "default", "default_value"):
                col_map["default_value"] = idx
            elif col_map["value_range"] is None and h_lower in ("有效值域", "值域", "范围", "value_range", "range"):
                col_map["value_range"] = idx
            elif col_map["description"] is None and h_lower in ("说明", "注释", "描述", "description", "去向", "来源", "comment"):
                col_map["description"] = idx

        return col_map

    def _map_struct_columns(self, headers: List[str]) -> Dict[str, Optional[int]]:
        """
        将结构体字段表头映射到标准字段名
        """
        col_map: Dict[str, Optional[int]] = {
            "field": None,
            "type": None,
            "default_value": None,
            "value_range": None,
            "description": None,
        }

        for idx, h in enumerate(headers):
            h_lower = h.lower().strip()
            if col_map["field"] is None and h_lower in ("字段", "名称", "变量名", "field", "name"):
                col_map["field"] = idx
            elif col_map["type"] is None and h_lower in ("类型", "数据类型", "type", "datatype"):
                col_map["type"] = idx
            elif col_map["default_value"] is None and h_lower in ("默认值", "初始值", "default", "default_value"):
                col_map["default_value"] = idx
            elif col_map["value_range"] is None and h_lower in ("有效值域", "值域", "范围", "value_range", "range"):
                col_map["value_range"] = idx
            elif col_map["description"] is None and h_lower in ("说明", "注释", "描述", "description", "comment"):
                col_map["description"] = idx

        return col_map

    @staticmethod
    def _get_cell(cells: List[str], idx: Optional[int], default: str = "") -> str:
        """安全获取单元格内容"""
        if idx is None or idx >= len(cells):
            return default
        return cells[idx]
