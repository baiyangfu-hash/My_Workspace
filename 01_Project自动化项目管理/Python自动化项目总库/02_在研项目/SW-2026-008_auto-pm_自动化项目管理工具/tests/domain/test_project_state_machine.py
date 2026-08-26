from __future__ import annotations

from auto_pm.domain.project.state_machine import build_change_state_machine


def test_build_change_state_machine_implementing() -> None:
    state_machine = build_change_state_machine("implementing")

    assert state_machine["current_node"] == 2
    assert state_machine["progress"] == 66
    assert state_machine["nodes"][0]["status"] == "done"
    assert state_machine["nodes"][1]["status"] == "done"
    assert state_machine["nodes"][2]["status"] == "active"
    assert state_machine["nodes"][3]["status"] == "pending"


def test_build_change_state_machine_closed_marks_all_done() -> None:
    state_machine = build_change_state_machine("closed")

    assert state_machine["current_node"] == 3
    assert state_machine["progress"] == 100
    assert all(node["status"] == "done" for node in state_machine["nodes"])


def test_build_change_state_machine_unknown_falls_back_to_draft() -> None:
    state_machine = build_change_state_machine("unknown-status")

    assert state_machine["current_node"] == 0
    assert state_machine["current_node_name"] == "需求澄清 (Draft)"
    assert state_machine["nodes"][0]["status"] == "active"
