"""变更中心 - 传播链可视化 QGraphicsView（M3-2 T65-T68）

将 §6.3 propagation_chain 字符串解析为节点+边，用 QGraphicsView 水平展示。
空传播链显示"无跨领域影响"。

示例：
  propagation_chain = "SCPT -> PLC -> HMI"

  渲染效果（水平左→右）：
    ┌──────────┐      ┌────────┐      ┌────────┐
    │ Python脚本 │ ──►  │ PLC程序 │ ──►  │ HMI程序 │
    └──────────┘      └────────┘      └────────┘

节点显示领域中文名（复用 auto_pm.change.models.DOMAINS 映射），
连线带箭头表示传播方向。

Tracing：解析和渲染全过程输出 DEBUG 级别日志，便于排查渲染问题。
"""

from __future__ import annotations

import re

from PySide6.QtCore import QLineF, QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPen,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsPolygonItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsTextItem,
    QGraphicsView,
    QWidget,
)

from auto_pm.change.models import DOMAINS
from auto_pm.logging.logging import setup_logger as get_logger

__all__ = ["PropagationView"]

log = get_logger(log_level="DEBUG", app_name="auto_pm")

# 节点视觉常量
_NODE_WIDTH = 100
_NODE_HEIGHT = 40
_NODE_SPACING = 60  # 节点间水平间距（含箭头）
_NODE_BG_COLOR = "#e8f0fe"
_NODE_BORDER_COLOR = "#4a90d9"
_NODE_TEXT_COLOR = "#333"

# 箭头视觉常量
_ARROW_COLOR = "#4a90d9"
_ARROW_SIZE = 8  # 箭头三角边长

# 空状态提示
_EMPTY_HINT = "无跨领域影响"

# 分隔符正则：兼容 -> 和 →
_ARROW_PATTERN = re.compile(r"\s*(?:->|→)\s*")


class PropagationView(QGraphicsView):
    """传播链可视化 - 水平展示变更传播路径

    数据来自 ChangeRequest.propagation_chain 字符串（如 "SCPT -> PLC -> HMI"）。
    每个领域渲染为圆角矩形节点，相邻节点间用带箭头的连线连接。
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        # 视图外观
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setStyleSheet("background: transparent; border: none;")
        self.setFixedHeight(80)
        # 初始空状态
        self._show_empty()

    # ── 数据解析 ──────────────────────────────────────────

    def _parse_chain(self, chain: str) -> tuple[list[str], list[tuple[int, int]]]:
        """解析传播链字符串为节点标签列表 + 边索引对列表

        Args:
            chain: 传播链字符串，如 "SCPT -> PLC -> HMI"

        Returns:
            (nodes, edges):
              nodes: 节点标签列表（原始字符串，未映射中文），如 ["SCPT", "PLC", "HMI"]
              edges: 边索引对列表，如 [(0, 1), (1, 2)]
              空字符串返回 ([], [])
        """
        log.debug("propagation_view._parse_chain input='%s'", chain)

        if not chain or not chain.strip():
            log.debug("propagation_view._parse_chain empty input → ([], [])")
            return [], []

        # 按箭头分隔符拆分
        parts = _ARROW_PATTERN.split(chain.strip())
        # 过滤空段（连续箭头或首尾箭头产生的空串）
        nodes = [p for p in parts if p]
        log.debug("propagation_view._parse_chain split_results=%s", parts)
        log.debug("propagation_view._parse_chain nodes=%s", nodes)

        if not nodes:
            log.debug("propagation_view._parse_chain no valid nodes → ([], [])")
            return [], []

        # 构建边：相邻节点对
        edges = [(i, i + 1) for i in range(len(nodes) - 1)]
        log.debug("propagation_view._parse_chain edges=%s", edges)
        return nodes, edges

    # ── 渲染 ─────────────────────────────────────────────

    def load_chain(self, chain: str) -> None:
        """加载并渲染传播链"""
        log.debug("propagation_view.load_chain input='%s'", chain)
        nodes, edges = self._parse_chain(chain)
        self._clear_scene()

        if not nodes:
            log.debug("propagation_view.load_chain no nodes → show empty hint")
            self._show_empty()
            return

        self._render(nodes, edges)

    def _clear_scene(self) -> None:
        """清空场景"""
        self._scene.clear()

    def _show_empty(self) -> None:
        """显示空状态提示"""
        item = QGraphicsTextItem(_EMPTY_HINT)
        font = QFont()
        font.setPointSize(10)
        item.setFont(font)
        item.setDefaultTextColor(QColor("#999"))
        # 居中放置
        item.setPos(10, 25)
        self._scene.addItem(item)
        self._scene.setSceneRect(QRectF(0, 0, 200, 80))
        log.debug("propagation_view._show_empty hint='%s'", _EMPTY_HINT)

    def _render(self, nodes: list[str], edges: list[tuple[int, int]]) -> None:
        """渲染节点和边

        节点水平排列，从左到右，间距 _NODE_SPACING。
        边为节点间的带箭头连线。
        """
        log.debug(
            "propagation_view._render node_count=%d edge_count=%d",
            len(nodes), len(edges),
        )

        node_positions: list[tuple[float, float]] = []
        for i, node_label in enumerate(nodes):
            x = i * (_NODE_WIDTH + _NODE_SPACING)
            y = 15
            node_positions.append((x, y))

            # 节点显示中文标签（若 DOMAINS 有映射）
            display_label = DOMAINS.get(node_label, node_label)
            log.debug(
                "propagation_view._render node[%d] pos=(%.0f, %.0f) raw='%s' display='%s'",
                i, x, y, node_label, display_label,
            )
            self._add_node(x, y, display_label)

        # 渲染边（箭头）
        for src, dst in edges:
            src_x, src_y = node_positions[src]
            dst_x, dst_y = node_positions[dst]
            # 边起点：源节点右边缘中点
            line_start_x = src_x + _NODE_WIDTH
            line_start_y = src_y + _NODE_HEIGHT / 2
            # 边终点：目标节点左边缘中点
            line_end_x = dst_x
            line_end_y = dst_y + _NODE_HEIGHT / 2
            log.debug(
                "propagation_view._render edge[%d→%d] line=(%.0f,%.0f)→(%.0f,%.0f)",
                src, dst, line_start_x, line_start_y, line_end_x, line_end_y,
            )
            self._add_arrow(line_start_x, line_start_y, line_end_x, line_end_y)

        # 设置场景矩形
        total_width = len(nodes) * _NODE_WIDTH + (len(nodes) - 1) * _NODE_SPACING
        scene_rect = QRectF(0, 0, total_width, 70)
        self._scene.setSceneRect(scene_rect)
        log.debug(
            "propagation_view._render scene_rect=(0, 0, %.0f, %.0f)",
            total_width, 70,
        )

    def _add_node(self, x: float, y: float, label: str) -> None:
        """添加一个节点（圆角矩形 + 文本）"""
        # 圆角矩形背景
        rect = QGraphicsRectItem(QRectF(x, y, _NODE_WIDTH, _NODE_HEIGHT))
        rect.setBrush(QBrush(QColor(_NODE_BG_COLOR)))
        pen = QPen(QColor(_NODE_BORDER_COLOR), 1)
        rect.setPen(pen)
        rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self._scene.addItem(rect)

        # 文本标签
        text = QGraphicsSimpleTextItem(label)
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        text.setFont(font)
        text.setBrush(QBrush(QColor(_NODE_TEXT_COLOR)))
        # 居中于节点
        text_rect = text.boundingRect()
        text_x = x + (_NODE_WIDTH - text_rect.width()) / 2
        text_y = y + (_NODE_HEIGHT - text_rect.height()) / 2
        text.setPos(text_x, text_y)
        self._scene.addItem(text)

    def _add_arrow(
        self, x1: float, y1: float, x2: float, y2: float
    ) -> None:
        """添加一条带箭头的连线"""
        pen = QPen(QColor(_ARROW_COLOR), 2)
        pen.setStyle(Qt.PenStyle.SolidLine)

        # 线段（缩短终点以给箭头留位置）
        line_end_x = x2 - _ARROW_SIZE
        line_item = QGraphicsLineItem(QLineF(x1, y1, line_end_x, y2))
        line_item.setPen(pen)
        self._scene.addItem(line_item)

        # 箭头三角
        arrow = QPolygonF()
        arrow.append(QPointF(x2, y2))  # 尖端
        arrow.append(QPointF(line_end_x, y2 - _ARROW_SIZE / 2))  # 上底
        arrow.append(QPointF(line_end_x, y2 + _ARROW_SIZE / 2))  # 下底

        arrow_item = QGraphicsPolygonItem(arrow)
        arrow_item.setBrush(QBrush(QColor(_ARROW_COLOR)))
        arrow_item.setPen(QPen(QColor(_ARROW_COLOR), 1))
        self._scene.addItem(arrow_item)
