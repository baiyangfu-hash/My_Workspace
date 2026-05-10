# -*- coding: utf-8 -*-
"""
STEditor 可选依赖测试
"""
import importlib

import pytest

pytest.importorskip("PyQt5")


def test_st_editor_fallback_when_qscintilla_missing(monkeypatch):
    from PyQt5.QtWidgets import QApplication
    from src.ui.widgets.st_editor import STEditor

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    real_import = importlib.import_module

    def fake_import(name, package=None):
        if name in ("PyQt5.Qsci", "Qsci"):
            raise ImportError("Qsci not available")
        return real_import(name, package)

    monkeypatch.setattr(importlib, "import_module", fake_import)

    editor = STEditor(show_dependency_notice=False)

    assert editor.has_full_features is False

    original = editor.get_text()
    assert "FUNCTION_BLOCK" in original

    editor.set_text("PROGRAM Test\nEND_PROGRAM")
    assert "PROGRAM Test" in editor.get_text()
