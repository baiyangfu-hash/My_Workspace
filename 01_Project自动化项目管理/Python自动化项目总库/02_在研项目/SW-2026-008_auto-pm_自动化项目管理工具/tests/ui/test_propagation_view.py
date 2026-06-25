"""PropagationView 单元测试（M3-2 T70）

测试内容：
- 空传播链显示"无跨领域影响"
- 单节点渲染（1 节点 + 0 箭头）
- 多节点渲染（3 节点 + 2 箭头）
- 节点显示领域中文名（DOMAINS 映射）
- 兼容 Unicode 箭头 →
- 节点水平排列方向（左→右）

使用 QGraphicsScene.items() 检查场景中的图元数量和类型。
"""

from __future__ import annotations

import os

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QGraphicsPolygonItem,
    QGraphicsRectItem,
    QGraphicsSimpleTextItem,
    QGraphicsTextItem,
)

from auto_pm.ui.change_center.propagation_view import (  # noqa: E402
    _EMPTY_HINT,
    PropagationView,
)

# ── fixtures ─────────────────────────────────────────────


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """提供全局 QApplication 实例（session 级复用）"""
    app = QApplication.instance() or QApplication([])
    yield app


# ── 辅助函数 ────────────────────────────────────────────


def _count_items(view: PropagationView) -> dict[str, int]:
    """统计场景中各类型图元数量"""
    items = view._scene.items()
    counts: dict[str, int] = {
        "rect": 0,  # 节点矩形
        "text": 0,  # 文本（节点标签或空提示）
        "polygon": 0,  # 箭头三角
    }
    for item in items:
        if isinstance(item, QGraphicsRectItem):
            counts["rect"] += 1
        elif isinstance(item, QGraphicsTextItem):
            counts["text"] += 1
        elif isinstance(item, QGraphicsPolygonItem):
            counts["polygon"] += 1
    return counts


def _get_text_items_text(view: PropagationView) -> list[str]:
    """获取场景中所有文本图元的文本（QGraphicsTextItem + QGraphicsSimpleTextItem）"""
    texts: list[str] = []
    for item in view._scene.items():
        if isinstance(item, QGraphicsTextItem):
            texts.append(item.toPlainText())
        elif isinstance(item, QGraphicsSimpleTextItem):
            texts.append(item.text())
    return texts


# ── 测试用例 ─────────────────────────────────────────────


def test_empty_chain_shows_hint(qapp: QApplication) -> None:
    """空传播链显示'无跨领域影响'"""
    view = PropagationView()
    view.load_chain("")
    texts = _get_text_items_text(view)
    assert _EMPTY_HINT in texts
    # 无节点矩形
    counts = _count_items(view)
    assert counts["rect"] == 0


def test_none_chain_shows_hint(qapp: QApplication) -> None:
    """None 传播链显示'无跨领域影响'"""
    view = PropagationView()
    view.load_chain(None)  # type: ignore[arg-type]
    texts = _get_text_items_text(view)
    assert _EMPTY_HINT in texts


def test_single_node_renders_one_node_no_arrows(qapp: QApplication) -> None:
    """单节点：1 矩形 + 0 箭头"""
    view = PropagationView()
    view.load_chain("SCPT")
    counts = _count_items(view)
    assert counts["rect"] == 1
    assert counts["polygon"] == 0


def test_three_nodes_render_two_arrows(qapp: QApplication) -> None:
    """3 节点链：3 矩形 + 2 箭头"""
    view = PropagationView()
    view.load_chain("SCPT -> PLC -> HMI")
    counts = _count_items(view)
    assert counts["rect"] == 3
    assert counts["polygon"] == 2


def test_node_shows_chinese_domain_label(qapp: QApplication) -> None:
    """节点显示领域中文名（SCPT → Python脚本）"""
    view = PropagationView()
    view.load_chain("SCPT")
    texts = _get_text_items_text(view)
    assert "Python脚本" in texts


def test_unicode_arrow_compatible(qapp: QApplication) -> None:
    """兼容 Unicode 箭头 →"""
    view = PropagationView()
    view.load_chain("SCPT → PLC → HMI")
    counts = _count_items(view)
    assert counts["rect"] == 3
    assert counts["polygon"] == 2


def test_nodes_horizontal_left_to_right(qapp: QApplication) -> None:
    """节点水平排列，从左到右 x 坐标递增"""
    view = PropagationView()
    view.load_chain("SCPT -> PLC -> HMI")
    rects = [
        item for item in view._scene.items()
        if isinstance(item, QGraphicsRectItem)
    ]
    assert len(rects) == 3
    # 按 x 坐标排序
    rects.sort(key=lambda r: r.rect().x())
    xs = [r.rect().x() for r in rects]
    # x 坐标严格递增
    assert xs[0] < xs[1] < xs[2]


def test_malformed_chain_no_arrow_treated_as_single_node(qapp: QApplication) -> None:
    """无箭头分隔的字符串视为单节点"""
    view = PropagationView()
    view.load_chain("SCPT PLC HMI")
    counts = _count_items(view)
    assert counts["rect"] == 1
    assert counts["polygon"] == 0
