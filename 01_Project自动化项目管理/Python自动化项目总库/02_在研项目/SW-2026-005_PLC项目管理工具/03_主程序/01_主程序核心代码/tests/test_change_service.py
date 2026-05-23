# -*- coding: utf-8 -*-
"""ChangeService 单元测试"""
from pathlib import Path

import pytest

from src.core.constants import ChangeCategory, ChangeStatus
from src.services.change_service import ChangeService


def _make_change_root(project_path: Path) -> Path:
    """创建变更单根目录"""
    root = project_path / ChangeService.CHANGE_ROOT
    root.mkdir(parents=True, exist_ok=True)
    return root


def _write_change_file(change_root: Path, change_id: str, status: str) -> Path:
    """写入一个变更单 .md 文件

    _read_status 返回文件中第一个非空非标题行，
    所以 ## 状态 必须是第一个内容节，确保状态值被正确读取。
    """
    sub = change_root / f"CHG-{change_id.split('-')[1] if '-' in change_id else 'DOCU'}"
    sub.mkdir(parents=True, exist_ok=True)
    fp = sub / f"{change_id}.md"
    fp.write_text(
        f"# {change_id}\n\n"
        f"## 状态\n{status}\n\n"
        f"## 标题\n测试变更单\n\n"
        f"## 描述\n测试描述\n",
        encoding="utf-8",
    )
    return fp


def test_list_change_requests_empty(tmp_path: Path):
    """项目目录无变更单时返回空列表"""
    project = tmp_path / "EmptyProject"
    project.mkdir()

    result = ChangeService.list_change_requests(str(project))

    assert result == []


def test_list_change_requests_with_files(tmp_path: Path):
    """扫描到变更单文件后返回对应列表"""
    project = tmp_path / "DemoProject"
    root = _make_change_root(project)

    _write_change_file(root, "CHG-PLC-2026-001", "draft")
    _write_change_file(root, "CHG-DOCU-2026-001", "review")

    result = ChangeService.list_change_requests(str(project))

    assert len(result) == 2
    ids = [r.change_id for r in result]
    assert "CHG-DOCU-2026-001" in ids
    assert "CHG-PLC-2026-001" in ids


def test_create_change_request(tmp_path: Path):
    """创建变更单后文件存在且内容正确"""
    project = tmp_path / "NewProject"
    project.mkdir()

    request, error = ChangeService.create_change_request(
        project_path=str(project),
        category=ChangeCategory.PLC,
        title="新增PLC逻辑",
        description="测试创建变更单",
    )

    assert error is None
    assert request is not None
    assert request.change_id.startswith("CHG-PLC-2026-")
    assert request.status == ChangeStatus.DRAFT.value
    assert request.title == "新增PLC逻辑"

    change_file = Path(request.affected_paths[0])
    assert (project / change_file).exists()


def test_update_status_valid_transition(tmp_path: Path):
    """有效状态转换成功"""
    project = tmp_path / "StatusProject"
    root = _make_change_root(project)
    _write_change_file(root, "CHG-PLC-2026-001", "draft")

    ok = ChangeService.update_status(
        str(project), "CHG-PLC-2026-001", ChangeStatus.REVIEW
    )

    assert ok is True

    fp = ChangeService._find_change_file(str(project), "CHG-PLC-2026-001")
    assert ChangeService._read_status(fp) == "review"


def test_update_status_invalid_transition(tmp_path: Path):
    """无效状态转换失败"""
    project = tmp_path / "InvalidProject"
    root = _make_change_root(project)
    _write_change_file(root, "CHG-PLC-2026-001", "draft")

    ok = ChangeService.update_status(
        str(project), "CHG-PLC-2026-001", ChangeStatus.APPROVED
    )

    assert ok is False

    fp = ChangeService._find_change_file(str(project), "CHG-PLC-2026-001")
    assert ChangeService._read_status(fp) == "draft"


def test_approve_change_request(tmp_path: Path):
    """审核通过变更单，状态从 review 变为 approved"""
    project = tmp_path / "ApproveProject"
    root = _make_change_root(project)
    _write_change_file(root, "CHG-PLC-2026-001", "review")

    ok = ChangeService.approve_change_request(
        str(project), "CHG-PLC-2026-001", approver="张三"
    )

    assert ok is True

    fp = ChangeService._find_change_file(str(project), "CHG-PLC-2026-001")
    content = fp.read_text(encoding="utf-8")
    assert "approved" in content
    assert "张三" in content


def test_approve_change_request_wrong_status(tmp_path: Path):
    """非 review 状态的变更单无法审核"""
    project = tmp_path / "WrongStatusProject"
    root = _make_change_root(project)
    _write_change_file(root, "CHG-PLC-2026-001", "draft")

    ok = ChangeService.approve_change_request(
        str(project), "CHG-PLC-2026-001", approver="张三"
    )

    assert ok is False


def test_valid_transitions_draft():
    """DRAFT 状态只能转到 REVIEW 或 CANCELLED"""
    valid = ChangeStatus.valid_transitions(ChangeStatus.DRAFT)
    assert ChangeStatus.REVIEW in valid
    assert ChangeStatus.CANCELLED in valid
    assert ChangeStatus.APPROVED not in valid


def test_valid_transitions_completed():
    """COMPLETED 状态无有效转换"""
    valid = ChangeStatus.valid_transitions(ChangeStatus.COMPLETED)
    assert valid == []


def test_update_status_nonexistent_change(tmp_path: Path):
    """更新不存在的变更单返回 False"""
    project = tmp_path / "NoChangeProject"
    project.mkdir()

    ok = ChangeService.update_status(
        str(project), "CHG-PLC-2026-999", ChangeStatus.REVIEW
    )

    assert ok is False
