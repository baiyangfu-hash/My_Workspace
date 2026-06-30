"""变量表解析模块

V2.3 吸收 SW-2026-001 变量表解析能力，提供多格式解析、编码检测、转换导出能力。

模块结构：
- models.py: 数据模型（VarEntry/VarTable/ParseResult/ParseError）
- parsers/: 各格式解析器（io_points_csv/program_blocks.yml/communications.yml/...）
- utils/: 工具（encoding 编码检测/...）
- converter/: 格式转换器（中间模型统一导出，V2.3 Week4）
"""

from auto_pm.vartable.models import (
    ParseError,
    ParseResult,
    VarEntry,
    VarTable,
)

__all__ = [
    "ParseError",
    "ParseResult",
    "VarEntry",
    "VarTable",
]
