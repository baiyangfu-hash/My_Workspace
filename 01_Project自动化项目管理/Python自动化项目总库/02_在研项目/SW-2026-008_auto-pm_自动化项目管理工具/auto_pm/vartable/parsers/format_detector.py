"""格式自动识别器

V2.3 Week2 T11：基于文件扩展名 + 内容特征识别 PLC 变量表格式。

识别策略（按优先级）：
1. 文件扩展名优先（io_points.csv / program_blocks.yml / communications.yml 显式命名）
2. 内容特征识别（前几行关键字）：
   - SCL: FUNCTION_BLOCK / VAR_INPUT / VAR_OUTPUT 等关键字
   - INT doc: ### N.N VAR_INPUT 区段标题
   - Autoshop: CSV 含中文列名 '变量名'
   - Codesys: CSV 含英文列名 'Name'/'Type'/'Address'
   - Work3: tab 分隔 + 前 2 行表头
3. 无法识别 → UNKNOWN

返回 FormatType 枚举。
"""

from __future__ import annotations

import re
from pathlib import Path

from auto_pm.vartable.models import FormatType
from auto_pm.vartable.utils.encoding import read_file_with_detection

# 扩展名 → FormatType 直接映射（优先级最高）
_EXTENSION_MAP: dict[str, FormatType] = {
    ".asc": FormatType.AUTOSHOP,
    ".asn": FormatType.AUTOSHOP,
    ".wr3": FormatType.WORK3,
    ".scl": FormatType.SCL,
    ".awl": FormatType.SCL,
}

# 文件名 → FormatType 直接映射（显式命名优先级最高）
_FILENAME_MAP: dict[str, FormatType] = {
    "io_points.csv": FormatType.IO_POINTS_CSV,
    "program_blocks.yml": FormatType.PROGRAM_BLOCKS_YML,
    "program_blocks.yaml": FormatType.PROGRAM_BLOCKS_YML,
    "communications.yml": FormatType.COMMUNICATIONS_YML,
    "communications.yaml": FormatType.COMMUNICATIONS_YML,
}

# SCL 内容特征正则
_SCL_KEYWORDS = re.compile(
    r"^\s*(FUNCTION_BLOCK|ORGANIZATION_BLOCK|PROGRAM|VAR_INPUT|VAR_OUTPUT|VAR_IN_OUT|VAR_TEMP|VAR\b|END_VAR)",
    re.IGNORECASE | re.MULTILINE,
)

# INT doc 内容特征正则（### N.N VAR_INPUT 区段标题）
_INTDOC_SECTION = re.compile(
    r"^#{2,4}\s*[\d.]*\s*(VAR_INPUT|VAR_OUTPUT|VAR(?:\s+CONSTANT)?)\b",
    re.IGNORECASE | re.MULTILINE,
)

# Autoshop CSV 中文列名特征
_AUTOSHOP_HEADER = re.compile(
    r"变量名|数据类型|作用域|类别", re.IGNORECASE
)

# Codesys CSV 英文列名特征（必须有 Name + Type 同时出现）
_CODESYS_HEADER = re.compile(r"Name.*Type|Type.*Name", re.IGNORECASE)

# Work3 文件特征：第 1 行通常含 "Name" "Type" "Address"（tab 分隔）
_WORK3_HEADER = re.compile(r"Name\t.*Type\t|Scope\t.*Name\t", re.IGNORECASE)


def detect_format(file_path: str | Path) -> FormatType:
    """识别文件格式

    Args:
        file_path: 待识别文件路径

    Returns:
        FormatType：识别到的格式；无法识别返回 UNKNOWN

    识别顺序：
    1. 文件名精确匹配（io_points.csv / program_blocks.yml / communications.yml）
    2. 扩展名匹配（.asc/.asn → autoshop / .wr3 → work3 / .scl/.awl → scl）
    3. 内容特征识别（前 50 行关键字）
    4. 兜底 → UNKNOWN
    """
    path = Path(file_path)
    filename = path.name

    # 1. 文件名精确匹配（优先级最高）
    if filename in _FILENAME_MAP:
        return _FILENAME_MAP[filename]

    # 2. 扩展名匹配
    ext = path.suffix.lower()
    if ext in _EXTENSION_MAP:
        # 对 .csv/.txt/.doc/.docx/.md 需要内容特征识别
        # 但 .asc/.asn/.wr3/.scl/.awl 直接返回扩展名映射
        return _EXTENSION_MAP[ext]

    # 3. 内容特征识别
    if not path.exists():
        return FormatType.UNKNOWN

    try:
        content, _ = read_file_with_detection(path)
    except OSError:
        return FormatType.UNKNOWN

    return _detect_by_content(content, ext)


def _detect_by_content(content: str, ext: str) -> FormatType:
    """根据文件内容特征识别格式

    Args:
        content: 文件内容
        ext: 文件扩展名（小写）

    Returns:
        FormatType
    """
    if not content.strip():
        return FormatType.UNKNOWN

    # 取前 50 行做特征识别（避免大文件全扫）
    head_lines = content.splitlines()[:50]
    head = "\n".join(head_lines)

    # 3.1 SCL 关键字识别（强信号）
    if _SCL_KEYWORDS.search(head):
        return FormatType.SCL

    # 3.2 INT doc 区段标题识别（强信号）
    if _INTDOC_SECTION.search(head):
        return FormatType.INTDOC

    # 3.3 program_blocks.yml / communications.yml（YAML 内容特征）
    if ext in (".yml", ".yaml"):
        if "blocks:" in head and "name:" in head and "type:" in head:
            return FormatType.PROGRAM_BLOCKS_YML
        if "channels:" in head and "protocol:" in head:
            return FormatType.COMMUNICATIONS_YML

    # 3.4 Autoshop CSV 中文列名识别
    if _AUTOSHOP_HEADER.search(head):
        return FormatType.AUTOSHOP

    # 3.5 Work3 tab 分隔特征（前 2 行表头）
    if len(head_lines) >= 2:
        if "\t" in head_lines[0] and _WORK3_HEADER.search(head_lines[0]):
            return FormatType.WORK3

    # 3.6 Codesys CSV 英文列名特征
    if _CODESYS_HEADER.search(head):
        return FormatType.CODESYS

    # 3.7 io_points.csv 内容特征（CSV 含 station/signal_type/tag 等列）
    if ext == ".csv":
        first_line = head_lines[0] if head_lines else ""
        if "station" in first_line.lower() and "signal_type" in first_line.lower():
            return FormatType.IO_POINTS_CSV

    return FormatType.UNKNOWN


def get_parser_for_format(fmt: FormatType) -> type | None:
    """根据 FormatType 返回对应解析器类

    Args:
        fmt: 格式类型

    Returns:
        解析器类（type），未知格式返回 None

    工厂模式：调用方拿到类后实例化并调用 parse()
    """
    # 延迟导入避免循环依赖
    from auto_pm.vartable.parsers.autoshop_parser import AutoshopParser
    from auto_pm.vartable.parsers.codesys_parser import CodesysParser
    from auto_pm.vartable.parsers.communications_parser import CommunicationsParser
    from auto_pm.vartable.parsers.intdoc_parser import IntDocParser
    from auto_pm.vartable.parsers.io_points_parser import IoPointsParser
    from auto_pm.vartable.parsers.program_blocks_parser import ProgramBlocksParser
    from auto_pm.vartable.parsers.scl_parser import SclParser
    from auto_pm.vartable.parsers.work3_parser import Work3Parser

    parser_map: dict[FormatType, type] = {
        FormatType.AUTOSHOP: AutoshopParser,
        FormatType.WORK3: Work3Parser,
        FormatType.CODESYS: CodesysParser,
        FormatType.SCL: SclParser,
        FormatType.INTDOC: IntDocParser,
        FormatType.IO_POINTS_CSV: IoPointsParser,
        FormatType.PROGRAM_BLOCKS_YML: ProgramBlocksParser,
        FormatType.COMMUNICATIONS_YML: CommunicationsParser,
    }
    return parser_map.get(fmt)


def list_supported_formats() -> tuple[tuple[FormatType, str, tuple[str, ...]], ...]:
    """列出支持的格式（供 CLI list-formats 命令使用）

    Returns:
        元组：(format_type, description, extensions)
    """
    return (
        (FormatType.AUTOSHOP, "Autoshop 变量表（中文列名 CSV）", (".asc", ".asn")),
        (FormatType.WORK3, "Work3 变量表（tab 分隔）", (".wr3",)),
        (FormatType.CODESYS, "Codesys 变量表（英文列名 CSV）", (".csv", ".txt")),
        (FormatType.SCL, "Siemens SCL 源文件", (".scl", ".awl")),
        (FormatType.INTDOC, "Markdown 接口文档", (".md", ".doc", ".docx", ".txt")),
        (
            FormatType.IO_POINTS_CSV,
            "工程资产 IO 点位表",
            ("io_points.csv",),
        ),
        (
            FormatType.PROGRAM_BLOCKS_YML,
            "工程资产程序块清单",
            ("program_blocks.yml",),
        ),
        (
            FormatType.COMMUNICATIONS_YML,
            "工程资产通信通道清单",
            ("communications.yml",),
        ),
    )
