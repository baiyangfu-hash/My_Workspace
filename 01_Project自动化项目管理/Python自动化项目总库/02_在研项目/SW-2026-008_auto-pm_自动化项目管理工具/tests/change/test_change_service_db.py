"""M2-3 T55: ChangeService DB 集成测试

验证 ChangeService 在注入 DatabaseManager 后，CRUD 和状态流转操作会同步持久化到 DB：
- T53: create_change_request 同步写入 change_requests + impact_analysis
- T52: transition_status 同步写入 approval_history
- T54: update_change_request 同步更新 impact_analysis
"""

from __future__ import annotations

import gc
import os
from collections.abc import Generator

import pytest

from auto_pm.change.change_service import ChangeService
from auto_pm.db.connection import DatabaseManager
from auto_pm.db.repository import ChangeRequestRepository


@pytest.fixture
def svc_with_db(workspace_root: str) -> Generator[tuple[ChangeService, DatabaseManager], None, None]:
    """创建带 DB 的 ChangeService

    依赖 conftest.py 的 workspace_root fixture（创建 TEST-2026-001 项目结构）。
    teardown 时显式清理 DB 文件，避免 SQLite WAL 模式文件锁定导致临时目录无法删除。
    """
    db = DatabaseManager(workspace_root)
    db.init_schema()
    svc = ChangeService(workspace_root, db=db)
    yield svc, db
    # teardown: 释放 DB 资源，清理 WAL/SHM 文件（Windows 文件锁定规避）
    try:
        db.drop_all()
    except Exception:
        pass
    db.close()  # CHG-100 T2: 显式关闭连接，避免复用连接持有文件锁
    gc.collect()
    for ext in ("", "-wal", "-shm"):
        f = db.db_path + ext
        if os.path.isfile(f):
            try:
                os.remove(f)
            except (PermissionError, OSError):
                pass


@pytest.fixture
def created_change(
    svc_with_db: tuple[ChangeService, DatabaseManager], project_id: str
) -> Generator[tuple[str, ChangeService, DatabaseManager], None, None]:
    """创建一个测试变更单并返回 (change_number, svc, db)

    测试结束后自动清理变更单文件。
    """
    svc, db = svc_with_db
    cr = svc.create_change_request(
        project_id=project_id,
        domain="PLC",
        business_nature="DEF",
        impact_scope=["LOCAL"],
        applicant="集成测试",
        background="M2-3 集成测试变更背景",
        necessity="M2-3 集成测试变更必要性",
    )
    yield cr.change_number, svc, db
    # 清理变更单文件
    file_path = svc._locator.find_change_file(cr.change_number)
    if file_path and os.path.isfile(file_path):
        os.remove(file_path)


class TestChangeServiceDBIntegration:
    """M2-3 T55: ChangeService DB 持久化集成测试"""

    def test_create_writes_to_db(
        self,
        created_change: tuple[str, ChangeService, DatabaseManager],
    ) -> None:
        """T53: create_change_request 同步写入 change_requests + impact_analysis"""
        change_number, svc, db = created_change

        # 验证 change_requests 表有记录
        repo = ChangeRequestRepository(db)
        changes = repo.list_all()
        assert any(c.change_number == change_number for c in changes), \
            f"change_requests 表中应有 {change_number} 记录"

        # 验证 impact_analysis 表有记录
        analysis = repo.get_impact_analysis(change_number)
        assert analysis is not None, f"impact_analysis 表中应有 {change_number} 记录"
        assert analysis.change_number == change_number
        # 新创建的变更单 §6 影响分析为空（模板初始状态）
        assert analysis.risk_level == ""
        assert analysis.mitigation == ""
        assert analysis.updated_at != ""  # 自动填充时间

    def test_transition_writes_approval_history(
        self,
        created_change: tuple[str, ChangeService, DatabaseManager],
    ) -> None:
        """T52: transition_status 同步写入 approval_history"""
        change_number, svc, db = created_change

        # 流转: draft → submitted
        svc.transition_status(
            change_number=change_number,
            new_status="submitted",
            approver="测试审批人",
            comment="提交审批",
        )

        # 验证 approval_history 表有记录
        repo = ChangeRequestRepository(db)
        history = repo.list_approval_history(change_number)
        assert len(history) == 1, "应有 1 条审批历史记录"
        assert history[0].change_number == change_number
        assert history[0].from_status == "draft"
        assert history[0].to_status == "submitted"
        assert history[0].approver == "测试审批人"
        assert history[0].comment == "提交审批"

    def test_multiple_transitions_append_history(
        self,
        created_change: tuple[str, ChangeService, DatabaseManager],
    ) -> None:
        """T52: 多次流转追加多条审批历史记录"""
        change_number, svc, db = created_change

        # draft → submitted
        svc.transition_status(change_number, "submitted", "张三", "提交")
        # submitted → under_review
        svc.transition_status(change_number, "under_review", "李四", "开始审查")
        # under_review → approved
        svc.transition_status(change_number, "approved", "王五", "审批通过")

        repo = ChangeRequestRepository(db)
        history = repo.list_approval_history(change_number)
        assert len(history) == 3, "应有 3 条审批历史记录"
        # 验证按时间顺序
        assert history[0].to_status == "submitted"
        assert history[1].to_status == "under_review"
        assert history[2].to_status == "approved"
        # 验证 from_status 链
        assert history[0].from_status == "draft"
        assert history[1].from_status == "submitted"
        assert history[2].from_status == "under_review"

    def test_update_updates_impact_analysis(
        self,
        created_change: tuple[str, ChangeService, DatabaseManager],
    ) -> None:
        """T54: update_change_request 同步更新 impact_analysis"""
        change_number, svc, db = created_change

        # 修改变更单字段（background 是可修改字段）
        updated = svc.update_change_request(
            change_number, background="修改后的变更背景描述"
        )
        assert updated is not None

        # 验证 impact_analysis 记录仍存在（update 不应删除）
        repo = ChangeRequestRepository(db)
        analysis = repo.get_impact_analysis(change_number)
        assert analysis is not None, "impact_analysis 记录应仍存在"
        assert analysis.change_number == change_number

    def test_no_db_no_persistence(
        self,
        workspace_root: str,
        project_id: str,
    ) -> None:
        """T55: 未注入 DB 时不持久化（向后兼容，不报错）"""
        svc = ChangeService(workspace_root)  # 不注入 DB
        cr = svc.create_change_request(
            project_id=project_id,
            domain="PLC",
            business_nature="DEF",
            impact_scope=["LOCAL"],
            applicant="无DB测试",
            background="无DB测试背景",
            necessity="无DB测试必要性",
        )

        # 应正常创建文件，不报错
        assert os.path.isfile(cr.file_path)

        # 流转也应正常工作
        result = svc.transition_status(cr.change_number, "submitted", "测试", "提交")
        assert result is not None

        # 清理
        file_path = svc._locator.find_change_file(cr.change_number)
        if file_path and os.path.isfile(file_path):
            os.remove(file_path)
