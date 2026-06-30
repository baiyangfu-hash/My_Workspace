"""变量表数据模型

V2.3 Week1 T01：定义变量表解析的统一数据模型。

设计原则：
- frozen dataclass 保证不可变，可哈希
- 字段对齐 io_points.csv 7 字段 + 解析元数据
- ParseResult 统一成功/失败返回，避免异常控制流
- VarTable.entries 用 tuple 而非 list（frozen 兼容）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class VarEntry:
    """单个变量条目（io_points.csv 一行对应一个 VarEntry）

    字段对齐 DJ-2026-005 io_points.csv 的 7 列：
    station,signal_type,address,tag,signal_name,device,comment

    多地址格式示例：
    - cpu 站点: Y0/X0（直接 IO 地址）
    - remote_io 站点: RIO1:Y10（站点前缀:地址）

    comment 字段可能含分号分隔的多值，按原样保留：
    - "P40/EFS1/24.7; 源程序用途: 变频器1异常检测"
    """

    station: str
    signal_type: str
    address: str
    tag: str
    signal_name: str
    device: str
    comment: str
    source_format: str = "io_points_csv"
    line_number: int = 0

    def to_dict(self) -> dict[str, Any]:
        """转换为可序列化字典（供 JSON 输出）"""
        return {
            "station": self.station,
            "signal_type": self.signal_type,
            "address": self.address,
            "tag": self.tag,
            "signal_name": self.signal_name,
            "device": self.device,
            "comment": self.comment,
            "source_format": self.source_format,
            "line_number": self.line_number,
        }


@dataclass(frozen=True, slots=True)
class ParseError:
    """解析错误条目（某行某字段校验失败）"""

    line_number: int
    field: str
    message: str
    raw_value: str = ""


@dataclass(frozen=True, slots=True)
class VarTable:
    """变量表容器（一次解析的结果集）

    entries 用 tuple 而非 list，保证 frozen dataclass 可哈希。
    metadata 存放解析过程中收集的额外信息（如站点统计、地址段统计）。
    """

    entries: tuple[VarEntry, ...]
    source_path: str
    source_format: str
    parsed_at: str
    encoding: str = "utf-8"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def total_count(self) -> int:
        """变量条目总数"""
        return len(self.entries)

    @property
    def stations(self) -> tuple[str, ...]:
        """去重后的站点列表"""
        return tuple(sorted({entry.station for entry in self.entries}))

    @property
    def signal_types(self) -> tuple[str, ...]:
        """去重后的信号类型列表"""
        return tuple(sorted({entry.signal_type for entry in self.entries}))

    def to_dict(self) -> dict[str, Any]:
        """转换为可序列化字典（供 JSON 输出）"""
        return {
            "entries": [entry.to_dict() for entry in self.entries],
            "source_path": self.source_path,
            "source_format": self.source_format,
            "parsed_at": self.parsed_at,
            "encoding": self.encoding,
            "metadata": dict(self.metadata),
            "total_count": self.total_count,
            "stations": list(self.stations),
            "signal_types": list(self.signal_types),
        }


@dataclass(frozen=True, slots=True)
class ParseResult:
    """解析结果（统一成功/失败返回）

    成功时 var_table 非 None，errors 为空；
    失败时 var_table 为 None，errors 含失败原因；
    部分成功时 var_table 含已解析条目，errors 含失败行（容错模式）。
    """

    success: bool
    var_table: VarTable | None
    errors: tuple[ParseError, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def error_count(self) -> int:
        """错误数"""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """警告数"""
        return len(self.warnings)

    @property
    def entry_count(self) -> int:
        """已解析条目数（部分成功时也有值）"""
        return 0 if self.var_table is None else self.var_table.total_count

    def to_dict(self) -> dict[str, Any]:
        """转换为可序列化字典（供 JSON 输出）"""
        return {
            "success": self.success,
            "var_table": self.var_table.to_dict() if self.var_table else None,
            "errors": [
                {
                    "line_number": err.line_number,
                    "field": err.field,
                    "message": err.message,
                    "raw_value": err.raw_value,
                }
                for err in self.errors
            ],
            "warnings": list(self.warnings),
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "entry_count": self.entry_count,
        }
