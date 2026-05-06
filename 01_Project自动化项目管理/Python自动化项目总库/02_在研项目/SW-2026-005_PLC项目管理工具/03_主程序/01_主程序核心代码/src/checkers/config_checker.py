# -*- coding: utf-8 -*-
"""
PLC项目配置检查器模块

用于验证 .plc.json 配置文件的完整性和规范性。
基于 907_项目配置规范.md 文档实现，确保配置符合 Siemens LSP 要求。

实现规则:
- CONFIG_001: 必填字段完整性检查
- CONFIG_002: 项目名称格式验证
- CONFIG_003: 版本号格式验证
- CONFIG_004: libraries 字段名正确性检查
- CONFIG_005: 库路径类型检查（必须为相对路径）
- CONFIG_006: 库路径有效性验证
- CONFIG_007: 路径分隔符规范化检查

Usage:
    from src.checkers.config_checker import ConfigChecker

    checker = ConfigChecker()
    violations = checker.check(config_content, file_path=".plc.json", context={"project_path": "/path/to/project"})
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.checkers.base_checker import BaseChecker, Severity, RuleInfo
from src.models.check_result import Violation
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConfigChecker(BaseChecker):
    """
    PLC项目配置文件(.plc.json)检查器

    继承BaseChecker，专门用于验证Siemens LSP的.plc.json配置文件。
    支持通过context参数传入project_path以进行路径验证。

    Attributes:
        _rule_info: 规则元信息
        _enabled: 是否启用

    Example:
        >>> checker = ConfigChecker()
        >>> config_json = '{"name": "DJ-2026-005", "description": "测试", "version": "V1.0.0"}'
        >>> violations = checker.check(
        ...     config_json,
        ...     file_path="/project/.plc.json",
        ...     context={"project_path": "/project"}
        ... )
        >>> print(len(violations))
        0
    """

    # 必填字段列表
    REQUIRED_FIELDS = ["name", "description", "version"]

    # 项目名称正则表达式 (如 DJ-2026-005)
    NAME_PATTERN = re.compile(r"^[A-Z]{2,4}-\d{4}-\d{3}$")

    # 版本号正则表达式 (如 V1.0.0 或 V6.0.0)
    VERSION_PATTERN = re.compile(r"^V\d+\.\d+\.\d+$")

    def __init__(self):
        """
        初始化ConfigChecker

        创建所有7条规则的RuleInfo并初始化基类
        """
        rule_info = RuleInfo(
            rule_id="CONFIG_CHECKER",
            name="PLC项目配置检查器",
            description="验证.plc.json配置文件的完整性和规范性",
            category="config",
            severity=Severity.WARNING,
            tags=["plc", "config", "siemens-lsp", "json"],
        )
        super().__init__(rule_info=rule_info)
        logger.info("ConfigChecker初始化完成")

    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        """
        执行配置文件检查

        对.plc.json内容进行完整的7项规则检查。

        Args:
            source_code: .plc.json文件的文本内容（JSON字符串）
            file_path: 配置文件路径（可选，用于错误定位）
            context: 上下文信息字典，可包含：
                - project_path: 项目根目录路径（用于验证库路径）

        Returns:
            List[Violation]: 发现的违规列表，可能包含：
                - CONFIG_001: 必填字段缺失
                - CONFIG_002: 名称格式错误
                - CONFIG_003: 版本格式错误
                - CONFIG_004: 使用了错误的字段名libraryDirectories
                - CONFIG_005: 使用了绝对路径
                - CONFIG_006: 路径无效或不存在
                - CONFIG_007: 路径分隔符不正确
        """
        violations: List[Violation] = []
        project_path = None

        # 提取上下文中的项目路径
        if context and isinstance(context, dict):
            project_path = context.get("project_path")

        try:
            # 解析JSON
            config_data = json.loads(source_code)

            if not isinstance(config_data, dict):
                violations.append(Violation(
                    rule_id="CONFIG_001",
                    severity=Severity.ERROR,
                    message="配置文件必须是JSON对象（字典）",
                    file_path=file_path,
                    suggestion="确保.plc.json的根元素是JSON对象{}",
                ))
                return violations

            # 执行各项检查
            violations.extend(self._check_required_fields(config_data, file_path))
            violations.extend(self._check_name_format(config_data, file_path))
            violations.extend(self._check_version_format(config_data, file_path))
            violations.extend(self._check_libraries_field_name(config_data, file_path))
            violations.extend(self._check_library_path_type(config_data, file_path, project_path))
            violations.extend(self._check_library_path_validity(config_data, file_path, project_path))
            violations.extend(self._check_path_separator(config_data, file_path))

        except json.JSONDecodeError as e:
            violations.append(Violation(
                rule_id="CONFIG_001",
                severity=Severity.ERROR,
                message=f"JSON解析失败: {str(e)}",
                file_path=file_path,
                line_number=e.lineno if hasattr(e, 'lineno') else 0,
                column=e.colno if hasattr(e, 'colno') else 0,
                suggestion="请检查JSON语法，确保引号、括号、逗号正确",
            ))
            logger.error(f"JSON解析错误: {e}")
        except Exception as e:
            violations.append(Violation(
                rule_id="CONFIG_001",
                severity=Severity.ERROR,
                message=f"配置检查过程中发生异常: {str(e)}",
                file_path=file_path,
                suggestion="请检查配置文件格式或联系技术支持",
            ))
            logger.exception(f"配置检查异常: {e}")

        return violations

    def _check_required_fields(
        self,
        config_data: Dict[str, Any],
        file_path: str,
    ) -> List[Violation]:
        """
        CONFIG_001: 检查必填字段完整性

        验证name、description、version三个必填字段是否存在且非空。

        Args:
            config_data: 已解析的配置字典
            file_path: 文件路径

        Returns:
            List[Violation]: 缺失字段的违规列表
        """
        violations = []

        for field in self.REQUIRED_FIELDS:
            if field not in config_data:
                violations.append(Violation(
                    rule_id="CONFIG_001",
                    severity=Severity.ERROR,
                    message=f"缺少必填字段 '{field}'",
                    file_path=file_path,
                    suggestion=f"在.plc.json中添加 '{field}' 字段",
                ))
                logger.warning(f"缺少必填字段: {field}")
            elif not config_data[field] or (isinstance(config_data[field], str) and not config_data[field].strip()):
                violations.append(Violation(
                    rule_id="CONFIG_001",
                    severity=Severity.ERROR,
                    message=f"必填字段 '{field}' 不能为空",
                    file_path=file_path,
                    suggestion=f"为 '{field}' 字段提供有效值",
                ))
                logger.warning(f"字段值为空: {field}")

        return violations

    def _check_name_format(
        self,
        config_data: Dict[str, Any],
        file_path: str,
    ) -> List[Violation]:
        """
        CONFIG_002: 检查项目名称格式

        验证name字段是否符合项目编号格式（如 DJ-2026-005）。

        Args:
            config_data: 已解析的配置字典
            file_path: 文件路径

        Returns:
            List[Violation]: 格式不符的违规列表
        """
        violations = []

        name = config_data.get("name")
        if name and isinstance(name, str):
            if not self.NAME_PATTERN.match(name):
                violations.append(Violation(
                    rule_id="CONFIG_002",
                    severity=Severity.WARNING,
                    message=f"项目名称格式不符合规范: '{name}'",
                    file_path=file_path,
                    suggestion="项目名称应采用 'XX-YYYY-ZZZ' 格式（如 DJ-2026-005）",
                ))
                logger.warning(f"项目名称格式不规范: {name}")
            else:
                logger.debug(f"项目名称格式正确: {name}")

        return violations

    def _check_version_format(
        self,
        config_data: Dict[str, Any],
        file_path: str,
    ) -> List[Violation]:
        """
        CONFIG_003: 检查版本号格式

        验证version字段是否符合语义化版本号格式（如 V1.0.0）。

        Args:
            config_data: 已解析的配置字典
            file_path: 文件路径

        Returns:
            List[Violation]: 格式不符的违规列表
        """
        violations = []

        version = config_data.get("version")
        if version and isinstance(version, str):
            if not self.VERSION_PATTERN.match(version):
                violations.append(Violation(
                    rule_id="CONFIG_003",
                    severity=Severity.WARNING,
                    message=f"版本号格式不符合规范: '{version}'",
                    file_path=file_path,
                    suggestion="版本号应采用 'V主版本号.次版本号.修订号' 格式（如 V1.0.0, V6.0.0）",
                ))
                logger.warning(f"版本号格式不规范: {version}")
            else:
                logger.debug(f"版本号格式正确: {version}")

        return violations

    def _check_libraries_field_name(
        self,
        config_data: Dict[str, Any],
        file_path: str,
    ) -> List[Violation]:
        """
        CONFIG_004: 检查libraries字段名正确性

        这是关键规则！Siemens LSP只识别 'libraries' 字段，
        不识别 'libraryDirectories'。如果使用了后者，LSP会静默忽略。

        Args:
            config_data: 已解析的配置字典
            file_path: 文件路径

        Returns:
            List[Violation]: 使用了错误字段名的违规列表
        """
        violations = []

        has_wrong_field = "libraryDirectories" in config_data
        has_correct_field = "libraries" in config_data

        if has_wrong_field:
            violations.append(Violation(
                rule_id="CONFIG_004",
                severity=Severity.ERROR,
                message="使用了无效的字段名 'libraryDirectories'",
                file_path=file_path,
                line_number=1,
                column=1,
                suggestion="将 'libraryDirectories' 改为 'libraries'（Siemens LSP只识别 libraries 字段）",
                code_snippet='"libraryDirectories": [...]',
            ))
            logger.error("检测到错误的字段名: libraryDirectories")

        # 如果只有正确的字段，没有问题
        if has_correct_field and not has_wrong_field:
            logger.debug("libraries字段名正确")

        return violations

    def _check_library_path_type(
        self,
        config_data: Dict[str, Any],
        file_path: str,
        project_path: Optional[str],
    ) -> List[Violation]:
        """
        CONFIG_005: 检查库路径类型

        验证libraries中的路径是否为相对路径（不应使用绝对路径）。
        绝对路径会导致跨机器不兼容问题。

        Args:
            config_data: 已解析的配置字典
            file_path: 文件路径
            project_path: 项目根目录路径（可选）

        Returns:
            List[Violation]: 使用了绝对路径的违规列表
        """
        violations = []

        libraries = config_data.get("libraries")
        if not libraries or not isinstance(libraries, list):
            return violations

        for i, lib_path in enumerate(libraries):
            if lib_path and isinstance(lib_path, str):
                # 检测Windows绝对路径 (C:\, D:\ 等)
                if re.match(r'^[A-Za-z]:[/\\]', lib_path):
                    violations.append(Violation(
                        rule_id="CONFIG_005",
                        severity=Severity.WARNING,
                        message=f"库路径使用了Windows绝对路径: '{lib_path}'",
                        file_path=file_path,
                        suggestion="改用相对于.plc.json所在目录的相对路径以提高可移植性",
                    ))
                    logger.warning(f"检测到Windows绝对路径: {lib_path}")

                # 检测Unix/Linux绝对路径 (/path/to/lib)
                elif lib_path.startswith('/'):
                    violations.append(Violation(
                        rule_id="CONFIG_005",
                        severity=Severity.WARNING,
                        message=f"库路径使用了Unix绝对路径: '{lib_path}'",
                        file_path=file_path,
                        suggestion="改用相对于.plc.json所在目录的相对路径以提高可移植性",
                    ))
                    logger.warning(f"检测到Unix绝对路径: {lib_path}")

        return violations

    def _check_library_path_validity(
        self,
        config_data: Dict[str, Any],
        file_path: str,
        project_path: Optional[str],
    ) -> List[Violation]:
        """
        CONFIG_006: 验证库路径有效性

        当提供了project_path时，验证相对路径能否正确解析到实际存在的目录。
        这有助于在部署前发现路径配置错误。

        Args:
            config_data: 已解析的配置字典
            file_path: 文件路径
            project_path: 项目根目录路径（可选，提供时进行路径验证）

        Returns:
            List[Violation]: 路径无效的违规列表
        """
        violations = []

        libraries = config_data.get("libraries")
        if not libraries or not isinstance(libraries, list):
            return violations

        # 如果没有提供project_path，跳过此检查
        if not project_path:
            logger.debug("未提供project_path，跳过路径有效性验证")
            return violations

        plc_json_dir = Path(file_path).parent if file_path else Path(project_path)

        for i, lib_path in enumerate(libraries):
            if lib_path and isinstance(lib_path, str):
                try:
                    # 计算绝对路径
                    # 将正斜杠转换为当前操作系统的路径分隔符
                    normalized_path = lib_path.replace('/', Path.sep)
                    absolute_path = (plc_json_dir / normalized_path).resolve()

                    # 检查路径是否存在
                    if not absolute_path.exists():
                        violations.append(Violation(
                            rule_id="CONFIG_006",
                            severity=Severity.WARNING,
                            message=f"库路径指向不存在的位置: '{lib_path}' (解析为: {absolute_path})",
                            file_path=file_path,
                            suggestion=f"请确认路径 '{lib_path}' 是否正确，或目标目录尚未创建",
                        ))
                        logger.warning(f"库路径不存在: {lib_path} -> {absolute_path}")
                    elif not absolute_path.is_dir():
                        violations.append(Violation(
                            rule_id="CONFIG_006",
                            severity=Severity.WARNING,
                            message=f"库路径不是有效的目录: '{lib_path}'",
                            file_path=file_path,
                            suggestion="libraries中的每个条目都应指向一个目录",
                        ))
                        logger.warning(f"库路径不是目录: {absolute_path}")
                    else:
                        logger.debug(f"库路径有效: {lib_path} -> {absolute_path}")

                except (ValueError, OSError) as e:
                    violations.append(Violation(
                        rule_id="CONFIG_006",
                        severity=Severity.WARNING,
                        message=f"无法解析库路径: '{lib_path}' (错误: {str(e)})",
                        file_path=file_path,
                        suggestion="检查路径格式是否合法",
                    ))
                    logger.error(f"路径解析错误: {lib_path} - {e}")

        return violations

    def _check_path_separator(
        self,
        config_data: Dict[str, Any],
        file_path: str,
    ) -> List[Violation]:
        """
        CONFIG_007: 检查路径分隔符规范化

        根据907规范，libraries中的路径应使用正斜杠(/)作为分隔符。
        虽然Windows系统也支持反斜杠，但为了跨平台兼容性建议统一使用正斜杠。

        Args:
            config_data: 已解析的配置字典
            file_path: 文件路径

        Returns:
            List[Violation]: 使用了反斜杠的违规列表
        """
        violations = []

        libraries = config_data.get("libraries")
        if not libraries or not isinstance(libraries, list):
            return violations

        for i, lib_path in enumerate(libraries):
            if lib_path and isinstance(lib_path, str):
                # 检测反斜杠（排除UNC路径 \\server\share）
                if '\\' in lib_path and not lib_path.startswith('\\\\'):
                    violations.append(Violation(
                        rule_id="CONFIG_007",
                        severity=Severity.INFO,
                        message=f"库路径使用了反斜杠: '{lib_path}'",
                        file_path=file_path,
                        suggestion="建议将反斜杠(\\)替换为正斜杠(/)以确保跨平台兼容性",
                    ))
                    logger.info(f"检测到反斜杠路径: {lib_path}")

        return violations

    def get_all_rule_ids(self) -> List[str]:
        """
        获取此检查器包含的所有规则ID列表

        Returns:
            List[str]: 规则ID列表 ['CONFIG_001', ..., 'CONFIG_007']
        """
        return [
            "CONFIG_001",
            "CONFIG_002",
            "CONFIG_003",
            "CONFIG_004",
            "CONFIG_005",
            "CONFIG_006",
            "CONFIG_007",
        ]

    def get_rule_description(self, rule_id: str) -> Optional[str]:
        """
        获取指定规则的描述信息

        Args:
            rule_id: 规则ID

        Returns:
            Optional[str]: 规则描述，如果rule_id不存在则返回None
        """
        descriptions = {
            "CONFIG_001": "必填字段完整性检查（name, description, version）",
            "CONFIG_002": "项目名称格式验证（XX-YYYY-ZZZ）",
            "CONFIG_003": "版本号格式验证（V主版本.次版本.修订号）",
            "CONFIG_004": "libraries字段名正确性检查（不能是libraryDirectories）",
            "CONFIG_005": "库路径类型检查（必须为相对路径）",
            "CONFIG_006": "库路径有效性验证（路径必须存在）",
            "CONFIG_007": "路径分隔符规范化检查（推荐使用正斜杠）",
        }
        return descriptions.get(rule_id)
