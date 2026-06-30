"""GUI 全功能测试专用 fixture

测试项目生命周期（V2.1.0 R-C06 修复 TD-T09 根因）：
- session 开始：在 tmp_path_factory 隔离目录下创建测试工作空间 + DJ-2026-998 测试项目
- session 结束：pytest 自动清理 tmp 目录（无论成功失败，全量清理）
- 每个测试函数：创建独立 MainWindow，避免状态污染

禁止在真实工作空间 0100_PLC自动化/DJ-2026-998 下创建测试项目（TD-T09 教训）。
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# 必须在导入 PySide6 前设置离屏渲染（GUI_VISIBLE=1 时切换为可见窗口演示模式）
if not os.environ.get("GUI_VISIBLE"):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from tests.gui.helpers.bug_recorder import BugRecorder  # noqa: E402

# ── 常量 ──────────────────────────────────────────────────

# 项目根（仅用于定位 test_reports，不在真实工作空间下创建测试项目）
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TEST_PROJECT_ID = "DJ-2026-998"
TEST_PROJECT_NAME = "auto_pm_gui_test"
# 0100_PLC自动化 子目录名（与真实工作空间结构对齐，确保 MainWindow 扫描逻辑一致）
PLC_SUBDIR = "0100_PLC自动化"
REPORT_DIR = PROJECT_ROOT / "test_reports" / "gui"


# ── Session 级 fixture ────────────────────────────────────


@pytest.fixture(scope="session")
def test_workspace_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """session 级隔离测试工作空间（R-C06：tmp_path 替代真实工作空间）。

    在 pytest tmp 目录下创建独立工作空间，包含 0100_PLC自动化 子目录，
    session 结束后由 pytest 自动清理（全量清理，无论成功失败）。

    TD-T09 根因修复：不再在真实工作空间 0100_PLC自动化/DJ-2026-998 下创建项目，
    消除生产数据污染风险。
    """
    ws = tmp_path_factory.mktemp("gui_ws")
    (ws / PLC_SUBDIR).mkdir(parents=True, exist_ok=True)
    return ws


@pytest.fixture(scope="session")
def workspace_root(test_workspace_dir: Path) -> str:
    """测试工作空间根目录（隔离 tmp，非真实工作空间）"""
    return str(test_workspace_dir)


@pytest.fixture(scope="session")
def test_project_id() -> str:
    """测试项目 ID"""
    return TEST_PROJECT_ID


@pytest.fixture(scope="session")
def test_project_dir(test_workspace_dir: Path) -> Path:
    """测试项目目录路径（在隔离 tmp 工作空间内）"""
    return test_workspace_dir / PLC_SUBDIR / f"{TEST_PROJECT_ID}_{TEST_PROJECT_NAME}"


@pytest.fixture(scope="session")
def bug_recorder() -> BugRecorder:
    """Bug 记录器（session 级单例）"""
    recorder = BugRecorder(report_dir=REPORT_DIR)
    yield recorder
    # session 结束生成报告
    recorder.dump_report()


@pytest.fixture(scope="session", autouse=True)
def setup_test_project(
    qapp: QApplication,
    test_project_dir: Path,
):
    """session 级：在隔离 tmp 工作空间创建测试项目，session 结束 pytest 自动清理。

    R-C06 修复：不再在真实工作空间 0100_PLC自动化/DJ-2026-998 下创建项目，
    全量清理（无论成功失败），消除 TD-T09 生产数据污染根因。
    """
    # ── Setup：在 tmp 工作空间创建最小测试项目 ──
    _create_minimal_project(test_project_dir)

    qapp.processEvents()

    yield

    # ── Teardown：pytest 自动清理 tmp 工作空间（无需手动 rmtree）──
    # 不再保留任何测试项目（TD-T09 根因修复）；bug_recorder 自身的
    # teardown 会生成 Bug 报告，此处无需重复调用


def _create_minimal_project(project_dir: Path) -> None:
    """手动创建最小 PLC 项目结构（在隔离 tmp 工作空间内）"""
    import json

    project_dir.mkdir(parents=True, exist_ok=True)
    # .plc.json（项目标志文件，MainWindow 扫描依赖）
    (project_dir / ".plc.json").write_text(
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
    (project_dir / "00_项目管理").mkdir(exist_ok=True)
    (project_dir / "02_PLC程序").mkdir(exist_ok=True)
    # PM_SESSION（项目标志文件，ChangeFileLocator 依赖）
    (project_dir / f"PM_SESSION_{TEST_PROJECT_ID}.md").write_text(
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
