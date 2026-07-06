"""Delivery Facade 接口层"""

from typing import Any

from auto_pm.ui.contracts.result import CommandResult, QueryResult


class DeliveryFacade:
    """提供给 UI 层的 Delivery (文档/报告/发布) 用例聚合入口"""

    def __init__(
        self,
        doc_refresh_service: Any = None,
        report_service: Any = None,
        asset_summary_service: Any = None,
    ):
        self._doc_refresh_service = doc_refresh_service
        self._report_service = report_service
        self._asset_summary_service = asset_summary_service

    @property
    def has_report_service(self) -> bool:
        return self._report_service is not None

    @property
    def has_asset_summary_service(self) -> bool:
        return self._asset_summary_service is not None

    @property
    def has_doc_refresh_service(self) -> bool:
        return self._doc_refresh_service is not None

    def refresh_project_docs(self, project_id: str, dry_run: bool = False) -> CommandResult[dict]:
        try:
            if not self._doc_refresh_service:
                return CommandResult(success=False, message="No doc_refresh_service", payload={})
            result = self._doc_refresh_service.refresh_project_documents(project_id, dry_run=dry_run)
            return CommandResult(success=True, message="Success", payload=result)
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload={})

    def get_project_report(self) -> QueryResult[dict]:
        try:
            if not self._report_service:
                return QueryResult(success=False, message="No report_service", payload={})
            return QueryResult(success=True, message="Success", payload=self._report_service.get_project_overview())
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload={})

    def get_change_report(self) -> QueryResult[dict]:
        try:
            if not self._report_service:
                return QueryResult(success=False, message="No report_service", payload={})
            return QueryResult(success=True, message="Success", payload=self._report_service.get_change_overview())
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload={})

    def get_spec_report(self) -> QueryResult[dict]:
        try:
            if not self._report_service:
                return QueryResult(success=False, message="No report_service", payload={})
            return QueryResult(success=True, message="Success", payload=self._report_service.get_spec_report())
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload={})

    def get_scan_report(self) -> QueryResult[dict]:
        try:
            if not self._report_service:
                return QueryResult(success=False, message="No report_service", payload={})
            return QueryResult(success=True, message="Success", payload=self._report_service.get_scan_report())
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload={})

    def refresh_asset_summary(self) -> CommandResult[dict]:
        try:
            if not self._asset_summary_service:
                return CommandResult(success=False, message="No asset_summary_service", payload={})
            result = self._asset_summary_service.refresh_all()
            return CommandResult(success=True, message="Success", payload=result)
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload={})

    def get_asset_summary(self) -> QueryResult[dict]:
        try:
            if not self._asset_summary_service:
                return QueryResult(success=False, message="No asset_summary_service", payload={})
            return QueryResult(success=True, message="Success", payload=self._asset_summary_service.get_summary())
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload={})
