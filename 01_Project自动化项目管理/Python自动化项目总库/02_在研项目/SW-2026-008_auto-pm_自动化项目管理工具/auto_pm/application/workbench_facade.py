"""PLC-HMI 概念映射：FB_Workbench 功能块

对应 PLC 的 FB，封装"工作台"域的完整业务逻辑。
- 输入引脚：__init__ 参数（project_service, dashboard_service 等）
- 输出引脚：返回 QueryResult/CommandResult（写回 HMI 变量表 → Bridge Signal 通知画面刷新）
- 内部调用：SFB 库函数（core/ 下的 Service）

--- 原始注释 ---
Workbench Facade 接口层"""

import logging
from typing import Any

from auto_pm.core.protocols import (
    AssetSummaryServiceProtocol,
    DashboardServiceProtocol,
    ProjectServiceProtocol,
    TemplateServiceProtocol,
)
from auto_pm.ui.contracts.dto.workbench_dto import (
    ClearCacheResultDTO,
    DashboardSnapshotDTO,
    ProjectCardDTO,
    ProjectWorkspaceDTO,
    RebuildIndexResultDTO,
    SettingsSummaryDTO,
)
from auto_pm.ui.contracts.result import CommandResult, QueryResult

log = logging.getLogger(__name__)


# CHG-106: 12 状态 → 4 节点状态机映射
# V7 原型 view-platform-dashboard 状态机：Draft → Review → Implementing → Closed
_STATE_MACHINE_NODES: tuple[dict[str, str], ...] = (
    {"name": "需求澄清 (Draft)", "icon": "pencil-simple"},
    {"name": "方案评审 (Review)", "icon": "paper-plane-tilt"},
    {"name": "实施中 (Implementing)", "icon": "code"},
    {"name": "闭环归档 (Closed)", "icon": "check"},
)

_STATUS_TO_NODE_INDEX: dict[str, int] = {
    "draft": 0,
    "submitted": 0,
    "under_review": 0,
    "approved": 1,
    "implementing": 2,
    "pending_acceptance": 2,
    "accepting": 2,
    "completed": 3,
    "closed": 3,
}


def _build_state_machine(status: str) -> dict[str, Any]:
    """根据 12 状态构建 4 节点状态机视图数据

    Returns:
        {
            "current_node": 0-3,
            "current_node_name": "...",
            "progress": 0-100,
            "nodes": [{"name", "icon", "status": "done"|"active"|"pending"}]
        }
    """
    current_node = _STATUS_TO_NODE_INDEX.get(status, 0)
    # 终态节点（Closed）：所有节点标 done，当前节点不再 active
    is_final = current_node == len(_STATE_MACHINE_NODES) - 1
    nodes: list[dict[str, Any]] = []
    for i, node_def in enumerate(_STATE_MACHINE_NODES):
        if i < current_node:
            node_status = "done"
        elif i == current_node:
            node_status = "done" if is_final else "active"
        else:
            node_status = "pending"
        nodes.append(
            {
                "name": node_def["name"],
                "icon": node_def["icon"],
                "status": node_status,
            }
        )
    # 线性进度：4 节点对应 0%, 33%, 66%, 100%
    total_nodes = len(_STATE_MACHINE_NODES)
    if total_nodes > 1:
        progress = int((current_node / (total_nodes - 1)) * 100)
    else:
        progress = 0
    return {
        "current_node": current_node,
        "current_node_name": _STATE_MACHINE_NODES[current_node]["name"],
        "progress": progress,
        "nodes": nodes,
    }


class WorkbenchFacade:
    """提供给 UI 层的 Workbench 用例聚合入口"""

    def __init__(
        self,
        project_service: ProjectServiceProtocol,
        dashboard_service: DashboardServiceProtocol | None = None,
        asset_summary_service: AssetSummaryServiceProtocol | None = None,
        template_service: TemplateServiceProtocol | None = None,
        change_service: Any = None,
        reload_callback: Any = None,
    ):
        self._dashboard_service = dashboard_service
        self._project_service = project_service
        self._asset_summary_service = asset_summary_service
        self._template_service = template_service
        self._change_service = change_service
        self._reload_callback = reload_callback

    @property
    def has_project_service(self) -> bool:
        return self._project_service is not None

    @property
    def has_dashboard_service(self) -> bool:
        return self._dashboard_service is not None

    def get_dashboard_snapshot(self) -> QueryResult[DashboardSnapshotDTO]:
        """获取驾驶舱摘要数据"""
        if not self._dashboard_service:
            return QueryResult(
                success=False,
                message="DashboardService 未启用",
                errors=["DashboardService 未启用"],
            )
        try:
            summary = self._dashboard_service.get_summary()
            dto = DashboardSnapshotDTO(
                total_projects=summary.total_projects,
                phase_counts=summary.phase_counts,
                open_change_count=summary.open_change_count,
                failed_check_project_count=summary.failed_check_project_count,
                not_applicable_project_count=summary.not_applicable_project_count,
                recent_activities=summary.recent_activities,
                risk_hints=summary.risk_hints,
                failed_check_project_ids=summary.failed_check_project_ids,
                not_applicable_project_ids=summary.not_applicable_project_ids,
                tech_debt_count=summary.tech_debt_count,
                tech_debt_total=summary.tech_debt_total,
                test_pass_rate=summary.test_pass_rate,
                test_total=summary.test_total,
            )
            return QueryResult(success=True, message="Success", payload=dto)
        except Exception as e:
            return QueryResult(success=False, message=str(e), errors=[str(e)])

    def get_active_change_status(self, project_id: str) -> QueryResult[dict[str, Any]]:
        """获取项目主线变更单的状态机视图数据（CHG-106 新增）

        用于平台驾驶舱状态机视图，返回最近一条活跃变更单 + 4 节点状态机结构。
        若无活跃变更单，返回 active=False 的空状态。

        Returns:
            QueryResult[dict], payload 结构:
            {
                "active": bool,
                "change_number": str,
                "title": str,
                "status": str,  # 原始 12 状态
                "apply_date": str,
                "state_machine": {
                    "current_node": int,
                    "current_node_name": str,
                    "progress": int,
                    "nodes": [{"name", "icon", "status"}]
                }
            }
        """
        try:
            if not self._dashboard_service:
                return QueryResult(
                    success=False,
                    message="DashboardService 未启用",
                    errors=["DashboardService 未启用"],
                )

            change = self._dashboard_service.get_active_change_for_project(project_id)
            if change is None:
                payload = {
                    "active": False,
                    "change_number": "",
                    "title": "",
                    "status": "",
                    "apply_date": "",
                    "state_machine": _build_state_machine("draft"),
                }
                return QueryResult(success=True, message="No active change", payload=payload)

            payload = {
                "active": True,
                "change_number": change.change_number,
                "title": change.title or change.change_number,
                "status": change.status,
                "apply_date": change.apply_date,
                "state_machine": _build_state_machine(change.status),
            }
            return QueryResult(success=True, message="Success", payload=payload)
        except Exception as e:
            return QueryResult(success=False, message=str(e), errors=[str(e)])

    def get_project_change_summary(self, project_id: str) -> QueryResult[dict[str, Any]]:
        """获取项目级变更聚合摘要（项目工作区变更Tab驾驶舱模式）

        返回预计算的 KPI、状态机和活动时间线数据，避免 QML 端重复计算。

        Args:
            project_id: 项目编号

        Returns:
            QueryResult[dict], payload 结构:
            {
                "kpi": {
                    "total": int,
                    "implementing": int,
                    "pending_review": int,
                    "this_week": int
                },
                "state_machine": {
                    "current_node": int,
                    "current_node_name": str,
                    "progress": float,
                    "nodes": list[dict]
                },
                "activities": list[dict]
            }
        """
        try:
            if not self._dashboard_service:
                return QueryResult(
                    success=False,
                    message="DashboardService 未启用",
                    errors=["DashboardService 未启用"],
                )

            payload = self._dashboard_service.get_change_summary_for_project(project_id)
            return QueryResult(success=True, message="Success", payload=payload)
        except Exception as e:
            return QueryResult(success=False, message=str(e), errors=[str(e)])

    def list_project_cards(self) -> QueryResult[list[ProjectCardDTO]]:
        """获取项目列表卡片

        优先使用 DB 缓存模式（list_projects_with_change_count，含 change_count 聚合），
        无 DB 时降级为文件系统扫描（list_projects，change_count=0）。
        """
        try:
            # 优先走 DB 缓存（含 change_count 聚合）
            try:
                items = self._project_service.list_projects_with_change_count()
            except RuntimeError:
                # 无 DB 时降级为文件系统扫描
                projects = self._project_service.list_projects()
                cards = [
                    ProjectCardDTO(
                        project_id=p.project_id,
                        name=p.name,
                        stack=str(p.stack),
                        phase=str(p.phase),
                        version=p.version,
                        health_status="Unknown",  # TODO M3: 接入 Change 域实时状态
                        open_change_count=0,
                        last_activity_at=None,  # TODO M3: 从 file_mtime 转换
                        path=p.path,
                        business_line=str(p.business_line),
                    )
                    for p in projects
                ]
                return QueryResult(success=True, message="Success", payload=cards)

            # DB 缓存模式：ProjectListItem → ProjectCardDTO
            cards = [
                ProjectCardDTO(
                    project_id=item.project_id,
                    name=item.name,
                    stack=str(item.stack),
                    phase=str(item.phase),
                    version=item.version,
                    health_status="Unknown",  # TODO M3: 接入 Change 域实时状态
                    open_change_count=item.change_count,
                    last_activity_at=None,  # TODO M3: 从 file_mtime 转换
                    path=item.path,
                    business_line=str(item.business_line),
                )
                for item in items
            ]
            return QueryResult(success=True, message="Success", payload=cards)
        except Exception as e:
            return QueryResult(success=False, message=str(e), errors=[str(e)])

    def get_project_workspace(self, project_id: str) -> QueryResult[ProjectWorkspaceDTO]:
        """获取单个项目的工作台聚合信息"""
        try:
            project = self._project_service.get_project(project_id)
            if not project:
                return QueryResult(success=False, message=f"Project not found: {project_id}", errors=["ProjectNotFound"])
            
            summary = project.model_dump() if hasattr(project, "model_dump") else {}
            # stack 等枚举类型转字符串以匹配旧的行为
            for k, v in summary.items():
                if hasattr(v, "value"):
                    summary[k] = str(v.value)
            
            asset_summary = None
            if self._asset_summary_service:
                stack_str = str(project.stack)
                asset_summary = self._asset_summary_service.build_summary(
                    project_path=project.path,
                    stack=stack_str,
                    project_type=project.project_type,
                )
            
            dto = ProjectWorkspaceDTO(
                project_id=project_id,
                summary=summary,
                asset_summary=asset_summary,
                document_status=None,  # TODO M3/M4: 接入 DocumentService
                vartable_status=None,  # TODO M3/M4: 接入 VartableService
                pending_actions=[],    # TODO M3: 从 ChangeService 查询 open changes
            )
            return QueryResult(success=True, message="Success", payload=dto)
        except Exception as e:
            return QueryResult(success=False, message=str(e), errors=[str(e)])

    def get_settings_summary(self) -> QueryResult[SettingsSummaryDTO]:
        """获取设置页摘要基本信息（除 change_count 以外）"""
        try:
            if not self._project_service:
                return QueryResult(success=False, message="No project_service")

            db_path = self._project_service.get_db_path()
            db_available = self._project_service.is_cache_available()
            project_count = self._project_service.get_project_count()

            try:
                last_sync = self._project_service.get_last_sync_time()
            except Exception as e:
                log.warning("获取最后同步时间失败: %s", e, exc_info=True)
                last_sync = "—"

            dto = SettingsSummaryDTO(
                workspace_root=self._project_service.workspace_root,
                db_path=db_path,
                project_count=project_count,
                last_sync=last_sync,
                db_available=db_available,
            )
            return QueryResult(success=True, message="Success", payload=dto)
        except Exception as e:
            return QueryResult(success=False, message=str(e))

    def clear_cache(self) -> CommandResult[ClearCacheResultDTO]:
        """清除 DB 缓存并重新初始化"""
        try:
            if not self._project_service:
                return CommandResult(
                    success=False,
                    message="No project_service",
                    payload=ClearCacheResultDTO(success=False, message="No project_service"),
                )

            if not self._project_service.is_cache_available():
                return CommandResult(
                    success=False,
                    message="DB 未初始化，无需清除",
                    payload=ClearCacheResultDTO(success=False, message="DB 未初始化，无需清除"),
                )

            result = self._project_service.clear_cache()
            dto = ClearCacheResultDTO(
                success=result["success"],
                message=result["message"],
            )
            return CommandResult(success=True, message=dto.message, payload=dto)
        except Exception as e:
            return CommandResult(
                success=False,
                message=str(e),
                payload=ClearCacheResultDTO(success=False, message=f"清除缓存失败: {e}"),
            )

    def rebuild_index(self) -> CommandResult[RebuildIndexResultDTO]:
        """重建 DB 索引"""
        try:
            if not self._project_service:
                return CommandResult(
                    success=False,
                    message="No project_service",
                    payload=RebuildIndexResultDTO(
                        projects_found=0, changes_found=0, message="No project_service"
                    ),
                )

            if not self._project_service.is_cache_available():
                return CommandResult(
                    success=False,
                    message="DB 未初始化，无法重建索引",
                    payload=RebuildIndexResultDTO(
                        projects_found=0, changes_found=0, message="DB 未初始化，无法重建索引"
                    ),
                )

            result = self._project_service.sync_to_cache(force_full=True)
            projects_found = int(result.get("projects_found", 0))
            changes_found = int(result.get("changes_found", 0))
            dto = RebuildIndexResultDTO(
                projects_found=projects_found,
                changes_found=changes_found,
                message=f"重建完成：发现 {projects_found} 个项目，{changes_found} 条变更单",
            )
            return CommandResult(success=True, message="Success", payload=dto)
        except Exception as e:
            return CommandResult(
                success=False,
                message=str(e),
                payload=RebuildIndexResultDTO(
                    projects_found=0, changes_found=0, message=f"重建索引失败: {e}"
                ),
            )

    def create_project(
        self,
        project_id: str,
        project_name: str,
        stack: str,
        mode: str,
        business_line: str,
        dest_dir: str = "",
    ) -> CommandResult[dict[str, Any] | None]:
        """QML GUI: 创建新项目（去伪存真，对接 Copier 模板生成骨架）

        Args:
            dest_dir: 项目存放目录（空字符串表示用默认目录 0100_项目/）
        """
        try:
            if not self._template_service:
                return CommandResult(success=False, message="TemplateService 未注入", payload=None)

            import os

            from auto_pm.core.constants import get_template_name
            from auto_pm.core.paths import get_default_projects_dir

            # V1.0.1: 默认项目存放目录改为 auto-pm 工具目录下的 0100_项目/
            # 用户可通过 dest_dir 参数指定其他目录
            if dest_dir:
                dest_root = os.path.abspath(dest_dir)
            else:
                dest_root = get_default_projects_dir()
            project_dir = f"{project_id}_{project_name}"
            dest_path = os.path.abspath(os.path.join(dest_root, project_dir))

            if os.path.exists(dest_path):
                return CommandResult(success=False, message=f"目标路径已存在: {dest_path}", payload=None)

            template_name = get_template_name(stack, mode if stack == "plc" else "")

            # 业务线推断：未指定时从项目编号前缀提取
            if not business_line:
                business_line = project_id.split("-", 1)[0] if "-" in project_id else ""

            data = {
                "project_id": project_id,
                "project_name": project_name,
                "description": project_name,
                "version": "V1.0.0",
                "stack": stack,
                "mode": mode if stack == "plc" else "",
                "business_line": business_line,
            }

            os.makedirs(dest_root, exist_ok=True)
            self._template_service.copy_template(template_name, dest_path, data)

            # 补全元数据
            if hasattr(self._project_service, "retrofit_project_by_path"):
                try:
                    self._project_service.retrofit_project_by_path(dest_path)
                except Exception:
                    pass

            # 同步缓存
            self._project_service.sync_to_cache(force_full=True)

            # 审计日志
            try:
                from auto_pm.logging.audit import audit_log
                audit_log(
                    "project_create",
                    project_id=project_id,
                    project_name=project_name,
                    stack=stack,
                    mode=mode if stack == "plc" else "",
                    business_line=business_line,
                    path=dest_path,
                )
            except Exception:
                pass

            return CommandResult(
                success=True,
                message=f"项目创建成功: {project_id}",
                payload={"project_id": project_id, "path": dest_path},
            )
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload=None)

    def generate_project_code(self, business_line: str) -> CommandResult[str]:
        """自动生成项目编号"""
        try:
            code = self._project_service.generate_project_code(business_line)
            return CommandResult(success=True, message="", payload=code)
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload=None)

    def detect_project(self, path: str) -> CommandResult[dict[str, Any] | None]:
        """检测指定路径是否为有效项目目录

        调用 ProjectScanner.try_identify_project 识别项目元数据，
        供 Bridge 层 detectProject 使用，避免 Bridge 层直接访问私有属性。
        """
        try:
            from auto_pm.core.project_scanner import ProjectScanner

            scanner = ProjectScanner(self._project_service.workspace_root)
            proj = scanner.try_identify_project(path)
            if proj:
                return CommandResult(
                    success=True,
                    message="",
                    payload={
                        "project_id": proj.project_id,
                        "name": proj.name,
                        "stack": str(proj.stack),
                    },
                )
            return CommandResult(
                success=False,
                message="无法在此路径下识别到有效的项目元数据文件",
                payload=None,
            )
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload=None)

    def import_project(self, src_path: str) -> CommandResult[dict[str, Any] | None]:
        """QML GUI: 导入外部项目目录"""
        try:
            import os
            # 调用 project_service.import_project(src_path)
            dest_path = self._project_service.import_project(src_path)

            # 解析 project_id
            from auto_pm.core.project_scanner import ProjectScanner
            scanner = ProjectScanner(self._project_service.workspace_root)
            proj_info = scanner.try_identify_project(dest_path)
            project_id = proj_info.project_id if proj_info else os.path.basename(dest_path)

            return CommandResult(
                success=True,
                message=f"项目导入成功: {project_id}",
                payload={"project_id": project_id, "path": dest_path},
            )
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload=None)

    def edit_project(self, project_id: str, **kwargs: str) -> CommandResult[dict[str, Any] | None]:
        """编辑项目元数据（M4 CHG-115 新增）

        调用 ProjectService.update_project_meta 更新项目字段，
        支持 phase/description/version/business_line 等字段。
        """
        try:
            updated = self._project_service.update_project_meta(project_id, **kwargs)
            self._project_service.sync_to_cache(force_full=True)
            summary = updated.model_dump() if hasattr(updated, "model_dump") else {}
            return CommandResult(
                success=True,
                message=f"项目元数据已更新: {project_id}",
                payload={"project_id": project_id, "fields": kwargs, "summary": summary},
            )
        except FileNotFoundError:
            return CommandResult(success=False, message=f"项目不存在: {project_id}", payload=None)
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload=None)

    def delete_project(self, project_id: str) -> CommandResult[dict[str, Any] | None]:
        """删除项目（M4 CHG-115 新增，破坏性操作）

        删除项目目录并记录审计日志。
        """
        try:
            import shutil

            proj = self._project_service.get_project(project_id)
            if proj is None:
                return CommandResult(success=False, message=f"项目不存在: {project_id}", payload=None)

            proj_path = proj.path
            proj_name = proj.name

            shutil.rmtree(proj_path)

            from auto_pm.logging.audit import audit_log
            audit_log(
                "project_delete",
                project_id=project_id,
                project_name=proj_name,
                path=proj_path,
            )

            self._project_service.sync_to_cache(force_full=True)

            return CommandResult(
                success=True,
                message=f"项目已删除: {project_id}",
                payload={"project_id": project_id, "name": proj_name},
            )
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload=None)

    def save_workspace_root(self, workspace_root: str) -> CommandResult[None]:
        """保存全局工作空间根目录设置"""
        try:
            import os
            # 校验路径合法性
            workspace_root = os.path.abspath(workspace_root)
            if not os.path.isdir(workspace_root):
                return CommandResult(success=False, message=f"路径不存在或不是目录: {workspace_root}")

            # 写入 .auto-pm-workspace 配置文件
            from auto_pm.core.paths import get_config_file_path
            cfg_file = get_config_file_path()
            with open(cfg_file, "w", encoding="utf-8") as f:
                f.write(workspace_root)

            # 更新当前运行环境中的 workspace_root (以便能实时显示，尽管部分缓存库需要重启)
            if self._project_service:
                self._project_service.workspace_root = workspace_root

            if getattr(self, "_reload_callback", None):
                self._reload_callback(workspace_root)

            return CommandResult(
                success=True,
                message=f"工作空间已成功更新并重载为: {workspace_root}！",
            )
        except Exception as e:
            return CommandResult(success=False, message=f"保存失败: {str(e)}")

    def initialize_project_pm(self, project_id: str) -> CommandResult[dict[str, Any]]:
        """为已有项目一键初始化 PM 框架与变更管理（含创世变更单创建与缓存同步）"""
        try:
            if not self._project_service:
                return CommandResult(success=False, message="ProjectService 未启用", payload={"success": False})

            project = self._project_service.get_project(project_id)
            if not project:
                return CommandResult(success=False, message=f"未找到项目: {project_id}", payload={"success": False})

            # 1. 补齐 PM 目录及文档骨架
            stack_str = str(project.stack).lower()
            self._project_service.init_project_pm_framework(
                project_path=project.path,
                project_id=project_id,
                project_name=project.name,
                stack_type=stack_str,
            )

            # 2. 如果启用了 change_service，为其生成首张创世变更单自愈补齐台账
            if self._change_service:
                import os as _os
                _applicant = _os.getenv("AUTO_PM_AUTHOR", _os.getlogin())
                domain = "PLC" if stack_str == "plc" else "SCPT"
                self._change_service.create_change_request(
                    project_id=project_id,
                    domain=domain,
                    business_nature="DEF",
                    impact_scope=["LOCAL"],
                    applicant=_applicant,
                    background="项目 PM 连续性基础文档与变更管理机制初始化。",
                    necessity="对齐规范管理，启用变更管理与对账自愈系统。",
                    retrofit=True,
                )

            # 3. 强制进行一次数据库项目和变更缓存同步，保证 UI 界面状态立即可见
            self._project_service.sync_to_cache(force_full=True)

            return CommandResult(
                success=True,
                message="项目 PM 与变更管理规范初始化成功",
                payload={"success": True, "project_id": project_id},
            )
        except Exception as e:
            log.error("初始化项目 PM 失败: %s", e, exc_info=True)
            return CommandResult(success=False, message=str(e), payload={"success": False})
