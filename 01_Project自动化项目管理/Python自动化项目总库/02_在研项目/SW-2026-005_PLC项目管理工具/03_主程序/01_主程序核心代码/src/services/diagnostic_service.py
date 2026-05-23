# -*- coding: utf-8 -*-
"""
诊断服务层

编排完整的PLC项目诊断流程，
集成规范检查、LSP兼容性诊断和健康度分析三大功能模块。

主要功能：
- 完整诊断流程：按顺序执行规范检查 → LSP诊断 → 健康度分析
- 灵活配置：支持通过配置文件控制各步骤的启用/禁用
- 容错机制：每个步骤都有独立的异常保护，单步失败不影响整体流程
- 结果汇总：将各步骤结果整合为统一的诊断报告

设计原则：
- 编排者模式：作为各诊断组件的协调者和编排者
- 防御式编程：所有外部调用都使用try-except保护
- 可观测性：详细的日志记录和性能计时
- 松耦合：与具体实现解耦，仅依赖标准化的接口
"""
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DiagnosticService:
    """
    诊断服务类 - 编排完整的项目诊断流程

    职责：
    - 协调规范检查、LSP诊断、健康度分析的执行顺序
    - 管理各步骤的错误处理和降级策略
    - 整合多维度分析结果为统一报告
    - 提供配置驱动的灵活诊断能力

    Attributes:
        _config: 诊断服务配置
        _spec_checker: 规范检查服务实例（延迟初始化）
        _last_report: 最近一次的诊断报告缓存

    Usage:
        >>> service = DiagnosticService()
        >>> report, metrics = service.run_full_diagnostic("/path/to/project")
        >>> print(f"健康度评分: {metrics.overall_score}")
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化诊断服务

        Args:
            config: 自定义配置字典（可选，默认使用全局DIAGNOSTIC_CONFIG）
        """
        # 加载配置
        if config is None:
            try:
                from src.core.config import ConfigLoader
                self._config = ConfigLoader.get("diagnostic_config", None)
                if self._config is None:
                    raise ImportError("No diagnostic_config in ConfigLoader")
            except (ImportError, Exception):
                try:
                    from config import DIAGNOSTIC_CONFIG
                    self._config = DIAGNOSTIC_CONFIG
                except ImportError:
                    logger.warning("无法加载全局诊断配置，使用默认值")
                    self._config = self._get_default_config()
        else:
            self._config = config

        # 延迟初始化的服务实例
        self._spec_checker = None
        self._lsp_checker_instance = None
        self._health_analyzer_instance = None

        # 最近一次的诊断结果缓存
        self._last_report: Optional[Any] = None
        self._last_metrics: Optional[Any] = None

        # 性能统计
        self._timing_stats: Dict[str, float] = {}

        logger.info("DiagnosticService初始化完成")

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置（当全局配置不可用时）"""
        return {
            "full_diagnostic_flow": {
                "steps_order": ["spec_check", "lsp_diagnostic", "health_analysis"],
                "continue_on_error": True,
                "timeout_total": 120,
            },
            "lsp_diagnostic": {
                "enabled": True,
                "scan_plc_output_dir": True,
                "detect_stub_misuse": True,
                "analyze_call_chain": True,
                "check_missing_impl": True,
            },
            "health_analysis": {
                "enabled": True,
                "dimensions_weights": {
                    "compliance": 0.40,
                    "issues": 0.30,
                    "library": 0.15,
                    "structure": 0.15,
                },
                "generate_suggestions": True,
                "min_score_for_suggestions": 80,
            },
            "error_handling": {
                "log_detailed_errors": True,
                "collect_stack_trace": True,
                "notify_on_critical_error": True,
            },
        }

    # ===== 核心诊断方法 =====

    def run_full_diagnostic(
        self, project_path: str
    ) -> Tuple[Any, Any]:
        """
        执行完整的项目诊断流程

        按照配置的步骤顺序依次执行：
        1. 规范检查（SpecCheckerService.check_project）
        2. LSP兼容性诊断（LSPCompatibilityChecker.scan）
        3. 项目健康度分析（ProjectHealthAnalyzer.analyze）

        每个步骤都有独立的异常保护，
        单步失败不会中断整个流程（可通过配置控制此行为）。

        Args:
            project_path: PLC项目根目录路径

        Returns:
            tuple: (DiagnosticReport或None, HealthMetrics或None)
                   - DiagnosticReport: LSP诊断报告（可能为None如果LSP步骤失败）
                   - HealthMetrics: 健康度指标（可能为None如果健康度步骤失败）

        Raises:
            无显式抛出异常，所有异常都被内部捕获并记录日志
        """
        start_time = datetime.now()
        logger.info("=" * 70)
        logger.info(f"开始完整诊断流程: {Path(project_path).name}")
        logger.info("=" * 70)

        # 初始化结果容器
        check_report = None
        diagnostic_report = None
        health_metrics = None
        errors_encountered = []

        try:
            # 获取流程配置
            flow_config = self._config.get("full_diagnostic_flow", {})
            steps_order = flow_config.get(
                "steps_order",
                ["spec_check", "lsp_diagnostic", "health_analysis"],
            )
            continue_on_error = flow_config.get("continue_on_error", True)

            # ===== 步骤1：规范检查 =====
            if "spec_check" in steps_order:
                step_start = datetime.now()
                try:
                    logger.info("\n[步骤 1/3] 执行规范检查...")
                    check_report = self._run_spec_check(project_path)

                    elapsed = (datetime.now() - step_start).total_seconds()
                    self._timing_stats["spec_check"] = elapsed

                    if check_report:
                        logger.info(
                            f"规范检查完成 - "
                            f"问题数: {check_report.total_violations}, "
                            f"耗时: {elapsed:.2f}s"
                        )
                    else:
                        logger.warning("规范检查未返回有效结果")

                except Exception as e:
                    elapsed = (datetime.now() - step_start).total_seconds()
                    self._timing_stats["spec_check"] = elapsed
                    error_msg = f"规范检查步骤失败: {e}"
                    errors_encountered.append(error_msg)
                    logger.exception(error_msg)

                    if not continue_on_error:
                        logger.error("配置为遇到错误即停止，终止诊断")
                        return self._create_empty_result(project_path)

            # ===== 步骤2：LSP兼容性诊断 =====
            if "lsp_diagnostic" in steps_order:
                lsp_config = self._config.get("lsp_diagnostic", {})

                if lsp_config.get("enabled", True):
                    step_start = datetime.now()
                    try:
                        logger.info("\n[步骤 2/3] 执行LSP兼容性诊断...")
                        diagnostic_report = self._run_lsp_diagnostic(
                            project_path
                        )

                        elapsed = (
                            datetime.now() - step_start
                        ).total_seconds()
                        self._timing_stats["lsp_diagnostic"] = elapsed

                        if diagnostic_report:
                            logger.info(
                                f"LSP诊断完成 - "
                                f"问题数: {diagnostic_report.total_issues}, "
                                f"耗时: {elapsed:.2f}s"
                            )
                        else:
                            logger.warning("LSP诊断未返回有效结果")

                    except Exception as e:
                        elapsed = (
                            datetime.now() - step_start
                        ).total_seconds()
                        self._timing_stats["lsp_diagnostic"] = elapsed
                        error_msg = f"LSP诊断步骤失败: {e}"
                        errors_encountered.append(error_msg)
                        logger.exception(error_msg)

                        if not continue_on_error:
                            logger.error("配置为遇到错误即停止，终止诊断")
                            return diagnostic_report, None

            # ===== 步骤3：项目健康度分析 =====
            if "health_analysis" in steps_order:
                health_config = self._config.get("health_analysis", {})

                if health_config.get("enabled", True):
                    step_start = datetime.now()
                    try:
                        logger.info("\n[步骤 3/3] 执行项目健康度分析...")
                        health_metrics = self._run_health_analysis(
                            project_path, check_report
                        )

                        elapsed = (
                            datetime.now() - step_start
                        ).total_seconds()
                        self._timing_stats["health_analysis"] = elapsed

                        if health_metrics:
                            logger.info(
                                f"健康度分析完成 - "
                                f"总分: {health_metrics.overall_score:.1f}, "
                                f"等级: {health_metrics.health_grade.value}, "
                                f"耗时: {elapsed:.2f}s"
                            )
                        else:
                            logger.warning("健康度分析未返回有效结果")

                    except Exception as e:
                        elapsed = (
                            datetime.now() - step_start
                        ).total_seconds()
                        self._timing_stats["health_analysis"] = elapsed
                        error_msg = f"健康度分析步骤失败: {e}"
                        errors_encountered.append(error_msg)
                        logger.exception(error_msg)

            # 缓存最新结果
            self._last_report = diagnostic_report
            self._last_metrics = health_metrics

            # 输出最终摘要
            total_elapsed = (datetime.now() - start_time).total_seconds()
            self._log_diagnostic_summary(
                total_elapsed, errors_encountered
            )

            return diagnostic_report, health_metrics

        except Exception as e:
            total_elapsed = (datetime.now() - start_time).total_seconds()
            logger.exception(f"诊断流程发生未预期的异常: {e}")

            error_cfg = self._config.get("error_handling", {})
            if error_cfg.get("collect_stack_trace", True):
                import traceback
                logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")

            return self._create_empty_result(project_path)

    # ===== 各步骤实现方法 =====

    def _run_spec_check(self, project_path: str) -> Any:
        """
        执行规范检查步骤

        使用SpecCheckerService对项目进行完整的规范检查。

        Args:
            project_path: 项目路径

        Returns:
            CheckReport: 规范检查报告
        """
        try:
            # 延迟初始化检查服务
            if self._spec_checker is None:
                from src.services.spec_checker_service import (
                    SpecCheckerService,
                )
                self._spec_checker = SpecCheckerService()

            # 执行项目级检查
            report = self._spec_checker.check_project(project_path)
            return report

        except ImportError as e:
            logger.error(f"导入SpecCheckerService失败: {e}")
            return None
        except Exception as e:
            logger.exception(f"规范检查执行失败: {e}")
            raise

    def _run_lsp_diagnostic(self, project_path: str) -> Any:
        """
        执行LSP兼容性诊断步骤

        使用LSPCompatibilityChecker扫描.plc-out目录，
        检测stub误用、FB缺失等问题。

        Args:
            project_path: 项目路径

        Returns:
            DiagnosticReport: LSP诊断报告
        """
        try:
            from src.diagnostics.lsp_compatibility_checker import (
                LSPCompatibilityChecker,
            )

            logger.debug("初始化LSPCompatibilityChecker...")

            # 创建并运行LSP检查器
            self._lsp_checker_instance = LSPCompatibilityChecker(
                project_path
            )
            report = self._lsp_checker_instance.scan()

            return report

        except ImportError as e:
            logger.error(f"导入LSPCompatibilityChecker失败: {e}")
            return None
        except Exception as e:
            logger.exception(f"LSP诊断执行失败: {e}")
            raise

    def _run_health_analysis(
        self, project_path: str, check_report: Optional[Any] = None
    ) -> Any:
        """
        执行项目健康度分析步骤

        使用ProjectHealthAnalyzer计算四维健康度评分。

        Args:
            project_path: 项目路径
            check_report: 规范检查报告（用于更准确的分析）

        Returns:
            HealthMetrics: 健康度指标对象
        """
        try:
            from src.diagnostics.project_health_analyzer import (
                ProjectHealthAnalyzer,
            )
            from src.models.check_result import CheckReport

            logger.debug("初始化ProjectHealthAnalyzer...")

            # 创建并运行健康度分析器
            self._health_analyzer_instance = ProjectHealthAnalyzer()
            metrics = self._health_analyzer_instance.analyze(
                check_report=check_report or CheckReport(),
                project_path=project_path,
            )

            return metrics

        except ImportError as e:
            logger.error(f"导入ProjectHealthAnalyzer失败: {e}")
            return None
        except Exception as e:
            logger.exception(f"健康度分析执行失败: {e}")
            raise

    # ===== 辅助方法 =====

    def _create_empty_result(
        self, project_path: str
    ) -> Tuple[Optional[Any], Optional[Any]]:
        """
        创建空的结果元组

        当诊断流程提前终止时返回空结果以保证接口一致性。

        Args:
            project_path: 项目路径（用于记录）

        Returns:
            tuple: (None, None) 空结果
        """
        logger.warning(f"诊断流程提前终止，返回空结果")
        return None, None

    def _log_diagnostic_summary(
        self, total_elapsed: float, errors: List[str]
    ) -> None:
        """
        输出诊断流程摘要信息

        Args:
            total_elapsed: 总耗时（秒）
            errors: 遇到的错误列表
        """
        logger.info("\n" + "=" * 70)
        logger.info("诊断流程摘要")
        logger.info("=" * 70)
        logger.info(f"总耗时: {total_elapsed:.2f}s")

        if self._timing_stats:
            logger.info("各步骤耗时:")
            for step, elapsed in self._timing_stats.items():
                logger.info(f"  - {step}: {elapsed:.2f}s")

        if errors:
            logger.warning(f"遇到的错误 ({len(errors)} 个):")
            for idx, error in enumerate(errors, 1):
                logger.warning(f"  {idx}. {error}")
        else:
            logger.info("所有步骤均成功完成")

        logger.info("=" * 70 + "\n")

    # ===== 公开查询方法 =====

    def get_last_diagnostics(
        self
    ) -> Tuple[Optional[Any], Optional[Any]]:
        """
        获取最近一次的诊断结果

        Returns:
            tuple: (最近DiagnosticReport, 最近HealthMetrics)
        """
        return self._last_report, self._last_metrics

    def get_timing_statistics(self) -> Dict[str, float]:
        """
        获取各步骤的性能计时统计

        Returns:
            Dict[str, float]: 各步骤耗时（秒）
        """
        return dict(self._timing_stats)

    def is_healthy(self) -> bool:
        """
        快速判断最近一次诊断是否显示项目健康

        Returns:
            bool: 如果最近健康度>=70分且无严重错误则返回True
        """
        if self._last_metrics is None:
            return False

        return (
            self._last_metrics.overall_score >= 70.0
            and self._last_metrics.health_grade.value
            in ["A", "B"]
        )

    def reset(self) -> None:
        """重置服务状态和缓存"""
        self._last_report = None
        self._last_metrics = None
        self._timing_stats.clear()
        logger.info("DiagnosticService状态已重置")

    def __repr__(self) -> str:
        """对象的字符串表示"""
        has_last = self._last_metrics is not None
        score = (
            self._last_metrics.overall_score if has_last else "N/A"
        )
        return (
            f"DiagnosticService("
            f"has_results={has_last}, "
            f"latest_score={score})"
        )
