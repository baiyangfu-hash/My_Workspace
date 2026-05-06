# -*- coding: utf-8 -*-
"""
801规范校验器

提供针对PLC工程文档和代码的规范校验功能。
基于801系列标准文档的规则定义进行自动化检查。

注意: 当前为基础框架，具体校验规则待后续迭代完善。
"""
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class CheckSeverity(Enum):
    """检查项严重程度"""
    ERROR = "error"       # 错误 - 必须修复
    WARNING = "warning"   # 警告 - 建议修复
    INFO = "info"         # 信息 - 提示性内容


@dataclass
class CheckResultItem:
    """单个检查结果项"""
    rule_id: str
    rule_name: str
    severity: CheckSeverity
    passed: bool
    message: str
    location: str = ""
    suggestion: str = ""


@dataclass
class CheckReport:
    """完整检查报告"""
    check_name: str
    items: List[CheckResultItem]
    total_count: int = 0
    pass_count: int = 0
    fail_count: int = 0
    warning_count: int = 0

    def __post_init__(self):
        self.total_count = len(self.items)
        self.pass_count = sum(1 for i in self.items if i.passed)
        self.fail_count = sum(
            1 for i in self.items
            if not i.passed and i.severity == CheckSeverity.ERROR
        )
        self.warning_count = sum(
            1 for i in self.items
            if not i.passed and i.severity == CheckSeverity.WARNING
        )


class SpecValidator801:
    """
    801规范校验器

    校验范围:
    - 文档命名规范 (编号格式、版本号格式等)
    - ST代码命名规范 (匈牙利前缀、POU命名等)
    - 变量声明规范 (注释完整性、类型使用等)
    - IO地址分配规范 (地址冲突检测等)
    """

    # 文档命名规范正则
    RE_DOC_NAME = re.compile(
        r"^\d{2,3}-[\u4e00-\u9fa5_a-zA-Z]+-V\d+\.\d+\.\d+\.md$"
    )

    # 项目编号规范正则
    RE_PROJECT_CODE = re.compile(r"^[A-Z]{2}-\d{4}-\d{3}$")

    # 版本号规范正则
    RE_VERSION = re.compile(r"^V\d+\.\d+\.\d+$")

    # 变量名前缀规则
    VAR_PREFIX_RULES = {
        "BOOL": ["b"],
        "INT": ["n", "i"],
        "DINT": ["n", "i", "di"],
        "REAL": ["r", "f"],
        "STRING": ["s", "str"],
        "TIME": ["t", "tm"],
        "DATE_AND_TIME": ["dt"],
        "WORD": ["w"],
        "DWORD": ["dw"],
    }

    @classmethod
    def validate_document_name(cls, file_name: str) -> CheckResultItem:
        """校验文档命名是否符合801规范"""
        is_valid = bool(cls.RE_DOC_NAME.match(file_name))

        return CheckResultItem(
            rule_id="DOC-001",
            rule_name="文档命名规范",
            severity=CheckSeverity.ERROR,
            passed=is_valid,
            message=(
                f"文档名 '{file_name}' "
                f"{'符合' if is_valid else '不符合'}801命名规范"
                f"(格式: XX-名称-Vx.x.x.md)"
                if not is_valid else ""
            ),
            location=file_name,
            suggestion=(
                "请使用格式: 序号-中文名称-V版本号.md\n"
                "示例: 01-需求规格说明书-V1.0.0.md"
            ) if not is_valid else "",
        )

    @classmethod
    def validate_version_format(cls, version: str) -> CheckResultItem:
        """校验版本号格式"""
        is_valid = bool(cls.RE_VERSION.match(version))

        return CheckResultItem(
            rule_id="DOC-002",
            rule_name="版本号格式",
            severity=CheckSeverity.WARNING,
            passed=is_valid,
            message=(
                f"版本号 '{version}' 格式"
                f"{'正确' if is_valid else '错误'}"
            ),
            suggestion="版本号格式应为 V主版本.次版本.修订号 (如 V1.0.0)"
            if not is_valid else "",
        )

    @classmethod
    def validate_variable_naming(
        cls, var_name: str, data_type: str
    ) -> CheckResultItem:
        """
        校验变量命名规范 (匈牙利前缀)

        Args:
            var_name: 变量名称
            data_type: 数据类型

        Returns:
            CheckResultItem: 检查结果
        """
        upper_type = data_type.upper().replace(" ", "")
        valid_prefixes = cls.VAR_PREFIX_RULES.get(upper_type, [])

        if not valid_prefixes:
            # 未知类型，跳过检查
            return CheckResultItem(
                rule_id="VAR-001",
                rule_name="变量前缀规范",
                severity=CheckSeverity.INFO,
                passed=True,
                message=f"变量 '{var_name}': 类型 '{data_type}' 无预定义前缀规则",
            )

        has_valid_prefix = any(
            var_name.lower().startswith(p.lower())
            for p in valid_prefixes
        )

        prefix_str = "/".join(valid_prefixes)

        return CheckResultItem(
            rule_id="VAR-001",
            rule_name="变量前缀规范",
            severity=CheckSeverity.WARNING,
            passed=has_valid_prefix,
            message=(
                f"变量 '{var_name}' ({data_type}): "
                f"{'符合' if has_valid_prefix else '未符合'}前缀规范"
                f"[建议前缀: {prefix_str}]"
            ),
            suggestion=f"建议将变量名改为: "
                       f"{valid_prefixes[0]}{var_name}"
            if not has_valid_prefix else "",
        )

    @classmethod
    def validate_io_address_conflict(
        cls, io_list: List[Dict[str, str]]
    ) -> List[CheckResultItem]:
        """
        检测IO地址冲突

        Args:
            io_list: IO信息列表，每项包含 address 字段

        Returns:
            List[CheckResultItem]: 冲突检测结果列表
        """
        results = []
        seen_addresses: Dict[str, str] = {}

        for io_item in io_list:
            addr = io_item.get("address", "").strip()
            name = io_item.get("name", "未知")

            if addr and addr in seen_addresses:
                results.append(CheckResultItem(
                    rule_id="IO-001",
                    rule_name="IO地址冲突检测",
                    severity=CheckSeverity.ERROR,
                    passed=False,
                    message=(
                        f"IO地址冲突: '{addr}' 同时被 "
                        f"'{seen_addresses[addr]}' 和 '{name}' 使用"
                    ),
                    location=addr,
                    suggestion="请修改其中一个变量的IO地址以消除冲突",
                ))
            elif addr:
                seen_addresses[addr] = name

        if not results:
            results.append(CheckResultItem(
                rule_id="IO-001",
                rule_name="IO地址冲突检测",
                severity=CheckSeverity.INFO,
                passed=True,
                message=f"共 {len(io_list)} 个IO地址，无冲突",
            ))

        return results

    @classmethod
    def run_full_check(cls, project_data: Dict[str, Any]) -> CheckReport:
        """
        运行完整的801规范校验

        Args:
            project_data: 项目数据字典

        Returns:
            CheckReport: 完整的检查报告
        """
        items: List[CheckResultItem] = []

        # 校验项目编号
        code = project_data.get("code", "")
        items.append(CheckResultItem(
            rule_id="PROJ-001",
            rule_name="项目编号格式",
            severity=CheckSeverity.WARNING,
            passed=bool(cls.RE_PROJECT_CODE.match(code)),
            message=f"项目编号: {code}",
        ))

        # 校验文档列表
        documents = project_data.get("documents", [])
        for doc in documents:
            doc_name = doc.get("name", "")
            items.append(cls.validate_document_name(doc_name))
            version = doc.get("version", "")
            items.append(cls.validate_version_format(version))

        report = CheckReport(check_name="801规范全面检查", items=items)

        logger.info(
            f"801规范校验完成: "
            f"{report.pass_count}/{report.total_count} 通过, "
            f"{report.fail_count} 错误, "
            f"{report.warning_count} 警告"
        )
        return report
