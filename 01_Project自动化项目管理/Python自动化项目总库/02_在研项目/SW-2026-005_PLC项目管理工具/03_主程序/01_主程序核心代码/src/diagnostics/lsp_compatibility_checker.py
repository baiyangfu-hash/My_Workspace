# -*- coding: utf-8 -*-
"""
LSP兼容性检查器

检测Siemens LSP生成的Go代码中的潜在问题，
包括builtin stub误用、OB→FB调用链分析、FB实现缺失检测等。

主要功能：
1. 扫描.plc-out/golang/目录下的Go源文件
2. 检测4类诊断规则（DIAG_001~DIAG_004）
3. 分析OB块到FB/FC的调用关系
4. 验证被调用的FB是否都有对应的实现
5. 生成详细的诊断报告
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple, Any
from dataclasses import dataclass

from src.models.diagnostic_report import (
    DiagnosticIssue,
    DiagnosticReport,
    DiagnosticSeverity,
)


# ============================================================
# 诊断规则定义常量
# ============================================================

class DiagnosticRules:
    """诊断规则ID和描述的常量定义"""

    # DIAG_001: Builtin Stub误用检测
    DIAG_001 = "DIAG_001"
    DIAG_001_DESC = "检测到可能的builtin stub误用模式"
    DIAG_001_DETAIL = (
        "在生成的Go代码中发现 `_ = builtins.B_xxx(...)` 模式，"
        "这通常表示LSP在处理某些PLC指令时生成了不正确的stub调用。"
        "这种模式可能导致运行时错误或未定义行为。"
    )

    # DIAG_002: OB→FB调用链中的缺失实现
    DIAG_002 = "DIAG_002"
    DIAG_002_DESC = "OB调用的FB缺少对应实现"
    DIAG_002_DETAIL = (
        "在OB块中检测到对某个FB/FC的调用，但在blocks_fb_autogen.go中"
        "未找到该FB的实现函数。这可能是由于：\n"
        "  - FB声明但未完成实现\n"
        "  - 编译配置问题导致未生成\n"
        "  - FB名称拼写错误"
    )

    # DIAG_003: 未使用的内存访问模式
    DIAG_003 = "DIAG_003"
    DIAG_003_DESC = "检测到可疑的内存访问模式"
    DIAG_003_DETAIL = (
        "发现可能存在问题的内存访问方式，如直接访问未初始化的变量或"
        "使用可能导致越界的索引操作。建议检查PLC程序的变量声明。"
    )

    # DIAG_004: 潜在的类型转换问题
    DIAG_004 = "DIAG_004"
    DIAG_004_DESC = "检测到潜在的不安全类型转换"
    DIAG_004_DETAIL = (
        "在Go代码中发现可能导致数据丢失或不一致的类型转换操作。"
        "建议验证原始SCL代码中的类型使用是否符合预期。"
    )


@dataclass
class FBCallInfo:
    """FB调用信息记录"""
    caller_name: str           # 调用者（OB名称）
    fb_name: str               # 被调用的FB/FC名称
    call_line: int             # 调用所在行号
    source_file: str           # 所在源文件
    source_line_ref: str       # SCL源码行引用（如 "d:/path/OB1.scl:19"）


class LSPCompatibilityChecker:
    """
    LSP兼容性检查器主类

    扫描Siemens LSP生成的Go代码，检测潜在的兼容性问题和错误模式。

    使用示例:
        >>> checker = LSPCompatibilityChecker(project_path)
        >>> report = checker.scan()
        >>> print(report.to_markdown())

    Attributes:
        project_path: 项目根目录路径
        plc_output_dir: .plc-output目录路径
        report: 生成的诊断报告对象
    """

    # 正则表达式模式定义
    # =====================

    # 匹配 builtin stub 调用模式: _ = builtins.B_xxx(...)
    # 例如: _ = builtins.B_TON(...)
    PATTERN_BUILTIN_STUB_MISUSE = re.compile(
        r'^\s*_\s*=\s*builtins\.B_\w+\s*\(',
        re.MULTILINE
    )

    # 匹配 OB 函数定义: func OB_xxx(mem *Memory) {
    PATTERN_OB_FUNCTION_DEF = re.compile(
        r'^func\s+(OB_\w+)\s*\(\s*mem\s*\*Memory\s*\)\s*\{',
        re.MULTILINE
    )

    # 匹配 FB 函数定义: func FB_xxx(mem *Memory, db *DB_xxx) {
    PATTERN_FB_FUNCTION_DEF = re.compile(
        r'^func\s+(FB_\w+)\s*\(\s*mem\s*\*Memory\s*,\s*db\s*\*\w+\s*\)\s*\{',
        re.MULTILINE
    )

    # 匹配 FB 调用: FB_xxx(mem, &mem.xxx)
    PATTERN_FB_CALL = re.compile(
        r'(FB_\w+)\s*\(\s*mem\s*,'
    )

    # 匹配 SCL 源码行引用: //line d:/path/file.scl:line:col
    PATTERN_SOURCE_LINE_REF = re.compile(
        r'//line\s+(.+?)(?::(\d+)(?::(\d+))?)?$'
    )

    # 匹配危险的类型转换: int16(xxx), int32(xxx) 等（用于DIAG_004）
    PATTERN_UNSAFE_TYPE_CAST = re.compile(
        r'(int8|int16|int32|int64|uint8|uint16|uint32|uint64)'
        r'\s*\(\s*[^)]+\s*\)'
    )

    # 匹配数组越界风险访问 (简化模式)
    PATTERN_RISKY_ARRAY_ACCESS = re.compile(
        r'\w+\[(?:\d+\s*[+\-]\s*\d+|\w+\s*[+\-]\s*\d+)\]'
    )

    def __init__(
        self,
        project_path: str,
        plc_output_name: str = ".plc-out"
    ):
        """
        初始化LSP兼容性检查器

        Args:
            project_path: PLC项目根目录路径
            plc_output_name: PLC输出目录名（默认为 .plc-out）
        """
        self.project_path = Path(project_path).resolve()
        self.plc_output_dir = self.project_path / plc_output_name / "golang"
        self.report = DiagnosticReport(
            project_name=self.project_path.name,
            project_path=str(self.project_path),
            plc_output_path=str(self.plc_output_dir),
        )

        # 分析结果缓存
        self._ob_functions: Dict[str, Tuple[str, int]] = {}   # {ob_name: (file, line)}
        self._fb_functions: Set[str] = set()                   # 实现的FB集合
        self._fb_call_chain: Dict[str, List[str]] = {}         # OB→FB调用链
        self._fb_call_details: List[FBCallInfo] = []           # FB调用详细信息

    def scan(self) -> DiagnosticReport:
        """
        执行完整的LSP兼容性扫描

        这是主要的扫描入口方法，按顺序执行所有诊断规则：
        1. 发现并扫描Go源文件
        2. 分析OB→FB调用链
        3. 验证FB实现完整性
        4. 检测stub误用和其他问题模式
        5. 生成完整报告

        Returns:
            DiagnosticReport: 包含所有诊断结果的报告对象
        """
        import time
        start_time = time.time()

        # 步骤1: 发现并读取Go文件
        go_files = self._discover_go_files()
        if not go_files:
            self.report.add_issue(DiagnosticIssue(
                rule_id=DiagnosticRules.DIAG_001,
                severity=DiagnosticSeverity.WARNING,
                message="未找到任何Go源文件，请确认.plc-out/golang目录存在",
                category="scan_error",
                suggestion="请先使用Siemens LSP编译项目以生成Go代码",
            ))
            return self.report

        self.report.scanned_files = [str(f) for f in go_files]

        # 步骤2: 分析每个Go文件
        for go_file in go_files:
            self._analyze_go_file(go_file)

        # 步骤3: 执行各诊断规则
        self._run_diagnostic_rules()

        # 记录扫描时间
        elapsed = time.time() - start_time
        self.report.scan_time = self.report.scan_time  # 保持原有时间

        return self.report

    def _discover_go_files(self) -> List[Path]:
        """
        发现.plc-out/golang目录下的所有.go文件

        Returns:
            List[Path]: Go文件路径列表
        """
        if not self.plc_output_dir.exists():
            return []

        go_files = []
        # 递归搜索所有.go文件，排除测试文件
        for file_path in self.plc_output_dir.rglob("*.go"):
            # 排除测试文件（*_test.go）
            if not file_path.name.endswith("_test.go"):
                go_files.append(file_path)

        return sorted(go_files)

    def _analyze_go_file(self, file_path: Path) -> None:
        """
        分析单个Go文件的内容

        提取OB/FB函数定义、调用关系等信息。

        Args:
            file_path: Go文件路径
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(self.plc_output_dir)

            # 提取OB函数定义
            self._extract_ob_functions(content, str(relative_path))

            # 提取FB函数定义
            self._extract_fb_functions(content)

            # 提取FB调用关系
            self._extract_fb_calls(content, str(relative_path))

        except Exception as e:
            # 文件读取错误，记录警告
            self.report.add_issue(DiagnosticIssue(
                rule_id=DiagnosticRules.DIAG_001,
                severity=DiagnosticSeverity.WARNING,
                message=f"无法读取文件: {e}",
                file_path=str(file_path.relative_to(self.plc_output_dir)),
                category="io_error",
                suggestion=f"请检查文件权限和编码: {file_path}",
            ))

    def _extract_ob_functions(
        self, content: str, relative_path: str
    ) -> None:
        """
        从Go代码中提取OB函数定义

        Args:
            content: Go文件内容
            relative_path: 相对路径
        """
        for match in self.PATTERN_OB_FUNCTION_DEF.finditer(content):
            ob_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            self._ob_functions[ob_name] = (relative_path, line_num)

    def _extract_fb_functions(self, content: str) -> None:
        """
        从Go代码中提取已实现的FB函数

        Args:
            content: Go文件内容
        """
        for match in self.PATTERN_FB_FUNCTION_DEF.finditer(content):
            fb_name = match.group(1)
            self._fb_functions.add(fb_name)

    def _extract_fb_calls(self, content: str, relative_path: str) -> None:
        """
        从OB函数中提取FB调用关系

        分析OB函数体内部对FB/FC的调用。

        Args:
            content: Go文件内容
            relative_path: 文件相对路径
        """
        lines = content.split('\n')
        current_ob: Optional[str] = None

        for line_num, line in enumerate(lines, 1):
            # 检测OB函数开始
            ob_match = self.PATTERN_OB_FUNCTION_DEF.match(line)
            if ob_match:
                current_ob = ob_match.group(1)
                if current_ob not in self._fb_call_chain:
                    self._fb_call_chain[current_ob] = []
                continue

            # 检测OB函数结束（简单的括号匹配）
            if current_ob and line.strip() == "}":
                current_ob = None
                continue

            # 在OB函数体内检测FB调用
            if current_ob:
                call_matches = self.PATTERN_FB_CALL.findall(line)
                for fb_name in call_matches:
                    # 记录调用关系
                    if fb_name not in self._fb_call_chain.get(current_ob, []):
                        self._fb_call_chain[current_ob].append(fb_name)

                    # 提取源码行引用
                    source_ref = self._extract_source_line_reference(lines, line_num)

                    # 记录详细调用信息
                    self._fb_call_details.append(FBCallInfo(
                        caller_name=current_ob,
                        fb_name=fb_name,
                        call_line=line_num,
                        source_file=relative_path,
                        source_line_ref=source_ref,
                    ))

    def _extract_source_line_reference(
        self, lines: List[str], current_line: int
    ) -> str:
        """
        从当前行向前查找最近的源码行引用注释

        Siemens LSP生成的Go代码包含 //line 注释，
        用于映射回原始SCL源码位置。

        Args:
            lines: 所有行的列表
            current_line: 当前行号（从1开始）

        Returns:
            str: 源码行引用字符串，如 "d:/path/OB1.scl:19"
        """
        # 向前搜索最多10行寻找 //line 注释
        search_start = max(0, current_line - 11)
        for i in range(current_line - 1, search_start, -1):
            if i < 0 or i >= len(lines):
                continue
            line_match = self.PATTERN_SOURCE_LINE_REF.search(lines[i])
            if line_match:
                source_path = line_match.group(1)
                source_line = line_match.group(2) or ""
                if source_line:
                    return f"{source_path}:{source_line}"
                return source_path
        return ""

    def _run_diagnostic_rules(self) -> None:
        """
        执行所有诊断规则检查

        按顺序运行4条诊断规则：
        - DIAG_001: Builtin stub误用检测
        - DIAG_002: 缺失FB实现检测
        - DIAG_003: 可疑内存访问检测
        - DIAG_004: 不安全类型转换检测
        """
        # 规则1: Builtin stub误用检测
        self._check_builtin_stub_misuse()

        # 规则2: 缺失FB实现检测
        self._check_missing_fb_implementations()

        # 规则3: 可疑内存访问检测
        self._check_risky_memory_access()

        # 规则4: 不安全类型转换检测
        self._check_unsafe_type_casts()

        # 更新报告的分析结果
        self.report.ob_fb_call_chain = self._fb_call_chain

    def _check_builtin_stub_misuse(self) -> None:
        """
        DIAG_001: 检测builtin stub误用模式

        在Go代码中搜索 `_ = builtins.B_xxx(...)` 模式。
        这种模式通常是LSP生成代码时的错误，表示：
        - 某个PLC指令被错误地转换为builtin stub调用
        - 可能会导致运行时panic或未定义行为
        """
        for file_path_str in self.report.scanned_files:
            file_path = Path(file_path_str)
            if not file_path.exists():
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                relative_path = str(file_path.relative_to(self.plc_output_dir))
                lines = content.split('\n')

                # 搜索所有stub误用模式
                for match in self.PATTERN_BUILTIN_STUB_MISUSE.finditer(content):
                    line_num = content[:match.start()].count('\n') + 1
                    matched_text = match.group(0).strip()

                    # 提取stub名称
                    stub_match = re.search(r'builtins\.(B_\w+)', matched_text)
                    stub_name = stub_match.group(1) if stub_match else "未知"

                    # 提取源码位置
                    source_ref = self._extract_source_line_reference(lines, line_num)

                    # 创建诊断问题
                    issue = DiagnosticIssue(
                        rule_id=DiagnosticRules.DIAG_001,
                        severity=DiagnosticSeverity.ERROR,
                        message=(
                            f"检测到builtin stub误用: {stub_name}。"
                            f"{DiagnosticRules.DIAG_001_DETAIL}"
                        ),
                        file_path=relative_path,
                        line_number=line_num,
                        category="stub_misuse",
                        code_snippet=matched_text,
                        source_line=source_ref,
                        related_symbols=[stub_name],
                        suggestion=(
                            f"检查SCL源码中对应位置的指令，"
                            f"确保正确使用系统函数。"
                            f"如确认为LSP bug，可考虑升级LSP版本或调整代码写法。"
                        ),
                    )
                    self.report.add_issue(issue)

                    # 记录到stub误用列表
                    self.report.stub_misuses.append({
                        "stub_name": stub_name,
                        "file_path": relative_path,
                        "line_number": line_num,
                        "usage_pattern": matched_text,
                        "source_location": source_ref,
                    })

            except Exception as e:
                self.report.add_issue(DiagnosticIssue(
                    rule_id=DiagnosticRules.DIAG_001,
                    severity=DiagnosticSeverity.WARNING,
                    message=f"分析文件时出错: {e}",
                    file_path=file_path_str,
                    category="analysis_error",
                ))

    def _check_missing_fb_implementations(self) -> None:
        """
        DIAG_002: 检查缺失的FB实现

        对比OB中调用的FB与实际实现的FB，
        找出被调用但未实现的FB/FC。
        """
        called_fbs: Set[str] = set()

        # 收集所有被调用的FB
        for ob_name, fb_list in self._fb_call_chain.items():
            called_fbs.update(fb_list)

        # 检查哪些被调用的FB没有实现
        missing_fbs = called_fbs - self._fb_functions

        for missing_fb in missing_fbs:
            # 找出是哪个OB调用了这个缺失的FB
            callers = [
                detail.caller_name
                for detail in self._fb_call_details
                if detail.fb_name == missing_fb
            ]

            # 获取第一个调用位置的详细信息
            first_call = next(
                (d for d in self._fb_call_details if d.fb_name == missing_fb),
                None
            )

            location_info = ""
            if first_call:
                location_info = f"{first_call.source_file}:{first_call.call_line}"
                if first_call.source_line_ref:
                    location_info += f" ({first_call.source_line_ref})"

            # 创建诊断问题
            issue = DiagnosticIssue(
                rule_id=DiagnosticRules.DIAG_002,
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"FB '{missing_fb}' 在OB中被调用但缺少实现。"
                    f"{DiagnosticRules.DIAG_002_DETAIL}"
                ),
                file_path=first_call.source_file if first_call else "",
                line_number=first_call.call_line if first_call else 0,
                category="missing_implementation",
                source_line=(
                    first_call.source_line_ref if first_call else None
                ),
                related_symbols=[missing_fb] + list(set(callers)),
                suggestion=(
                    f"请检查FB '{missing_fb}' 是否已正确创建并实现。"
                    f"可能的解决方案:\n"
                    f"  1. 确认FB声明文件存在且语法正确\n"
                    f"  2. 检查项目配置确保该FB被包含在编译范围内\n"
                    f"  3. 验证FB名称大小写是否匹配\n"
                    f"  4. 如果是外部库FB，确认库引用配置正确"
                ),
            )
            self.report.add_issue(issue)

            # 记录到缺失实现列表
            self.report.missing_implementations.append({
                "missing_fb": missing_fb,
                "callers": list(set(callers)),
                "location": location_info,
            })

    def _check_risky_memory_access(self) -> None:
        """
        DIAG_003: 检测可疑的内存访问模式

        搜索可能导致问题的数组访问或内存操作。
        这是一个启发式检查，可能会产生误报。
        """
        for file_path_str in self.report.scanned_files:
            file_path = Path(file_path_str)
            if not file_path.exists():
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                relative_path = str(file_path.relative_to(self.plc_output_dir))
                lines = content.split('\n')

                # 搜索可疑的数组访问模式
                for match in self.PATTERN_RISKY_ARRAY_ACCESS.finditer(content):
                    line_num = content[:match.start()].count('\n') + 1
                    matched_text = match.group(0)

                    # 排除明显的安全模式（简单索引）
                    if re.match(r'\w+\[\d+\]', matched_text):
                        continue

                    # 提取源码位置
                    source_ref = self._extract_source_line_reference(
                        lines, line_num
                    )

                    # 只在信息级别报告（启发式检查）
                    issue = DiagnosticIssue(
                        rule_id=DiagnosticRules.DIAG_003,
                        severity=DiagnosticSeverity.INFO,
                        message=(
                            f"检测到可疑的数组访问模式: {matched_text}。"
                            f"建议验证索引值范围。"
                        ),
                        file_path=relative_path,
                        line_number=line_num,
                        category="memory_access",
                        code_snippet=matched_text,
                        source_line=source_ref,
                        suggestion=(
                            "检查对应的SCL代码，确保数组索引不会越界。"
                            "如果这是预期的行为，可以忽略此提示。"
                        ),
                    )
                    self.report.add_issue(issue)

            except Exception:
                pass  # 此规则非关键，忽略读取错误

    def _check_unsafe_type_casts(self) -> None:
        """
        DIAG_004: 检测潜在的不安全类型转换

        查找Go代码中的显式类型转换，
        特别是可能导致数据丢失的窄化转换（如int32→int16）。
        """
        # 定义可能丢失数据的转换组合
        narrowing_casts = [
            (r'int32', r'int16'),
            (r'int32', r'int8'),
            (r'int64', r'int32'),
            (r'int64', r'int16'),
            (r'uint32', r'uint16'),
            (r'uint32', r'uint8'),
            (r'uint16', r'uint8'),
        ]

        for file_path_str in self.report.scanned_files:
            file_path = Path(file_path_str)
            if not file_path.exists():
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                relative_path = str(file_path.relative_to(self.plc_output_dir))
                lines = content.split('\n')

                # 搜索所有类型转换
                for match in self.PATTERN_UNSAFE_TYPE_CAST.finditer(content):
                    line_num = content[:match.start()].count('\n') + 1
                    cast_expr = match.group(0)

                    # 检查是否是窄化转换
                    is_narrowing = False
                    for from_type, to_type in narrowing_casts:
                        if re.search(f'{to_type}\\s*\\([^)]*{from_type}', cast_expr):
                            is_narrowing = True
                            break

                    # 确定严重级别
                    severity = (
                        DiagnosticSeverity.WARNING
                        if is_narrowing
                        else DiagnosticSeverity.INFO
                    )

                    # 提取源码位置
                    source_ref = self._extract_source_line_reference(
                        lines, line_num
                    )

                    issue = DiagnosticIssue(
                        rule_id=DiagnosticRules.DIAG_004,
                        severity=severity,
                        message=(
                            f"{'窄化' if is_narrowing else ''}类型转换: {cast_expr}"
                            f"。{'可能造成数据丢失！' if is_narrowing else ''}"
                        ),
                        file_path=relative_path,
                        line_number=line_num,
                        category="type_conversion",
                        code_snippet=cast_expr,
                        source_line=source_ref,
                        suggestion=(
                            "验证原始SCL代码中的类型使用是否符合业务逻辑需求。"
                            "如果是窄化转换，请确认溢出处理逻辑正确。"
                        ),
                    )
                    self.report.add_issue(issue)

            except Exception:
                pass  # 此规则非关键，忽略读取错误

    def get_call_chain_summary(self) -> Dict[str, Any]:
        """
        获取OB→FB调用链的摘要信息

        Returns:
            Dict: 包含调用链统计和分析结果的字典
        """
        total_ob_calls = sum(len(fbs) for fbs in self._fb_call_chain.values())
        unique_called_fbs = set()
        for fbs in self._fb_call_chain.values():
            unique_called_fbs.update(fbs)

        return {
            "total_ob_blocks": len(self._ob_functions),
            "total_fb_implemented": len(self._fb_functions),
            "total_fb_calls_from_ob": total_ob_calls,
            "unique_called_fbs": len(unique_called_fbs),
            "missing_implementations": len(unique_called_fbs - self._fb_functions),
            "call_chain_details": {
                ob_name: fb_list
                for ob_name, fb_list in self._fb_call_chain.items()
            },
        }

    def scan_single_file(self, file_path: str) -> List[DiagnosticIssue]:
        """
        扫描单个文件的快捷方法

        适用于IDE集成或实时检查场景。

        Args:
            file_path: 要扫描的Go文件路径

        Returns:
            List[DiagnosticIssue]: 该文件中发现的问题列表
        """
        path = Path(file_path)
        if not path.exists() or not path.suffix == ".go":
            return []

        # 临时重置报告
        original_issues = self.report.issues.copy()
        self.report.issues.clear()

        # 分析单个文件
        self._analyze_go_file(path)

        # 返回新发现的问题
        new_issues = self.report.issues.copy()

        # 恢复原始状态
        self.report.issues = original_issues

        return new_issues


# ============================================================
# 便捷函数
# ============================================================

def check_project_lsp_compatibility(
    project_path: str,
    output_format: str = "report"
) -> Any:
    """
    检查项目LSP兼容性的便捷函数

    Args:
        project_path: 项目路径
        output_format: 输出格式 ('report', 'dict', 'markdown', 'json')

    Returns:
        根据format参数返回不同格式的结果
    """
    checker = LSPCompatibilityChecker(project_path)
    report = checker.scan()

    if output_format == "dict":
        return report.to_dict()
    elif output_format == "markdown":
        return report.to_markdown()
    elif output_format == "json":
        return report.to_json_string()
    else:
        return report
