"""Spec Facade 接口层

M4 第 1 批重构：从"转发层"升级为"用例编排层"，返回带类型 DTO。
"""

from typing import Any

from auto_pm.core.protocols import (
    ProjectServiceProtocol,
    SpecCenterServiceProtocol,
    SpecCheckServiceProtocol,
)
from auto_pm.ui.contracts.dto.spec_dto import (
    SpecCenterEntryDTO,
    SpecCenterOverviewDTO,
    SpecCheckResultDTO,
    SpecFrontmatterResultDTO,
    SpecIndexResultDTO,
    SpecReportResultDTO,
)
from auto_pm.ui.contracts.result import CommandResult, QueryResult


class SpecFacade:
    """提供给 UI 层的 Spec 用例聚合入口"""

    def __init__(
        self,
        spec_check_service: SpecCheckServiceProtocol | None = None,
        spec_center_service: SpecCenterServiceProtocol | None = None,
        index_service: Any | None = None,
        report_service: Any | None = None,
        frontmatter_service: Any | None = None,
        project_service: ProjectServiceProtocol | None = None,
    ):
        self._spec_check_service = spec_check_service
        self._spec_center_service = spec_center_service
        self._index_service = index_service
        self._report_service = report_service
        self._frontmatter_service = frontmatter_service
        self._project_service = project_service

    @property
    def has_spec_check_service(self) -> bool:
        return self._spec_check_service is not None or self._project_service is not None

    @property
    def has_spec_center_service(self) -> bool:
        return self._spec_center_service is not None

    def run_spec_check(self, project_id: str = "") -> CommandResult[SpecCheckResultDTO | None]:
        try:
            if project_id and self._project_service:
                proj = self._project_service.get_project(project_id)
                if proj and proj.stack == "python":
                    from auto_pm.core.python_service import PythonProjectService
                    py_svc = PythonProjectService(self._project_service.workspace_root)
                    check_res = py_svc.check_project_spec(proj.path, project_id)
                    results = [
                        {
                            "check_id": c["name"],
                            "severity": "ERROR" if not c["ok"] else "INFO",
                            "message": c["name"],
                            "details": c.get("detail", ""),
                            "fix_suggestion": "使用一键修复补齐规范文件" if not c["ok"] else "",
                        }
                        for c in check_res["checks"]
                    ]
                    dto = SpecCheckResultDTO(
                        error_count=check_res["total"] - check_res["passed"],
                        warning_count=0,
                        info_count=check_res["passed"],
                        exit_code=0 if check_res["all_ok"] else 1,
                        results=results,
                    )
                    return CommandResult(success=True, message="Success", payload=dto)

            if not self._spec_check_service:
                return CommandResult(success=False, message="No spec_check_service", payload=None)
            output = self._spec_check_service.run()

            results = [
                {
                    "check_id": r.check_id,
                    "severity": r.severity.name if hasattr(r.severity, "name") else str(r.severity),
                    "message": r.message,
                    "details": r.details,
                    "fix_suggestion": r.fix_suggestion,
                }
                for r in output.results
            ]

            dto = SpecCheckResultDTO(
                error_count=output.error_count,
                warning_count=output.warning_count,
                info_count=output.info_count,
                exit_code=output.exit_code,
                results=results,
            )
            return CommandResult(success=True, message="Success", payload=dto)
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload=None)

    def run_spec_repair(self, project_id: str) -> CommandResult[dict[str, Any] | None]:
        try:
            if not project_id or not self._project_service:
                return CommandResult(success=False, message="Missing project_service or project_id", payload=None)
            proj = self._project_service.get_project(project_id)
            if not proj:
                return CommandResult(success=False, message=f"Project {project_id} not found", payload=None)
            
            if proj.stack == "python":
                from auto_pm.core.python_service import PythonProjectService
                py_svc = PythonProjectService(self._project_service.workspace_root)
                repaired_items = py_svc.repair_project_spec(proj.path, project_id, dry_run=False)
                return CommandResult(
                    success=True,
                    message=f"成功修复 {len(repaired_items)} 项",
                    payload={"repaired_items": repaired_items}
                )
            elif proj.stack == "plc":
                if not self._spec_check_service:
                    return CommandResult(success=False, message="No spec_check_service", payload=None)
                from pathlib import Path
                output = self._spec_check_service.run(
                    auto_fix=True,
                    scope="project",
                    project_root=Path(proj.path),
                )
                repaired = [fr.check_id for fr in (output.fix_results or []) if fr.applied]
                return CommandResult(
                    success=True,
                    message=f"成功自动修复 {len(repaired)} 项 PLC 规范",
                    payload={"repaired_items": repaired}
                )
            return CommandResult(success=False, message=f"Project stack {proj.stack} not supported for repair", payload=None)
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload=None)

    def get_spec_center_overview(self) -> QueryResult[SpecCenterOverviewDTO | None]:
        try:
            if not self._spec_center_service:
                return QueryResult(success=False, message="No spec_center_service", payload=None)
            overview = self._spec_center_service.get_overview()
            health = overview.health_summary
            dto = SpecCenterOverviewDTO(
                spec_count=overview.spec_count,
                domain_counts=dict(overview.domain_counts),
                lifecycle_counts=dict(overview.lifecycle_counts),
                health_summary={
                    "error_count": health.error_count,
                    "warning_count": health.warning_count,
                    "info_count": health.info_count,
                    "exit_code": health.exit_code,
                },
            )
            return QueryResult(success=True, message="Success", payload=dto)
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload=None)

    def list_spec_center_entries(self, filter_domain: str | None = None) -> QueryResult[list[SpecCenterEntryDTO]]:
        try:
            if not self._spec_center_service:
                return QueryResult(success=False, message="No spec_center_service", payload=[])
            entries = self._spec_center_service.list_entries(filter_domain)
            dtos = [
                SpecCenterEntryDTO(
                    spec_id=e.spec_id,
                    title=e.title,
                    number=e.number,
                    domain=e.domain,
                    lifecycle=e.lifecycle,
                    canonical_path=e.canonical_path,
                    version=e.version,
                    file_exists=e.file_exists,
                )
                for e in entries
            ]
            return QueryResult(success=True, message="Success", payload=dtos)
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload=[])

    def generate_spec_index(self, domain: str = "all") -> CommandResult[SpecIndexResultDTO | None]:
        """生成规范索引文件（M5 CHG-119 新增）

        Args:
            domain: 生成域，"all" 生成全部（pm/plc/python），或指定单域
        """
        try:
            if not self._index_service:
                return CommandResult(success=False, message="No index_service", payload=None)

            domains = None if domain == "all" else [domain]
            output = self._index_service.run(domains=domains)

            dto = SpecIndexResultDTO(
                domain=domain,
                generated_files=[str(f) for f in output.generated_files],
                errors=list(output.errors),
            )
            return CommandResult(success=True, message="Success", payload=dto)
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload=None)

    def generate_spec_report(self, fmt: str = "markdown") -> CommandResult[SpecReportResultDTO | None]:
        """生成规范报告（M5 CHG-120 新增）

        Args:
            fmt: 报告格式，"markdown" 或 "json"
        """
        try:
            if not self._report_service:
                return CommandResult(success=False, message="No report_service", payload=None)

            output = self._report_service.generate(fmt=fmt)

            dto = SpecReportResultDTO(
                fmt=output.fmt,
                output_path=str(output.output_path),
                content=output.content,
                file_size=len(output.content),
            )
            return CommandResult(success=True, message="Success", payload=dto)
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload=None)

    def check_spec_frontmatter(self, auto_fix: bool = False) -> CommandResult[SpecFrontmatterResultDTO | None]:
        """检查/修复规范 Frontmatter（M5 CHG-121 新增）

        Args:
            auto_fix: True 时自动添加缺失的 frontmatter（调用 apply 写入磁盘）
        """
        try:
            if not self._frontmatter_service:
                return CommandResult(success=False, message="No frontmatter_service", payload=None)

            items = self._frontmatter_service.preview()
            modified_count = 0

            if auto_fix:
                pending_items = [i for i in items if i.status == "pending"]
                if pending_items:
                    result = self._frontmatter_service.apply(pending_items)
                    modified_count = result.modified_count

            pending_count = sum(1 for i in items if i.status == "pending")
            skipped_count = sum(1 for i in items if i.status == "skipped")
            error_count = sum(1 for i in items if i.status == "error")

            dto = SpecFrontmatterResultDTO(
                items=[
                    {
                        "spec_id": i.spec_id,
                        "file_path": str(i.file_path),
                        "has_frontmatter": i.has_frontmatter,
                        "is_deprecated": i.is_deprecated,
                        "file_exists": i.file_exists,
                        "status": i.status,
                        "new_frontmatter": i.new_frontmatter[:200] if i.new_frontmatter else "",
                    }
                    for i in items
                ],
                total_count=len(items),
                pending_count=pending_count,
                skipped_count=skipped_count,
                error_count=error_count,
                modified_count=modified_count,
                auto_fixed=auto_fix,
            )
            return CommandResult(success=True, message="Success", payload=dto)
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload=None)
