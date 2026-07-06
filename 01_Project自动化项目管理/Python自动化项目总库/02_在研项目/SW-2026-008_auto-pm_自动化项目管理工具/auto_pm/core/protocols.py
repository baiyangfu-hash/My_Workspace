"""Service 层 Protocol 接口定义（M3-Iter3）

定义 Service 层对外契约的 Protocol 接口，实现依赖倒置：
- UI/CLI 层依赖 Protocol，不依赖具体 Service 实现
- 便于单元测试时用 Fake/Mock 替换真实 Service
- 为未来扩展（如 RemoteProjectService）预留接口

Protocol 是结构性子类型（duck typing 的静态化），Service 无需显式继承。
"""

from __future__ import annotations

from typing import Any, Optional, Protocol, runtime_checkable

from auto_pm.models import (
    ChangeRequest,
    ChangeSummary,
    ProjectInfo,
    ProjectListItem,
)

# ── Project 域 ────────────────────────────────────────────

@runtime_checkable
class ProjectServiceProtocol(Protocol):
    """项目服务接口契约

    定义项目 CRUD + 查询 + 缓存同步的对外方法。
    ProjectService 实现此接口（无需显式继承）。
    """

    def list_projects(self, scan_depth: int = 4) -> list[ProjectInfo]:
        """扫描工作空间，返回所有项目"""
        ...

    def get_project(self, project_id: str) -> Optional[ProjectInfo]:
        """按 project_id 查询项目"""
        ...

    def find_project_path(self, project_id: str) -> Optional[str]:
        """按 project_id 查询项目路径"""
        ...

    def search_projects(self, keyword: str) -> list[ProjectInfo]:
        """关键字搜索项目"""
        ...

    def import_project(
        self,
        src_path: str,
        business_line: str | None = None,
        move: bool = False,
        force: bool = False,
    ) -> str:
        """导入外部项目目录到工作空间"""
        ...

    def update_project_meta(self, project_id: str, **kwargs: str) -> ProjectInfo:
        """更新项目元数据"""
        ...

    def list_projects_filtered(
        self,
        stack: Optional[str] = None,
        phase: Optional[str] = None,
        business_line: Optional[str] = None,
    ) -> list[ProjectInfo]:
        """按条件筛选项目"""
        ...

    def list_projects_with_change_count(self) -> list[ProjectListItem]:
        """返回带变更数统计的项目列表"""
        ...

    def sync_to_cache(self, force_full: bool = False) -> dict[str, Any]:
        """同步文件系统项目到 DB 缓存"""
        ...

    def get_last_sync_time(self) -> str:
        """获取上次同步时间（格式 YYYY-MM-DD HH:MM，无记录返回 '—'）"""
        ...

    def is_cache_available(self) -> bool:
        """DB 缓存是否可用"""
        ...

    def get_project_count(self) -> int:
        """获取项目总数（优先查缓存）"""
        ...

    def get_db_path(self) -> str:
        """获取 DB 文件路径（若未初始化则返回空字符串）"""
        ...


@runtime_checkable
class ProjectScannerProtocol(Protocol):
    """项目扫描器接口契约"""

    def scan(self, scan_depth: int = 4) -> list[ProjectInfo]:
        """扫描工作空间，返回所有项目"""
        ...

    def try_identify_project(self, project_path: str) -> Optional[ProjectInfo]:
        """尝试识别目录是否为项目"""
        ...


# ── Change 域 ─────────────────────────────────────────────

@runtime_checkable
class ChangeServiceProtocol(Protocol):
    """变更管理服务接口契约

    定义变更单 CRUD + 状态流转的对外方法。
    ChangeService 实现此接口（无需显式继承）。
    """

    def create_change_request(
        self,
        project_id: str,
        domain: str,
        business_nature: str,
        impact_scope: list[str],
        applicant: str,
        background: str,
        necessity: str,
        references: str = "",
        planned_date: str | None = None,
        urgency: str = "normal",
    ) -> ChangeRequest:
        """创建变更单"""
        ...

    def list_change_requests(
        self,
        project_id: str,
        status: str | None = None,
        domain: str | None = None,
    ) -> list[ChangeSummary]:
        """列出变更单，支持筛选"""
        ...

    def get_change_request(self, change_number: str) -> Optional[ChangeRequest]:
        """获取变更单完整内容"""
        ...

    def transition_status(
        self,
        change_number: str,
        new_status: str,
        approver: str = "",
        comment: str = "",
        verification_conclusion: str = "全部通过",
    ) -> Optional[ChangeRequest]:
        """状态流转"""
        ...

    def list_all_changes(
        self,
        status: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> list[ChangeSummary]:
        """跨项目查询所有变更单"""
        ...

    def update_change_request(
        self,
        change_number: str,
        **kwargs: Any,
    ) -> Optional[ChangeRequest]:
        """修改变更单字段"""
        ...

    def delete_change_request(self, change_number: str) -> bool:
        """删除变更单"""
        ...


# ── PLC 域 ────────────────────────────────────────────────

@runtime_checkable
class PlcServiceProtocol(Protocol):
    """PLC 服务接口契约（M3-Iter4 将提供实现）

    封装 PlcChecker/PlcRepairer，提供统一的 PLC 项目检查/修复/标准化入口。
    """

    def check(self, project_path: str, fix: bool = False) -> Any:
        """检查 PLC 项目规范性"""
        ...

    def repair(self, project_path: str) -> Any:
        """修复 PLC 项目规范问题"""
        ...

    def standardize(self, project_path: str, dry_run: bool = False) -> Any:
        """标准化 PLC 项目命名"""
        ...


# ── 通用 ──────────────────────────────────────────────────

@runtime_checkable
class ServiceProtocol(Protocol):
    """所有 Service 的基础接口

    标记一个类是 Service 层组件，便于运行时检查。
    """

    @property
    def workspace_root(self) -> str:
        """工作空间根目录"""
        ...
