# -*- coding: utf-8 -*-
"""
FB接口调用一致性检查器

Epic A核心模块 - 检查OB1中FB调用参数与FB接口定义的一致性。

6项检查规则:
  FB_IFC_001 缺少必要输入参数    [ERROR]   VAR_INPUT未赋值
  FB_IFC_002 未知参数名           [WARNING] 调用了FB不存在的参数
  FB_IFC_003 输出未连接          [WARNING] VAR_OUTPUT未用=>接出
  FB_IFC_004 IN_OUT缺失          [ERROR]   VAR_IN_OUT参数未处理
  FB_IFC_005 类型不匹配          [WARNING] 赋值源类型与参数类型不一致(基础推断)
  FB_IFC_006 实例数据块不匹配     [ERROR]   DB结构体字段数≠FB实际引脚数

依赖:
  - FBCallParser: 解析OB1中的FB调用语句
  - FBSignatureBuilder: 构建FB接口签名
  - fb_registry: 实例名→FB类型名映射
"""
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from src.checkers.base_checker import BaseChecker, RuleInfo, Severity
from src.models.check_result import Violation
from src.parsers.fb_call_parser import FBCallParser, FBCallSite, FBCallArgument
from src.parsers.fb_signature_builder import (
    FBSignatureBuilder,
    FBInterfaceSignature,
    VarDef,
)
from src.sync.fb_registry import resolve_title_en
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

_TYPE_PREFIX_MAP = {
    "BOOL": {"b"},
    "INT": {"i", "w"},
    "DINT": {"i", "d", "di"},
    "REAL": {"r"},
    "TIME": {"t", "tm"},
    "TOD": {"tod"},
    "DT": {"dt"},
    "STRING": {"s", "str"},
    "WORD": {"w"},
    "DWORD": {"dw"},
    "BYTE": {"by"},
    "ARRAY": {"a", "arr"},
}

_SIMPLE_LITERAL_RE = re.compile(
    r"^(TRUE|FALSE|0|(-?\d+\.?\d*))$",
    re.IGNORECASE,
)


class FBInterfaceChecker(BaseChecker):
    """
    FB接口调用一致性检查器

    Usage:
        checker = FBInterfaceChecker()
        violations = checker.check(
            ob1_source_code,
            file_path="OB1.scl",
            context={
                "project_path": "/path/to/plc/project",
                "syslib_path": "/path/to/SysLib",
            }
        )
    """

    RULE_DEFINITIONS = [
        RuleInfo(
            rule_id="FB_IFC_001",
            name="缺少必要输入参数",
            description=(
                "FB定义了VAR_INPUT变量，但调用时未通过:=赋值。"
                "缺少必要输入可能导致FB内部逻辑异常或使用默认值运行。"
            ),
            category="interface",
            severity=Severity.ERROR,
            tags=["fb-call", "missing-input", "interface"],
        ),
        RuleInfo(
            rule_id="FB_IFC_002",
            name="未知参数名",
            description=(
                "调用FB时传入了FB接口定义中不存在的参数名。"
                "可能是拼写错误、版本不一致或已删除的旧参数。"
            ),
            category="interface",
            severity=Severity.WARNING,
            tags=["fb-call", "unknown-param", "interface"],
        ),
        RuleInfo(
            rule_id="FB_IFC_003",
            name="输出未连接",
            description=(
                "FB定义了VAR_OUTPUT变量，但调用时未使用=>接出。"
                "该输出值将被丢弃，下游无法读取此信号。"
            ),
            category="interface",
            severity=Severity.WARNING,
            tags=["fb-call", "unconnected-output", "interface"],
        ),
        RuleInfo(
            rule_id="FB_IFC_004",
            name="IN_OUT缺失",
            description=(
                "FB定义了VAR_IN_OUT参数，但调用时未传入。"
                "IN_OUT参数是引用传递，缺失将导致FB内部读写无效地址。"
            ),
            category="interface",
            severity=Severity.ERROR,
            tags=["fb-call", "missing-inout", "interface"],
        ),
        RuleInfo(
            rule_id="FB_IFC_005",
            name="类型不匹配",
            description=(
                "赋值表达式的推断类型与参数声明的数据类型不一致。"
                "基于匈牙利命名前缀和字面量进行基础类型推断，可能存在误报。"
            ),
            category="interface",
            severity=Severity.WARNING,
            tags=["fb-call", "type-mismatch", "interface"],
        ),
        RuleInfo(
            rule_id="FB_IFC_006",
            name="实例数据块不匹配",
            description=(
                "GlobalVars.db中对应结构体的字段数量与FB的实际引脚数不一致。"
                "DB与FB接口不同步会导致PLC下载时报I/O访问错误。"
            ),
            category="interface",
            severity=Severity.ERROR,
            tags=["fb-call", "db-mismatch", "interface"],
        ),
    ]

    def __init__(self):
        super().__init__(rule_info=self.RULE_DEFINITIONS[0])
        self._all_rules = {r.rule_id: r for r in self.RULE_DEFINITIONS}
        self._rule_enabled = {r.rule_id: True for r in self.RULE_DEFINITIONS}
        self._call_parser = FBCallParser()
        self._sig_builder = FBSignatureBuilder()
        self._signatures_cache: Optional[Dict[str, FBInterfaceSignature]] = None
        logger.info(f"FBInterfaceChecker初始化完成，共{len(self.RULE_DEFINITIONS)}条规则")

    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        """
        执行FB接口一致性检查

        Args:
            source_code: OB1.scl源码文本
            file_path: 源文件路径
            context: 上下文字典，支持:
                - project_path: PLC项目根目录（用于查找FB定义文件）
                - syslib_path: SysLib库路径
                - signatures: 预构建的签名字典{fb_name_lower: signature}
                - db_field_counts: 预解析的DB字段数{struct_key: count}

        Returns:
            List[Violation]: 违规列表
        """
        ctx = context or {}
        violations: List[Violation] = []

        call_sites = self._call_parser.parse_ob1_calls(source_code, file_path)
        if not call_sites:
            logger.debug("未发现FB调用点")
            return violations

        signatures = ctx.get("signatures")
        if signatures is None:
            project_path = ctx.get("project_path", "")
            syslib_path = ctx.get("syslib_path")
            if project_path:
                signatures = self._sig_builder.build_project_signatures(
                    project_path, syslib_path,
                )
            else:
                signatures = {}
        self._signatures_cache = signatures

        db_field_counts = ctx.get("db_field_counts", {})

        for site in call_sites:
            signature = self._resolve_signature(site, signatures)
            if signature is None or not signature.fb_name:
                logger.debug(
                    f"跳过无签名FB: {site.fb_instance_name}"
                )
                continue

            site.fb_type_name = signature.fb_name

            if self._is_rule_enabled("FB_IFC_001"):
                violations.extend(
                    self._check_missing_inputs(site, signature),
                )
            if self._is_rule_enabled("FB_IFC_002"):
                violations.extend(
                    self._check_unknown_params(site, signature),
                )
            if self._is_rule_enabled("FB_IFC_003"):
                violations.extend(
                    self._check_unconnected_outputs(site, signature),
                )
            if self._is_rule_enabled("FB_IFC_004"):
                violations.extend(
                    self._check_missing_inouts(site, signature),
                )
            if self._is_rule_enabled("FB_IFC_005"):
                violations.extend(
                    self._check_type_mismatch(site, signature),
                )
            if self._is_rule_enabled("FB_IFC_006") and db_field_counts:
                violations.extend(
                    self._check_db_mismatch(site, signature, db_field_counts),
                )

        logger.info(
            f"FB接口检查完成: {file_path}, "
            f"{len(call_sites)}个调用点, "
            f"{len(violations)}个违规"
        )
        return violations

    def _is_rule_enabled(self, rule_id: str) -> bool:
        return self._rule_enabled.get(rule_id, True)

    def enable_rule(self, rule_id: str) -> bool:
        if rule_id in self._rule_enabled:
            self._rule_enabled[rule_id] = True
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        if rule_id in self._rule_enabled:
            self._rule_enabled[rule_id] = False
            return True
        return False

    def get_all_rules(self) -> Dict[str, RuleInfo]:
        return dict(self._all_rules)

    def _resolve_signature(
        self,
        site: FBCallSite,
        signatures: Dict[str, FBInterfaceSignature],
    ) -> Optional[FBInterfaceSignature]:
        """根据调用点实例名推断并查找对应的FB签名"""
        instance = site.fb_instance_name

        title_en = resolve_title_en(instance)
        if title_en and title_en != instance:
            key = title_en.lower().split("_")[0]
            for sig_key, sig in signatures.items():
                if sig_key.startswith(key) or title_en.lower() == sig_key:
                    return sig

        dot_parts = instance.rsplit(".", 1)
        short_name = dot_parts[-1] if len(dot_parts) > 1 else instance

        candidates = []
        for sig_key, sig in signatures.items():
            fb_short = sig.fb_name.split("_")[0].lower() if "_" in sig.fb_name else sig.fb_name.lower()
            inst_lower = short_name.lower()

            if sig_key == inst_lower or sig_key == instance.lower():
                return sig

            if inst_lower.replace("fb", "").replace("_", "") in fb_lower_for(sig.fb_name):
                candidates.append((sig, 2))

            parts = inst_lower.split("_")
            if len(parts) >= 2:
                core = "".join(parts[1:])
                if core and core in fb_lower_for(sig.fb_name):
                    candidates.append((sig, 1))

            if any(kw in sig_key for kw in [short_name.lower(), inst_lower]):
                candidates.append((sig, 1))

        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]

        direct = signatures.get(instance.lower())
        if direct:
            return direct

        return None

    # ========================================================================
    # FB_IFC_001: 缺少必要输入参数
    # ========================================================================

    def _check_missing_inputs(
        self,
        site: FBCallSite,
        signature: FBInterfaceSignature,
    ) -> List[Violation]:
        rule = self._all_rules["FB_IFC_001"]
        violations: List[Violation] = []
        called_names = {n.lower() for n in site.get_called_param_names()}

        for var_def in signature.inputs:
            if var_def.has_default:
                continue
            if var_def.name.lower() in called_names:
                continue

            violations.append(Violation(
                rule_id=rule.rule_id,
                severity=rule.severity,
                message=(
                    f"[{site.fb_instance_name}] 缺少必要输入参数 '{var_def.name}' "
                    f"(类型: {var_def.data_type})。"
                    f"FB '{signature.fb_name}' 定义了该VAR_INPUT但调用时未赋值"
                ),
                file_path=site.file_path,
                line_number=site.line_number,
                suggestion=f"添加: {var_def.name} := <表达式>",
                code_snippet=f"{site.fb_instance_name}(...)",
            ))

        return violations

    # ========================================================================
    # FB_IFC_002: 未知参数名
    # ========================================================================

    def _check_unknown_params(
        self,
        site: FBCallSite,
        signature: FBInterfaceSignature,
    ) -> List[Violation]:
        rule = self._all_rules["FB_IFC_002"]
        violations: List[Violation] = []
        valid_names = {n.lower() for n in signature.all_param_names}

        for arg in site.all_args:
            if arg.param_name.lower() not in valid_names:
                violations.append(Violation(
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    message=(
                        f"[{site.fb_instance_name}] 未知参数名 '{arg.param_name}'。"
                        f"FB '{signature.fb_name}' 接口中不存在此参数"
                    ),
                    file_path=site.file_path,
                    line_number=arg.line_number,
                    suggestion=f"确认参数名是否正确，或检查FB是否需要升级",
                    code_snippet=f"{arg.param_name} :=/=> {arg.value_expression[:40]}",
                ))

        return violations

    # ========================================================================
    # FB_IFC_003: 输出未连接
    # ========================================================================

    def _check_unconnected_outputs(
        self,
        site: FBCallSite,
        signature: FBInterfaceSignature,
    ) -> List[Violation]:
        rule = self._all_rules["FB_IFC_003"]
        violations: List[Violation] = []
        connected_outputs = {a.param_name.lower() for a in site.output_args}

        for var_def in signature.outputs:
            if var_def.name.lower() not in connected_outputs:
                violations.append(Violation(
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    message=(
                        f"[{site.fb_instance_name}] 输出参数 '{var_def.name}' 未连接。"
                        f"FB '{signature.fb_name}' 的VAR_OUTPUT未用=>接出，值将被丢弃"
                    ),
                    file_path=site.file_path,
                    line_number=site.line_number,
                    suggestion=f"添加 => 接收变量，如: {var_def.name} => GlobalVars.xxx.o_{var_def.name}",
                    code_snippet=f"{site.fb_instance_name}(...)",
                ))

        return violations

    # ========================================================================
    # FB_IFC_004: IN_OUT缺失
    # ========================================================================

    def _check_missing_inouts(
        self,
        site: FBCallSite,
        signature: FBInterfaceSignature,
    ) -> List[Violation]:
        rule = self._all_rules["FB_IFC_004"]
        violations: List[Violation] = []
        called_input_inout = {
            a.param_name.lower()
            for a in site.input_args + site.inout_args
        }

        for var_def in signature.in_outs:
            if var_def.name.lower() not in called_input_inout:
                violations.append(Violation(
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    message=(
                        f"[{site.fb_instance_name}] IN_OUT参数 '{var_def.name}' 缺失。"
                        f"FB '{signature.fb_name}' 定义了VAR_IN_OUT但调用时未传入"
                    ),
                    file_path=site.file_path,
                    line_number=site.line_number,
                    suggestion=f"添加: {var_def.name} := <变量引用>",
                    code_snippet=f"{site.fb_instance_name}(...)",
                ))

        return violations

    # ========================================================================
    # FB_IFC_005: 类型不匹配 (基础推断)
    # ========================================================================

    def _check_type_mismatch(
        self,
        site: FBCallSite,
        signature: FBInterfaceSignature,
    ) -> List[Violation]:
        rule = self._all_rules["FB_IFC_005"]
        violations: List[Violation] = []

        for arg in site.input_args + site.inout_args:
            var_def = signature.get_var_def(arg.param_name)
            if var_def is None:
                continue

            expected_type = var_def.data_type.upper()
            inferred_type = self._infer_type_from_expr(arg.value_expression)

            if inferred_type and expected_type != inferred_type:
                compatible = self._are_types_compatible(expected_type, inferred_type)
                if not compatible:
                    violations.append(Violation(
                        rule_id=rule.rule_id,
                        severity=rule.severity,
                        message=(
                            f"[{site.fb_instance_name}] 参数 '{arg.param_name}' 类型可能不匹配: "
                            f"期望 {expected_type}, 赋值源推断为 {inferred_type}。"
                            f"表达式: {arg.value_expression[:60]}"
                        ),
                        file_path=site.file_path,
                        line_number=arg.line_number,
                        suggestion=f"确认赋值源的数据类型是否为 {expected_type}",
                        code_snippet=(
                            f"{arg.param_name} := {arg.value_expression[:50]}"
                        ),
                    ))

        return violations

    def _infer_type_from_expr(self, expr: str) -> Optional[str]:
        """从赋值表达式推断数据类型"""
        clean = expr.strip()

        if _SIMPLE_LITERAL_RE.match(clean):
            upper = clean.upper()
            if upper in ("TRUE", "FALSE"):
                return "BOOL"
            if "." in clean:
                return "REAL"
            return "DINT"

        last_segment = clean.rsplit(".", 1)[-1] if "." in clean else clean
        field_name = last_segment.rstrip(")").split("[")[0].strip()

        prefix_match = re.match(r"^([a-z]+)_", field_name, re.IGNORECASE)
        if prefix_match:
            prefix = prefix_match.group(1).lower()
            for type_name, prefixes in _TYPE_PREFIX_MAP.items():
                if prefix in prefixes:
                    return type_name

        array_match = re.search(r"\w+(\[\w+\])", clean)
        if array_match:
            return "ARRAY"

        return None

    @staticmethod
    def _are_types_compatible(expected: str, actual: str) -> bool:
        """判断两种基础类型是否兼容"""
        compatible_groups = [
            {"INT", "DINT", "WORD", "DWORD", "BYTE"},
            {"INT", "WORD", "BYTE"},
            {"DINT", "DWORD"},
        ]
        for group in compatible_groups:
            if expected in group and actual in group:
                return True
        return expected == actual

    # ========================================================================
    # FB_IFC_006: 实例数据块不匹配
    # ========================================================================

    def _check_db_mismatch(
        self,
        site: FBCallSite,
        signature: FBInterfaceSignature,
        db_field_counts: Dict[str, int],
    ) -> List[Violation]:
        rule = self._all_rules["FB_IFC_006"]
        violations: List[Violation] = []

        from src.sync.fb_registry import resolve_struct_key
        struct_key = resolve_struct_key(site.fb_instance_name)
        if not struct_key or struct_key == "__ALL__":
            return violations

        db_count = db_field_counts.get(struct_key.lower())
        if db_count is None:
            return violations

        fb_pin_count = signature.total_pin_count
        if db_count != fb_pin_count:
            violations.append(Violation(
                rule_id=rule.rule_id,
                severity=rule.severity,
                message=(
                    f"[{site.fb_instance_name}] DB结构体字段数不匹配: "
                    f"GlobalVars.{struct_key} 有 {db_count} 个字段, "
                    f"FB '{signature.fb_name}' 有 {fb_pin_count} 个引脚"
                ),
                file_path=site.file_path,
                line_number=site.line_number,
                suggestion=(
                    f"同步GlobalVars.db中 {struct_key} 结构体定义，"
                    f"使其包含 {fb_pin_count} 个字段(与FB引脚一致)"
                ),
                code_snippet=f"{site.fb_instance_name} (DB字段={db_count}, FB引脚={fb_pin_count})",
            ))

        return violations

    def get_statistics(self) -> Dict[str, Any]:
        total_rules = len(self.RULE_DEFINITIONS)
        enabled_rules = sum(1 for v in self._rule_enabled.values() if v)
        return {
            "checker_name": "FBInterfaceChecker",
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
        enabled_count = sum(1 for v in self._rule_enabled.values() if v)
        total_count = len(self._rule_enabled)
        return (
            f"<FBInterfaceChecker "
            f"(rules={enabled_count}/{total_count} enabled)>"
        )


def fb_lower_for(fb_name: str) -> str:
    return fb_name.lower()
