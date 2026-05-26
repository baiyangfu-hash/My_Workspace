from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from specmgr.core.checker_base import CheckResult, HealthChecker, Severity
from specmgr.core.config import WorkspaceConfig
from specmgr.core.registry import SpecRegistry
from specmgr.core.scanner import SpecScanner


@dataclass
class CheckOutput:
    results: list[CheckResult]
    error_count: int
    warning_count: int
    info_count: int
    exit_code: int


class CheckService:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.config = WorkspaceConfig(workspace=workspace)
        self.registry = SpecRegistry(workspace)
        self.registry_loaded = self.registry.load()
        self.scanner = SpecScanner(workspace, self.config)
        self.checker = HealthChecker()

    def run(
        self,
        check_ids: list[str] | None = None,
        min_severity: Severity = Severity.INFO,
    ) -> CheckOutput:
        if not self.registry_loaded:
            return CheckOutput(
                results=[
                    CheckResult(
                        check_id="SHC-000",
                        severity=Severity.ERROR,
                        message=f"注册表文件不存在或格式错误: {self.registry.path}",
                        details="",
                        fix_suggestion="确认工作空间路径正确且spec_registry.json存在",
                    )
                ],
                error_count=1,
                warning_count=0,
                info_count=0,
                exit_code=1,
            )
        if check_ids:
            results: list[CheckResult] = []
            for cid in check_ids:
                results.extend(self.checker.run_by_id(cid, self.registry, self.scanner))
        else:
            results = self.checker.run_all(self.registry, self.scanner)

        filtered = [r for r in results if r.severity >= min_severity]
        error_count = sum(1 for r in filtered if r.severity == Severity.ERROR)
        warning_count = sum(1 for r in filtered if r.severity == Severity.WARNING)
        info_count = sum(1 for r in filtered if r.severity == Severity.INFO)
        exit_code = 1 if error_count else (2 if warning_count else 0)

        return CheckOutput(
            results=filtered,
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            exit_code=exit_code,
        )
