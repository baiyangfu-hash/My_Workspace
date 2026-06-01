# -*- coding: utf-8 -*-
"""
诊断面板组件

提供PLC项目的综合诊断UI界面，包括：
- LSP兼容性诊断（stub误用、FB缺失、类型转换等）
- 项目健康度分析（四维评分：符合度/问题/库引用/结构）
- 问题列表展示与颜色编码
- 根因分析与结构化报告
- 健康度仪表盘（圆环图+柱状图）
- OB->FB调用链可视化
- 报告导出（Markdown/JSON）

架构设计：
- 采用MVP模式，Panel作为View层
- 通过信号槽与外部Service层交互
- 使用QThread实现异步诊断执行
- 自定义绘图组件实现数据可视化

依赖项：
- PyQt5: UI框架
- LSPCompatibilityChecker: LSP兼容性检查器
- ProjectHealthAnalyzer: 项目健康度分析器
- 数据模型: DiagnosticReport / HealthMetrics / CheckReport

作者：双栖资深开发
版本：1.0.0
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QTabWidget,
    QTextBrowser,
    QTextEdit,
    QLabel,
    QPushButton,
    QComboBox,
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSplitter,
    QFileDialog,
    QMessageBox,
    QApplication,
    QFrame,
    QScrollArea,
    QSizePolicy,
)
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QThread,
    QMutex,
    QTimer,
    QSize,
    QRect,
    QPointF,
)
from PyQt5.QtGui import (
    QFont,
    QColor,
    QPainter,
    QPen,
    QBrush,
    QConicalGradient,
    QLinearGradient,
    QRadialGradient,
    QPalette,
    QTextCursor,
)

from src.utils.logger import setup_logger
from src.diagnostics.lsp_compatibility_checker import (
    LSPCompatibilityChecker,
)
from src.diagnostics.project_health_analyzer import (
    ProjectHealthAnalyzer,
)
from src.models.diagnostic_report import (
    DiagnosticReport,
    DiagnosticIssue,
    DiagnosticSeverity,
)
from src.models.health_metrics import (
    HealthMetrics,
    HealthGrade,
    DimensionScore,
    ImprovementSuggestion,
)
from src.models.check_result import CheckReport

logger = setup_logger(__name__)


# ============================================================================
# 常量定义
# ============================================================================

DIAGNOSTIC_TYPES = {
    'lsp': 'LSP兼容性',
    'health': '项目健康度',
    'full': '完整诊断',
}

SEVERITY_COLORS = {
    DiagnosticSeverity.ERROR: QColor('#fff1f0'),
    DiagnosticSeverity.WARNING: QColor('#fffbe6'),
    DiagnosticSeverity.INFO: QColor('#e6f7ff'),
    DiagnosticSeverity.HINT: QColor('#f6ffed'),
}

SEVERITY_FG_COLORS = {
    DiagnosticSeverity.ERROR: QColor('#cf1322'),
    DiagnosticSeverity.WARNING: QColor('#d48806'),
    DiagnosticSeverity.INFO: QColor('#1890ff'),
    DiagnosticSeverity.HINT: QColor('#52c41a'),
}

SEVERITY_ICONS = {
    DiagnosticSeverity.ERROR: 'ERROR',
    DiagnosticSeverity.WARNING: 'WARN',
    DiagnosticSeverity.INFO: 'INFO',
    DiagnosticSeverity.HINT: 'HINT',
}

GRADE_COLORS = {
    'A': '#52c41a',
    'B': '#1890ff',
    'C': '#faad14',
    'D': '#ff4d4f',
}

DIMENSION_COLORS = [
    '#1890ff',
    '#ff4d4f',
    '#faad14',
    '#52c41a',
]

ROLE_ISSUE = Qt.UserRole + 10
ROLE_CALLER = Qt.UserRole + 11


# ============================================================================
# 异步诊断工作线程
# ============================================================================

class DiagnosticWorker(QThread):
    """
    诊断工作线程

    在后台线程中执行LSP诊断和健康度分析任务，
    避免阻塞UI主线程。通过信号向主线程报告进度和结果。
    """

    progress_updated = pyqtSignal(str)
    lsp_finished = pyqtSignal(object)
    health_finished = pyqtSignal(object)
    all_finished = pyqtSignal(object, object)
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        project_path: str,
        diagnostic_type: str = 'full',
        check_report: Optional[CheckReport] = None,
        parent=None
    ):
        """
        初始化工作线程

        Args:
            project_path: PLC项目根目录路径
            diagnostic_type: 诊断类型 ('lsp'/'health'/'full')
            check_report: 规范检查报告（用于健康度分析）
            parent: 父对象
        """
        super().__init__(parent)
        self._project_path = project_path
        self._diagnostic_type = diagnostic_type
        self._check_report = check_report
        self._is_cancelled = False
        self._mutex = QMutex()

    def run(self):
        """线程主函数 - 执行诊断"""
        try:
            report = None
            metrics = None

            if self._diagnostic_type in ('lsp', 'full'):
                self._mutex.lock()
                if self._is_cancelled:
                    self._mutex.unlock()
                    return
                self._mutex.unlock()
                self.progress_updated.emit('正在执行LSP兼容性扫描...')

                checker = LSPCompatibilityChecker(self._project_path)
                report = checker.scan()

                self.lsp_finished.emit(report)
                logger.info(f"LSP诊断完成: {len(report.issues)} 个问题")

            if self._diagnostic_type in ('health', 'full'):
                self._mutex.lock()
                if self._is_cancelled:
                    self._mutex.unlock()
                    return
                self._mutex.unlock()
                self.progress_updated.emit('正在分析项目健康度...')

                analyzer = ProjectHealthAnalyzer()
                metrics = analyzer.analyze(
                    check_report=self._check_report or CheckReport(),
                    project_path=self._project_path
                )

                self.health_finished.emit(metrics)
                logger.info(f"健康度分析完成: {metrics.overall_score:.1f}分")

            self._mutex.lock()
            cancelled = self._is_cancelled
            self._mutex.unlock()
            if not cancelled:
                self.all_finished.emit(report, metrics)

        except Exception as e:
            logger.error(f"诊断执行异常: {e}", exc_info=True)
            self.error_occurred.emit(str(e))

    def cancel(self):
        """请求取消执行（线程安全）"""
        self._mutex.lock()
        self._is_cancelled = True
        self._mutex.unlock()


# ============================================================================
# 自定义绘图组件 - 圆环分数控件
# ============================================================================

class ScoreRingWidget(QWidget):
    """
    圆环分数控件

    使用自定义绑制绘制渐变色圆环进度条，
    在中心显示分数值和等级评定。

    支持动态更新分数，带有平滑过渡动画效果。
    """

    def __init__(self, parent=None):
        """
        初始化圆环分数控件

        Args:
            parent: 父窗口部件
        """
        super().__init__(parent)
        self._score = 0.0
        self._target_score = 0.0
        self._grade = '-'
        self._grade_label = ''
        self._animated_score = 0.0

        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._animation_timer = QTimer(self)
        self._animation_timer.timeout.connect(self._animate_step)
        self._animation_interval = 20

    def set_score(
        self,
        score: float,
        grade: str = '',
        grade_label: str = ''
    ):
        """
        设置分数并启动动画

        Args:
            score: 分数值 (0-100)
            grade: 等级字符 (A/B/C/D)
            grade_label: 等级中文标签
        """
        self._target_score = max(0.0, min(100.0, score))
        self._grade = grade or HealthGrade.from_score(score).value
        self._grade_label = grade_label or HealthGrade.from_score(score).label

        if not self._animation_timer.isActive():
            self._animation_timer.start(self._animation_interval)

    def _animate_step(self):
        """动画步进 - 平滑过渡到目标分"""
        diff = self._target_score - self._animated_score
        if abs(diff) < 0.5:
            self._animated_score = self._target_score
            self._animation_timer.stop()
        else:
            self._animated_score += diff * 0.12

        self.update()

    def paintEvent(self, event):
        """
        绑制事件处理

        绘制圆环进度条、分数文字和等级标签。
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        side = min(self.width(), self.height())
        margin = 12
        rect = QRect(
            (self.width() - side) // 2 + margin,
            (self.height() - side) // 2 + margin,
            side - 2 * margin,
            side - 2 * margin
        )

        pen_width = max(14, side // 16)
        outer_radius = min(rect.width(), rect.height()) // 2
        center = QPointF(rect.center())

        bg_pen = QPen(QColor('#f0f0f0'))
        bg_pen.setWidth(pen_width)
        bg_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(bg_pen)
        painter.drawEllipse(center, outer_radius - pen_width // 2,
                           outer_radius - pen_width // 2)

        if self._animated_score > 0.5:
            color = QColor(GRADE_COLORS.get(
                self._grade,
                HealthGrade.from_score(self._animated_score).color
            ))

            gradient = QConicalGradient(center, 90)
            gradient.setColorAt(0, color.lighter(120))
            gradient.setColorAt(0.5, color)
            gradient.setColorAt(1, color.darker(110))

            span_angle = int((self._animated_score / 100.0) * 360 * 16)

            fg_pen = QPen(QBrush(gradient), pen_width)
            fg_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(fg_pen)
            painter.drawArc(
                rect.x(), rect.y(), rect.width(), rect.height(),
                90 * 16,
                -span_angle
            )

        score_text = f'{self._animated_score:.0f}'
        font_score = QFont('Arial', max(32, side // 7), QFont.Bold)
        painter.setFont(font_score)

        text_color = QColor(GRADE_COLORS.get(self._grade, '#333333'))
        painter.setPen(text_color)

        text_rect = QRect(
            int(center.x() - side // 4),
            int(center.y() - side // 8),
            side // 2,
            side // 4
        )
        painter.drawText(text_rect, Qt.AlignCenter, score_text)

        font_grade = QFont('Microsoft YaHei', max(11, side // 18))
        painter.setFont(font_grade)
        painter.setPen(QColor('#666666'))

        grade_text = f'[ {self._grade}级 - {self._grade_label} ]'
        grade_rect = QRect(
            int(center.x() - side // 4),
            int(center.y() + side // 18),
            side // 2,
            side // 9
        )
        painter.drawText(grade_rect, Qt.AlignCenter, grade_text)

        font_title = QFont('Microsoft YaHei', 9)
        painter.setFont(font_title)
        painter.setPen(QColor('#999999'))
        title_rect = QRect(
            int(center.x() - side // 4),
            int(center.y() + side // 7),
            side // 2,
            side // 12
        )
        painter.drawText(title_rect, Qt.AlignCenter, '综合健康度得分')

    def cleanup(self):
        """停止动画定时器"""
        if hasattr(self, '_animation_timer') and self._animation_timer.isActive():
            self._animation_timer.stop()


# ============================================================================
# 自定义绘图组件 - 四维柱状图控件
# ============================================================================

class BarChartWidget(QWidget):
    """
    四维柱状图控件

    使用自定义绑制绘制四个评估维度的柱状图，
    包括维度名称、分数值和等级标签。

    维度顺序：规范符合度 | 问题严重程度 | 库引用状态 | 结构合规性
    """

    def __init__(self, parent=None):
        """
        初始化柱状图控件

        Args:
            parent: 父窗口部件
        """
        super().__init__(parent)
        self._dimensions: List[Dict[str, Any]] = []
        self._bar_animation_progress: List[float] = []

        self.setMinimumSize(320, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_dimensions(self, dimensions: List[DimensionScore]):
        """
        设置维度数据并触发重绘

        Args:
            dimensions: 维度得分列表（最多4个）
        """
        self._dimensions = [
            {
                'name': dim.name,
                'score': dim.score,
                'grade': dim.grade,
                'weight': dim.weight,
            }
            for dim in dimensions[:4]
        ]
        self._bar_animation_progress = [0.0] * len(self._dimensions)

        QTimer.singleShot(50, self._start_animation)

    def _start_animation(self):
        """启动柱状图增长动画"""
        self._anim_step = 0
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._animate_bars)
        self._anim_timer.start(25)

    def _animate_bars(self):
        """柱状图增长动画步进"""
        self._anim_step += 1
        progress = min(1.0, self._anim_step / 24.0)
        ease_out = 1 - pow(1 - progress, 3)

        for i in range(len(self._bar_animation_progress)):
            target = self._dimensions[i]['score'] if i < len(self._dimensions) else 0
            self._bar_animation_progress[i] = target * ease_out

        self.update()

        if progress >= 1.0:
            self._anim_timer.stop()

    def paintEvent(self, event):
        """
        绘制事件处理

        绘制坐标轴、柱状图、维度标签和分数值。
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if not self._dimensions:
            painter.setPen(QColor('#cccccc'))
            font = QFont('Microsoft YaHei', 11)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter,
                           '暂无数据，请先运行诊断')
            return

        margin_left = 60
        margin_right = 30
        margin_top = 30
        margin_bottom = 55

        chart_width = self.width() - margin_left - margin_right
        chart_height = self.height() - margin_top - margin_bottom

        if chart_width <= 0 or chart_height <= 0:
            return

        bar_count = len(self._dimensions)
        bar_spacing = chart_width // (bar_count + 1)
        bar_width = max(28, min(bar_spacing - 16, 70))

        painter.setPen(QColor('#f0f0f0'))
        grid_y_positions = [25, 50, 75, 100]
        for grid_val in grid_y_positions:
            y = margin_top + chart_height - int((grid_val / 100.0) * chart_height)
            painter.drawLine(margin_left, y, self.width() - margin_right, y)

            font_grid = QFont('Arial', 8)
            painter.setFont(font_grid)
            painter.setPen(QColor('#bbbbbb'))
            painter.drawText(
                margin_left - 22, y + 4,
                f'{grid_val}'
            )

        painter.setPen(QColor('#dddddd'))
        painter.drawLine(
            margin_left, margin_top + chart_height,
            self.width() - margin_right, margin_top + chart_height
        )

        for i, dim in enumerate(self._dimensions):
            cx = margin_left + bar_spacing * (i + 1)
            bar_height_raw = (
                self._bar_animation_progress[i]
                if i < len(self._bar_animation_progress)
                else 0
            )
            bar_height = int((bar_height_raw / 100.0) * chart_height)

            bx = cx - bar_width // 2
            by = margin_top + chart_height - bar_height

            color = QColor(DIMENSION_COLORS[i % len(DIMENSION_COLORS)])
            gradient = QLinearGradient(bx, by + bar_height, bx, by)
            gradient.setColorAt(0, color.lighter(130))
            gradient.setColorAt(1, color)

            from math import pi
            radius = min(5, bar_width // 5)
            from PyQt5.QtGui import QPainterPath
            path = QPainterPath()
            path.addRoundedRect(bx, by, bar_width, bar_height, radius, radius)
            painter.fillPath(path, QBrush(gradient))

            if bar_height > 15:
                font_value = QFont('Arial', 9, QFont.Bold)
                painter.setFont(font_value)
                painter.setPen(color.darker(120))
                value_text = f'{bar_height_raw:.0f}'
                painter.drawText(
                    cx - 15, by - 6,
                    value_text
                )

            font_name = QFont('Microsoft YaHei', 8)
            painter.setFont(font_name)
            painter.setPen(QColor('#555555'))

            name_parts = dim['name']
            if len(name_parts) > 4:
                mid = len(name_parts) // 2
                line1 = name_parts[:mid]
                line2 = name_parts[mid:]
            else:
                line1 = name_parts
                line2 = ''

            label_y = margin_top + chart_height + 14
            painter.drawText(cx - 40, label_y, 80, 16,
                           Qt.AlignCenter, line1)
            if line2:
                painter.drawText(cx - 40, label_y + 14, 80, 16,
                               Qt.AlignCenter, line2)

            font_grade = QFont('Microsoft YaHei', 8)
            painter.setFont(font_grade)
            grade_color = QColor(
                GRADE_COLORS.get(dim['grade'][0], '#888888')
                if dim['grade'] else '#888888'
            )
            painter.setPen(grade_color)
            painter.drawText(cx - 20, margin_top + chart_height + 42,
                           40, 14, Qt.AlignCenter, f"[{dim['grade']}]")

    def cleanup(self):
        """停止动画定时器"""
        if hasattr(self, '_anim_timer') and self._anim_timer.isActive():
            self._anim_timer.stop()


# ============================================================================
# 主面板类
# ============================================================================

class DiagnosticPanel(QWidget):
    """
    诊断面板主类

    提供PLC项目的综合诊断界面，集成LSP兼容性检查和
    项目健康度分析功能。支持异步执行、多Tab展示和
    报告导出。

    主要功能区域：
    1. 顶部工具栏：诊断控制按钮、类型选择、导出、状态
    2. 中间Tab容器：问题列表/根因分析/健康仪表盘/调用链视图
    3. 底部详情区：代码片段+修复步骤

    使用示例：
        >>> panel = DiagnosticPanel()
        >>> panel.set_project_path(Path("/path/to/project"))
        >>> panel.run_diagnostic('full')
        >>> panel.show()
    """

    diagnostic_started = pyqtSignal()
    diagnostic_finished = pyqtSignal(object)
    health_analysis_finished = pyqtSignal(object)
    source_jump_requested = pyqtSignal(str, int)

    def __init__(self, parent=None):
        """
        初始化诊断面板

        Args:
            parent: 父窗口部件
        """
        super().__init__(parent)

        self._project_path: Optional[str] = None
        self._report: Optional[DiagnosticReport] = None
        self._metrics: Optional[HealthMetrics] = None
        self._worker: Optional[DiagnosticWorker] = None
        self._check_report: Optional[CheckReport] = None
        self._is_running = False

        self._lsp_checker: Optional[LSPCompatibilityChecker] = None
        self._health_analyzer: Optional[ProjectHealthAnalyzer] = None

        self._init_ui()

        logger.info("DiagnosticPanel初始化完成")

    # ========================================================================
    # UI初始化方法
    # ========================================================================

    def _init_ui(self):
        """初始化用户界面布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        self._init_toolbar(main_layout)

        self._init_tab_widget(main_layout)

        self._init_detail_area(main_layout)

    def _init_toolbar(self, parent_layout: QVBoxLayout):
        """
        初始化顶部工具栏

        包含：开始诊断按钮、诊断类型选择、导出按钮、状态标签

        Args:
            parent_layout: 父布局
        """
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self._btn_start = QPushButton('开始诊断')
        self._btn_start.setToolTip('运行选中的诊断类型')
        self._btn_start.setProperty("PrimaryBtn", True)
        self._btn_start.clicked.connect(self._on_start_diagnostic)
        toolbar.addWidget(self._btn_start)

        type_label = QLabel('诊断类型:')
        toolbar.addWidget(type_label)

        self._combo_type = QComboBox()
        self._combo_type.addItems(list(DIAGNOSTIC_TYPES.values()))
        self._combo_type.setCurrentIndex(2)
        self._combo_type.setMinimumWidth(120)
        self._combo_type.setToolTip('选择要执行的诊断类型')
        toolbar.addWidget(self._combo_type)

        toolbar.addSpacing(16)

        self._btn_export = QPushButton('导出报告')
        self._btn_export.setToolTip('将诊断结果导出为Markdown或JSON文件')
        self._btn_export.setEnabled(False)
        self._btn_export.clicked.connect(self.export_report)
        toolbar.addWidget(self._btn_export)

        toolbar.addStretch()

        self._lbl_status = QLabel('\U0001F7E2 就绪')
        self._lbl_status.setProperty("treeStatus", True)
        self._lbl_status.setMinimumWidth(160)
        toolbar.addWidget(self._lbl_status)

        parent_layout.addLayout(toolbar)

    def _init_tab_widget(self, parent_layout: QVBoxLayout):
        """
        初始化中间Tab容器

        包含4个标签页：问题列表、根因分析、健康度仪表盘、调用链视图

        Args:
            parent_layout: 父布局
        """
        self._tab_widget = QTabWidget()
        self._tab_widget.setDocumentMode(True)

        self._init_issues_tab()

        self._init_root_cause_tab()

        self._init_health_dashboard_tab()

        self._init_call_chain_tab()

        parent_layout.addWidget(self._tab_widget, stretch=1)

    def _init_issues_tab(self):
        """初始化问题列表Tab（QTableWidget）"""
        issues_widget = QWidget()
        layout = QVBoxLayout(issues_widget)
        layout.setContentsMargins(6, 6, 6, 6)

        self._table_issues = QTableWidget()
        self._table_issues.setColumnCount(6)
        self._table_issues.setHorizontalHeaderLabels([
            '严重级别', '规则ID', '类型', '描述', '文件', '行号'
        ])

        header = self._table_issues.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Interactive)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        self._table_issues.setAlternatingRowColors(True)
        self._table_issues.setSelectionBehavior(QTableWidget.SelectRows)
        self._table_issues.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table_issues.itemSelectionChanged.connect(
            self._on_issue_selection_changed
        )
        self._table_issues.itemDoubleClicked.connect(
            self._on_issue_double_clicked
        )

        self._table_issues.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table_issues.customContextMenuRequested.connect(
            self._show_issue_context_menu
        )

        layout.addWidget(self._table_issues)

        stats_bar = QHBoxLayout()
        self._lbl_issue_count = QLabel('共 0 个问题')
        self._lbl_issue_count.setProperty("treeStatus", True)
        stats_bar.addWidget(self._lbl_issue_count)
        stats_bar.addStretch()
        layout.addLayout(stats_bar)

        self._tab_widget.addTab(issues_widget, '问题列表')

    def _init_root_cause_tab(self):
        """初始化根因分析Tab（QTextBrowser）"""
        root_cause_widget = QWidget()
        layout = QVBoxLayout(root_cause_widget)
        layout.setContentsMargins(6, 6, 6, 6)

        self._browser_root_cause = QTextBrowser()
        self._browser_root_cause.setOpenExternalLinks(True)
        self._browser_root_cause.setFont(QFont('Consolas', 9))
        self._browser_root_cause.setPlaceholderText(
            '根因分析报告将在诊断完成后显示...'
        )
        layout.addWidget(self._browser_root_cause, stretch=1)

        btn_bar = QHBoxLayout()
        self._btn_copy_report = QPushButton('复制报告')
        self._btn_copy_report.setEnabled(False)
        self._btn_copy_report.clicked.connect(self._copy_root_cause_report)
        btn_bar.addWidget(self._btn_copy_report)
        btn_bar.addStretch()
        layout.addLayout(btn_bar)

        self._tab_widget.addTab(root_cause_widget, '根因分析')

    def _init_health_dashboard_tab(self):
        """
        初始化健康度仪表盘Tab（自定义绘制）

        包含：圆环总分图、四维柱状图、Top5问题列表、改进建议列表
        """
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)
        layout.setContentsMargins(8, 8, 8, 8)

        top_layout = QHBoxLayout()

        ring_group = QGroupBox('综合评分')
        ring_layout = QVBoxLayout(ring_group)
        self._ring_widget = ScoreRingWidget()
        ring_layout.addWidget(self._ring_widget)
        top_layout.addWidget(ring_group, stretch=3)

        bar_group = QGroupBox('各维度得分')
        bar_layout = QVBoxLayout(bar_group)
        self._bar_chart_widget = BarChartWidget()
        bar_layout.addWidget(self._bar_chart_widget)
        top_layout.addWidget(bar_group, stretch=4)

        layout.addLayout(top_layout, stretch=4)

        bottom_layout = QHBoxLayout()

        top5_group = QGroupBox('Top 5 高频问题')
        top5_layout = QVBoxLayout(top5_group)
        self._list_top5_issues = QListWidget()
        self._list_top5_issues.setAlternatingRowColors(True)
        self._list_top5_issues.setMaximumHeight(180)
        top5_layout.addWidget(self._list_top5_issues)
        bottom_layout.addWidget(top5_group, stretch=1)

        suggestion_group = QGroupBox('改进建议')
        suggestion_layout = QVBoxLayout(suggestion_group)
        self._list_suggestions = QListWidget()
        self._list_suggestions.setAlternatingRowColors(True)
        self._list_suggestions.setMaximumHeight(180)
        suggestion_layout.addWidget(self._list_suggestions)
        bottom_layout.addWidget(suggestion_group, stretch=1)

        layout.addLayout(bottom_layout, stretch=3)

        self._tab_widget.addTab(dashboard_widget, '健康度仪表盘')

    def _init_call_chain_tab(self):
        """
        初始化调用链视图Tab（QTreeWidget）

        显示OB到FB的调用关系树，高亮有问题的节点。
        """
        call_chain_widget = QWidget()
        layout = QVBoxLayout(call_chain_widget)
        layout.setContentsMargins(6, 6, 6, 6)

        chain_toolbar = QHBoxLayout()
        self._lbl_chain_info = QLabel('OB -> FB 调用关系树')
        self._lbl_chain_info.setProperty("sectionTitle", True)
        chain_toolbar.addWidget(self._lbl_chain_info)
        chain_toolbar.addStretch()

        self._btn_expand_all = QPushButton('展开全部')
        self._btn_expand_all.setMaximumWidth(70)
        self._btn_expand_all.clicked.connect(
            lambda: self._tree_call_chain.expandAll()
        )
        chain_toolbar.addWidget(self._btn_expand_all)

        self._btn_collapse_all = QPushButton('折叠全部')
        self._btn_collapse_all.setMaximumWidth(70)
        self._btn_collapse_all.clicked.connect(
            lambda: self._tree_call_chain.collapseAll()
        )
        chain_toolbar.addWidget(self._btn_collapse_all)

        layout.addLayout(chain_toolbar)

        self._tree_call_chain = QTreeWidget()
        self._tree_call_chain.setHeaderLabels(['组织块(OB)', '调用的FB/FC'])
        self._tree_call_chain.setColumnWidth(0, 220)
        self._tree_call_chain.setColumnWidth(1, 300)
        self._tree_call_chain.setAlternatingRowColors(True)
        self._tree_call_chain.itemDoubleClicked.connect(
            self._on_call_chain_item_double_clicked
        )
        layout.addWidget(self._tree_call_chain, stretch=1)

        self._tab_widget.addTab(call_chain_widget, '调用链视图')

    def _init_detail_area(self, parent_layout: QVBoxLayout):
        """
        初始化底部详情区

        包含左侧的问题代码片段和右侧的修复步骤列表。

        Args:
            parent_layout: 父布局
        """
        detail_group = QGroupBox('问题详情')
        detail_layout = QHBoxLayout(detail_group)

        left_panel = QVBoxLayout()
        code_label = QLabel('问题代码片段:')
        left_panel.addWidget(code_label)

        self._txt_code_snippet = QTextEdit()
        self._txt_code_snippet.setMaximumHeight(140)
        self._txt_code_snippet.setReadOnly(True)
        self._txt_code_snippet.setFont(QFont('Consolas', 9))
        self._txt_code_snippet.setPlaceholderText(
            '选中一个问题后在此处查看相关代码片段...'
        )
        left_panel.addWidget(self._txt_code_snippet)

        detail_layout.addLayout(left_panel, stretch=2)

        right_panel = QVBoxLayout()
        fix_label = QLabel('修复步骤:')
        right_panel.addWidget(fix_label)

        self._list_fix_steps = QListWidget()
        self._list_fix_steps.setMaximumHeight(140)
        self._list_fix_steps.setAlternatingRowColors(True)
        right_panel.addWidget(self._list_fix_steps)

        fix_btn_layout = QHBoxLayout()
        self._btn_copy_fix = QPushButton('复制步骤')
        self._btn_copy_fix.setMaximumWidth(90)
        self._btn_copy_fix.clicked.connect(self._copy_fix_steps)
        fix_btn_layout.addWidget(self._btn_copy_fix)
        fix_btn_layout.addStretch()
        right_panel.addLayout(fix_btn_layout)

        detail_layout.addLayout(right_panel, stretch=1)

        parent_layout.addWidget(detail_group)

    # ========================================================================
    # 公共API方法
    # ========================================================================

    def set_project_path(self, project_path: str):
        """
        设置项目路径

        Args:
            project_path: PLC项目根目录路径
        """
        self._project_path = str(project_path)
        logger.info(f"项目路径已设置: {self._project_path}")

    def set_check_report(self, check_report: CheckReport):
        """
        设置规范检查报告（用于健康度分析）

        Args:
            check_report: 规范检查器的完整报告
        """
        self._check_report = check_report
        logger.info("规范检查报告已设置")

    def run_lsp_diagnostic(self, project_path: str = '') -> Optional[DiagnosticReport]:
        """
        运行LSP兼容性诊断

        扫描.plc-out/golang目录下的Go源文件，
        检测stub误用、FB缺失等问题。

        Args:
            project_path: 项目路径（空则使用当前设置的路径）

        Returns:
            DiagnosticReport或None（如果失败）
        """
        target_path = project_path or self._project_path
        if not target_path:
            QMessageBox.warning(self, '提示', '请先设置项目路径')
            return None

        try:
            self._lsp_checker = LSPCompatibilityChecker(target_path)
            report = self._lsp_checker.scan()
            self._report = report
            logger.info(f"LSP诊断完成: {len(report.issues)} 个问题")
            return report
        except Exception as e:
            logger.error(f"LSP诊断失败: {e}")
            QMessageBox.critical(self, '错误', f'LSP诊断失败:\n{str(e)}')
            return None

    def run_health_analysis(
        self,
        project_path: str = '',
        check_report: Optional[CheckReport] = None
    ) -> Optional[HealthMetrics]:
        """
        运行项目健康度分析

        基于检查报告计算四维健康度评分。

        Args:
            project_path: 项目路径
            check_report: 规范检查报告（空则使用当前设置的报告）

        Returns:
            HealthMetrics或None（如果失败）
        """
        target_path = project_path or self._project_path
        report = check_report or self._check_report
        if not target_path:
            QMessageBox.warning(self, '提示', '请先设置项目路径')
            return None

        try:
            self._health_analyzer = ProjectHealthAnalyzer()
            metrics = self._health_analyzer.analyze(
                check_report=report or CheckReport(),
                project_path=target_path
            )
            self._metrics = metrics
            logger.info(f"健康度分析完成: {metrics.overall_score:.1f}分")
            return metrics
        except Exception as e:
            logger.error(f"健康度分析失败: {e}")
            QMessageBox.critical(self, '错误', f'健康度分析失败:\n{str(e)}')
            return None

    def run_diagnostic(self, diagnostic_type: str = 'full'):
        """
        运行诊断（异步方式）

        在后台线程中执行诊断任务，避免阻塞UI。

        Args:
            diagnostic_type: 诊断类型 ('lsp'/'health'/'full')
        """
        if self._is_running:
            logger.warning("诊断已在运行中")
            return

        if not self._project_path:
            QMessageBox.warning(self, '提示', '请先设置项目路径')
            return

        self._update_ui_for_running(diagnostic_type)

        self._worker = DiagnosticWorker(
            project_path=self._project_path,
            diagnostic_type=diagnostic_type,
            check_report=self._check_report
        )

        self._worker.progress_updated.connect(self._on_progress_update)
        self._worker.lsp_finished.connect(self._on_lsp_finished)
        self._worker.health_finished.connect(self._on_health_finished)
        self._worker.all_finished.connect(self._on_all_finished)
        self._worker.error_occurred.connect(self._on_error_occurred)
        self._worker.finished.connect(self._on_worker_finished)

        self.diagnostic_started.emit()

        logger.info(f"开始{diagnostic_type}诊断: {self._project_path}")
        self._worker.start()

    def update_all_tabs(self, report: DiagnosticReport):
        """
        更新所有标签页的数据显示

        根据诊断报告内容刷新问题列表、根因分析等Tab。

        Args:
            report: 诊断报告对象
        """
        self._report = report

        self._populate_issues_table(report)
        self._populate_root_cause_browser(report)
        self._populate_call_chain_tree(report)

        self._lbl_issue_count.setText(
            f'共 {report.total_issues} 个问题 '
            f'(Error:{report.error_count} Warn:{report.warning_count} '
            f'Info:{report.info_count} Hint:{report.hint_count})'
        )

        self._btn_export.setEnabled(True)
        self._btn_copy_report.setEnabled(True)

        logger.info("所有标签页已更新")

    def update_health_dashboard(self, metrics: HealthMetrics):
        """
        更新健康度仪表盘

        刷新圆环图、柱状图、Top5问题和改进建议。

        Args:
            metrics: 健康度指标对象
        """
        self._metrics = metrics

        self._ring_widget.set_score(
            metrics.overall_score,
            metrics.health_grade.value,
            metrics.health_grade.label
        )

        if metrics.dimensions:
            self._bar_chart_widget.set_dimensions(metrics.dimensions)

        self._populate_top5_list(metrics)

        self._populate_suggestions_list(metrics.suggestions)

        logger.info("健康度仪表盘已更新")

    def export_report(self, format: str = 'markdown'):
        """
        导出诊断报告

        将当前诊断结果保存为文件。

        Args:
            format: 导出格式 ('markdown' 或 'json')
        """
        if not self._report and not self._metrics:
            QMessageBox.information(self, '提示', '暂无诊断结果可导出')
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if format == 'json':
            default_name = f'diagnostic_report_{timestamp}.json'
            file_filter = 'JSON Files (*.json);;All Files (*)'
        else:
            default_name = f'diagnostic_report_{timestamp}.md'
            file_filter = 'Markdown Files (*.md);;Text Files (*.txt);;All Files (*)'

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            '导出诊断报告',
            default_name,
            file_filter
        )

        if not file_path:
            return

        try:
            if format == 'json':
                content = self._generate_json_report()
            else:
                content = self._generate_markdown_report()

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            QMessageBox.information(
                self,
                '成功',
                f'报告已导出至:\n{file_path}'
            )
            logger.info(f"报告已导出: {file_path}")

        except Exception as e:
            QMessageBox.critical(
                self,
                '错误',
                f'导出报告失败:\n{str(e)}'
            )
            logger.error(f"导出报告失败: {e}")

    # ========================================================================
    # 内部实现方法 - 事件处理
    # ========================================================================

    def _on_start_diagnostic(self):
        """开始诊断按钮点击处理"""
        type_index = self._combo_type.currentIndex()
        type_key = list(DIAGNOSTIC_TYPES.keys())[type_index]
        self.run_diagnostic(type_key)

    def _on_progress_update(self, message: str):
        """进度更新回调"""
        self._update_status_label(f'{message}')

    def _on_lsp_finished(self, report: DiagnosticReport):
        """LSP诊断完成的回调"""
        self._report = report
        self.diagnostic_finished.emit(report)

    def _on_health_finished(self, metrics: HealthMetrics):
        """健康度分析完成的回调"""
        self._metrics = metrics
        self.health_analysis_finished.emit(metrics)

    def _on_all_finished(
        self,
        report: Optional[DiagnosticReport],
        metrics: Optional[HealthMetrics]
    ):
        """所有诊断完成的回调"""
        self._update_ui_for_completed()

        if report:
            self.update_all_tabs(report)

        if metrics:
            self.update_health_dashboard(metrics)

        total_issues = report.total_issues if report else 0
        score_str = f'{metrics.overall_score:.0f}分[{metrics.health_grade.value}]' if metrics else ''
        self._update_status_label(
            f'\u2705 诊断完成 - {total_issues}个问题 {score_str}'
        )

    def _on_error_occurred(self, error_msg: str):
        """发生错误的回调"""
        logger.error(f"诊断错误: {error_msg}")
        self._update_ui_for_completed()
        self._update_status_label(f'\u274C 诊断出错: {error_msg}')
        QMessageBox.critical(self, '诊断错误', error_msg)

    def _on_worker_finished(self):
        """工作线程结束的清理"""
        self._worker = None

    def cleanup(self):
        """清理后台资源，窗口关闭前调用"""
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.finished.disconnect(self._on_worker_finished)
            self._worker.wait(2000)
            self._worker = None

        for attr in ('_ring_widget', '_bar_chart_widget'):
            widget = getattr(self, attr, None)
            if widget and hasattr(widget, 'cleanup'):
                widget.cleanup()

    def _on_issue_selection_changed(self):
        """问题列表选择变化处理 - 更新底部详情区"""
        selected_items = self._table_issues.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        issue = self._get_issue_at_row(row)
        if issue:
            self._show_issue_detail(issue)

    def _on_issue_double_clicked(self, item: QTableWidgetItem):
        """问题列表双击事件 - 跳转到源码位置"""
        row = item.row()
        issue = self._get_issue_at_row(row)
        if issue and issue.file_path:
            self.source_jump_requested.emit(issue.file_path, issue.line_number)

    def _on_call_chain_item_double_clicked(
        self,
        item: QTreeWidgetItem,
        column: int
    ):
        """调用链节点双击事件"""
        file_path = item.data(0, ROLE_CALLER)
        if file_path and isinstance(file_path, str):
            self.source_jump_requested.emit(file_path, 0)

    def _show_issue_context_menu(self, position):
        """显示问题列表右键菜单"""
        item = self._table_issues.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        action_view_detail = menu.addAction('查看详情')
        action_view_detail.triggered.connect(
            lambda: self._on_issue_selection_changed()
        )

        action_jump_source = menu.addAction('跳转到源码')
        action_jump_source.triggered.connect(
            lambda: self._on_issue_double_clicked(item)
        )

        menu.addSeparator()

        action_copy = menu.addAction('复制问题描述')
        action_copy.triggered.connect(self._copy_selected_issue)

        menu.exec_(self._table_issues.viewport().mapToGlobal(position))

    # ========================================================================
    # 内部实现方法 - UI状态管理
    # ========================================================================

    def _update_ui_for_running(self, diagnostic_type: str):
        """更新UI为运行中状态"""
        self._is_running = True

        self._btn_start.setEnabled(False)
        self._btn_start.setText('\u23F3 诊断中...')

        self._combo_type.setEnabled(False)

        type_name = DIAGNOSTIC_TYPES.get(diagnostic_type, diagnostic_type)
        self._update_status_label(f'正在执行{type_name}诊断...')

    def _update_ui_for_completed(self):
        """更新UI为完成状态"""
        self._is_running = False

        self._btn_start.setEnabled(True)
        self._btn_start.setText('开始诊断')

        self._combo_type.setEnabled(True)

    def _update_status_label(self, text: str):
        """更新状态标签文本"""
        self._lbl_status.setText(text)

    # ========================================================================
    # 内部实现方法 - 数据填充
    # ========================================================================

    def _populate_issues_table(self, report: DiagnosticReport):
        """
        填充问题列表表格

        Args:
            report: 诊断报告
        """
        self._table_issues.setRowCount(len(report.issues))

        for row, issue in enumerate(report.issues):
            severity_item = QTableWidgetItem(
                SEVERITY_ICONS.get(issue.severity, '?')
            )
            severity_fg = SEVERITY_FG_COLORS.get(
                issue.severity, QColor('#333')
            )
            severity_bg = SEVERITY_COLORS.get(
                issue.severity, QColor('#ffffff')
            )
            severity_item.setForeground(severity_fg)
            severity_item.setBackground(severity_bg)
            severity_item.setData(Qt.UserRole, issue)
            self._table_issues.setItem(row, 0, severity_item)

            rule_item = QTableWidgetItem(issue.rule_id)
            rule_item.setData(Qt.UserRole, issue)
            self._table_issues.setItem(row, 1, rule_item)

            category_item = QTableWidgetItem(issue.category or '-')
            category_item.setData(Qt.UserRole, issue)
            self._table_issues.setItem(row, 2, category_item)

            desc_text = issue.message
            if len(desc_text) > 80:
                desc_text = desc_text[:77] + '...'
            desc_item = QTableWidgetItem(desc_text)
            desc_item.setToolTip(issue.message)
            desc_item.setData(Qt.UserRole, issue)
            self._table_issues.setItem(row, 3, desc_item)

            filename = Path(issue.file_path).name if issue.file_path else '-'
            file_item = QTableWidgetItem(filename)
            file_item.setToolTip(issue.file_path or '')
            file_item.setData(Qt.UserRole, issue)
            self._table_issues.setItem(row, 4, file_item)

            line_num = str(issue.line_number) if issue.line_number > 0 else '-'
            line_item = QTableWidgetItem(line_num)
            line_item.setData(Qt.UserRole, issue)
            self._table_issues.setItem(row, 5, line_item)

            if row % 2 == 0:
                for col in range(6):
                    table_item = self._table_issues.item(row, col)
                    if table_item and col != 0:
                        table_item.setBackground(severity_bg)

    def _populate_root_cause_browser(self, report: DiagnosticReport):
        """
        填充根因分析浏览器（Markdown格式）

        Args:
            report: 诊断报告
        """
        markdown_content = report.to_markdown()

        html_content = self._markdown_to_html(markdown_content)
        self._browser_root_cause.setHtml(html_content)

    def _populate_call_chain_tree(self, report: DiagnosticReport):
        """
        填充调用链树视图

        构建OB->FB调用关系的层级结构，
        对有问题的节点进行高亮标记。

        Args:
            report: 诊断报告
        """
        self._tree_call_chain.clear()

        if not report.ob_fb_call_chain:
            empty_item = QTreeWidgetItem(
                ['未检测到OB->FB调用链', '']
            )
            empty_item.setForeground(0, QColor('#999999'))
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsSelectable)
            self._tree_call_chain.addTopLevelItem(empty_item)
            return

        problem_fbs: set = set()
        for issue in report.issues:
            if issue.category == 'missing_implementation':
                problem_fbs.update(issue.related_symbols)
            elif issue.category == 'stub_misuse':
                problem_fbs.update(issue.related_symbols)

        for ob_name, fb_list in report.ob_fb_call_chain.items():
            ob_item = QTreeWidgetItem([ob_name, f'({len(fb_list)} 个调用)'])
            ob_item.setData(0, ROLE_CALLER, ob_name)
            ob_item.setForeground(0, QColor('#1976D2'))
            ob_item.setFont(0, QFont('Consolas', 10, QFont.Bold))

            for fb_name in fb_list:
                fb_item = QTreeWidgetItem([fb_name, ''])

                has_problem = fb_name in problem_fbs
                if has_problem:
                    fb_item.setForeground(0, QColor('#cf1322'))
                    fb_item.setBackground(0, QColor('#fff1f0'))
                    fb_item.setText(1, '[问题]')
                    fb_item.setForeground(1, QColor('#cf1322'))
                else:
                    fb_item.setForeground(0, QColor('#389e0d'))

                ob_item.addChild(fb_item)

            ob_item.setExpanded(True)
            self._tree_call_chain.addTopLevelItem(ob_item)

        total_obs = len(report.ob_fb_call_chain)
        total_calls = sum(len(v) for v in report.ob_fb_call_chain.values())
        self._lbl_chain_info.setText(
            f'OB -> FB 调用关系树 '
            f'({total_obs}个OB块, {total_calls}次调用)'
        )

    def _populate_top5_list(self, metrics: HealthMetrics):
        """
        填充Top5高频问题列表

        Args:
            metrics: 健康度指标
        """
        self._list_top5_issues.clear()

        worst_files = metrics.issue_distribution.worst_files[:5]
        if not worst_files:
            self._list_top5_issues.addItem(
                QListWidgetItem('\u2705 未发现高频问题文件')
            )
            return

        for rank, (file_path, count) in enumerate(worst_files, 1):
            filename = Path(file_path).name
            item = QListWidgetItem(f'{rank}. {filename}: {count} 个问题')
            item.setToolTip(file_path)

            if count >= 10:
                item.setForeground(QColor('#cf1322'))
            elif count >= 5:
                item.setForeground(QColor('#d48806'))
            else:
                item.setForeground(QColor('#333'))

            self._list_top5_issues.addItem(item)

    def _populate_suggestions_list(
        self,
        suggestions: List[ImprovementSuggestion]
    ):
        """
        填充改进建议列表

        Args:
            suggestions: 改进建议列表
        """
        self._list_suggestions.clear()

        if not suggestions:
            self._list_suggestions.addItem(
                QListWidgetItem('\u2705 项目状态良好，暂无改进建议')
            )
            return

        priority_icons = {'\uE042': '高', '\u26A0': '中', '\u2139': '低'}

        for sug in suggestions:
            icon_map = {'高': '[高]', '中': '[中]', '低': '[低]'}
            prefix = icon_map.get(sug.priority, '')

            item = QListWidgetItem(f'{prefix} {sug.title}')
            item.setToolTip(sug.description)

            colors = {'高': '#cf1322', '中': '#d48806', '低': '#1890ff'}
            item.setForeground(QColor(colors.get(sug.priority, '#333')))

            self._list_suggestions.addItem(item)

    def _show_issue_detail(self, issue: DiagnosticIssue):
        """
        显示问题的详细信息到底部详情区

        Args:
            issue: 诊断问题对象
        """
        if issue.code_snippet:
            snippet_text = f'// 文件: {issue.file_path}\n'
            snippet_text += f'// 行号: {issue.line_number}\n'
            snippet_text += f'// 规则: [{issue.rule_id}] {issue.severity.value}\n'
            snippet_text += '-' * 50 + '\n\n'
            snippet_text += issue.code_snippet
            self._txt_code_snippet.setPlainText(snippet_text)
        elif issue.source_line:
            self._txt_code_snippet.setPlainText(
                f'SCL源码位置: {issue.source_line}\n\n'
                f'规则: [{issue.rule_id}] {issue.severity.value}\n'
                f'描述: {issue.message}'
            )
        else:
            self._txt_code_snippet.setPlainText(
                f'规则: [{issue.rule_id}] {issue.severity.value}\n'
                f'描述: {issue.message}\n'
                f'文件: {issue.file_path}:{issue.line_number}'
            )

        self._list_fix_steps.clear()
        if issue.suggestion:
            lines = issue.suggestion.strip().split('\n')
            for i, line in enumerate(lines, 1):
                clean_line = line.strip()
                if clean_line:
                    step_item = QListWidgetItem(f'{i}. {clean_line}')
                    self._list_fix_steps.addItem(step_item)
        else:
            self._list_fix_steps.addItem(
                QListWidgetItem('暂无具体修复步骤')
            )

    def _get_issue_at_row(self, row: int) -> Optional[DiagnosticIssue]:
        """
        获取指定行对应的诊断问题对象

        Args:
            row: 表格行号

        Returns:
            DiagnosticIssue或None
        """
        if row < 0 or row >= self._table_issues.rowCount():
            return None
        item = self._table_issues.item(row, 0)
        if item:
            data = item.data(Qt.UserRole)
            if isinstance(data, DiagnosticIssue):
                return data
        return None

    # ========================================================================
    # 内部实现方法 - 辅助操作
    # ========================================================================

    def _copy_selected_issue(self):
        """复制选中的问题描述到剪贴板"""
        selected = self._table_issues.selectedItems()
        if not selected:
            return

        row = selected[0].row()
        issue = self._get_issue_at_row(row)
        if issue:
            clipboard = QApplication.clipboard()
            clipboard.setText(str(issue))

    def _copy_fix_steps(self):
        """复制修复步骤到剪贴板"""
        steps = []
        for i in range(self._list_fix_steps.count()):
            item = self._list_fix_steps.item(i)
            steps.append(item.text())

        if steps:
            clipboard = QApplication.clipboard()
            clipboard.setText('\n'.join(steps))

    def _copy_root_cause_report(self):
        """复制根因分析报告到剪贴板"""
        if self._report:
            clipboard = QApplication.clipboard()
            clipboard.setText(self._report.to_markdown())
        elif self._metrics:
            clipboard = QApplication.clipboard()
            clipboard.setText(self._metrics.get_summary_text())

    def _markdown_to_html(self, markdown_text: str) -> str:
        """
        将Markdown文本转换为简单HTML用于QTextBrowser展示

        实现基本的Markdown语法转换（标题、粗体、表格、列表等）。

        Args:
            markdown_text: Markdown格式文本

        Returns:
            str: HTML格式文本
        """
        import re

        html_lines = []
        html_lines.append('<html><body style="font-family: \'Microsoft YaHei UI\', sans-serif; font-size: 10pt; line-height: 1.6;">')

        for line in markdown_text.split('\n'):
            stripped = line.strip()

            if not stripped:
                html_lines.append('<br>')
                continue

            if stripped.startswith('---'):
                html_lines.append('<hr style="border:none; border-top:1px solid #e8e8e8; margin:12px 0;">')
                continue

            if stripped.startswith('####'):
                text = stripped[4:].strip()
                html_lines.append(f'<h4 style="color:#333; margin:10px 0 4px 0;">{text}</h4>')
            elif stripped.startswith('###'):
                text = stripped[3:].strip()
                html_lines.append(f'<h3 style="color:#444; margin:12px 0 6px 0;">{text}</h3>')
            elif stripped.startswith('##'):
                text = stripped[2:].strip()
                html_lines.append(f'<h2 style="color:#222; margin:14px 0 8px 0; border-bottom:2px solid #1890ff; padding-bottom:4px;">{text}</h2>')
            elif stripped.startswith('#'):
                text = stripped[1:].strip()
                html_lines.append(f'<h1 style="color:#1890ff; margin:16px 0 10px 0;">{text}</h1>')

            elif stripped.startswith('|') and stripped.endswith('|'):
                cells = [c.strip() for c in stripped.split('|')[1:-1]]
                if all(set(c) <= set('- :') for c in cells):
                    continue
                html_lines.append('<tr>' +
                    ''.join(f'<td style="padding:4px 8px; border-bottom:1px solid #eee;">{c}</td>'
                             for c in cells) + '</tr>')

            elif stripped.startswith('- ') or stripped.startswith('* '):
                text = stripped[2:]
                text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
                text = re.sub(r'`(.+?)`', r'<code style="background:#f5f5f5;padding:1px 4px;border-radius:2px;font-size:9pt;">\1</code>', text)
                html_lines.append(f'<div style="margin-left:16px; padding:2px 0;">\u2022 {text}</div>')

            else:
                text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', stripped)
                text = re.sub(r'`(.+?)`', r'<code style="background:#f5f5f5;padding:1px 4px;border-radius:2px;font-size:9pt;">\1</code>', text)
                html_lines.append(f'<p style="margin:4px 0;">{text}</p>')

        html_lines.append('</body></html>')
        return '\n'.join(html_lines)

    def _generate_json_report(self) -> str:
        """
        生成JSON格式的完整报告

        Returns:
            str: JSON字符串
        """
        result = {}

        if self._report:
            result['lsp_diagnostic'] = self._report.to_dict()

        if self._metrics:
            result['health_analysis'] = self._metrics.to_dict()

        result['export_time'] = datetime.now().isoformat()

        return json.dumps(result, ensure_ascii=False, indent=2)

    def _generate_markdown_report(self) -> str:
        """
        生成Markdown格式的完整报告

        合并LSP诊断报告和健康度分析报告。

        Returns:
            str: Markdown文本
        """
        sections = []

        sections.append('# PLC项目综合诊断报告')
        sections.append('')
        sections.append(f'**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        sections.append(f'**项目路径**: `{self._project_path or "未指定"}`')
        sections.append('')

        if self._report:
            sections.append('---')
            sections.append(self._report.to_markdown())
            sections.append('')

        if self._metrics:
            sections.append('---')
            sections.append('## \U0001F4CA 项目健康度分析')
            sections.append('')
            sections.append(self._metrics.get_summary_text())
            sections.append('')

            sections.append('### \U0001F4CB 各维度得分')
            sections.append('')
            sections.append('| 维度 | 得分 | 权重 | 等级 |')
            sections.append('|------|------|------|------|')
            for dim in self._metrics.dimensions:
                sections.append(
                    f'| {dim.name} | {dim.score:.1f}/100 | '
                    f'{dim.weight*100:.0f}% | {dim.grade} |'
                )
            sections.append('')

            if self._metrics.suggestions:
                sections.append('### 改进建议')
                sections.append('')
                for i, sug in enumerate(self._metrics.suggestions, 1):
                    sections.append(
                        f'**{i}. [{sug.priority}] {sug.title}**'
                    )
                    sections.append(f'   {sug.description}')
                    sections.append('')

        sections.append('---')
        sections.append('')
        sections.append(
            '*由 PLC项目管理工具 诊断面板 自动生成*'
        )

        return '\n'.join(sections)


# ============================================================================
# 主程序入口（用于测试）
# ============================================================================

if __name__ == '__main__':
    app = QApplication(sys.argv)

    panel = DiagnosticPanel()
    panel.setWindowTitle('PLC项目诊断面板 - DiagnosticPanel')
    panel.resize(1100, 750)

    if len(sys.argv) > 1:
        panel.set_project_path(sys.argv[1])

    panel.show()
    sys.exit(app.exec_())
