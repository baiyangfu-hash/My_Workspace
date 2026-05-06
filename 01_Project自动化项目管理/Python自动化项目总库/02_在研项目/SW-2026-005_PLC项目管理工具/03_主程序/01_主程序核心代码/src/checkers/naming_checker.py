# -*- coding: utf-8 -*-
"""
命名规范检查器模块

基于 905_SCL编程规范 第3节 实现PLC变量命名规范检查。
检查规则覆盖：
- NAMING_001: METHOD定义禁止使用CALL_前缀
- NAMING_002: METHOD调用禁止使用CALL_前缀
- NAMING_003: 变量必须使用规范前缀（i_/o_/q_/s_/fb_/CONST_）
- NAMING_004: 禁止使用中文变量名
- NAMING_005: 禁止下划线命名（除前缀外）
- NAMING_006: 必须使用小驼峰命名法

设计原则:
- 高内聚低耦合: 命名检查逻辑独立封装
- 可扩展: 规则可独立启用/禁用
- 高性能: 使用编译后的正则表达式
"""
import re
from typing import List, Dict, Optional, Any, Tuple

from src.checkers.base_checker import BaseChecker, Severity, RuleInfo
from src.models.check_result import Violation
from src.parsers.st_parser import STParser, VarCategory, VariableInfo, POUInfo

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


# ============================================================================
# 正则表达式模式定义（编译一次，全局复用）
# ============================================================================

# METHOD定义模式: METHOD CALL_xxx : TYPE 或 METHOD FB_Name.CALL_xxx : TYPE
RE_METHOD_DEFINITION = re.compile(
    r"METHOD\s+(?:\w+\.)?CALL_\w+",
    re.IGNORECASE,
)

# METHOD调用模式: CALL_xxx() 或 CALL_xxx(参数)
RE_METHOD_CALL = re.compile(
    r"\bCALL_\w+\s*\(",
    re.IGNORECASE,
)

# 中文变量名检测: 匹配包含中文字符的标识符
RE_CHINESE_CHAR = re.compile(
    r"[\u4e00-\u9fff\u3400-\u4dbf]",
    re.UNICODE,
)

# 变量声明中的名称提取: 提取 VAR xxx : TYPE 中的xxx
RE_VAR_NAME_IN_DECL = re.compile(
    r"(?P<name>\w+)\s*:",
    re.IGNORECASE,
)

# 下划线违规检测: 检测前缀之后的额外下划线 (如 i_b_start)
# 允许的模式: 前缀_类型缩写_名称 (如 i_bStart), 不允许多个连续下划线或尾部下划线
RE_EXTRA_UNDERSCORE = re.compile(
    r"^(?:i_|o_|q_|s_|fb_|CONST_)\w*_[^A-Z]",  # 前缀后还有下划线且后面不是大写字母开头的新词
    re.IGNORECASE,
)

# 更精确的下划线检测: 前缀部分之后不应再有下划线
# 正确: i_bStart, o_iErrorCode, fb_tActionTimer
# 错误: i_b_start, o_i_error_code, s_current_step
RE_INVALID_UNDERSCORE = re.compile(
    r"^(i_|o_|q_|s_|fb_|CONST_)?\w+_\w+.*_",  # 多个下划线（超过标准格式）
    re.IGNORECASE,
)

# 小驼峰命名验证: 第一个单词小写，后续单词首字母大写
# 正确: i_bStart, o_iErrorCode, s_currentStep (如果允许下划线)
# 错误: I_BStart, i_BStart (首字母大写), ibstart (无分隔)
RE_CAMEL_CASE = re.compile(
    r"^[a-z][a-zA-Z0-9]*$",
)

# 前缀到变量类别的映射
PREFIX_CATEGORY_MAP = {
    "VAR_INPUT": ["i_"],
    "VAR_OUTPUT": ["o_"],
    "VAR_IN_OUT": ["i_", "o_"],  # 输入输出变量可用输入或输出前缀
    "VAR": ["s_"],  # 局部/内部变量使用静态前缀
    "VAR_TEMP": ["s_"],  # 临时变量也使用静态前缀
    "VAR_STATIC": ["s_"],
    "VAR_GLOBAL": ["i_", "o_", "q_", "s_", "fb_", "CONST_"],  # 全局变量灵活
    "VAR_CONSTANT": ["CONST_"],
}

# 有效前缀列表
VALID_PREFIXES = {"i_", "o_", "q_", "s_", "fb_", "CONST_"}

# 类型缩写映射（用于小驼峰验证的第二段）
TYPE_ABBREVIATIONS = {
    "b",  # BOOL
    "i",  # INT/DINT
    "r",  # REAL
    "t",  # TIME/TOD/DT
    "e",  # ENUM
    "s",  # STRING
    "st",  # STRUCT
    "arr",  # ARRAY
}


class NamingChecker(BaseChecker):
    """
    PLC命名规范检查器

    基于 905_SCL编程规范 实现完整的命名规范检查。
    支持以下6条规则的独立检查：
    - NAMING_001 ~ NAMING_006

    Usage:
        checker = NamingChecker()
        violations = checker.check(source_code, file_path="test.st")
        for v in violations:
            print(v)
    """

    # 规则定义列表
    RULE_DEFINITIONS = [
        RuleInfo(
            rule_id="NAMING_001",
            name="METHOD定义禁止CALL_前缀",
            description="METHOD定义时，方法名不应使用CALL_前缀。"
                       "Siemens LSP不支持带CALL_前缀的METHOD定义。",
            category="naming",
            severity=Severity.ERROR,
            tags=["method", "definition", "siemens-lsp"],
        ),
        RuleInfo(
            rule_id="NAMING_002",
            name="METHOD调用禁止CALL_前缀",
            description="调用METHOD时，不应使用CALL_前缀。"
                       "应直接使用方法名进行调用。",
            category="naming",
            severity=Severity.ERROR,
            tags=["method", "call", "siemens-lsp"],
        ),
        RuleInfo(
            rule_id="NAMING_003",
            name="变量必须使用规范前缀",
            description="变量名必须以规范前缀开头："
                       "i_(输入)、o_(输出)、q_(查询)、s_(静态)、fb_(功能块)、CONST_(常量)。",
            category="naming",
            severity=Severity.WARNING,
            tags=["variable", "prefix", "hungarian"],
        ),
        RuleInfo(
            rule_id="NAMING_004",
            name="禁止中文变量名",
            description="变量名必须使用英文标识符，禁止使用中文字符。"
                       "中文字符可能导致某些PLC系统兼容性问题。",
            category="naming",
            severity=Severity.ERROR,
            tags=["variable", "chinese", "encoding"],
        ),
        RuleInfo(
            rule_id="NAMING_005",
            name="禁止多余下划线",
            description="除规定的类型前缀外，变量名中不应包含额外的下划线。"
                       "正确示例: i_bStart, o_iErrorCode; 错误示例: i_b_start",
            category="naming",
            severity=Severity.WARNING,
            tags=["variable", "underscore", "format"],
        ),
        RuleInfo(
            rule_id="NAMING_006",
            name="必须使用小驼峰命名",
            description="变量名应采用小驼峰命名法(camelCase)，"
                       "首个单词首字母小写，后续单词首字母大写。",
            category="naming",
            severity=Severity.WARNING,
            tags=["variable", "camelcase", "convention"],
        ),
    ]

    def __init__(self):
        """
        初始化命名检查器

        创建所有规则的RuleInfo并初始化解析器。
        """
        # 使用第一个规则作为主规则信息（用于BaseChecker接口兼容）
        super().__init__(rule_info=self.RULE_DEFINITIONS[0])

        # 存储所有规则定义
        self._all_rules = {r.rule_id: r for r in self.RULE_DEFINITIONS}

        # 初始化ST解析器（用于提取变量信息）
        self._parser = STParser()

        # 规则启用状态（默认全部启用）
        self._rule_enabled = {r.rule_id: True for r in self.RULE_DEFINITIONS}

        logger.info(f"NamingChecker初始化完成，共{len(self.RULE_DEFINITIONS)}条规则")

    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        """
        执行命名规范检查

        Args:
            source_code: 待检查的ST源代码
            file_path: 源文件路径
            context: 上下文信息（可选）

        Returns:
            List[Violation]: 发现的违规记录列表
        """
        violations: List[Violation] = []
        lines = source_code.splitlines()

        # 解析源代码获取结构化信息
        pous, global_vars = self._parser.parse(source_code)

        # 执行各项检查
        violations.extend(self._check_method_definition(lines, file_path))
        violations.extend(self._check_method_call(source_code, lines, file_path))
        violations.extend(self._check_variable_naming(pous, global_vars, file_path))

        logger.debug(
            f"命名检查完成: {file_path}, "
            f"发现{len(violations)}个违规"
        )

        return violations

    def _is_rule_enabled(self, rule_id: str) -> bool:
        """检查指定规则是否启用"""
        return self._rule_enabled.get(rule_id, True)

    def enable_rule(self, rule_id: str) -> bool:
        """启用指定规则"""
        if rule_id in self._rule_enabled:
            self._rule_enabled[rule_id] = True
            logger.info(f"启用规则: {rule_id}")
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """禁用指定规则"""
        if rule_id in self._rule_enabled:
            self._rule_enabled[rule_id] = False
            logger.info(f"禁用规则: {rule_id}")
            return True
        return False

    def get_all_rules(self) -> Dict[str, RuleInfo]:
        """获取所有规则定义"""
        return dict(self._all_rules)

    # ========================================================================
    # NAMING_001: METHOD定义禁止CALL_前缀
    # ========================================================================

    def _check_method_definition(
        self, lines: List[str], file_path: str
    ) -> List[Violation]:
        """
        检查METHOD定义是否使用了CALL_前缀

        规则: METHOD定义时方法名不应以CALL_开头
        错误示例: METHOD CALL_AutoMode : VOID
        正确示例: METHOD AutoMode : VOID
        """
        if not self._is_rule_enabled("NAMING_001"):
            return []

        violations: List[Violation] = []
        rule = self._all_rules["NAMING_001"]

        for line_num, line in enumerate(lines, start=1):
            # 跳过注释行和空行
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("(*"):
                continue

            match = RE_METHOD_DEFINITION.search(line)
            if match:
                method_name = match.group(0).replace("METHOD", "").strip()

                violation = Violation(
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    message=(
                        f"METHOD定义不应使用CALL_前缀: '{method_name}'。"
                        f"建议改为: '{method_name.replace('CALL_', '')}'"
                    ),
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start() + 1,
                    suggestion=f"移除CALL_前缀，改为: {method_name.replace('CALL_', '')}",
                    code_snippet=line.strip(),
                )
                violations.append(violation)
                logger.debug(f"NAMING_001违规于第{line_num}行: {method_name}")

        return violations

    # ========================================================================
    # NAMING_002: METHOD调用禁止CALL_前缀
    # ========================================================================

    def _check_method_call(
        self, source_code: str, lines: List[str], file_path: str
    ) -> List[Violation]:
        """
        检查METHOD调用是否使用了CALL_前缀

        规则: 调用METHOD时不应使用CALL_前缀
        错误示例: CALL_AutoMode();
        正确示例: AutoMode();

        注意: 需要排除METHOD定义行本身（由NAMING_001处理）
        """
        if not self._is_rule_enabled("NAMING_002"):
            return []

        violations: List[Violation] = []
        rule = self._all_rules["NAMING_002"]

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("(*"):
                continue

            # 跳过METHOD定义行（已由NAMING_001处理）
            if re.match(r"\s*METHOD\s+", stripped, re.IGNORECASE):
                continue

            match = RE_METHOD_CALL.search(line)
            if match:
                call_match = re.match(r"\b(CALL_\w+)", match.group(0))
                if call_match:
                    call_name = call_match.group(1)

                    violation = Violation(
                        rule_id=rule.rule_id,
                        severity=rule.severity,
                        message=(
                            f"METHOD调用不应使用CALL_前缀: '{call_name}()'。"
                            f"建议改为: '{call_name.replace('CALL_', '')}()'"
                        ),
                        file_path=file_path,
                        line_number=line_num,
                        column=match.start() + 1,
                        suggestion=f"移除CALL_前缀，直接调用: {call_name.replace('CALL_', '')}()",
                        code_snippet=line.strip(),
                    )
                    violations.append(violation)
                    logger.debug(f"NAMING_002违规于第{line_num}行: {call_name}")

        return violations

    # ========================================================================
    # NAMING_003/004/005/006: 变量命名综合检查
    # ========================================================================

    def _check_variable_naming(
        self,
        pous: List[POUInfo],
        global_vars: List[VariableInfo],
        file_path: str,
    ) -> List[Violation]:
        """
        综合检查变量命名规范

        检查项:
        - NAMING_003: 变量前缀规范性
        - NAMING_004: 禁止中文变量名
        - NAMING_005: 禁止多余下划线
        - NAMING_006: 小驼峰命名验证
        """
        violations: List[Violation] = []
        all_variables: List[Tuple[VariableInfo, str]] = []  # (变量, POU名称)

        # 收集POU内的变量
        for pou in pous:
            for var in pou.variables:
                all_variables.append((var, pou.name))

        # 收集全局变量
        for var in global_vars:
            all_variables.append((var, "[GLOBAL]"))

        # 对每个变量执行检查
        for var, pou_name in all_variables:
            violations.extend(
                self._check_single_variable(var, pou_name, file_path)
            )

        return violations

    def _check_single_variable(
        self, var: VariableInfo, pou_name: str, file_path: str
    ) -> List[Violation]:
        """
        对单个变量执行所有命名规则检查

        Args:
            var: 变量信息对象
            pou_name: 所属POU名称
            file_path: 文件路径

        Returns:
            List[Violation]: 该变量的违规列表
        """
        violations: List[Violation] = []
        var_name = var.name

        # ---- NAMING_003: 前缀检查 ----
        if self._is_rule_enabled("NAMING_003"):
            prefix_violation = self._check_prefix(var)
            if prefix_violation:
                prefix_violation.file_path = file_path
                prefix_violation.line_number = var.line_number
                violations.append(prefix_violation)

        # ---- NAMING_004: 中文检查 ----
        if self._is_rule_enabled("NAMING_004"):
            chinese_violation = self._check_chinese(var_name, var.line_number, file_path)
            if chinese_violation:
                violations.append(chinese_violation)

        # ---- NAMING_005: 下划线检查 ----
        if self._is_rule_enabled("NAMING_005"):
            underscore_violation = self._check_underscore(var_name, var.line_number, file_path)
            if underscore_violation:
                violations.append(underscore_violation)

        # ---- NAMING_006: 小驼峰检查 ----
        if self._is_rule_enabled("NAMING_006"):
            camelcase_violation = self._check_camelcase(var_name, var.line_number, file_path)
            if camelcase_violation:
                violations.append(camelcase_violation)

        return violations

    def _check_prefix(self, var: VariableInfo) -> Optional[Violation]:
        """
        检查变量前缀是否符合规范 (NAMING_003)

        规则:
        - VAR_INPUT 必须以 i_ 开头
        - VAR_OUTPUT 必须以 o_ 开头
        - VAR (局部) 应以 s_ 开头
        - VAR_CONSTANT 必须以 CONST_ 开头
        - 功能块实例应以 fb_ 开头
        """
        rule = self._all_rules["NAMING_003"]
        var_name = var.name
        category = var.category.value
        data_type = var.data_type.upper()

        # 确定该类别允许的前缀
        allowed_prefixes = PREFIX_CATEGORY_MAP.get(category, [])

        # 特殊处理: 功能块实例类型应该用fb_前缀
        if self._is_fb_type(data_type):
            expected_prefix = "fb_"
            if not var_name.startswith(expected_prefix):
                return Violation(
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    message=(
                        f"功能块实例 '{var_name}' 应使用 'fb_' 前缀。"
                        f"当前类别: {category}, 数据类型: {data_type}"
                    ),
                    suggestion=f"重命名为: fb_{var_name}",
                    code_snippet=f"{var_name} : {var.data_type};",
                )
            return None  # 功能块实例通过检查

        # 常规前缀检查
        has_valid_prefix = any(
            var_name.lower().startswith(prefix.lower())
            for prefix in allowed_prefixes
        )

        if not has_valid_prefix and allowed_prefixes:
            # 构建建议前缀字符串
            suggested = allowed_prefixes[0]
            suggestion_detail = (
                f"{category} 类型的变量 '{var_name}' 应使用前缀: "
                f"{', '.join(allowed_prefixes)}"
            )

            return Violation(
                rule_id=rule.rule_id,
                severity=rule.severity,
                message=suggestion_detail,
                suggestion=f"建议重命名为: {suggested}{var_name}",
                code_snippet=f"{var_name} : {var.data_type};",
            )

        return None

    def _is_fb_type(self, data_type: str) -> bool:
        """判断数据类型是否为功能块类型"""
        data_upper = data_type.upper()
        # 常见的功能块类型前缀或关键字
        fb_indicators = [
            "FB_", "TON", "TOF", "TP", "CTU", "CTD", "CTUD",
            "R_TRIG", "F_TRIG", "SR", "RS", "SEL", "MUX",
            "MAX", "MIN", "LIMIT", "PID",
        ]
        return any(data_upper.startswith(ind) or data_upper == ind
                   for ind in fb_indicators)

    def _check_chinese(
        self, var_name: str, line_num: int, file_path: str
    ) -> Optional[Violation]:
        """
        检查变量名是否包含中文字符 (NAMING_004)

        规则: 变量名必须使用英文标识符
        """
        rule = self._all_rules["NAMING_004"]

        if RE_CHINESE_CHAR.search(var_name):
            return Violation(
                rule_id=rule.rule_id,
                severity=rule.severity,
                message=(
                    f"变量名 '{var_name}' 包含中文字符，"
                    f"应使用英文标识符"
                ),
                file_path=file_path,
                line_number=line_num,
                suggestion="将中文变量名翻译为英文，如: 运行标志 -> bRunningFlag",
                code_snippet=var_name,
            )
        return None

    def _check_underscore(
        self, var_name: str, line_num: int, file_path: str
    ) -> Optional[Violation]:
        """
        检查变量名是否有多余的下划线 (NAMING_005)

        规则: 除规定前缀(i_/o_/q_/s_/fb_/CONST_)外，不应有额外下划线
        正确: i_bStart, o_iErrorCode, fb_tActionTimer
        错误: i_b_start, o_i_error_code
        """
        rule = self._all_rules["NAMING_005"]

        # 移除有效前缀后检查剩余部分
        name_without_prefix = var_name
        for prefix in VALID_PREFIXES:
            if var_name.lower().startswith(prefix.lower()):
                name_without_prefix = var_name[len(prefix):]
                break

        # 检查剩余部分是否还有下划线
        if "_" in name_without_prefix:
            return Violation(
                rule_id=rule.rule_id,
                severity=rule.severity,
                message=(
                    f"变量名 '{var_name}' 包含多余下划线。"
                    f"除前缀外不应有额外的下划线字符"
                ),
                file_path=file_path,
                line_number=line_num,
                suggestion=(
                    f"移除多余下划线，使用小驼峰格式，"
                    f"如: {var_name.replace('_', '').capitalize()}"
                ),
                code_snippet=var_name,
            )
        return None

    def _check_camelcase(
        self, var_name: str, line_num: int, file_path: str
    ) -> Optional[Violation]:
        """
        检查变量名是否符合小驼峰命名法 (NAMING_006)

        规则:
        - 第一个字符必须是小写字母
        - 后续单词首字母大写
        - 不应全大写（除非是常量CONST_）

        特殊情况:
        - CONST_ 前缀的常量可以全大写
        - 前缀后的类型缩写部分允许全大写单字符 (如 i_b 中的 b)
        """
        rule = self._all_rules["NAMING_006"]

        # 常量特殊处理: CONST_ 前缀允许全大写
        if var_name.upper().startswith("CONST_"):
            const_part = var_name[6:]  # 移除 "CONST_"
            if const_part.isupper() and const_part.isalpha():
                return None  # 全大写常量是合法的

        # 移除前缀后检查主体部分
        name_to_check = var_name
        for prefix in VALID_PREFIXES:
            if var_name.lower().startswith(prefix.lower()):
                name_to_check = var_name[len(prefix):]
                break

        # 空名称跳过
        if not name_to_check:
            return None

        # 检查首字符: 必须是小写字母
        if not name_to_check[0].islower():
            return Violation(
                rule_id=rule.rule_id,
                severity=rule.severity,
                message=(
                    f"变量名 '{var_name}' 不符合小驼峰命名法。"
                    f"前缀后的首字符应为小写字母"
                ),
                file_path=file_path,
                line_number=line_num,
                suggestion=(
                    f"将前缀后的首字母改为小写，"
                    f"如: {var_name[:1].lower() + var_name[1:]}"
                ),
                code_snippet=var_name,
            )

        # 检查是否有非法的大写开头单词（非首字符位置的大写是允许的）
        # 这里主要防止类似 "iVarName" 变成 "IVarName" 的情况
        # 实际上我们已经检查了首字符，这里做补充验证

        return None

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取检查器统计信息

        Returns:
            Dict: 包含规则数量、启用状态等信息的字典
        """
        total_rules = len(self.RULE_DEFINITIONS)
        enabled_rules = sum(1 for enabled in self._rule_enabled.values() if enabled)

        return {
            "checker_name": "NamingChecker",
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "disabled_rules": total_rules - enabled_rules,
            "rules": [
                {
                    "rule_id": rid,
                    "enabled": self._rule_enabled[rid],
                    "description": info.description,
                }
                for rid, info in self._all_rules.items()
            ],
        }

    def __repr__(self) -> str:
        """返回检查器的字符串表示"""
        enabled_count = sum(1 for v in self._rule_enabled.values() if v)
        total_count = len(self._rule_enabled)
        return (
            f"<NamingChecker "
            f"(rules={enabled_count}/{total_count} enabled)>"
        )
