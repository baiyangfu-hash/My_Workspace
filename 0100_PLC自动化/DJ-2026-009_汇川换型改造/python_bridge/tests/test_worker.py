import pytest
from pydantic import ValidationError
from PySide6.QtCore import QThreadPool

from bridge.dto import ST_Station1, ST_Station1_Control
from bridge.worker import OpcUaWorker


def test_dto_default_values():
    """Test that DTO initializes correctly with default values."""
    station = ST_Station1()
    assert station.control.bAutoEnable is False
    assert station.status.iStep == 0

def test_dto_immutability():
    """Test that DTO is frozen per DEV-210 guidelines for immutability."""
    station = ST_Station1()
    with pytest.raises(ValidationError):
        station.control = ST_Station1_Control()


def test_worker_signals_and_run(qtbot):
    """
    Test worker initialization and basic signal emission.
    Uses qtbot to wait for signals.
    """
    worker = OpcUaWorker(url="opc.tcp://localhost:4840", node_id="mock")

    # We will test if connection status changed is emitted.
    # We run it in the QThreadPool just like in production.
    with qtbot.waitSignal(worker.signals.connection_status_changed, timeout=2000) as blocker:
        QThreadPool.globalInstance().start(worker)

    assert blocker.args[0] in ("CONNECTING", "COMM_ERROR")

    # Clean up
    worker.stop()
    QThreadPool.globalInstance().waitForDone(2000)
