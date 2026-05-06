# -*- coding: utf-8 -*-
"""
变量名解析器

用于从ST源码、GVL文件、IO配置等来源中提取和标准化变量信息。
支持多种PLC品牌的变量格式。
"""
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple
from pathlib import Path

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class VariableRecord:
    """变量记录数据结构"""
    name: str
    address: str = ""
    data_type: str = ""
    category: str = ""          # INPUT/OUTPUT/GLOBAL/LOCAL
    description: str = ""
    unit: str = ""
    min_value: float = None
    max_value: float = None
    initial_value: str = ""
    source_file: str = ""
    line_number: int = 0


class VariableParser:
    """
    变量名解析器

    功能:
    - 从GVL (Global Variable List) 文件中提取变量
    - 从IO配置文件解析地址分配
    - 标准化不同品牌的变量命名格式
    - 变量重复检测
    """

    # IEC地址模式
    RE_IEC_ADDRESS = re.compile(
        r"%(?P<prefix>[IQM])(?P<size>[XBWDL])?"
        r"(?P<base>[A-Za-z]*)?(?P<offset>\d+)"
        r"(?:\.(?P<bit>\d+))?",
    )

    # 变量名规范模式 (匈牙利前缀)
    PREFIX_RULES = {
        "b": "BOOL",         # 布尔
        "n": "INT", "i": "INT",   # 整数
        "r": "REAL", "f": "REAL", # 浮点
        "s": "STRING",       # 字符串
        "t": "TIME", "dt": "DATE_AND_TIME",  # 时间
        "e": "ENUM",         # 枚举
        "arr": "ARRAY",       # 数组
    }

    def __init__(self):
        self._variables: List[VariableRecord] = []

    def parse_gvl_file(self, file_path: str) -> Tuple[int, int]:
        """
        解析GVL文件

        Args:
            file_path: GVL文件路径

        Returns:
            Tuple[int, int]: (成功解析的变量数, 错误数)
        """
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"GVL文件不存在: {file_path}")
            return 0, 1

        try:
            content = path.read_text(encoding="utf-8")
            success_count, error_count = self._parse_gvl_content(content, file_path)
            logger.info(f"GVL解析完成: {path.name} - {success_count} 个变量")
            return success_count, error_count
        except Exception as e:
            logger.exception(f"GVL文件读取失败: {e}")
            return 0, 1

    def _parse_gvl_content(
        self, content: str, source: str
    ) -> Tuple[int, int]:
        """解析GVL内容文本"""
        success_count = 0
        error_count = 0
        lines = content.splitlines()

        # 简化的GVL变量声明正则
        var_decl_re = re.compile(
            r"^\s*(?P<names>[\w,\s]+?)\s*:\s*"
            r"(?P<type>\w+(?:\s*\([^)]*\))?(?:\s*\{.*?\})?)"
            r"(?:\s*:=\s*(?P<init>[^;]*?))?"
            r"\s*(?:\(\*\s*(?P<comment>[^*]*(?:\*(?!)[^*]*)*)\*\))?\s*;",
            re.IGNORECASE,
        )

        for line_idx, line in enumerate(lines, 1):
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith("(*") or line.startswith("//"):
                continue
            # 跳过关键字行
            if any(kw in line.upper() for kw in [
                "VAR_GLOBAL", "END_VAR", "VAR", "END_VAR",
                "PROGRAM", "FUNCTION_BLOCK", "FUNCTION",
            ]):
                continue

            match = var_decl_re.match(line)
            if match:
                names_str = match.group("names").strip()
                data_type = match.group("type") or "UNKNOWN"
                init_val = (match.group("init") or "").strip()
                comment = (match.group("comment") or "").strip()

                for name in [n.strip() for n in names_str.split(",")]:
                    if name and name.isidentifier():
                        self._variables.append(VariableRecord(
                            name=name,
                            data_type=data_type,
                            category="GLOBAL",
                            description=comment,
                            initial_value=init_val,
                            source_file=source,
                            line_number=line_idx,
                        ))
                        success_count += 1
                    elif name:
                        error_count += 1

        return success_count, error_count

    def find_duplicates(self) -> List[Tuple[str, List[str]]]:
        """
        查找重复变量名

        Returns:
            List[Tuple[str, List[str]]]: [(变量名, [出现位置列表])]
        """
        name_map: dict = {}
        for var in self._variables:
            lower_name = var.name.lower()
            if lower_name not in name_map:
                name_map[lower_name] = []
            location = f"{var.source_file}:{var.line_number}"
            name_map[lower_name].append(location)

        duplicates = [
            (name, locations)
            for name, locations in name_map.items()
            if len(locations) > 1
        ]

        if duplicates:
            logger.warning(f"发现 {len(duplicates)} 组重复变量定义")

        return duplicates

    def validate_naming_convention(
        self, prefix_rules: dict = None
    ) -> List[dict]:
        """
        验证变量命名规范 (匈牙利命名法)

        Args:
            prefix_rules: 自定义前缀规则字典，为None时使用内置规则

        Returns:
            List[dict]: 不符合规范的变量列表
        """
        rules = prefix_rules or self.PREFIX_RULES
        violations = []

        for var in self._variables:
            name = var.name
            # 跳过以下划线或特殊字符开头的变量
            if name.startswith("_"):
                continue

            # 检查前缀是否符合规则
            expected_prefixes = list(rules.keys())
            matched_prefix = None

            for prefix in sorted(expected_prefixes, key=len, reverse=True):
                if name.startswith(prefix):
                    matched_prefix = prefix
                    break

            if matched_prefix is None:
                violations.append({
                    "variable": name,
                    "type": var.data_type,
                    "issue": "缺少类型前缀",
                    "location": f"{var.source_file}:{var.line_number}",
                    "suggestion": f"建议使用前缀: {self._suggest_prefix(var.data_type, rules)}",
                })

        if violations:
            logger.info(f"命名规范检查: {len(violations)} 个变量不符合规范")

        return violations

    def _suggest_prefix(self, data_type: str, rules: dict) -> str:
        """根据数据类型推荐前缀"""
        upper_type = data_type.upper().replace(" ", "")
        for prefix, ptype in rules.items():
            if upper_type == ptype.upper() or upper_type.startswith(ptype.upper()):
                return prefix
        return "x"

    def parse_io_address(self, address: str) -> Optional[dict]:
        """
        解析IEC标准IO地址

        Args:
            address: IO地址字符串 (如 "%IX0.0", "%QW64")

        Returns:
            Optional[dict]: 解析结果字典或None
        """
        match = self.RE_IEC_ADDRESS.match(address.strip())
        if not match:
            return None

        size_map = {
            "X": ("BOOL", 1),
            "B": ("BYTE", 8),
            "W": ("WORD", 16),
            "D": ("DWORD", 32),
            "L": ("LWORD", 64),
        }

        prefix = match.group("prefix")
        size_char = match.group("size") or "X"
        base = match.group("base") or ""
        offset = match.group("offset")
        bit = match.group("bit")

        data_type, bits = size_map.get(size_char, ("UNKNOWN", 0))

        direction = {
            "I": "INPUT",
            "Q": "OUTPUT",
            "M": "MEMORY",
        }.get(prefix, "UNKNOWN")

        return {
            "full_address": address,
            "direction": direction,
            "size_prefix": size_char,
            "data_type": data_type,
            "bit_width": bits,
            "base_address": base,
            "byte_offset": int(offset),
            "bit_offset": int(bit) if bit else None,
        }

    @property
    def variables(self) -> List[VariableRecord]:
        """获取已解析的所有变量"""
        return self._variables

    @property
    def variable_count(self) -> int:
        """获取变量总数"""
        return len(self._variables)

    def clear(self):
        """清空已解析的变量列表"""
        self._variables.clear()
