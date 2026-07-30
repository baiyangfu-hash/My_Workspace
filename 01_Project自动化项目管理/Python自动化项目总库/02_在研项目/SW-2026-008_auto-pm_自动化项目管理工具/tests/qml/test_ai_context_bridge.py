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
    assert not (old_workspace / ".auto-pm" / "ai_context.json").exists()
    context_file = new_workspace / ".auto-pm" / "ai_context.json"
    assert context_file.exists()
    content = json.loads(context_file.read_text(encoding="utf-8"))
    assert content["workspace_root"] == str(new_workspace)


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
