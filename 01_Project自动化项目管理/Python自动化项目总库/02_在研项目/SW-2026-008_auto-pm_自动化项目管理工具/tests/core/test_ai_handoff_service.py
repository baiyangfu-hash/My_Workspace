from __future__ import annotations

import json

from auto_pm.core.ai_handoff_service import AiHandoffService


def test_list_pending_normalizes_handoff_v2_defaults(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """最小交接包也应被补齐为可消费的 V2 默认结构。"""
    workspace = tmp_path / "workspace"
    handoff_dir = workspace / ".auto-pm" / "handoffs"
    handoff_dir.mkdir(parents=True)
    payload = {
        "request_id": "AI-20260813-001",
        "project_id": "SW-2026-008",
        "executor_skill": "fullstack-engineer",
        "summary": "完成变更中心状态筛选改造",
    }
    (handoff_dir / "AI-20260813-001.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    service = AiHandoffService(workspace)
    handoffs = service.list_pending("SW-2026-008")

    assert len(handoffs) == 1
    handoff = handoffs[0]
    assert handoff["status"] == "pending"
    assert handoff["changed_files"] == []
    assert handoff["verification"]["other_checks"] == []
    assert handoff["product_impact"]["needs_user_validation"] is False
    assert handoff["pm_closure"]["required"] is True
    assert handoff["pm_closure"]["suggested_status"] == "pending_review"


def test_list_pending_skips_consumed_and_invalid_handoffs(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """只返回字段完整且状态为 pending 的交接包。"""
    workspace = tmp_path / "workspace"
    handoff_dir = workspace / ".auto-pm" / "handoffs"
    handoff_dir.mkdir(parents=True)
    valid_payload = {
        "request_id": "AI-20260813-002",
        "project_id": "SW-2026-008",
        "executor_skill": "plc-electrical-engineer",
        "summary": "待 PM 收口",
    }
    consumed_payload = {
        "request_id": "AI-20260813-003",
        "project_id": "SW-2026-008",
        "executor_skill": "fullstack-engineer",
        "summary": "已被消费",
        "status": "consumed",
    }
    invalid_payload = {
        "request_id": "AI-20260813-004",
        "project_id": "SW-2026-008",
        "executor_skill": "",
        "summary": "缺少执行技能",
    }
    (handoff_dir / "valid.json").write_text(json.dumps(valid_payload, ensure_ascii=False), encoding="utf-8")
    (handoff_dir / "consumed.json").write_text(json.dumps(consumed_payload, ensure_ascii=False), encoding="utf-8")
    (handoff_dir / "invalid.json").write_text(json.dumps(invalid_payload, ensure_ascii=False), encoding="utf-8")

    service = AiHandoffService(workspace)
    handoffs = service.list_pending()

    assert [handoff["request_id"] for handoff in handoffs] == ["AI-20260813-002"]
    assert service.get_pending("AI-20260813-002") is not None
    assert service.get_pending("AI-20260813-003") is None
