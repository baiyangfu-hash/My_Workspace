"""Facade Registry 装配器"""

from typing import Any

from auto_pm.application.change_facade import ChangeFacade
from auto_pm.application.delivery_facade import DeliveryFacade
from auto_pm.application.spec_facade import SpecFacade
from auto_pm.application.system_facade import SystemFacade
from auto_pm.application.workbench_facade import WorkbenchFacade


class FacadeRegistry:
    """手工依赖注入装配器，负责持有各基础 Service 并组装出 Application Facades"""

    def __init__(self):
        self.workbench_facade: WorkbenchFacade | None = None
        self.change_facade: ChangeFacade | None = None
        self.spec_facade: SpecFacade | None = None
        self.delivery_facade: DeliveryFacade | None = None
        self.system_facade: SystemFacade | None = None

    def initialize(self, services: dict[str, Any]) -> None:
        """根据传入的基础 Service 字典，装配 Facades"""
        # 取出 services
        dashboard_service = services.get("dashboard_service")
        project_service = services.get("project_service")
        asset_summary_service = services.get("asset_summary_service")
        change_service = services.get("change_service")
        spec_check_service = services.get("spec_check_service")
        spec_center_service = services.get("spec_center_service")
        doc_refresh_service = services.get("doc_refresh_service")
        report_service = services.get("report_service")
        pm_session_service = services.get("pm_session_service")

        template_service = services.get("template_service")

        # 装配 Facades
        self.workbench_facade = WorkbenchFacade(
            dashboard_service=dashboard_service,
            project_service=project_service,
            asset_summary_service=asset_summary_service,
        )

        self.change_facade = ChangeFacade(
            change_service=change_service,
        )

        self.spec_facade = SpecFacade(
            spec_check_service=spec_check_service,
            spec_center_service=spec_center_service,
        )

        self.delivery_facade = DeliveryFacade(
            doc_refresh_service=doc_refresh_service,
            report_service=report_service,
            asset_summary_service=asset_summary_service,
        )

        self.system_facade = SystemFacade(
            pm_session_service=pm_session_service,
            template_service=template_service,
        )
