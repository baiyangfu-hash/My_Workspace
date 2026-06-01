# -*- coding: utf-8 -*-
"""
规范检查服务层

提供高性能的PLC代码规范检查服务，
支持并行检查、结果缓存和项目级规则覆盖。

主要功能：
- 项目级批量检查：扫描所有.scl文件并使用线程池并行检查
- 单文件检查：对指定文件执行完整规范检查
- 规则管理：获取启用的检查器列表、加载项目级规则覆盖
- 缓存机制：基于文件路径和修改时间的智能缓存，避免重复检查

设计原则：
- 高性能：使用ThreadPoolExecutor实现多文件并行检查
- 高可用：完整的异常处理和日志记录机制
- 可扩展：支持通过.rules.json配置文件自定义规则参数
- 低耦合：与UI层解耦，仅返回标准化的CheckReport对象
"""
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SpecCheckerService:
    """
    规范检查服务类

    提供高性能的PLC代码规范检查功能，
    支持多线程并行处理、智能缓存和规则定制。

    Attributes:
        _cache: 结果缓存字典 {filepath+mtimes: CheckResult}
        _project_rules: 当前项目的规则覆盖配置
        _config: 服务配置（从config.SPEC_CHECK_CONFIG加载）

    Usage:
        >>> service = SpecCheckerService()
        >>> report = service.check_project("/path/to/plc/project")
        >>> result = service.check_file("/path/to/file.st")
        >>> checkers = service.get_enabled_checkers()
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化规范检查服务

        Args:
            config: 自定义配置字典（可选，默认使用全局配置）
        """
        # 加载配置（优先使用传入配置，否则从全局配置加载）
        if config is None:
            try:
                from src.core.config import ConfigLoader
                self._config = ConfigLoader.get("spec_check_config", None)
                if self._config is None:
                    raise ImportError("No spec_check_config in ConfigLoader")
            except (ImportError, Exception):
                try:
                    from config import SPEC_CHECK_CONFIG
                    self._config = SPEC_CHECK_CONFIG
                except ImportError:
                    logger.warning("无法加载全局配置，使用默认值")
                    self._config = self._get_default_config()
        else:
            self._config = config

        # 初始化缓存存储
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}

        # 项目级规则覆盖（延迟加载）
        self._project_rules: Dict[str, Any] = {}
        self._current_project_path: Optional[str] = None

        # 统计计数器
        self._stats = {
            "total_files_checked": 0,
            "total_cache_hits": 0,
            "total_cache_misses": 0,
            "total_errors": 0,
        }

        logger.info("SpecCheckerService初始化完成")

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置（当全局配置不可用时）"""
        return {
            "concurrency": {
                "max_workers": 4,
                "timeout_per_file": 30,
                "enable_parallel": True,
            },
            "file_scanning": {
                "supported_extensions": [".st", ".TcPOU", ".st7"],
                "exclude_patterns": ["_test", "test_", "example"],
                "max_file_size": 1024 * 1024,
                "recursive_scan": True,
            },
            "caching": {
                "enabled": True,
                "cache_max_size": 1000,
                "cache_ttl_seconds": 300,
            },
            "project_rules": {
                "rules_file_name": ".rules.json",
                "auto_load_on_check": True,
                "fallback_to_default": True,
            },
        }

    # ===== 核心检查方法 =====

    def check_project(self, project_path: str) -> Any:
        """
        执行项目级规范检查

        扫描项目中所有符合规范的源码文件，
        使用线程池并行执行检查以提高效率。

        流程：
        1. 验证项目目录有效性
        2. 收集所有待检查的.scl文件
        3. （可选）加载项目级规则覆盖
        4. 使用ThreadPoolExecutor并行检查各文件
        5. 汇总结果生成CheckReport

        Args:
            project_path: PLC项目根目录路径

        Returns:
            CheckReport: 完整的项目检查报告对象
        """
        start_time = datetime.now()

        try:
            # 验证项目路径
            project_dir = Path(project_path).resolve()
            if not project_dir.exists():
                logger.error(f"项目目录不存在: {project_path}")
                raise FileNotFoundError(f"项目目录不存在: {project_path}")

            logger.info(f"开始项目级规范检查: {project_dir.name}")

            # 加载项目级规则（如果启用）
            rules_config = self._config.get("project_rules", {})
            if rules_config.get("auto_load_on_check", True):
                try:
                    self.load_project_rules(project_path)
                    self._current_project_path = project_path
                except Exception as e:
                    logger.warning(f"加载项目规则失败，使用默认规则: {e}")

            # 收集待检查文件列表
            st_files = self._collect_st_files(project_path)

            if not st_files:
                logger.warning("未找到可检查的ST源码文件")
                from src.models.check_result import CheckReport
                return CheckReport(
                    project_name=project_dir.name,
                    project_path=str(project_dir),
                )

            logger.info(f"找到 {len(st_files)} 个ST源码文件")

            # 创建报告对象
            from src.models.check_result import CheckReport
            report = CheckReport(
                project_name=project_dir.name,
                project_path=str(project_dir),
            )

            # 获取并发配置
            concurrency_cfg = self._config.get("concurrency", {})
            max_workers = concurrency_cfg.get("max_workers", 4)
            enable_parallel = concurrency_cfg.get("enable_parallel", True)

            # 执行检查（根据配置选择串行或并行）
            if enable_parallel and len(st_files) > 1:
                results = self._check_files_parallel(
                    st_files, max_workers=max_workers
                )
            else:
                results = self._check_files_sequential(st_files)

            # 将结果添加到报告
            for file_result in results:
                if file_result:
                    report.add_result(file_result)

            # 更新统计信息
            elapsed = (datetime.now() - start_time).total_seconds()
            self._stats["total_files_checked"] += len(st_files)

            logger.info(
                f"项目检查完成 - "
                f"文件数: {report.total_files_checked}, "
                f"问题数: {report.total_violations} "
                f"(错误:{report.total_errors}, "
                f"警告:{report.total_warnings}, "
                f"提示:{report.total_infos}), "
                f"耗时: {elapsed:.2f}s"
            )

            return report

        except Exception as e:
            logger.exception(f"项目级检查过程发生异常: {e}")
            self._stats["total_errors"] += 1

            # 返回空报告以保证接口稳定性
            from src.models.check_result import CheckReport
            return CheckReport(
                project_name=Path(project_path).name,
                project_path=project_path,
            )

    def check_file(self, file_path: str) -> Any:
        """
        执行单文件规范检查

        对指定的单个文件执行完整的规范检查流程，
        包括缓存命中检测、规则加载和检查器执行。

        Args:
            file_path: 待检查的源码文件完整路径

        Returns:
            CheckResult: 单文件检查结果对象
        """
        try:
            # 验证文件存在性
            file_obj = Path(file_path).resolve()
            if not file_obj.exists():
                logger.error(f"文件不存在: {file_path}")
                raise FileNotFoundError(f"文件不存在: {file_path}")

            # 验证文件大小限制
            file_size = file_obj.stat().st_size
            max_size = self._config.get("file_scanning", {}).get(
                "max_file_size", 1024 * 1024
            )
            if file_size > max_size:
                logger.warning(
                    f"文件过大 ({file_size / 1024:.1f}KB > {max_size / 1024:.1f}KB): "
                    f"{file_obj.name}"
                )

            # 检查缓存
            cache_key = self._generate_cache_key(file_path)
            cached_result = self._get_from_cache(cache_key, file_path)

            if cached_result is not None:
                self._stats["total_cache_hits"] += 1
                logger.debug(f"缓存命中: {file_obj.name}")
                return cached_result

            self._stats["total_cache_misses"] += 1
            logger.debug(f"执行实际检查: {file_obj.name}")

            # 读取文件内容
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            # 创建结果对象
            from src.models.check_result import CheckResult
            file_result = CheckResult(source_file=str(file_obj))

            # 获取并执行所有启用的检查器
            checkers = self.get_enabled_checkers()

            for checker in checkers:
                try:
                    # 应用项目级规则覆盖（如果有）
                    checker_params = self._get_checker_overrides(
                        checker.rule_info.rule_id
                    )
                    if checker_params:
                        checker.configure(checker_params)

                    violations = checker.check(
                        source_code,
                        file_path=str(file_obj),
                    )

                    if violations:
                        file_result.add_violations(violations)

                except Exception as e:
                    logger.error(
                        f"检查器 {checker.rule_info.rule_id} "
                        f"执行异常: {e}"
                    )

            # 存入缓存
            self._put_to_cache(cache_key, file_result, file_path)

            self._stats["total_files_checked"] += 1

            logger.debug(
                f"单文件检查完成: {file_obj.name} - "
                f"{file_result.total_violations} 个问题"
            )

            return file_result

        except Exception as e:
            logger.exception(f"单文件检查失败: {file_path} - {e}")
            self._stats["total_errors"] += 1

            # 返回空结果以保证接口稳定性
            from src.models.check_result import CheckResult
            return CheckResult(source_file=file_path)

    # ===== SysLib 扫描方法 =====

    def check_syslib(self, syslib_path: str, rule_ids=None) -> Any:
        """
        对SysLib公共库执行规范检查

        扫描SysLib目录下所有.scl文件，使用现有检查器进行规范检查。
        结果中标记来源为"库文件"以便区分。

        Args:
            syslib_path: SysLib根目录路径
            rule_ids: 指定检查的规则ID列表（可选，默认全部启用规则）

        Returns:
            CheckReport: SysLib库的检查报告对象
        """
        from src.models.check_result import CheckReport

        start_time = datetime.now()
        syslib_dir = Path(syslib_path).resolve()

        if not syslib_dir.exists():
            logger.error(f"SysLib目录不存在: {syslib_path}")
            return CheckReport(
                project_name="SysLib",
                project_path=str(syslib_dir),
            )

        logger.info(f"开始SysLib规范检查: {syslib_dir.name}")

        try:
            from src.scanners.syslib_scanner import SysLibScanner

            scl_files = SysLibScanner.scan_all_scl_files(syslib_path)
            if not scl_files:
                logger.warning("SysLib目录中未找到SCL文件")
                return CheckReport(
                    project_name="SysLib",
                    project_path=str(syslib_dir),
                )

            report = CheckReport(
                project_name="SysLib",
                project_path=str(syslib_dir),
            )

            checkers = self._get_filtered_checkers(rule_ids)
            file_paths = [f.file_path for f in scl_files]

            concurrency_cfg = self._config.get("concurrency", {})
            max_workers = concurrency_cfg.get("max_workers", 4)
            enable_parallel = concurrency_cfg.get("enable_parallel", True)

            if enable_parallel and len(file_paths) > 1:
                results = self._check_files_parallel(file_paths, max_workers=max_workers)
            else:
                results = self._check_files_sequential(file_paths)

            for file_result in results:
                if file_result:
                    report.add_result(file_result)

            elapsed = (datetime.now() - start_time).total_seconds()
            self._stats["total_files_checked"] += len(scl_files)

            logger.info(
                f"SysLib检查完成 - "
                f"文件数: {report.total_files_checked}, "
                f"问题数: {report.total_violations}, "
                f"耗时: {elapsed:.2f}s"
            )
            return report

        except Exception as e:
            logger.exception(f"SysLib检查过程异常: {e}")
            return CheckReport(project_name="SysLib", project_path=syslib_path)

    def check_project_with_syslib(
        self,
        project_path: str,
        syslib_path: str,
        rule_ids=None,
    ) -> Dict[str, Any]:
        """
        联合检查项目和SysLib公共库

        同时对PLC项目文件和SysLib库文件执行规范检查，
        并检测项目中引用的库FB/FC版本一致性。

        Args:
            project_path: PLC项目根目录路径
            syslib_path: SysLib根目录路径
            rule_ids: 指定检查的规则ID列表（可选）

        Returns:
            Dict[str, Any]: 包含以下键的字典:
                - "project_report": 项目检查报告 (CheckReport)
                - "syslib_report": SysLib检查报告 (CheckReport)
                - "library_issues": 库引用问题列表 (List[LibraryRefIssue])
                - "summary": 汇总统计信息
        """
        from src.scanners.syslib_scanner import (
            SysLibScanner,
            GlobalFBIndex,
        )

        start_time = datetime.now()
        logger.info(f"开始联合检查: 项目={project_path}, SysLib={syslib_path}")

        project_report = self.check_project(project_path)
        syslib_report = self.check_syslib(syslib_path, rule_ids)

        library_issues: List[Any] = []
        try:
            syslib_index = SysLibScanner.build_global_fb_index(syslib_path)
            library_issues = SysLibScanner.find_outdated_references(
                project_path, syslib_index
            )
        except Exception as e:
            logger.warning(f"库引用检查失败: {e}")

        elapsed = (datetime.now() - start_time).total_seconds()

        result = {
            "project_report": project_report,
            "syslib_report": syslib_report,
            "library_issues": library_issues,
            "summary": {
                "project_files": project_report.total_files_checked,
                "project_violations": project_report.total_violations,
                "syslib_files": syslib_report.total_files_checked,
                "syslib_violations": syslib_report.total_violations,
                "library_ref_issues": len(library_issues),
                "total_elapsed_seconds": round(elapsed, 2),
            },
        }

        logger.info(
            f"联合检查完成 - "
            f"项目问题: {project_report.total_violations}, "
            f"库问题: {syslib_report.total_violations}, "
            f"引用问题: {len(library_issues)}, "
            f"耗时: {elapsed:.2f}s"
        )
        return result

    def _get_filtered_checkers(self, rule_ids=None) -> List[Any]:
        """根据rule_ids过滤检查器，为空时返回所有启用的检查器"""
        all_checkers = self.get_enabled_checkers()
        if rule_ids is None:
            return all_checkers
        rule_set = set(rule_ids) if isinstance(rule_ids, list) else {rule_ids}
        return [c for c in all_checkers if c.rule_info.rule_id in rule_set]

    # ===== 检查器管理方法 =====

    def get_enabled_checkers(self) -> List[Any]:
        """
        获取所有已启用的检查器实例列表

        从RuleRegistry中获取当前注册的所有检查器，
        过滤出is_enabled()为True的检查器。

        Returns:
            List[BaseChecker]: 已启用的检查器实例列表
        """
        try:
            from src.checkers.rule_registry import RuleRegistry

            registry = RuleRegistry.get_instance()
            all_checkers = registry.get_all_checkers(enabled_only=True)

            logger.debug(f"获取到 {len(all_checkers)} 个启用的检查器")
            return all_checkers

        except ImportError as e:
            logger.error(f"导入RuleRegistry失败: {e}")
            return []
        except Exception as e:
            logger.exception(f"获取检查器列表失败: {e}")
            return []

    # ===== 项目规则管理方法 =====

    def load_project_rules(self, project_path: str) -> bool:
        """
        加载项目级规则覆盖配置

        从项目根目录读取.rules.json文件，
        解析其中的规则参数覆盖配置。
        配置格式示例：
        {
            "checker_overrides": {
                "NAMING_001": {"min_length": 3},
                "SYNTAX_002": {"enabled": false}
            }
        }

        Args:
            project_path: PLC项目根目录路径

        Returns:
            bool: 成功加载返回True，无配置或失败返回False
        """
        try:
            rules_config = self._config.get("project_rules", {})
            rules_filename = rules_config.get("rules_file_name", ".rules.json")

            rules_file = Path(project_path) / rules_filename

            if not rules_file.exists():
                logger.debug(f"未找到项目规则文件: {rules_file}")
                self._project_rules = {}
                return False

            # 读取并解析JSON配置
            with open(rules_file, "r", encoding="utf-8") as f:
                rules_data = json.load(f)

            # 验证数据结构
            if not isinstance(rules_data, dict):
                logger.warning(f"规则文件格式错误: {rules_file}")
                return False

            self._project_rules = rules_data
            self._current_project_path = project_path

            override_count = len(rules_data.get("checker_overrides", {}))
            logger.info(
                f"成功加载项目规则: {rules_file.name} - "
                f"{override_count} 个规则覆盖"
            )

            return True

        except json.JSONDecodeError as e:
            logger.error(f"解析规则文件JSON失败: {e}")
            return False
        except Exception as e:
            logger.exception(f"加载项目规则失败: {e}")
            return False

    def _get_checker_overrides(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定规则的覆盖参数

        Args:
            rule_id: 规则ID（如 NAMING_001）

        Returns:
            Optional[Dict]: 参数覆盖字典，无覆盖时返回None
        """
        overrides = self._project_rules.get("checker_overrides", {})
        return overrides.get(rule_id)

    # ===== 缓存管理方法 =====

    def _generate_cache_key(self, file_path: str) -> str:
        """
        生成缓存键值

        基于文件路径和修改时间生成唯一标识，
        确保文件更新后能正确失效旧缓存。

        Args:
            file_path: 文件完整路径

        Returns:
            str: 缓存键值字符串
        """
        try:
            mtime = Path(file_path).stat().st_mtime
            return f"{file_path}:{mtime}"
        except Exception:
            return file_path

    def _get_from_cache(
        self, cache_key: str, file_path: str
    ) -> Optional[Any]:
        """
        从缓存获取检查结果

        检查缓存是否有效（未过期且未超限），
        有效则返回缓存的CheckResult。

        Args:
            cache_key: 缓存键值
            file_path: 文件路径（用于验证）

        Returns:
            Optional[CheckResult]: 缓存的结果对象，无效时返回None
        """
        cache_cfg = self._config.get("caching", {})

        # 检查缓存功能是否启用
        if not cache_cfg.get("enabled", True):
            return None

        # 检查缓存是否存在
        if cache_key not in self._cache:
            return None

        # 检查缓存有效期
        ttl_seconds = cache_cfg.get("cache_ttl_seconds", 300)
        cached_time = self._cache_timestamps.get(cache_key)

        if cached_time:
            elapsed = (datetime.now() - cached_time).total_seconds()
            if elapsed > ttl_seconds:
                # 缓存过期，清除
                del self._cache[cache_key]
                if cache_key in self._cache_timestamps:
                    del self._cache_timestamps[cache_key]
                logger.debug(f"缓存已过期: {Path(file_path).name}")
                return None

        # 返回缓存结果
        return self._cache[cache_key]

    def _put_to_cache(
        self, cache_key: str, result: Any, file_path: str
    ) -> None:
        """
        存储检查结果到缓存

        当缓存达到上限时，采用LRU策略淘汰最旧的条目。

        Args:
            cache_key: 缓存键值
            result: 检查结果对象
            file_path: 文件路径（用于日志）
        """
        cache_cfg = self._config.get("caching", {})

        if not cache_cfg.get("enabled", True):
            return

        max_size = cache_cfg.get("cache_max_size", 1000)

        # 检查缓存容量，超出时清理
        if len(self._cache) >= max_size:
            self._evict_oldest_cache_entries(count=max_size // 4)

        # 存入缓存
        self._cache[cache_key] = result
        self._cache_timestamps[cache_key] = datetime.now()

        logger.debug(
            f"结果已缓存: {Path(file_path).name} "
            f"(缓存大小: {len(self._cache)}/{max_size})"
        )

    def _evict_oldest_cache_entries(self, count: int = 10) -> None:
        """
        淘汰最旧的缓存条目

        基于时间戳删除最早的条目以释放空间。

        Args:
            count: 要淘汰的条目数量
        """
        if not self._cache_timestamps:
            return

        # 按时间戳排序，删除最早的条目
        sorted_keys = sorted(
            self._cache_timestamps.keys(),
            key=lambda k: self._cache_timestamps[k],
        )

        keys_to_remove = sorted_keys[:count]

        for key in keys_to_remove:
            del self._cache[key]
            del self._cache_timestamps[key]

        logger.debug(f"已淘汰 {len(keys_to_remove)} 个旧缓存条目")

    def clear_cache(self) -> None:
        """清空所有缓存数据"""
        cache_size = len(self._cache)
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info(f"缓存已清空，共清除 {cache_size} 条记录")

    # ===== 内部辅助方法 =====

    def _collect_st_files(self, project_path: str) -> List[str]:
        """
        收集项目中所有的ST源码文件

        根据配置中的文件扫描参数收集文件，
        排除不符合条件的文件（测试文件、过大文件等）。

        Args:
            project_path: 项目根目录路径

        Returns:
            List[str]: 符合条件的ST文件路径列表
        """
        scan_config = self._config.get("file_scanning", {})
        extensions = scan_config.get(
            "supported_extensions", [".st", ".TcPOU", ".st7"]
        )
        exclude_patterns = scan_config.get(
            "exclude_patterns", ["_test", "test_", "example"]
        )
        recursive = scan_config.get("recursive_scan", True)

        project_dir = Path(project_path)
        st_files = []

        # 根据配置选择递归或非递归扫描
        glob_pattern = "**/*" if recursive else "*"

        for ext in extensions:
            if recursive:
                files = project_dir.rglob(f"*{ext}")
            else:
                files = project_dir.glob(glob_pattern + ext)

            for file_path in files:
                if not file_path.is_file():
                    continue

                # 检查排除模式
                file_str = str(file_path)
                should_exclude = any(
                    pattern in file_str.lower()
                    for pattern in exclude_patterns
                )

                if not should_exclude:
                    st_files.append(str(file_path))

        # 排序保证顺序一致性
        st_files.sort()

        logger.debug(f"文件扫描完成: 找到 {len(st_files)} 个文件")
        return st_files

    def _check_files_parallel(
        self, file_paths: List[str], max_workers: int = 4
    ) -> List[Any]:
        """
        使用线程池并行检查多个文件

        通过ThreadPoolExecutor实现多线程并发检查，
        显著提升大项目的检查速度。

        Args:
            file_paths: 待检查的文件路径列表
            max_workers: 最大并发线程数

        Returns:
            List[CheckResult]: 各文件的检查结果列表
        """
        results = []
        timeout = self._config.get("concurrency", {}).get(
            "timeout_per_file", 30
        )

        logger.info(
            f"启动并行检查: {len(file_paths)} 个文件, "
            f"{max_workers} 个工作线程"
        )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有检查任务
            future_to_file = {
                executor.submit(self.check_file, fp): fp
                for fp in file_paths
            }

            # 收集完成的任务结果
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]

                try:
                    # 设置超时防止死锁
                    result = future.result(timeout=timeout)
                    results.append(result)

                except Exception as e:
                    logger.error(
                        f"并行检查文件异常: {Path(file_path).name} - {e}"
                    )
                    # 创建空结果保持索引一致性
                    from src.models.check_result import CheckResult
                    results.append(CheckResult(source_file=file_path))

        logger.info(f"并行检查完成: {len(results)}/{len(file_paths)} 个文件")
        return results

    def _check_files_sequential(
        self, file_paths: List[str]
    ) -> List[Any]:
        """
        串行检查多个文件（备用方案）

        当并行检查被禁用或只有单个文件时使用。

        Args:
            file_paths: 待检查的文件路径列表

        Returns:
            List[CheckResult]: 各文件的检查结果列表
        """
        results = []

        logger.info(f"启动串行检查: {len(file_paths)} 个文件")

        for idx, file_path in enumerate(file_paths, 1):
            logger.debug(
                f"正在检查 ({idx}/{len(file_paths)}): "
                f"{Path(file_path).name}"
            )

            try:
                result = self.check_file(file_path)
                results.append(result)
            except Exception as e:
                logger.error(f"串行检查文件异常: {file_path} - {e}")
                from src.models.check_result import CheckResult
                results.append(CheckResult(source_file=file_path))

        logger.info(f"串行检查完成: {len(results)} 个文件")
        return results

    # ===== 统计和调试方法 =====

    def get_statistics(self) -> Dict[str, int]:
        """
        获取服务运行统计信息

        Returns:
            Dict[str, int]: 包含各项统计数据的字典
        """
        return dict(self._stats)

    def reset_statistics(self) -> None:
        """重置所有统计计数器"""
        for key in self._stats:
            self._stats[key] = 0
        logger.info("统计计数器已重置")

    def __repr__(self) -> str:
        """对象的字符串表示"""
        return (
            f"SpecCheckerService("
            f"cached={len(self._cache)}, "
            f"checked={self._stats['total_files_checked']}, "
            f"errors={self._stats['total_errors']})"
        )
