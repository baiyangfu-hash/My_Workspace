"""
测试结果数据模型模块

本模块定义了PLC测试执行的结果数据结构，包括：
- TestResult: 单个测试用例的执行结果
- AssertionResult: 单个断言语句的执行结果
- TestRunSummary: 一次测试运行的总结统计

设计原则：
- 完整记录测试执行的详细信息
- 支持多种状态：PASSED/FAILED/ERROR/SKIPPED
- 提供丰富的统计和分析方法
- 支持时间戳和耗时追踪
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path


class TestStatus(Enum):
    """测试状态枚举"""
    PASSED = auto()      # 测试通过
    FAILED = auto()      # 测试失败（断言不满足）
    ERROR = auto()       # 执行错误（异常或超时）
    SKIPPED = auto()     # 跳过未执行


class AssertionStatus(Enum):
    """断言状态枚举"""
    PASSED = auto()      # 断言通过
    FAILED = auto()      # 断言失败（实际值不等于期望值）
    ERROR = auto()       # 断言执行错误
    SKIPPED = auto()     # 未执行


@dataclass
class AssertionResult:
    """
    断言结果数据类

    记录单个ASSERT语句的执行结果。

    Attributes:
        variable: 被断言的变量名
        expected_value: 期望值
        actual_value: 实际值（执行后获得）
        status: 断言状态（PASSED/FAILED/ERROR/SKIPPED）
        error_message: 错误信息（如有）
        execution_time_ms: 执行耗时（毫秒）
        line_number: 源代码行号
    """
    variable: str
    expected_value: Any
    actual_value: Any = None
    status: AssertionStatus = AssertionStatus.SKIPPED
    error_message: str = ""
    execution_time_ms: float = 0.0
    line_number: int = 0

    @property
    def is_passed(self) -> bool:
        """断言是否通过"""
        return self.status == AssertionStatus.PASSED

    @property
    def is_failed(self) -> bool:
        """断言是否失败"""
        return self.status == AssertionStatus.FAILED

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'variable': self.variable,
            'expected_value': self.expected_value,
            'actual_value': self.actual_value,
            'status': self.status.name,
            'error_message': self.error_message,
            'execution_time_ms': self.execution_time_ms,
            'line_number': self.line_number
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssertionResult':
        """从字典创建"""
        return cls(
            variable=data['variable'],
            expected_value=data['expected_value'],
            actual_value=data.get('actual_value'),
            status=AssertionStatus[data['status']],
            error_message=data.get('error_message', ''),
            execution_time_ms=data.get('execution_time_ms', 0.0),
            line_number=data.get('line_number', 0)
        )

    def __str__(self) -> str:
        """可读字符串"""
        if self.status == AssertionStatus.PASSED:
            return f"✓ {self.variable} = {self.actual_value} (expected {self.expected_value})"
        elif self.status == AssertionStatus.FAILED:
            return f"✗ {self.variable} = {self.actual_value} (expected {self.expected_value})"
        elif self.status == AssertionStatus.ERROR:
            return f"⚠ {self.variable}: ERROR - {self.error_message}"
        return f"- {self.variable}: SKIPPED"


@dataclass
class TestResult:
    """
    测试结果数据类

    记录单个测试用例的完整执行结果。

    Attributes:
        test_case_name: 测试用例名称
        file_path: 源文件路径
        status: 总体测试状态
        assertion_results: 所有断言的结果列表
        start_time: 开始执行时间
        end_time: 结束执行时间
        duration_seconds: 执行时长（秒）
        error_message: 错误信息（如有）
        stdout_output: 标准输出内容
        stderr_output: 标准错误输出
        exit_code: 进程退出码
    """
    test_case_name: str
    file_path: Optional[Path] = None
    status: TestStatus = TestStatus.SKIPPED
    assertion_results: List[AssertionResult] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    error_message: str = ""
    stdout_output: str = ""
    stderr_output: str = ""
    exit_code: Optional[int] = None

    @property
    def assertion_count(self) -> int:
        """断言总数"""
        return len(self.assertion_results)

    @property
    def passed_assertions(self) -> int:
        """通过的断言数"""
        return sum(1 for ar in self.assertion_results if ar.is_passed)

    @property
    def failed_assertions(self) -> int:
        """失败的断言数"""
        return sum(1 for ar in self.assertion_results if ar.is_failed)

    @property
    def error_assertions(self) -> int:
        """出错的断言数"""
        return sum(1 for ar in self.assertion_results if ar.status == AssertionStatus.ERROR)

    @property
    def is_passed(self) -> bool:
        """测试是否通过"""
        return self.status == TestStatus.PASSED

    @property
    def is_failed(self) -> bool:
        """测试是否失败"""
        return self.status == TestStatus.FAILED

    @property
    def has_error(self) -> bool:
        """是否有错误"""
        return self.status == TestStatus.ERROR

    def calculate_duration(self) -> float:
        """计算并返回执行时长"""
        if self.start_time and self.end_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        return self.duration_seconds

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'test_case_name': self.test_case_name,
            'file_path': str(self.file_path) if self.file_path else None,
            'status': self.status.name,
            'assertion_results': [ar.to_dict() for ar in self.assertion_results],
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'error_message': self.error_message,
            'stdout_output': self.stdout_output,
            'stderr_output': self.stderr_output,
            'exit_code': self.exit_code
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestResult':
        """从字典创建"""
        return cls(
            test_case_name=data['test_case_name'],
            file_path=Path(data['file_path']) if data.get('file_path') else None,
            status=TestStatus[data['status']],
            assertion_results=[
                AssertionResult.from_dict(ar) for ar in data.get('assertion_results', [])
            ],
            start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else None,
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            duration_seconds=data.get('duration_seconds', 0.0),
            error_message=data.get('error_message', ''),
            stdout_output=data.get('stdout_output', ''),
            stderr_output=data.get('stderr_output', ''),
            exit_code=data.get('exit_code')
        )

    def __str__(self) -> str:
        """可读字符串"""
        status_icon = {
            TestStatus.PASSED: '✓',
            TestStatus.FAILED: '✗',
            TestStatus.ERROR: '⚠',
            TestStatus.SKIPPED: '-'
        }.get(self.status, '?')

        info = f"{status_icon} {self.test_case_name} [{self.status.name}]"
        if self.duration_seconds > 0:
            info += f" ({self.duration_seconds:.3f}s)"
        if self.assertion_count > 0:
            info += f" - {self.passed_assertions}/{self.assertion_count} assertions"
        return info

    def __repr__(self) -> str:
        """详细表示"""
        return (
            f"TestResult(name='{self.test_case_name}', "
            f"status={self.status.name}, "
            f"assertions={self.passed_assertions}/{self.assertion_count})"
        )


@dataclass
class TestRunSummary:
    """
    测试运行总结数据类

    记录一次完整测试运行的统计信息和元数据。

    Attributes:
        run_id: 运行唯一标识符
        start_time: 运行开始时间
        end_time: 运行结束时间
        total_duration_seconds: 总运行时长
        test_results: 所有测试结果列表
        suite_file_path: 测试套件文件路径
        project_path: 项目根目录路径
        plccheck_version: PLC检查工具版本
        command_line: 执行的命令行
        filter_pattern: 测试用例过滤模式
    """
    run_id: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    test_results: List[TestResult] = field(default_factory=list)
    suite_file_path: Optional[Path] = None
    project_path: Optional[Path] = None
    plccheck_version: str = ""
    command_line: str = ""
    filter_pattern: str = ""

    @property
    def total_tests(self) -> int:
        """测试用例总数"""
        return len(self.test_results)

    @property
    def passed_tests(self) -> int:
        """通过的测试数"""
        return sum(1 for tr in self.test_results if tr.is_passed)

    @property
    def failed_tests(self) -> int:
        """失败的测试数"""
        return sum(1 for tr in self.test_results if tr.is_failed)

    @property
    def error_tests(self) -> int:
        """出错的测试数"""
        return sum(1 for tr in self.test_results if tr.has_error)

    @property
    def skipped_tests(self) -> int:
        """跳过的测试数"""
        return sum(1 for tr in self.test_results if tr.status == TestStatus.SKIPPED)

    @property
    def success_rate(self) -> float:
        """成功率（百分比）"""
        if self.total_tests == 0:
            return 0.0
        executed = self.total_tests - self.skipped_tests
        if executed == 0:
            return 0.0
        return (self.passed_tests / executed) * 100.0

    @property
    def total_assertions(self) -> int:
        """总断言数"""
        return sum(tr.assertion_count for tr in self.test_results)

    @property
    def passed_assertions(self) -> int:
        """总通过断言数"""
        return sum(tr.passed_assertions for tr in self.test_results)

    @property
    def failed_assertions(self) -> int:
        """总失败断言数"""
        return sum(tr.failed_assertions for tr in self.test_results)

    @property
    def all_passed(self) -> bool:
        """是否全部通过"""
        return self.failed_tests == 0 and self.error_tests == 0 and self.passed_tests > 0

    @property
    def has_failures(self) -> bool:
        """是否有失败"""
        return self.failed_tests > 0 or self.error_tests > 0

    def calculate_duration(self) -> float:
        """计算总运行时长"""
        if self.start_time and self.end_time:
            self.total_duration_seconds = (self.end_time - self.start_time).total_seconds()
        return self.total_duration_seconds

    def get_result_by_name(self, test_name: str) -> Optional[TestResult]:
        """按测试用例名查找结果"""
        for tr in self.test_results:
            if tr.test_case_name == test_name:
                return tr
        return None

    def get_failed_results(self) -> List[TestResult]:
        """获取所有失败/错误的结果"""
        return [
            tr for tr in self.test_results
            if tr.is_failed or tr.has_error
        ]

    def generate_report_text(self) -> str:
        """生成文本格式的测试报告"""
        lines = [
            "=" * 70,
            "PLC TEST EXECUTION REPORT",
            "=" * 70,
            "",
            f"Run ID:          {self.run_id}",
            f"Timestamp:       {self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else 'N/A'}",
            f"Duration:        {self.total_duration_seconds:.3f}s",
            f"Suite File:      {self.suite_file_path.name if self.suite_file_path else 'N/A'}",
            f"Filter Pattern:  {self.filter_pattern or '(none)'}",
            "",
            "-" * 70,
            "RESULTS SUMMARY",
            "-" * 70,
            f"Total Tests:     {self.total_tests}",
            f"  Passed:        {self.passed_tests}",
            f"  Failed:        {self.failed_tests}",
            f"  Error:         {self.error_tests}",
            f"  Skipped:       {self.skipped_tests}",
            f"",
            f"Success Rate:    {self.success_rate:.1f}%",
            f"Total Assertions:{self.total_assertions} ({self.passed_assertions} passed)",
            "",
        ]

        if self.test_results:
            lines.extend([
                "-" * 70,
                "DETAILED RESULTS",
                "-" * 70
            ])
            for tr in self.test_results:
                lines.append(str(tr))
                if tr.is_failed or tr.has_error:
                    if tr.error_message:
                        lines.append(f"  Error: {tr.error_message}")
                    for ar in tr.assertion_results:
                        if not ar.is_passed:
                            lines.append(f"  {ar}")
                lines.append("")

        lines.extend([
            "=" * 70,
            f"STATUS: {'ALL TESTS PASSED' if self.all_passed else 'TESTS FAILED'}",
            "=" * 70
        ])

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'run_id': self.run_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_duration_seconds': self.total_duration_seconds,
            'test_results': [tr.to_dict() for tr in self.test_results],
            'suite_file_path': str(self.suite_file_path) if self.suite_file_path else None,
            'project_path': str(self.project_path) if self.project_path else None,
            'plccheck_version': self.plccheck_version,
            'command_line': self.command_line,
            'filter_pattern': self.filter_pattern,
            'summary_stats': {
                'total_tests': self.total_tests,
                'passed_tests': self.passed_tests,
                'failed_tests': self.failed_tests,
                'error_tests': self.error_tests,
                'skipped_tests': self.skipped_tests,
                'success_rate': self.success_rate,
                'total_assertions': self.total_assertions,
                'passed_assertions': self.passed_assertions,
                'all_passed': self.all_passed
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestRunSummary':
        """从字典创建"""
        summary = cls(
            run_id=data.get('run_id', ''),
            start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else None,
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            total_duration_seconds=data.get('total_duration_seconds', 0.0),
            suite_file_path=Path(data['suite_file_path']) if data.get('suite_file_path') else None,
            project_path=Path(data['project_path']) if data.get('project_path') else None,
            plccheck_version=data.get('plccheck_version', ''),
            command_line=data.get('command_line', ''),
            filter_pattern=data.get('filter_pattern', '')
        )
        summary.test_results = [
            TestResult.from_dict(tr) for tr in data.get('test_results', [])
        ]
        return summary

    def __str__(self) -> str:
        """简短摘要"""
        status = "PASSED" if self.all_passed else "FAILED"
        return (
            f"TestRunSummary: {self.passed_tests}/{self.total_tests} passed, "
            f"{self.total_duration_seconds:.2f}s [{status}]"
        )

    def __repr__(self) -> str:
        """详细表示"""
        return (
            f"TestRunSummary(tests={self.total_tests}, "
            f"passed={self.passed_tests}, "
            f"failed={self.failed_tests}, "
            f"errors={self.error_tests}, "
            f"duration={self.total_duration_seconds:.2f}s)"
        )
