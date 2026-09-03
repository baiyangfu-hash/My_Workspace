"""单元测试：决策包与 Handoff 派发强校验绑定（Decision to Handoff Binding）"""

import json
from pathlib import Path
import pytest

from auto_pm.application.core.ai_handoff_service import (
    AiHandoffService,
    HandoffValidationError,
)
from auto_pm.contracts.decision_package import DecisionPackageDTO
from auto_pm.domain.change.decision_service import DecisionService


@pytest.fixture
def mock_decision(tmp_path: Path) -> DecisionPackageDTO:
    """创建测试用的已固化决策包"""
    service = DecisionService(tmp_path)
    # 直接写入一个标准的已固化决策包
    dto = DecisionPackageDTO(
        decision_id="DEC-20260903-TEST8888",
        project_id="SW-2026-009",
        change_id="CHG-SCPT-2026-002",
        approved_scope="MODULE",
        approved_files=["src/services/dictionary_service.py", "tests/test_services.py"],
        approver="fubai",
        approved_at="2026-09-03T12:00:00Z",
        decision_conclusion="approved",
    )
    dec_file = service.decisions_dir / f"{dto.decision_id}.json"
    dec_file.write_text(json.dumps(dto.to_dict(), ensure_ascii=False), encoding="utf-8")
    return dto


def test_handoff_create_with_valid_decision(tmp_path: Path, mock_decision: DecisionPackageDTO):
    """测试携带合法决策包创建 handoff 成功并注入白名单"""
    service = AiHandoffService(tmp_path)
    payload = service.create_request(
        project_id="SW-2026-009",
        executor_skill="fullstack-engineer",
        summary="测试实施",
        change_id="CHG-SCPT-2026-002",
        decision_id=mock_decision.decision_id,
        mode="execution",
    )
    assert payload["decision_id"] == mock_decision.decision_id
    assert payload["change_id"] == "CHG-SCPT-2026-002"
    context = payload["skill_context"]
    assert context["decision_id"] == mock_decision.decision_id
    assert context["approved_scope"] == "MODULE"
    assert "src/services/dictionary_service.py" in context["approved_files"]


def test_handoff_create_rejects_nonexistent_decision(tmp_path: Path):
    """测试提供不存在的 decision_id 时抛出 HandoffValidationError 阻断"""
    service = AiHandoffService(tmp_path)
    with pytest.raises(HandoffValidationError) as exc_info:
        service.create_request(
            project_id="SW-2026-009",
            executor_skill="fullstack-engineer",
            summary="测试实施",
            decision_id="DEC-NON-EXISTENT",
        )
    assert "决策包验证失败" in str(exc_info.value)


def test_handoff_create_rejects_mismatched_project(tmp_path: Path, mock_decision: DecisionPackageDTO):
    """测试决策包项目编号与 handoff project_id 不匹配时阻断"""
    service = AiHandoffService(tmp_path)
    with pytest.raises(HandoffValidationError) as exc_info:
        service.create_request(
            project_id="DJ-2026-005",  # 与决策包 SW-2026-009 冲突
            executor_skill="plc-electrical-engineer",
            summary="测试实施",
            decision_id=mock_decision.decision_id,
        )
    assert "决策包项目编号不匹配" in str(exc_info.value)


def test_handoff_create_rejects_mismatched_change_id(tmp_path: Path, mock_decision: DecisionPackageDTO):
    """测试决策包关联变更单与 handoff change_id 不匹配时阻断"""
    service = AiHandoffService(tmp_path)
    with pytest.raises(HandoffValidationError) as exc_info:
        service.create_request(
            project_id="SW-2026-009",
            executor_skill="fullstack-engineer",
            summary="测试实施",
            change_id="CHG-SCPT-2026-999",  # 与决策包 CHG-SCPT-2026-002 冲突
            decision_id=mock_decision.decision_id,
        )
    assert "决策包关联变更单不匹配" in str(exc_info.value)
