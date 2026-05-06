# -*- coding: utf-8 -*-
"""
PLC服务层 - 集成检查、诊断和测试功能

提供完整的PLC项目分析服务，包括：
- 规范检查：集成TimerChecker, NamingChecker, SyntaxChecker, CommentChecker, ConfigChecker
- 深度诊断：集成LSPCompatibilityChecker, ProjectHealthAnalyzer
- 测试执行：集成TestManagementService

设计原则：
- 高内聚低耦合：服务层封装业务逻辑，UI层只负责展示
- 统一接口：通过标准化的方法对外提供服务
- 容错处理：所有方法都有try-except保护和日志记录
- 延迟导入：避免循环依赖，按需加载模块
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class PLCService:
    """
    PLC服务类 - 提供完整的PLC项目分析功能

    职责：
    - 管理检查器生命周期（注册、初始化、执行）
    - 协调诊断器进行深度分析
    - 执行测试用例并收集结果
    - 统一错误处理和日志记录

    使用示例：
        >>> service = PLCService()
        >>> service.initialize_checkers()
        >>> report = service.check_specifications("/path/to/project")
        >>> diagnostic = service.run_diagnostics("/path/to/project")
        >>> test_results = service.run_tests("/path/to/project")
    """

    def __init__(self):
        """初始化PLC服务"""
        # 检查器注册表
        self._checkers: Dict[str, Any] = {}
        self._checkers_initialized = False

        # 诊断器实例（延迟初始化）
        self._lsp_checker = None
        self._health_analyzer = None

        # 测试服务实例（延迟初始化）
        self._test_service = None

        logger.info("PLC服务初始化完成")

    # ===== 检查器管理方法 =====

    def initialize_checkers(self) -> bool:
        """
        初始化并注册所有检查器

        注册的检查器包括：
        - TimerChecker: 定时器使用规范检查
        - NamingChecker: 变量命名规范检查
        - SyntaxChecker: ST语法结构检查
        - CommentChecker: 注释规范检查
        - ConfigChecker: 配置文件检查

        Returns:
            bool: 初始化成功返回True，失败返回False
        """
        if self._checkers_initialized:
            logger.warning("检查器已经初始化过，跳过重复初始化")
            return True

        try:
            # 导入基础检查器类
            from src.checkers.timer_checker import TimerChecker
            from src.checkers.naming_checker import NamingChecker
            from src.checkers.syntax_checker import SyntaxChecker
            from src.checkers.comment_checker import CommentChecker
            from src.checkers.config_checker import ConfigChecker

            # 创建检查器实例
            checker_classes = {
                'timer': TimerChecker,
                'naming': NamingChecker,
                'syntax': SyntaxChecker,
                'comment': CommentChecker,
                'config': ConfigChecker,
            }

            # 初始化每个检查器
            for name, checker_class in checker_classes.items():
                try:
                    instance = checker_class()
                    self._checkers[name] = instance
                    logger.debug(f"检查器已注册: {name} - {instance.rule_info.rule_id}")
                except Exception as e:
                    logger.error(f"初始化检查器 {name} 失败: {e}")

            self._checkers_initialized = True
            logger.info(f"检查器初始化完成，共注册 {len(self._checkers)} 个检查器")
            return True

        except ImportError as e:
            logger.error(f"导入检查器模块失败: {e}")
            return False
        except Exception as e:
            logger.exception(f"检查器初始化过程发生异常: {e}")
            return False

    def check_specifications(
        self,
        project_path: str,
        file_path: Optional[str] = None
    ) -> Any:
        """
        执行规范检查

        对指定的PLC项目或单个文件执行完整的规范检查，
        包括命名规范、语法结构、注释规范等。

        Args:
            project_path: 项目根目录路径
            file_path: 单个文件路径（可选，不指定则检查整个项目）

        Returns:
            CheckReport: 检查报告对象，包含所有违规记录和统计信息
        """
        try:
            # 确保检查器已初始化
            if not self._checkers_initialized:
                self.initialize_checkers()

            from src.models.check_result import CheckReport
            from pathlib import Path

            # 创建报告对象
            report = CheckReport(
                project_name=Path(project_path).name,
                project_path=project_path,
            )

            # 确定要检查的文件列表
            if file_path:
                files_to_check = [file_path]
            else:
                files_to_check = self._collect_st_files(project_path)

            if not files_to_check:
                logger.warning(f"未找到ST源码文件: {project_path}")
                return report

            logger.info(f"开始规范检查: {len(files_to_check)} 个文件")

            # 逐文件执行检查
            for file_path_item in files_to_check:
                try:
                    # 读取文件内容
                    with open(file_path_item, 'r', encoding='utf-8') as f:
                        source_code = f.read()

                    # 创建文件结果对象
                    from src.models.check_result import CheckResult
                    file_result = CheckResult(source_file=file_path_item)

                    # 执行所有检查器
                    for checker_name, checker in self._checkers.items():
                        if not checker.is_enabled():
                            continue

                        try:
                            violations = checker.check(
                                source_code,
                                file_path=file_path_item,
                            )
                            if violations:
                                file_result.add_violations(violations)
                                logger.debug(
                                    f"{checker_name} 在 {Path(file_path_item).name} "
                                    f"发现 {len(violations)} 个问题"
                                )
                        except Exception as e:
                            logger.error(
                                f"检查器 {checker_name} 执行异常: {e}"
                            )

                    # 添加文件结果到报告
                    report.add_result(file_result)

                except Exception as e:
                    logger.error(f"处理文件失败: {file_path_item} - {e}")

            # 输出检查摘要
            logger.info(
                f"规范检查完成 - "
                f"总计: {report.total_violations} 个问题 "
                f"(错误:{report.total_errors}, "
                f"警告:{report.total_warnings}, "
                f"提示:{report.total_infos})"
            )

            return report

        except Exception as e:
            logger.exception(f"规范检查过程发生异常: {e}")
            # 返回空报告
            from src.models.check_result import CheckReport
            return CheckReport(project_name=Path(project_path).name, project_path=project_path)

    # ===== 诊断方法 =====

    def run_diagnostics(
        self,
        project_path: str,
        diagnostic_type: str = "full",
        check_report: Optional[Any] = None
    ) -> tuple:
        """
        运行深度诊断

        支持的诊断类型：
        - lsp: LSP兼容性诊断（检测stub误用、FB缺失等问题）
        - health: 项目健康度分析（四维评分）
        - full: 完整诊断（包含LSP和健康度）

        Args:
            project_path: PLC项目根目录路径
            diagnostic_type: 诊断类型 ('lsp'/'health'/'full')
            check_report: 规范检查报告（用于健康度分析）

        Returns:
            tuple: (DiagnosticReport或None, HealthMetrics或None)
        """
        report = None
        metrics = None

        try:
            # LSP兼容性诊断
            if diagnostic_type in ('lsp', 'full'):
                try:
                    from src.diagnostics.lsp_compatibility_checker import (
                        LSPCompatibilityChecker,
                    )

                    logger.info("正在执行LSP兼容性扫描...")
                    self._lsp_checker = LSPCompatibilityChecker(project_path)
                    report = self._lsp_checker.scan()

                    logger.info(
                        f"LSP诊断完成: {len(report.issues)} 个问题"
                    )
                except Exception as e:
                    logger.error(f"LSP诊断失败: {e}")

            # 项目健康度分析
            if diagnostic_type in ('health', 'full'):
                try:
                    from src.diagnostics.project_health_analyzer import (
                        ProjectHealthAnalyzer,
                    )
                    from src.models.check_result import CheckReport

                    logger.info("正在分析项目健康度...")
                    self._health_analyzer = ProjectHealthAnalyzer()
                    metrics = self._health_analyzer.analyze(
                        check_report=check_report or CheckReport(),
                        project_path=project_path
                    )

                    logger.info(
                        f"健康度分析完成: {metrics.overall_score:.1f} 分"
                    )
                except Exception as e:
                    logger.error(f"健康度分析失败: {e}")

            return report, metrics

        except Exception as e:
            logger.exception(f"诊断过程发生异常: {e}")
            return None, None

    # ===== 测试方法 =====

    def run_tests(
        self,
        project_path: str,
        test_cases: Optional[List[str]] = None
    ) -> Optional[Any]:
        """
        运行测试用例

        执行PLC项目的测试套件，支持选择特定测试用例。

        Args:
            project_path: PLC项目根目录路径
            test_cases: 要运行的测试用例名称列表（None=全部）

        Returns:
            TestRunSummary: 测试运行摘要，包含详细结果统计
        """
        try:
            from pathlib import Path
            from src.services.test_management_service import (
                TestManagementService,
                TestExecutionConfig,
            )

            # 初始化测试服务
            project_path_obj = Path(project_path).resolve()
            config = TestExecutionConfig()

            self._test_service = TestManagementService(
                project_path_obj,
                config=config
            )

            # 扫描测试文件
            test_files = self._test_service.scan_test_files(project_path_obj)
            if not test_files:
                logger.warning(f"未找到测试文件: {project_path}")
                return None

            # 解析测试文件
            suites = self._test_service.parse_all_test_files(test_files)
            if not suites:
                logger.warning("未找到有效的测试用例")
                return None

            # 合并所有suite（简化实现）
            target_suite = suites[0]

            # 设置回调函数
            self._test_service.set_progress_callback(
                lambda data: logger.debug(
                    f"测试进度: {data.get('current', 0)}/{data.get('total', 0)}"
                )
            )

            # 执行测试
            logger.info(
                f"开始执行测试: {len(test_cases) or '全部'} 个用例"
            )
            summary = self._test_service.run_tests(
                target_suite,
                test_names=test_cases
            )

            logger.info(
                f"测试执行完成: "
                f"{summary.passed_tests}/{summary.total_tests} 通过, "
                f"耗时 {summary.total_duration_seconds:.3f}s"
            )

            return summary

        except ImportError as e:
            logger.error(f"导入测试服务模块失败: {e}")
            return None
        except Exception as e:
            logger.exception(f"测试执行过程发生异常: {e}")
            return None

    # ===== 健康度方法 =====

    def get_project_health(
        self,
        project_path: str,
        check_report: Optional[Any] = None
    ) -> Optional[Any]:
        """
        获取项目健康度指标

        计算项目的四维健康度评分，包括：
        - 规范符合度
        - 问题严重程度
        - 库引用状态
        - 结构合规性

        Args:
            project_path: PLC项目根目录路径
            check_report: 规范检查报告（用于更准确的分析）

        Returns:
            HealthMetrics: 健康度指标对象，包含各维度得分和改进建议
        """
        try:
            from src.diagnostics.project_health_analyzer import (
                ProjectHealthAnalyzer,
            )
            from src.models.check_result import CheckReport

            logger.info("正在计算项目健康度...")

            analyzer = ProjectHealthAnalyzer()
            metrics = analyzer.analyze(
                check_report=check_report or CheckReport(),
                project_path=project_path
            )

            logger.info(
                f"健康度计算完成: "
                f"总分 {metrics.overall_score:.1f} [{metrics.health_grade.value}]"
            )

            return metrics

        except Exception as e:
            logger.exception(f"获取项目健康度失败: {e}")
            return None

    # ===== 辅助方法 =====

    def _collect_st_files(self, project_path: str) -> List[str]:
        """
        收集项目中所有的ST源码文件

        Args:
            project_path: 项目根目录

        Returns:
            List[str]: ST文件路径列表
        """
        st_extensions = {'.st', '.TcPOU', '.st7'}
        st_files = []

        project_dir = Path(project_path)
        if not project_dir.exists():
            logger.warning(f"项目目录不存在: {project_path}")
            return st_files

        # 递归查找ST源码文件
        for ext in st_extensions:
            st_files.extend([
                str(p) for p in project_dir.rglob(f"*{ext}")
                if p.is_file()
            ])

        # 排除测试文件和示例文件
        st_files = [
            f for f in st_files
            if "_test" not in f.lower()
               and "test_" not in f.lower()
               and "example" not in f.lower()
        ]

        logger.info(f"在项目中找到 {len(st_files)} 个ST源码文件")
        return sorted(st_files)

    # ===== 向后兼容方法（保留原有接口） =====

    @classmethod
    def check_syntax(cls, st_code: str) -> tuple:
        """
        ST语法检查 (向后兼容接口)

        Args:
            st_code: ST源代码文本

        Returns:
            tuple: (passed: bool, errors: list, warnings: list)
        """
        logger.warning("check_syntax() 是遗留接口，建议使用 check_specifications()")

        try:
            # 尝试使用新的语法检查器
            from src.checkers.syntax_checker import SyntaxChecker

            checker = SyntaxChecker()
            violations = checker.check(st_code)

            errors = [
                v.message for v in violations
                if v.severity.name == 'ERROR'
            ]
            warnings = [
                v.message for v in violations
                if v.severity.name == 'WARNING'
            ]

            return len(errors) == 0, errors, warnings

        except Exception as e:
            logger.error(f"语法检查失败: {e}")
            return False, [], [f"语法检查异常: {str(e)}"]

    @classmethod
    def compile_program(cls, project_path: str) -> tuple:
        """
        编译PLC程序 (预留接口)

        Args:
            project_path: 项目路径

        Returns:
            tuple: (success: bool, output: str)
        """
        logger.warning("PLC编译功能正在开发中...")
        return False, "编译功能尚未实现"

    @classmethod
    def download_to_plc(cls, project_path: str, connection_config: dict) -> tuple:
        """
        下载程序到PLC (预留接口)

        Args:
            project_path: 项目路径
            connection_config: 连接配置

        Returns:
            tuple: (success: bool, message: str)
        """
        logger.warning("PLC下载功能正在开发中...")
        return False, "下载功能尚未实现"


# ============================================================================
# 单例实例（便于全局访问）
# =============================================================================

_service_instance: Optional[PLCService] = None


def get_plc_service() -> PLCService:
    """
    获取PLC服务单例

    Returns:
        PLCService: 全局唯一的PLC服务实例
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = PLCService()
    return _service_instance
