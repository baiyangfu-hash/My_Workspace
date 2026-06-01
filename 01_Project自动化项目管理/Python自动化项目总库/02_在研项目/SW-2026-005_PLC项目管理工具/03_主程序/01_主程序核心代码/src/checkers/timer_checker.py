# -*- coding: utf-8 -*-
"""
定时器规范检查器模块

基于IEC 61131-3标准实现PLC代码中定时器使用的规范检查。
检测TON、TOF、TP等标准定时器的命名、实例化、调用和复位等方面的常见问题。

实现的规则:
    - TIMER_001: 定时器变量命名规范检查
    - TIMER_002: 定时器实例化完整性检查
    - TIMER_003: 定时器调用参数完整性检查
    - TIMER_004: 定时器复位逻辑检查
    - TIMER_005: 定时器嵌套深度限制检查

Author: PLC Code Quality Team
Version: 1.0.0
"""

import re
from typing import List, Dict, Any, Optional, Tuple

from src.checkers.base_checker import BaseChecker, RuleInfo, Severity
from src.models.check_result import Violation
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TimerChecker(BaseChecker):
    """
    定时器规范检查器

    检查PLC结构化文本(ST)代码中定时器的使用是否符合规范，
    包括命名约定、实例化完整性、参数传递、复位逻辑等方面。

    支持的定时器类型:
        - TON (导通延时定时器)
        - TOF (断开延时定时器)
        - TP (脉冲定时器)

    Attributes:
        _rule_infos: 所有规则的元信息字典
        _timer_patterns: 定时器相关的正则表达式模式
        _max_nesting_depth: 最大允许的嵌套深度（默认3层）
    """

    # 定义支持的定时器类型
    TIMER_TYPES = ["TON", "TOF", "TP"]

    # 定时器命名前缀映射
    TIMER_PREFIXES = {
        "TON": "ton_",
        "TOF": "tof_",
        "TP": "tp_",
    }

    def __init__(self):
        """
        初始化定时器检查器

        注册所有定时器相关规则并编译正则表达式模式
        """
        # 初始化规则信息
        rule_info = RuleInfo(
            rule_id="TIMER_CHECKER",
            name="定时器规范检查器",
            description="检查PLC代码中定时器的使用规范",
            category="timer",
            severity=Severity.WARNING,
            version="1.0.0",
            author="PLC Code Quality Team",
            tags=["timer", "TON", "TOF", "TP", "IEC61131"],
        )

        super().__init__(rule_info)

        # 初始化所有子规则的详细信息
        self._rule_infos: Dict[str, RuleInfo] = {
            "TIMER_001": RuleInfo(
                rule_id="TIMER_001",
                name="定时器变量命名规范",
                description=(
                    "定时器变量名应使用有意义的命名前缀: "
                    "TON类型使用'ton_'前缀, TOF类型使用'tof_'前缀, "
                    "TP类型使用'tp_'前缀, 后跟描述性名称"
                ),
                category="timer",
                severity=Severity.WARNING,
                enabled=True,
                version="1.0.0",
                tags=["naming", "convention"],
            ),
            "TIMER_002": RuleInfo(
                rule_id="TIMER_002",
                name="定时器实例化完整性",
                description=(
                    "定时器实例声明必须包含PT(预设时间)和ET(经过时间)参数, "
                    "缺少必要参数可能导致运行时错误"
                ),
                category="timer",
                severity=Severity.ERROR,
                enabled=True,
                version="1.0.0",
                tags=["instantiation", "completeness"],
            ),
            "TIMER_003": RuleInfo(
                rule_id="TIMER_003",
                name="定时器调用参数完整性",
                description=(
                    "调用TON/TOF/TP功能块时必须提供IN(输入)和PT(预设时间)参数, "
                    "缺少必要参数会导致功能块无法正常工作"
                ),
                category="timer",
                severity=Severity.ERROR,
                enabled=True,
                version="1.0.0",
                tags=["invocation", "parameters"],
            ),
            "TIMER_004": RuleInfo(
                rule_id="TIMER_004",
                name="定时器复位逻辑检查",
                description=(
                    "定时器在完成计时任务后应在适当时机进行复位(IN:=FALSE), "
                    "避免定时器状态残留影响后续逻辑"
                ),
                category="timer",
                severity=Severity.WARNING,
                enabled=True,
                version="1.0.0",
                tags=["reset", "logic"],
            ),
            "TIMER_005": RuleInfo(
                rule_id="TIMER_005",
                name="定时器嵌套深度限制",
                description=(
                    "定时器嵌套调用深度不应超过3层, "
                    "过深的嵌套会增加代码复杂度, 降低可读性和可维护性"
                ),
                category="timer",
                severity=Severity.WARNING,
                enabled=True,
                version="1.0.0",
                tags=["nesting", "complexity"],
            ),
        }

        # 编译正则表达式模式
        self._patterns = self._compile_patterns()

        # 配置参数
        self._max_nesting_depth: int = 3

        logger.info("定时器规范检查器初始化完成")

    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """
        编译所有需要的正则表达式模式

        Returns:
            Dict[str, re.Pattern]: 编译后的正则表达式模式字典
        """
        patterns = {}

        # 模式1: 定时器变量声明 (如: ton_Delay : TON;)
        patterns["timer_declaration"] = re.compile(
            r'(\w+)\s*:\s*(TON|TOF|TP)\s*;',
            re.IGNORECASE | re.MULTILINE
        )

        # 模式2: 带参数的定时器实例化 (如: ton_Delay : TON := (PT := T#5s);)
        patterns["timer_instantiation"] = re.compile(
            r'(\w+)\s*:\s*(TON|TOF|TP)\s*:=\s*\(([^)]*)\)',
            re.IGNORECASE | re.MULTILINE
        )

        # 模式3: 定时器功能块调用 (如: ton_Delay(IN := xStart, PT := T#5s);)
        patterns["timer_invocation"] = re.compile(
            r'(TON|TOF|TP)\s*\(\s*([^)]*)\s*\)',
            re.IGNORECASE | re.MULTILINE
        )

        # 模式4: 定时器变量赋值/复位 (如: ton_Delay(IN := FALSE);)
        patterns["timer_assignment"] = re.compile(
            r'((?:ton_|tof_|tp_)\w*)\s*\(\s*([^)]*)\s*\)',
            re.IGNORECASE | re.MULTILINE
        )

        # 模式5: IN参数设置 (用于检测复位)
        patterns["in_parameter"] = re.compile(
            r'IN\s*:=\s*(TRUE|FALSE)',
            re.IGNORECASE
        )

        # 模式6: PT参数设置
        patterns["pt_parameter"] = re.compile(
            r'PT\s*:=\s*\S+',
            re.IGNORECASE
        )

        # 模式7: ET参数设置
        patterns["et_parameter"] = re.compile(
            r'ET\s*:=\s*\w+',
            re.IGNORECASE
        )

        return patterns

    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        """
        执行定时器规范检查

        对源代码执行所有已启用的定时器规则检查。

        Args:
            source_code: 待检查的ST源代码
            file_path: 源文件路径（可选）
            context: 上下文信息（可选）

        Returns:
            List[Violation]: 发现的所有违规记录列表
        """
        violations: List[Violation] = []

        if not source_code or not source_code.strip():
            logger.debug("源代码为空，跳过检查")
            return violations

        logger.debug(f"开始执行定时器规范检查: {file_path}")

        # 执行各项规则检查
        violations.extend(self._check_timer_001(source_code, file_path))
        violations.extend(self._check_timer_002(source_code, file_path))
        violations.extend(self._check_timer_003(source_code, file_path))
        violations.extend(self._check_timer_004(source_code, file_path))
        violations.extend(self._check_timer_005(source_code, file_path))

        logger.info(f"定时器检查完成，发现 {len(violations)} 个违规")

        return violations

    def _check_timer_001(
        self, source_code: str, file_path: str
    ) -> List[Violation]:
        """
        规则TIMER_001: 定时器变量命名规范检查

        检查所有定时器变量声明是否使用了正确的命名前缀:
        - TON类型应使用 'ton_' 前缀
        - TOF类型应使用 'tof_' 前缀
        - TP类型应使用 'tp_' 前缀

        Args:
            source_code: 源代码
            file_path: 文件路径

        Returns:
            List[Violation]: 命名不规范导致的违规列表
        """
        violations = []
        rule_info = self._rule_infos["TIMER_001"]

        if not rule_info.enabled:
            return violations

        # 查找所有定时器声明
        for match in self._patterns["timer_declaration"].finditer(source_code):
            var_name = match.group(1).strip()
            timer_type = match.group(2).upper()
            line_num = source_code[:match.start()].count('\n') + 1

            # 获取期望的前缀
            expected_prefix = self.TIMER_PREFIXES.get(timer_type, "")

            # 检查是否使用了正确的前缀
            if expected_prefix and not var_name.lower().startswith(expected_prefix):
                violation = Violation(
                    rule_id=rule_info.rule_id,
                    severity=rule_info.severity,
                    message=(
                        f"定时器变量 '{var_name}' 命名不符合规范: "
                        f"{timer_type}类型应使用 '{expected_prefix}' 前缀"
                    ),
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start(1) - source_code.rfind('\n', 0, match.start(1)),
                    suggestion=(
                        f"建议将 '{var_name}' 重命名为 "
                        f"'{expected_prefix}{var_name}'"
                    ),
                    code_snippet=match.group(0),
                )
                violations.append(violation)
                logger.debug(f"发现TIMER_001违规: {violation.message}")

        for match in self._patterns["timer_instantiation"].finditer(source_code):
            var_name = match.group(1).strip()
            timer_type = match.group(2).upper()
            line_num = source_code[:match.start()].count('\n') + 1

            expected_prefix = self.TIMER_PREFIXES.get(timer_type, "")

            if expected_prefix and not var_name.lower().startswith(expected_prefix):
                violation = Violation(
                    rule_id=rule_info.rule_id,
                    severity=rule_info.severity,
                    message=(
                        f"定时器变量 '{var_name}' 命名不符合规范: "
                        f"{timer_type}类型应使用 '{expected_prefix}' 前缀"
                    ),
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start(1) - source_code.rfind('\n', 0, match.start(1)),
                    suggestion=(
                        f"建议将 '{var_name}' 重命名为 "
                        f"'{expected_prefix}{var_name}'"
                    ),
                    code_snippet=match.group(0),
                )
                violations.append(violation)
                logger.debug(f"发现TIMER_001违规: {violation.message}")

        return violations

    def _check_timer_002(
        self, source_code: str, file_path: str
    ) -> List[Violation]:
        """
        规则TIMER_002: 定时器实例化完整性检查

        检查带初始值的定时器实例化是否包含必要的PT和ET参数。
        这是ERROR级别的规则，因为缺少参数会导致运行时错误。

        Args:
            source_code: 源代码
            file_path: 文件路径

        Returns:
            List[Violation]: 实例化不完整的违规列表
        """
        violations = []
        rule_info = self._rule_infos["TIMER_002"]

        if not rule_info.enabled:
            return violations

        # 查找所有带参数的定时器实例化
        for match in self._patterns["timer_instantiation"].finditer(source_code):
            var_name = match.group(1).strip()
            timer_type = match.group(2).upper()
            params_str = match.group(3).strip()
            line_num = source_code[:match.start()].count('\n') + 1

            # 检查是否包含PT参数
            has_pt = bool(self._patterns["pt_parameter"].search(params_str))

            # 检查是否包含ET参数
            has_et = bool(self._patterns["et_parameter"].search(params_str))

            # 收集缺失的参数
            missing_params = []
            if not has_pt:
                missing_params.append("PT(预设时间)")
            if not has_et:
                missing_params.append("ET(经过时间)")

            if missing_params:
                violation = Violation(
                    rule_id=rule_info.rule_id,
                    severity=rule_info.severity,
                    message=(
                        f"定时器 '{var_name}' ({timer_type}) 实例化不完整, "
                        f"缺少必要参数: {', '.join(missing_params)}"
                    ),
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start(1) - source_code.rfind('\n', 0, match.start(1)),
                    suggestion=(
                        f"请在实例化时添加缺失的参数, 例如: "
                        f"{var_name} : {timer_type} := (PT := T#5s, ET := tElapsed);"
                    ),
                    code_snippet=match.group(0),
                )
                violations.append(violation)
                logger.debug(f"发现TIMER_002违规: {violation.message}")

        return violations

    def _check_timer_003(
        self, source_code: str, file_path: str
    ) -> List[Violation]:
        """
        规则TIMER_003: 定时器调用参数完整性检查

        检查定时器功能块的调用是否提供了必要的IN和PT参数。
        缺少这些参数会导致功能块无法正常工作。

        Args:
            source_code: 源代码
            file_path: 文件路径

        Returns:
            List[Violation]: 调用参数不完整的违规列表
        """
        violations = []
        rule_info = self._rule_infos["TIMER_003"]

        if not rule_info.enabled:
            return violations

        # 查找所有定时器功能块调用（排除声明语句中的调用）
        for match in self._patterns["timer_invocation"].finditer(source_code):
            timer_type = match.group(1).upper()
            params_str = match.group(2).strip()
            line_num = source_code[:match.start()].count('\n') + 1

            # 排除实例化语句中的参数（形如 xxx := (...) 的形式）
            start_pos = max(0, match.start() - 20)
            preceding_text = source_code[start_pos:match.start()]
            if ':=' in preceding_text and ('TON' in preceding_text.upper() or
                                              'TOF' in preceding_text.upper() or
                                              'TP' in preceding_text.upper()):
                continue

            # 检查IN参数
            has_in = bool(re.search(r'IN\s*:=\s*\S+', params_str, re.IGNORECASE))

            # 检查PT参数
            has_pt = bool(self._patterns["pt_parameter"].search(params_str))

            # 收集缺失的参数
            missing_params = []
            if not has_in:
                missing_params.append("IN(输入信号)")
            if not has_pt:
                missing_params.append("PT(预设时间)")

            if missing_params:
                violation = Violation(
                    rule_id=rule_info.rule_id,
                    severity=rule_info.severity,
                    message=(
                        f"{timer_type} 功能块调用缺少必要参数: "
                        f"{', '.join(missing_params)}"
                    ),
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start() - source_code.rfind('\n', 0, match.start()),
                    suggestion=(
                        f"请补充必要的参数, 例如: "
                        f"{timer_type}(IN := bCondition, PT := T#5s);"
                    ),
                    code_snippet=match.group(0),
                )
                violations.append(violation)
                logger.debug(f"发现TIMER_003违规: {violation.message}")

        timer_var_names = set()
        for m in self._patterns["timer_declaration"].finditer(source_code):
            timer_var_names.add(m.group(1).strip())
        for m in self._patterns["timer_instantiation"].finditer(source_code):
            timer_var_names.add(m.group(1).strip())

        for match in self._patterns["timer_assignment"].finditer(source_code):
            var_name = match.group(1).strip()
            params_str = match.group(2).strip()
            line_num = source_code[:match.start()].count('\n') + 1

            start_pos = max(0, match.start() - 30)
            preceding_text = source_code[start_pos:match.start()]
            if ':=' in preceding_text:
                continue

            in_match = re.search(r'IN\s*:=\s*(TRUE|FALSE)', params_str, re.IGNORECASE)
            is_reset = in_match and in_match.group(1).upper() == 'FALSE'

            has_in = bool(re.search(r'IN\s*:=\s*\S+', params_str, re.IGNORECASE))
            has_pt = bool(self._patterns["pt_parameter"].search(params_str))

            missing_params = []
            if not has_in:
                missing_params.append("IN(输入信号)")
            if not has_pt and not is_reset:
                missing_params.append("PT(预设时间)")

            if missing_params:
                violation = Violation(
                    rule_id=rule_info.rule_id,
                    severity=rule_info.severity,
                    message=(
                        f"定时器 '{var_name}' 调用缺少必要参数: "
                        f"{', '.join(missing_params)}"
                    ),
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start(1) - source_code.rfind('\n', 0, match.start(1)),
                    suggestion=(
                        f"请补充必要的参数, 例如: "
                        f"{var_name}(IN := bCondition, PT := T#5s);"
                    ),
                    code_snippet=match.group(0),
                )
                violations.append(violation)
                logger.debug(f"发现TIMER_003违规: {violation.message}")

        general_call_pattern = re.compile(
            r'(\w+)\s*\(\s*([^)]*)\s*\)',
            re.IGNORECASE | re.MULTILINE
        )

        for match in general_call_pattern.finditer(source_code):
            var_name = match.group(1).strip()
            params_str = match.group(2).strip()
            line_num = source_code[:match.start()].count('\n') + 1

            if var_name.upper() in ('TON', 'TOF', 'TP'):
                continue

            if var_name.lower().startswith(('ton_', 'tof_', 'tp_')):
                continue

            if var_name not in timer_var_names:
                continue

            start_pos = max(0, match.start() - 30)
            preceding_text = source_code[start_pos:match.start()]
            if ':=' in preceding_text:
                continue

            in_match = re.search(r'IN\s*:=\s*(TRUE|FALSE)', params_str, re.IGNORECASE)
            is_reset = in_match and in_match.group(1).upper() == 'FALSE'

            has_in = bool(re.search(r'IN\s*:=\s*\S+', params_str, re.IGNORECASE))
            has_pt = bool(self._patterns["pt_parameter"].search(params_str))

            missing_params = []
            if not has_in:
                missing_params.append("IN(输入信号)")
            if not has_pt and not is_reset:
                missing_params.append("PT(预设时间)")

            if missing_params:
                violation = Violation(
                    rule_id=rule_info.rule_id,
                    severity=rule_info.severity,
                    message=(
                        f"定时器 '{var_name}' 调用缺少必要参数: "
                        f"{', '.join(missing_params)}"
                    ),
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start(1) - source_code.rfind('\n', 0, match.start(1)),
                    suggestion=(
                        f"请补充必要的参数, 例如: "
                        f"{var_name}(IN := bCondition, PT := T#5s);"
                    ),
                    code_snippet=match.group(0),
                )
                violations.append(violation)
                logger.debug(f"发现TIMER_003违规: {violation.message}")

        return violations

    def _check_timer_004(
        self, source_code: str, file_path: str
    ) -> List[Violation]:
        """
        规则TIMER_004: 定时器复位逻辑检查

        检查定时器在使用后是否有适当的复位操作(IN:=FALSE)。
        未复位的定时器可能影响后续控制逻辑的正确性。

        注意: 此规则采用启发式方法，通过分析代码中定时器的使用模式来判断
        是否存在潜在的复位遗漏问题。

        Args:
            source_code: 源代码
            file_path: 文件路径

        Returns:
            List[Violation]: 可能缺少复位的违规列表
        """
        violations = []
        rule_info = self._rule_infos["TIMER_004"]

        if not rule_info.enabled:
            return violations

        # 收集所有定时器变量及其使用情况
        timer_usages: Dict[str, Dict] = {}

        # 查找所有定时器声明
        for match in self._patterns["timer_declaration"].finditer(source_code):
            var_name = match.group(1).strip()
            timer_type = match.group(2).upper()

            timer_usages[var_name] = {
                "type": timer_type,
                "declared_at": source_code[:match.start()].count('\n') + 1,
                "has_reset": False,
                "in_true_count": 0,
                "invocations": [],
            }

        for match in self._patterns["timer_instantiation"].finditer(source_code):
            var_name = match.group(1).strip()
            timer_type = match.group(2).upper()

            if var_name not in timer_usages:
                timer_usages[var_name] = {
                    "type": timer_type,
                    "declared_at": source_code[:match.start()].count('\n') + 1,
                    "has_reset": False,
                    "in_true_count": 0,
                    "invocations": [],
                }

        for match in self._patterns["timer_assignment"].finditer(source_code):
            var_name = match.group(1)
            params_str = match.group(2).strip()
            line_num = source_code[:match.start()].count('\n') + 1

            if var_name in timer_usages:
                if re.search(r'IN\s*:=\s*TRUE', params_str, re.IGNORECASE):
                    timer_usages[var_name]["in_true_count"] += 1
                    timer_usages[var_name]["invocations"].append({
                        "line": line_num,
                        "is_reset": False,
                    })

                if re.search(r'IN\s*:=\s*FALSE', params_str, re.IGNORECASE):
                    timer_usages[var_name]["has_reset"] = True
                    if timer_usages[var_name]["invocations"]:
                        timer_usages[var_name]["invocations"][-1]["is_reset"] = True

        general_call_pattern = re.compile(
            r'(\w+)\s*\(\s*([^)]*)\s*\)',
            re.IGNORECASE | re.MULTILINE
        )

        for match in general_call_pattern.finditer(source_code):
            var_name = match.group(1).strip()
            params_str = match.group(2).strip()
            line_num = source_code[:match.start()].count('\n') + 1

            if var_name.upper() in ('TON', 'TOF', 'TP'):
                continue

            if var_name.lower().startswith(('ton_', 'tof_', 'tp_')):
                continue

            if var_name not in timer_usages:
                continue

            if re.search(r'IN\s*:=\s*TRUE', params_str, re.IGNORECASE):
                timer_usages[var_name]["in_true_count"] += 1
                timer_usages[var_name]["invocations"].append({
                    "line": line_num,
                    "is_reset": False,
                })

            if re.search(r'IN\s*:=\s*FALSE', params_str, re.IGNORECASE):
                timer_usages[var_name]["has_reset"] = True
                if timer_usages[var_name]["invocations"]:
                    timer_usages[var_name]["invocations"][-1]["is_reset"] = True

        # 检查每个定时器是否有复位逻辑
        for var_name, usage_info in timer_usages.items():
            # 如果定时器被激活过但没有复位
            if usage_info["in_true_count"] > 0 and not usage_info["has_reset"]:
                # 获取最后一次激活的行号
                last_activation_line = (
                    usage_info["invocations"][-1]["line"]
                    if usage_info["invocations"]
                    else usage_info["declared_at"]
                )

                violation = Violation(
                    rule_id=rule_info.rule_id,
                    severity=rule_info.severity,
                    message=(
                        f"定时器 '{var_name}' ({usage_info['type']}) 可能缺少复位逻辑, "
                        f"检测到 {usage_info['in_true_count']} 次激活但未发现复位操作"
                    ),
                    file_path=file_path,
                    line_number=last_activation_line,
                    suggestion=(
                        f"建议在适当的时机对 '{var_name}' 进行复位: "
                        f"{var_name}(IN := FALSE);"
                    ),
                )
                violations.append(violation)
                logger.debug(f"发现TIMER_004违规: {violation.message}")

        return violations

    def _check_timer_005(
        self, source_code: str, file_path: str
    ) -> List[Violation]:
        """
        规则TIMER_005: 定时器嵌套深度限制检查

        检查定时器调用的嵌套深度是否超过允许的最大值（默认3层）。
        过深的嵌套会显著增加代码复杂度，降低可读性和可维护性。

        使用括号匹配算法来计算嵌套深度。

        Args:
            source_code: 源代码
            file_path: 文件路径

        Returns:
            List[Violation]: 嵌套深度超限的违规列表
        """
        violations = []
        rule_info = self._rule_infos["TIMER_005"]

        if not rule_info.enabled:
            return violations

        lines = source_code.split('\n')
        nesting_stack: List[Tuple[int, int, str]] = []  # (line, col, timer_type)

        for line_idx, line in enumerate(lines, start=1):
            i = 0
            while i < len(line):
                # 查找定时器调用开始
                timer_match = re.match(
                    r'(TON|TOF|TP)\s*\(',
                    line[i:],
                    re.IGNORECASE
                )

                if timer_match:
                    timer_type = timer_match.group(1).upper()
                    col = i + 1

                    # 将此定时器压入栈
                    nesting_stack.append((line_idx, col, timer_type))

                    # 计算当前嵌套深度
                    current_depth = len(nesting_stack)

                    if current_depth > self._max_nesting_depth:
                        violation = Violation(
                            rule_id=rule_info.rule_id,
                            severity=rule_info.severity,
                            message=(
                                f"{timer_type} 定时器嵌套深度 ({current_depth}) "
                                f"超过最大限制 ({self._max_nesting_depth}), "
                                f"建议简化逻辑或拆分为独立的功能块"
                            ),
                            file_path=file_path,
                            line_number=line_idx,
                            column=col,
                            suggestion=(
                                f"建议将深层嵌套的定时器逻辑提取为独立的子程序或FB, "
                                f"以降低嵌套复杂度"
                            ),
                            code_snippet=line.strip(),
                        )
                        violations.append(violation)
                        logger.debug(f"发现TIMER_005违规: {violation.message}")

                    i += timer_match.end()
                else:
                    # 检查右括号（表示一个定时器调用结束）
                    if line[i] == ')':
                        if nesting_stack:
                            nesting_stack.pop()
                    i += 1

        return violations

    def get_rule_infos(self) -> Dict[str, RuleInfo]:
        """
        获取所有子规则的详细信息

        Returns:
            Dict[str, RuleInfo]: 规则ID到RuleInfo的映射
        """
        return self._rule_infos.copy()

    def get_rule_info_by_id(self, rule_id: str) -> Optional[RuleInfo]:
        """
        根据规则ID获取规则信息

        Args:
            rule_id: 规则ID（如 TIMER_001）

        Returns:
            Optional[RuleInfo]: 规则信息，不存在时返回None
        """
        return self._rule_infos.get(rule_id)

    def set_max_nesting_depth(self, depth: int) -> None:
        """
        设置最大允许的嵌套深度

        Args:
            depth: 最大嵌套深度（必须大于0）

        Raises:
            ValueError: 如果depth不是正整数
        """
        if not isinstance(depth, int) or depth <= 0:
            raise ValueError(f"嵌套深度必须是正整数, 当前值: {depth}")

        old_value = self._max_nesting_depth
        self._max_nesting_depth = depth
        logger.info(f"定时器最大嵌套深度已更新: {old_value} -> {depth}")

    def enable_rule(self, rule_id: str) -> bool:
        """
        启用指定的子规则

        Args:
            rule_id: 规则ID（如 TIMER_001）

        Returns:
            bool: 操作成功返回True，规则ID无效返回False
        """
        if rule_id in self._rule_infos:
            self._rule_infos[rule_id].enabled = True
            logger.info(f"启用规则: {rule_id}")
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """
        禁用指定的子规则

        Args:
            rule_id: 规则ID（如 TIMER_001）

        Returns:
            bool: 操作成功返回True，规则ID无效返回False
        """
        if rule_id in self._rule_infos:
            self._rule_infos[rule_id].enabled = False
            logger.info(f"禁用规则: {rule_id}")
            return True
        return False

    def __repr__(self) -> str:
        """返回检查器的字符串表示"""
        enabled_rules = sum(
            1 for info in self._rule_infos.values() if info.enabled
        )
        return (
            f"<{self.__class__.__name__} "
            f"(id={self._rule_info.rule_id}, "
            f"name={self._rule_info.name}, "
            f"rules={len(self._rule_infos)}, "
            f"enabled={enabled_rules})>"
        )
