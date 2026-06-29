"""GUI 全功能测试专用 fixture

测试项目生命周期：
- session 开始：在 0100_PLC自动化 下创建 DJ-2026-998 测试项目
- session 结束：清理测试失败的项目，保留测试成功的项目
- 每个测试函数：创建独立 MainWindow，避免状态污染
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# 必须在导入 PySide6 前设置离屏渲染（GUI_VISIBLE=1 时切换为可见窗口演示模式）
if not os.environ.get("GUI_VISIBLE"):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from tests.gui.helpers.bug_recorder import BugRecorder  # noqa: E402

# ── 常量 ──────────────────────────────────────────────────

WORKSPACE_ROOT = str(Path(__file__).resolve().parents[6])
PLC_ROOT = Path(WORKSPACE_ROOT) / "0100_PLC自动化"
TEST_PROJECT_ID = "DJ-2026-998"
TEST_PROJECT_NAME = "auto_pm_gui_test"
TEST_PROJECT_DIR = PLC_ROOT / f"{TEST_PROJECT_ID}_{TEST_PROJECT_NAME}"
REPORT_DIR = Path(__file__).resolve().parent.parent.parent / "test_reports" / "gui"


# ── Session 级 fixture ────────────────────────────────────


@pytest.fixture(scope="session")
def workspace_root() -> str:
    """工作空间根目录"""
    return WORKSPACE_ROOT


@pytest.fixture(scope="session")
def test_project_id() -> str:
    """测试项目 ID"""
    return TEST_PROJECT_ID


@pytest.fixture(scope="session")
def test_project_dir() -> Path:
    """测试项目目录路径"""
    return TEST_PROJECT_DIR


@pytest.fixture(scope="session")
def bug_recorder() -> BugRecorder:
    """Bug 记录器（session 级单例）"""
    recorder = BugRecorder(report_dir=REPORT_DIR)
    yield recorder
    # session 结束生成报告
    recorder.dump_report()


@pytest.fixture(scope="session", autouse=True)
def setup_test_project(qapp: QApplication, bug_recorder: BugRecorder):
    """session 级：创建测试项目，session 结束后清理失败项目"""
    # ── Setup：创建测试项目 ──
    if TEST_PROJECT_DIR.exists():
        # 已存在则复用
        pass
    else:
        # 通过 auto-pm CLI 创建
        try:
            result = subprocess.run(
                [
                    sys.executable, "-m", "auto_pm",
                    "-w", WORKSPACE_ROOT,
                    "plc", "init", TEST_PROJECT_ID,
                    "--name", "GUI自动化测试临时项目",
                ],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(Path(__file__).resolve().parent.parent.parent),
            )
            if result.returncode == 0:
                pass
            else:
                # CLI 失败则手动创建最小项目结构
                _create_minimal_project()
        except Exception:
            _create_minimal_project()

    qapp.processEvents()

    yield

    # ── Teardown：清理失败项目，保留成功项目 ──
    # 测试成功的项目保留（用户要求），失败的项目清理
    for failed_id in bug_recorder.failed_projects:
        failed_dir = PLC_ROOT / f"{failed_id}_auto_pm_gui_test"
        if failed_dir.exists():
            shutil.rmtree(failed_dir, ignore_errors=True)

    # 生成 Bug 报告
    bug_recorder.dump_report()


def _create_minimal_project() -> None:
    """手动创建最小 PLC 项目结构（CLI 失败时回退）"""
    TEST_PROJECT_DIR.mkdir(parents=True, exist_ok=True)
    # .plc.json
    import json

    (TEST_PROJECT_DIR / ".plc.json").write_text(
        json.dumps(
            {
                "name": TEST_PROJECT_ID,
                "version": "V1.0.0",
                "description": "GUI自动化测试临时项目",
                "type": "standard",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    # 基础目录
    (TEST_PROJECT_DIR / "00_项目管理").mkdir(exist_ok=True)
    (TEST_PROJECT_DIR / "02_PLC程序").mkdir(exist_ok=True)
    # PM_SESSION
    (TEST_PROJECT_DIR / f"PM_SESSION_{TEST_PROJECT_ID}.md").write_text(
        f"""# {TEST_PROJECT_ID} GUI自动化测试临时项目

- project_id: {TEST_PROJECT_ID}
- name: GUI自动化测试临时项目
- stack: plc
- phase: developing
- lifecycle: active
""",
        encoding="utf-8",
    )


# ── 函数级 fixture ────────────────────────────────────────


@pytest.fixture
def main_window(qapp: QApplication, workspace_root: str):
    """每个测试函数创建独立 MainWindow，避免状态污染"""
    from auto_pm.ui.main_window import MainWindow

    window = MainWindow(workspace_root=workspace_root)
    window.show()
    qapp.processEvents()
    QTest.qWait(500)
    yield window
    window.close()
    window.deleteLater()
    qapp.processEvents()
    QTest.qWait(100)


@pytest.fixture
def app(qapp: QApplication) -> QApplication:
    """QApplication 别名，便于测试函数引用"""
    return qapp


from PySide6.QtTest import QTest  # noqa: E402
