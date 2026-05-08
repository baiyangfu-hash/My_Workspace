"""
测试管理服务模块

本模块提供了PLC测试的完整生命周期管理功能，包括：
- 扫描和发现.scltest测试文件
- 调用plccheck test外部命令执行测试
- 实时捕获输出和进度更新
- 测试状态管理和历史记录
- 测试结果的持久化和查询

架构设计：
- 采用服务层模式，封装所有测试相关操作
- 通过subprocess调用外部PLC检查工具
- 支持异步执行和取消操作
- 提供回调机制用于UI集成

依赖项：
- subprocess: 外部命令调用
- threading/concurrent.futures: 异步执行
- json: 结果序列化
- pathlib: 文件路径操作

作者：双栖资深开发
版本：1.0.0
"""

import os
import sys
import json
import shutil
import subprocess
import threading
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Callable, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field

# 导入项目模块
from models.test_case import TestSuite, TestCase, StepType
from models.test_result import (
    TestResult, TestRunSummary, TestStatus, AssertionResult, AssertionStatus
)
from parsers.scltest_parser import SCLTestParser


@dataclass
class TestExecutionConfig:
    """
    测试执行配置

    定义测试运行的各种参数和选项。

    Attributes:
        timeout_seconds: 单个测试超时时间（秒）
        working_directory: 工作目录
        plccheck_path: plccheck可执行文件路径
        additional_args: 额外命令行参数
        environment_vars: 环境变量
        capture_output: 是否捕获输出
        verbose: 详细输出模式
    """
    timeout_seconds: int = 300  # 5分钟默认超时
    working_directory: Optional[Path] = None
    plccheck_path: Optional[str] = None
    additional_args: List[str] = field(default_factory=list)
    environment_vars: Dict[str, str] = field(default_factory=dict)
    capture_output: bool = True
    verbose: bool = False


class TestManagementService:
    """
    测试管理服务类

    提供PLC测试的完整管理功能，作为应用层与底层测试工具之间的桥梁。

    主要职责：
    1. 文件扫描：发现项目中的所有.scltest文件
    2. 解析管理：调用解析器提取测试用例
    3. 执行控制：启动、监控、取消测试执行
    4. 结果管理：收集、存储、查询测试结果
    5. 历史记录：维护测试执行历史

    使用示例：
        >>> service = TestManagementService(project_path)
        >>> suites = service.scan_test_files()
        >>> summary = service.run_tests(suites[0])
        >>> print(summary.generate_report_text())

    线程安全：
        - 所有公共方法都是线程安全的
        - 内部使用锁保护共享状态
    """

    # 支持的文件扩展名
    SCLTEST_EXTENSIONS = {'.scltest', '.SCLTEST'}

    # 默认的plccheck命令名
    DEFAULT_PLCHECK_COMMAND = 'plccheck'

    def __init__(
        self,
        project_path: Path,
        config: Optional[TestExecutionConfig] = None
    ):
        """
        初始化测试管理服务

        Args:
            project_path: 项目根目录路径
            config: 执行配置（可选）
        """
        self.project_path = Path(project_path).resolve()
        self.config = config or TestExecutionConfig()

        # 内部状态
        self._parser = SCLTestParser()
        self._lock = threading.RLock()
        self._current_run: Optional[TestRunSummary] = None
        self._is_running = False
        self._cancel_event = threading.Event()

        # 历史记录存储
        self._history: List[TestRunSummary] = []
        self._max_history_size = 100  # 最多保存100条历史

        # 回调函数（用于UI集成）
        self._on_progress_callback: Optional[Callable] = None
        self._on_complete_callback: Optional[Callable] = None
        self._on_output_callback: Optional[Callable[[str], None]] = None

        # 验证项目路径
        if not self.project_path.exists():
            raise ValueError(f"项目路径不存在: {self.project_path}")

    # ========================================================================
    # 文件扫描功能
    # ========================================================================

    def scan_test_files(
        self,
        search_path: Optional[Path] = None,
        recursive: bool = True
    ) -> List[Path]:
        """
        扫描目录下的所有SCLTest文件

        Args:
            search_path: 搜索路径（默认使用项目根目录）
            recursive: 是否递归搜索子目录

        Returns:
            找到的.scltest文件路径列表（排序后）
        """
        search_dir = search_path or self.project_path
        search_dir = Path(search_dir)

        if not search_dir.exists():
            return []

        found_files = []

        if recursive:
            for ext in self.SCLTEST_EXTENSIONS:
                found_files.extend(search_dir.rglob(f"*{ext}"))
        else:
            for ext in self.SCLTEST_EXTENSIONS:
                found_files.extend(search_dir.glob(f"*{ext}"))

        # 去重并排序
        seen = set()
        unique_files = []
        for f in found_files:
            if f not in seen:
                seen.add(f)
                unique_files.append(f)

        unique_files.sort()
        return unique_files

    def parse_test_file(self, file_path: Path) -> Optional[TestSuite]:
        """
        解析单个测试文件

        Args:
            file_path: .scltest文件路径

        Returns:
            解析后的TestSuite对象，失败返回None
        """
        try:
            return self._parser.parse_file(file_path)
        except Exception as e:
            print(f"解析文件失败 {file_path}: {e}")
            return None

    def parse_all_test_files(
        self,
        file_list: Optional[List[Path]] = None
    ) -> List[TestSuite]:
        """
        批量解析多个测试文件

        Args:
            file_list: 文件路径列表（None则自动扫描）

        Returns:
            TestSuite对象列表
        """
        files = file_list or self.scan_test_files()
        suites = []

        for file_path in files:
            suite = self.parse_test_file(file_path)
            if suite:
                suites.append(suite)

        return suites

    # ========================================================================
    # 测试执行功能
    # ========================================================================

    def run_tests(
        self,
        suite: TestSuite,
        test_names: Optional[List[str]] = None,
        config: Optional[TestExecutionConfig] = None
    ) -> TestRunSummary:
        """
        执行测试套件中的测试用例

        这是同步执行接口，会阻塞直到所有测试完成。

        Args:
            suite: 要执行的测试套件
            test_names: 指定要执行的测试用例名称（None=全部）
            config: 本次执行的配置覆盖

        Returns:
            TestRunSummary 包含所有测试结果
        """
        exec_config = config or self.config

        with self._lock:
            if self._is_running:
                raise RuntimeError("已有测试正在运行")

            self._is_running = True
            self._cancel_event.clear()

        try:
            # 创建运行摘要
            summary = TestRunSummary(
                run_id=str(uuid.uuid4())[:8],
                start_time=datetime.now(),
                suite_file_path=suite.file_path,
                project_path=self.project_path,
                filter_pattern=",".join(test_names) if test_names else ""
            )
            self._current_run = summary

            # 过滤要执行的测试用例
            tests_to_run = suite.test_cases
            if test_names:
                tests_to_run = [
                    tc for tc in suite.test_cases
                    if tc.name in test_names
                ]

            # 逐个执行测试用例
            for i, test_case in enumerate(tests_to_run):
                # 检查取消请求
                if self._cancel_event.is_set():
                    break

                # 报告进度
                self._report_progress(i, len(tests_to_run), test_case.name)

                # 执行单个测试用例
                result = self._execute_single_test(test_case, exec_config)
                summary.test_results.append(result)

            # 完成运行
            summary.end_time = datetime.now()
            summary.calculate_duration()

            # 保存到历史
            self._add_to_history(summary)

            return summary

        finally:
            with self._lock:
                self._is_running = False
                self._current_run = None

            # 触发完成回调
            if self._on_complete_callback:
                try:
                    self._on_complete_callback(summary)
                except Exception:
                    pass

    def run_tests_async(
        self,
        suite: TestSuite,
        test_names: Optional[List[str]] = None,
        config: Optional[TestExecutionConfig] = None
    ) -> Future:
        """
        异步执行测试

        在后台线程中运行测试，立即返回Future对象。

        Args:
            suite: 测试套件
            test_names: 要执行的测试名称
            config: 执行配置

        Returns:
            Future对象，可通过result()获取最终结果
        """
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(
            self.run_tests,
            suite,
            test_names,
            config
        )
        return future

    def cancel_running_tests(self):
        """
        取消当前正在运行的测试

        发出取消请求后，测试会在下一个安全点停止。
        """
        self._cancel_event.set()

    @property
    def is_running(self) -> bool:
        """是否有测试正在运行"""
        with self._lock:
            return self._is_running

    @property
    def current_run(self) -> Optional[TestRunSummary]:
        """获取当前运行的摘要"""
        with self._lock:
            return self._current_run

    # ========================================================================
    # 内部执行逻辑
    # ========================================================================

    def _execute_single_test(
        self,
        test_case: TestCase,
        config: TestExecutionConfig
    ) -> TestResult:
        """
        执行单个测试用例

        通过调用plccheck test命令来执行测试。

        Args:
            test_case: 测试用例
            config: 执行配置

        Returns:
            TestResult对象
        """
        result = TestResult(
            test_case_name=test_case.name,
            file_path=test_case.file_path,
            start_time=datetime.now(),
            status=TestStatus.ERROR  # 默认为ERROR，成功后会修改
        )

        try:
            # 构建命令
            cmd = self._build_plccheck_command(test_case, config)

            # 设置工作目录
            cwd = str(config.working_directory or self.project_path)

            # 准备环境变量
            env = os.environ.copy()
            env.update(config.environment_vars)

            # 执行命令
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd,
                env=env,
                shell=False,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )

            # 等待完成（带超时和取消支持）
            try:
                stdout, stderr = process.communicate(
                    timeout=config.timeout_seconds
                )
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                result.error_message = f"执行超时 ({config.timeout_seconds}秒)"
                result.status = TestStatus.ERROR
                result.exit_code = -1
            except Exception as e:
                if self._cancel_event.is_set():
                    process.terminate()
                    stdout, stderr = process.communicate()
                    result.error_message = "用户取消"
                    result.status = TestStatus.SKIPPED
                    result.exit_code = -1
                else:
                    raise

            # 记录输出
            result.stdout_output = stdout
            result.stderr_output = stderr
            result.exit_code = process.returncode
            result.end_time = datetime.now()
            result.calculate_duration()

            # 解析输出，提取断言结果
            self._parse_test_output(result, stdout, stderr)

            # 根据退出码和断言结果确定状态
            if result.exit_code == 0 and all(
                ar.is_passed for ar in result.assertion_results
            ):
                result.status = TestStatus.PASSED
            elif result.exit_code != 0:
                result.status = TestStatus.FAILED
            else:
                result.status = TestStatus.FAILED

            # 实时输出回调
            if self._on_output_callback and stdout:
                try:
                    self._on_output_callback(stdout)
                except Exception:
                    pass

        except Exception as e:
            result.error_message = str(e)
            result.status = TestStatus.ERROR
            result.end_time = datetime.now()
            result.calculate_duration()

        return result

    def _build_plccheck_command(
        self,
        test_case: TestCase,
        config: TestExecutionConfig
    ) -> List[str]:
        """
        构建plccheck命令行

        Args:
            test_case: 测试用例
            config: 配置

        Returns:
            命令参数列表
        """
        # 确定plccheck可执行文件路径
        plccheck = config.plccheck_path or self.DEFAULT_PLCCHECK_COMMAND

        # 基础命令
        cmd = [plccheck, 'test']

        # 添加测试文件
        if test_case.file_path:
            cmd.extend(['--file', str(test_case.file_path)])

        # 指定测试用例名称
        cmd.extend(['--test-case', test_case.name])

        # 添加额外参数
        cmd.extend(config.additional_args)

        # 保存命令行到配置（用于调试）
        if self._current_run:
            self._current_run.command_line = ' '.join(cmd)

        return cmd

    def _parse_test_output(
        self,
        result: TestResult,
        stdout: str,
        stderr: str
    ):
        """
        解析plccheck输出，提取断言结果

        解析plccheck test的标准输出格式，提取每个断言的执行情况。

        注意：具体的输出格式取决于plccheck版本，
        这里提供通用的解析框架，可能需要根据实际情况调整。

        Args:
            result: 要填充的TestResult对象
            stdout: 标准输出
            stderr: 标准错误
        """
        # TODO: 根据实际的plccheck输出格式实现解析逻辑
        # 这里提供一个框架性的实现

        output = stdout + "\n" + stderr
        lines = output.splitlines()

        # 示例模式：寻找类似 "PASS: variable = value" 或 "FAIL: variable = expected != actual"
        # 这需要根据实际的plccheck输出格式进行调整

        import re

        # 尝试匹配断言结果行
        assert_pattern = re.compile(
            r'(PASS|FAIL|ERROR):\s*(\w+)\s*=\s*(.+?)(?:\s*expected:\s*(.+))?',
            re.IGNORECASE
        )

        for line in lines:
            match = assert_pattern.search(line)
            if match:
                status_str = match.group(1).upper()
                variable = match.group(2)
                actual = match.group(3)
                expected = match.group(4)

                status_map = {
                    'PASS': AssertionStatus.PASSED,
                    'FAIL': AssertionStatus.FAILED,
                    'ERROR': AssertionStatus.ERROR
                }

                assertion = AssertionResult(
                    variable=variable,
                    expected_value=expected or actual,
                    actual_value=actual,
                    status=status_map.get(status_str, AssertionStatus.ERROR)
                )
                result.assertion_results.append(assertion)

        # 如果没有从输出中解析出断言结果，创建默认的占位结果
        # （这种情况发生在plccheck不支持详细输出格式时）
        if not result.assertion_results:
            # 基于测试用例的定义创建占位断言结果
            from models.test_case import StepType
            for step in self._get_test_case_by_name(result.test_case_name).steps:
                if step.step_type == StepType.ASSERT:
                    assertion = AssertionResult(
                        variable=step.variable,
                        expected_value=step.value,
                        actual_value=None,
                        status=AssertionStatus.SKIPPED,
                        error_message="无法从输出中解析断言结果"
                    )
                    result.assertion_results.append(assertion)

    def _get_test_case_by_name(self, name: str) -> Optional[TestCase]:
        """根据名称获取测试用例定义（辅助方法）"""
        # 这个方法应该访问当前的TestSuite
        # 简化实现，实际可能需要重构
        return None

    # ========================================================================
    # 进度报告和回调
    # ========================================================================

    def _report_progress(
        self,
        current: int,
        total: int,
        test_name: str
    ):
        """
        报告执行进度

        Args:
            current: 当前进度
            total: 总数
            test_name: 当前测试用例名
        """
        if self._on_progress_callback:
            try:
                progress_data = {
                    'current': current,
                    'total': total,
                    'percentage': (current / total * 100) if total > 0 else 0,
                    'current_test': test_name
                }
                self._on_progress_callback(progress_data)
            except Exception:
                pass

    def set_progress_callback(self, callback: Callable):
        """
        设置进度回调函数

        Args:
            callback: 回调函数，签名: callback(progress_dict)
        """
        self._on_progress_callback = callback

    def set_complete_callback(self, callback: Callable):
        """
        设置完成回调函数

        Args:
            callback: 回调函数，签名: callback(TestRunSummary)
        """
        self._on_complete_callback = callback

    def set_output_callback(self, callback: Callable[[str], None]):
        """
        设置输出回调函数

        Args:
            callback: 回调函数，接收输出文本
        """
        self._on_output_callback = callback

    # ========================================================================
    # 历史记录功能
    # ========================================================================

    def _add_to_history(self, summary: TestRunSummary):
        """
        添加运行记录到历史

        Args:
            summary: 运行摘要
        """
        with self._lock:
            self._history.append(summary)

            # 限制历史记录数量
            while len(self._history) > self._max_history_size:
                self._history.pop(0)

    def get_history(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> List[TestRunSummary]:
        """
        获取历史记录

        Args:
            limit: 返回条数上限
            offset: 起始偏移

        Returns:
            历史记录列表（按时间倒序）
        """
        with self._lock:
            history_copy = list(reversed(self._history))
            return history_copy[offset:offset + limit]

    def get_latest_summary(self) -> Optional[TestRunSummary]:
        """
        获取最近一次运行的摘要

        Returns:
            最新的TestRunSummary，如果没有则返回None
        """
        with self._lock:
            return self._history[-1] if self._history else None

    def clear_history(self):
        """清空历史记录"""
        with self._lock:
            self._history.clear()

    def export_history_json(self, output_path: Path):
        """
        导出历史记录为JSON文件

        Args:
            output_path: 输出文件路径
        """
        with self._lock:
            data = {
                'export_time': datetime.now().isoformat(),
                'total_records': len(self._history),
                'records': [record.to_dict() for record in self._history]
            }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_history_json(self, input_path: Path):
        """
        从JSON文件导入历史记录

        Args:
            input_path: 输入文件路径
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        imported = []
        for record_data in data.get('records', []):
            summary = TestRunSummary.from_dict(record_data)
            imported.append(summary)

        with self._lock:
            self._history.extend(imported)

            # 限制大小
            while len(self._history) > self._max_history_size:
                self._history.pop(0)

    # ========================================================================
    # 统计和分析
    # ========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取测试统计数据

        Returns:
            包含各项统计数据的字典
        """
        with self._lock:
            if not self._history:
                return {
                    'total_runs': 0,
                    'total_tests': 0,
                    'average_success_rate': 0.0,
                    'last_run_time': None
                }

            total_tests = sum(h.total_tests for h in self._history)
            total_passed = sum(h.passed_tests for h in self._history)

            avg_rate = (
                (total_passed / total_tests * 100)
                if total_tests > 0 else 0.0
            )

            return {
                'total_runs': len(self._history),
                'total_tests': total_tests,
                'total_passed': total_passed,
                'average_success_rate': round(avg_rate, 2),
                'last_run_time': self._history[-1].start_time.isoformat()
                                if self._history else None,
                'recent_failures': sum(1 for h in self._history[-10:] if h.has_failures)
            }


# ============================================================================
# 便捷函数
# ============================================================================

def create_test_service(
    project_path: Path,
    **kwargs
) -> TestManagementService:
    """
    创建测试管理服务的工厂函数

    Args:
        project_path: 项目路径
        **kwargs: 传递给TestExecutionConfig的参数

    Returns:
        配置好的TestManagementService实例
    """
    config = TestExecutionConfig(**{
        k: v for k, v in kwargs.items()
        if hasattr(TestExecutionConfig, k)
    })

    return TestManagementService(project_path, config)


if __name__ == "__main__":
    # 简单演示
    import sys

    if len(sys.argv) > 1:
        project = Path(sys.argv[1])
        print(f"项目路径: {project}")

        service = TestManagementService(project)

        # 扫描测试文件
        files = service.scan_test_files()
        print(f"\n找到 {len(files)} 个测试文件:")
        for f in files:
            print(f"  - {f.relative_to(project)}")

        # 解析第一个文件
        if files:
            suite = service.parse_test_file(files[0])
            print(f"\n解析 {files[0].name}:")
            print(f"  测试用例: {suite.test_case_count}")
            for tc in suite.test_cases:
                print(f"    - {tc.name}: {tc.step_count} 步骤")
    else:
        print("用法: python test_management_service.py <项目路径>")
