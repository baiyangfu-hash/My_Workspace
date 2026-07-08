"""Facade Registry 装配器"""

from typing import TypedDict

from auto_pm.application.change_facade import ChangeFacade
from auto_pm.application.delivery_facade import DeliveryFacade
from auto_pm.application.spec_facade import SpecFacade
from auto_pm.application.system_facade import SystemFacade
from auto_pm.application.workbench_facade import WorkbenchFacade
from auto_pm.core.protocols import (
    AssetSummaryServiceProtocol,
    ChangeServiceProtocol,
    DashboardServiceProtocol,
    DocRefreshServiceProtocol,
    PmSessionServiceProtocol,
    ProjectServiceProtocol,
    ReportServiceProtocol,
    SpecCenterServiceProtocol,
    SpecCheckServiceProtocol,
    TemplateServiceProtocol,
)


class ServiceContainer(TypedDict):
    """FacadeRegistry 装配所需的基础 Service 容器

    所有 key 均为必填（调用方必须提供完整字典）。除 project_service 外，其余
    Service 的工厂函数返回类型为 `Any | None`（如工作空间无 spec_registry.json
    时 spec_check_service 为 None），因此 TypedDict 字段统一标注为 `Protocol | None`；
    Facade 构造函数对 None 有降级处理。
    """

    # Service（工厂函数可能返回 None，Facade 内部降级处理）
    dashboard_service: DashboardServiceProtocol | None
    project_service: ProjectServiceProtocol
    asset_summary_service: AssetSummaryServiceProtocol | None
    pm_session_service: PmSessionServiceProtocol | None
    change_service: ChangeServiceProtocol | None
    spec_check_service: SpecCheckServiceProtocol | None
    spec_center_service: SpecCenterServiceProtocol | None
    doc_refresh_service: DocRefreshServiceProtocol | None
    report_service: ReportServiceProtocol | None
    template_service: TemplateServiceProtocol | None


class FacadeRegistry:
    """手工依赖注入装配器，负责持有各基础 Service 并组装出 Application Facades"""

    def __init__(self) -> None:
        self.workbench_facade: WorkbenchFacade | None = None
        self.change_facade: ChangeFacade | None = None
        self.spec_facade: SpecFacade | None = None
        self.delivery_facade: DeliveryFacade | None = None
        self.system_facade: SystemFacade | None = None

    def initialize(self, services: ServiceContainer) -> None:
        """根据传入的基础 Service 字典，装配 Facades"""
        # 取出 services（TypedDict 提供类型安全，无需 cast）
        dashboard_service = services["dashboard_service"]
        project_service = services["project_service"]
        asset_summary_service = services["asset_summary_service"]
        change_service = services["change_service"]
        spec_check_service = services["spec_check_service"]
        spec_center_service = services["spec_center_service"]
        doc_refresh_service = services["doc_refresh_service"]
        report_service = services["report_service"]
        pm_session_service = services["pm_session_service"]
        template_service = services["template_service"]

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
            project_service=project_service,  # 阶段 C: bug #1/#2/#3 修复需要
        )

        self.system_facade = SystemFacade(
            pm_session_service=pm_session_service,
            template_service=template_service,
            project_service=project_service,  # 阶段 C: bug #6 修复需要
        )
