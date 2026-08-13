from __future__ import annotations

import json

from auto_pm.ui.qml.bridges.ai_context_bridge import AiContextBridge


def test_ai_context_bridge_updates_workspace_root(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """切换工作空间后，后续上下文写入应落到新 workspace_root。"""
    old_workspace = tmp_path / "old"
    new_workspace = tmp_path / "new"
    old_workspace.mkdir()
    new_workspace.mkdir()

    bridge = AiContextBridge(str(old_workspace))
    result = bridge.setWorkspaceRoot(str(new_workspace))

    assert result["success"] is True
    write_result = bridge.writeAiContext(
        "SW-2026-008",
        "auto-pm",
        "python",
        "developing",
        "CHG-SCPT-2026-151",
        "修复工作空间重载状态",
        "SCPT",
        "DEF",
        "implementing",
        "changeCenter",
    )

    assert write_result["success"] is True
    assert write_result["request_id"].startswith("AI-")
    assert not (old_workspace / ".auto-pm" / "ai_context.json").exists()
    context_file = new_workspace / ".auto-pm" / "ai_context.json"
    assert context_file.exists()
    content = json.loads(context_file.read_text(encoding="utf-8"))
    assert content["workspace_root"] == str(new_workspace)
    assert content["request_id"].startswith("AI-")
    assert content["entry_mode"] == "cockpit"
    assert content["intent"] == "implement_change"
    assert content["target_skill"] == "fullstack-engineer"
    assert content["product_context"]["goal_ref"] == "PM_SESSION_SW-2026-008.md#product-goal"


def test_ai_context_bridge_feedback_missing_falls_back_to_empty_state(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """缺失 ai_feedback.json 时返回消费者可渲染的空反馈状态。"""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    bridge = AiContextBridge(str(workspace))

    result = bridge.readAiFeedback()

    assert result["success"] is False
    assert result["feedback_state"] == "missing"
    assert result["feedback"]["status"] == "missing"
    assert result["feedback"]["summary"] == "暂无 AI 反馈"


def test_ai_context_bridge_feedback_invalid_json_falls_back_to_error_state(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """损坏的 ai_feedback.json 应降级为 invalid 状态而不是抛异常。"""
    workspace = tmp_path / "workspace"
    feedback_dir = workspace / ".auto-pm"
    feedback_dir.mkdir(parents=True)
    (feedback_dir / "ai_feedback.json").write_text("{bad json", encoding="utf-8")
    bridge = AiContextBridge(str(workspace))

    result = bridge.readAiFeedback()

    assert result["success"] is False
    assert result["feedback_state"] == "invalid"
    assert result["feedback"]["status"] == "invalid"
    assert "格式错误" in result["message"]


def test_ai_context_bridge_feedback_success(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """正常反馈文件应原样返回 available 状态。"""
    workspace = tmp_path / "workspace"
    feedback_dir = workspace / ".auto-pm"
    feedback_dir.mkdir(parents=True)
    feedback = {
        "generated_at": "2026-07-31T00:00:00+00:00",
        "status": "completed",
        "skill": "fullstack-engineer",
        "summary": "已完成",
    }
    (feedback_dir / "ai_feedback.json").write_text(
        json.dumps(feedback, ensure_ascii=False),
        encoding="utf-8",
    )
    bridge = AiContextBridge(str(workspace))

    result = bridge.readAiFeedback()

    assert result["success"] is True
    assert result["feedback_state"] == "available"
    assert result["feedback"]["status"] == "completed"
    assert result["feedback"]["skill"] == "fullstack-engineer"


def test_ai_context_bridge_write_pm_closure_context_uses_pending_handoff(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """PM 收口上下文应复用交接包 request_id，并补齐 V2 入口字段。"""
    workspace = tmp_path / "workspace"
    handoff_dir = workspace / ".auto-pm" / "handoffs"
    handoff_dir.mkdir(parents=True)
    handoff = {
        "request_id": "AI-20260813-000001",
        "project_id": "SW-2026-008",
        "executor_skill": "plc-electrical-engineer",
        "summary": "完成 PLC 检查并等待 PM 收口",
        "change_number": "CHG-PLC-2026-009",
        "change_title": "修复联锁时序",
        "change_domain": "PLC",
        "change_nature": "DEF",
        "change_status": "pending_review",
        "product_context": {
            "goal_ref": "PM_SESSION_SW-2026-008.md#product-goal",
            "hypothesis_ref": "",
            "success_metric_ref": "",
        },
    }
    (handoff_dir / "AI-20260813-000001.json").write_text(json.dumps(handoff, ensure_ascii=False), encoding="utf-8")
    bridge = AiContextBridge(str(workspace))

    result = bridge.writePmClosureContext(
        "AI-20260813-000001",
        "SW-2026-008",
        "auto-pm",
        "python",
        "developing",
        "",
        "",
        "changeCenter",
    )

    assert result["success"] is True
    context = json.loads((workspace / ".auto-pm" / "ai_context.json").read_text(encoding="utf-8"))
    assert context["request_id"] == "AI-20260813-000001"
    assert context["entry_mode"] == "cockpit"
    assert context["intent"] == "close_handoff"
    assert context["target_skill"] == "pm-workflow"
    assert context["handoff_request_id"] == "AI-20260813-000001"
    assert context["active_change"]["number"] == "CHG-PLC-2026-009"
    assert context["active_change"]["domain"] == "PLC"
    assert context["product_context"]["goal_ref"] == "PM_SESSION_SW-2026-008.md#product-goal"
