from __future__ import annotations

from collections.abc import Generator

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp() -> Generator[QApplication, None, None]:
    """UI 测试共享的 QApplication 实例。

    避免每个模块重复声明 session 级 qapp fixture，导致 pytest
    把同一个 QApplication.instance() 当成多个独立 session fixture
    管理，放大 Qt 会话 teardown 的不确定性。
    """
    app = QApplication.instance() or QApplication([])
    assert isinstance(app, QApplication)
    yield app
