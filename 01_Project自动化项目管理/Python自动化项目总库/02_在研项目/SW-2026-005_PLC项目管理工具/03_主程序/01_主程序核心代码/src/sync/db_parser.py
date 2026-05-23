# -*- coding: utf-8 -*-
"""
GlobalVars.db 解析器

从 Siemens GVL 格式的 .db 文件中提取 STRUCT 定义和变量声明。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class VarRecord:
    """单条变量记录"""
    name: str = ""
    type_: str = ""
    default: str = ""
    comment: str = ""


@dataclass
class StructGroup:
    """一个 STRUCT 结构体组"""
    name: str = ""
    description: str = ""
    header_comment: str = ""
    variables: List[VarRecord] = field(default_factory=list)
    input_count: int = 0
    output_count: int = 0


class DbParser:
    """GlobalVars.db 解析器"""

    RE_DATA_BLOCK = re.compile(r'DATA_BLOCK\s+(\w+)')
    RE_STRUCT_START = re.compile(r'^\s*(\w+)\s*:\s*STRUCT\b')
    RE_VAR_LINE = re.compile(
        r'^\s*(\w+)\s*:\s*(.+?);\s*(?://\s*(.*))?$'
    )
    RE_TYPE_WITH_DEFAULT = re.compile(
        r'^(.+?)\s*:=\s*(.+)$'
    )

    @classmethod
    def parse_db_file(cls, file_path: str) -> List[StructGroup]:
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"文件不存在: {file_path}")
                return []

            content = path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()

            in_var = False
            structs = []
            i = 0
            while i < len(lines):
                line = lines[i].strip()

                if cls.RE_DATA_BLOCK.search(line):
                    in_var = False

                if line == "VAR" and not in_var:
                    in_var = True
                    i += 1
                    continue

                if line == "END_VAR":
                    in_var = False

                if in_var:
                    m = cls.RE_STRUCT_START.match(line)
                    if m:
                        struct = cls._parse_struct(lines, i)
                        if struct:
                            structs.append(struct)
                        while i < len(lines) and not line.startswith("END_STRUCT"):
                            i += 1
                            if i < len(lines):
                                line = lines[i].strip()
                        i += 1
                        continue

                i += 1

            logger.info(f"解析完成: {len(structs)} 个结构体, "
                        f"共 {sum(len(s.variables) for s in structs)} 个变量")
            return structs

        except Exception as e:
            logger.error(f"解析失败 {file_path}: {e}")
            return []

    @classmethod
    def _parse_struct(cls, lines: List[str], struct_line_idx: int) -> Optional[StructGroup]:
        m = cls.RE_STRUCT_START.match(lines[struct_line_idx].strip())
        if not m:
            return None
        name = m.group(1)

        desc = cls._collect_comment_block(lines, struct_line_idx - 1)

        header = ""
        for k in range(struct_line_idx - 1, max(struct_line_idx - 8, 0), -1):
            stripped = lines[k].strip()
            if stripped.startswith("// ===="):
                break
            if stripped.startswith("// ") and "接口统计" in stripped:
                header = stripped.lstrip("// ")
                break

        variables = []
        j = struct_line_idx + 1
        while j < len(lines):
            line = lines[j]
            stripped = line.strip()
            if stripped == "END_STRUCT;" or stripped.startswith("END_STRUCT"):
                break
            if stripped.startswith("//"):
                j += 1
                continue
            if not stripped:
                j += 1
                continue
            if stripped.startswith("DATA_BLOCK") or stripped == "END_VAR":
                break

            var = cls._parse_var_line(stripped)
            if var:
                variables.append(var)
            j += 1

        in_count = sum(1 for v in variables if v.name.startswith(("i_", "I_")))
        out_count = sum(1 for v in variables
                        if v.name.startswith(("o_", "O_", "q_", "Q_")))

        return StructGroup(
            name=name,
            description=desc,
            header_comment=header,
            variables=variables,
            input_count=in_count,
            output_count=out_count,
        )

    @classmethod
    def _parse_var_line(cls, line: str) -> Optional[VarRecord]:
        if line.startswith("//"):
            return None
        if line.startswith("END_"):
            return None

        m = cls.RE_VAR_LINE.match(line)
        if not m:
            return None

        name = m.group(1)
        raw_type = m.group(2).strip()
        comment = m.group(3) or ""

        type_ = raw_type
        default = ""

        tm = cls.RE_TYPE_WITH_DEFAULT.match(raw_type)
        if tm:
            type_ = tm.group(1).strip()
            default = tm.group(2).strip()

        return VarRecord(name=name, type_=type_, default=default, comment=comment)

    @classmethod
    def _collect_comment_block(cls, lines: List[str], end_idx: int) -> str:
        comments = []
        for k in range(end_idx, max(end_idx - 15, -1), -1):
            stripped = lines[k].strip()
            if stripped.startswith("// ===="):
                break
            if stripped.startswith("// "):
                text = stripped[3:]
                if text.strip():
                    comments.insert(0, text)
            else:
                break
        return "\n".join(comments)

    @classmethod
    def find_group_by_name(cls, groups: List[StructGroup], name: str) -> Optional[StructGroup]:
        name_lower = name.lower()
        for g in groups:
            if g.name.lower() == name_lower:
                return g
        for g in groups:
            if name_lower in g.name.lower() or g.name.lower() in name_lower:
                return g
        return None

    @classmethod
    def match_groups_for_fb(cls, groups: List[StructGroup], fb_name: str) -> List[StructGroup]:
        """
        按 FB 名称匹配对应的结构体组

        Mapping:
          "FB_1002_Conveyor" → stConveyor
          "FB_1003_PickPlace" → stPickPlace
          "FB_1004_Feeder" → stFeeder
          "FB_2001_Alarm" → stGlobal
          "FB_External" → stExternal
          "OB1" → 所有 struct
        """
        if not groups:
            return []

        mapping = {
            "conveyor": "stconveyor",
            "pickplace": "stpickplace",
            "feeder": "stfeeder",
            "common": "stglobal",
            "alarm": "stglobal",
            "2001": "stglobal",
            "external": "stexternal",
            "3001": "stexternal",
        }

        fb_lower = fb_name.lower()
        target = None
        for key, struct_key in mapping.items():
            if key in fb_lower:
                target = struct_key
                break

        if target:
            for g in groups:
                if g.name.lower() == target:
                    return [g]

        if "ob1" in fb_lower:
            return groups

        return []