# -*- coding: utf-8 -*-
"""
HMI映射组件 (预留接口)

用于管理PLC变量与HMI画面元素的映射关系，
支持变量地址绑定、报警关联和画面导航配置。

注意: 此模块为预留接口，待后续迭代实现。
"""
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QComboBox,
    QLineEdit,
    QGroupBox,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class HMIMapperWidget(QWidget):
    """
    HMI变量映射组件 (预留)

    功能规划:
    - PLC变量与HMI控件的双向绑定管理
    - 报警变量与HMI画面的自动关联
    - IO点位到HMI按钮/指示灯的映射表
    - 支持多品牌HMI格式导出 (威纶通/西门子/倍福等)
    - 映射冲突检测
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """初始化UI布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # 标题
        header = QHBoxLayout()
        title_label = QLabel("\uD83D\uDDA5 HMI\u53D8\u91CF\u6620\u5C04")
        title_label.setStyleSheet(
            "font-size: 12pt; font-weight: bold; color: #1976D2;"
        )
        header.addWidget(title_label)
        header.addStretch()

        hmi_brand_combo = QComboBox()
        hmi_brand_combo.addItems([
            "\u5A01\u7EAF\u901A (Weinview)",
            "\u897F\u95E8\u5B50 (WinCC)",
            "\u500D\u798F (TwinCAT)",
            "\u666E\u6D1B\u83F2 (Proface)",
        ])
        header.addWidget(QLabel("HMI\u54C1\u724C:"))
        header.addWidget(hmi_brand_combo)
        layout.addLayout(header)

        # ===== 映射表格 =====
        map_group = QGroupBox("\u53D8\u91CF\u6620\u5C04\u8868")
        map_layout = QVBoxLayout(map_group)

        columns = [
            "PLC\u53D8\u91CF", "\u5730\u5740", "\u6570\u636E\u7C7B\u578B",
            "HMI\u63A7\u4EF6", "\u753B\u9762ID", "\u6620\u5C04\u7C7B\u578B",
            "\u5907\u6CE8",
        ]

        self._table = QTableWidget()
        self._table.setColumnCount(len(columns))
        self._table.setHorizontalHeaderLabels(columns)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)

        col_widths = [140, 80, 70, 100, 80, 80, 150]
        for i, w in enumerate(col_widths):
            self._table.setColumnWidth(i, w)

        map_layout.addWidget(self._table)
        layout.addWidget(map_group)

        # ===== 操作栏 =====
        action_bar = QHBoxLayout()

        btn_add = QPushButton("\u002B \u6DFB\u52A0\u6620\u5C04")
        btn_add.clicked.connect(self._on_add_mapping)
        btn_import_var = QPushButton("\u5BFC\u5165\u53D8\u91CF\u8868")
        btn_export = QPushButton("\u5BFC\u51FAHMI\u914D\u7F6E")
        btn_check = QPushButton("\u2705 \u68C0\u67E5\u51B2\u7A81")

        action_bar.addWidget(btn_add)
        action_bar.addWidget(btn_import_var)
        action_bar.addWidget(btn_export)
        action_bar.addWidget(btn_check)
        action_bar.addStretch()
        layout.addLayout(action_bar)

        # ===== 预留提示 =====
        info_label = QLabel(
            "\uD83D\uDDA5 HMI\u6620\u5C04\u529F\u80FD\u6B63\u5728\u5F00\u53D1\u4E2D...\n\n"
            "\u89C4\u5219\u529F\u80FD:\n"
            "- PLC\u5168\u5C40\u53D8\u91CF\u4E0EHMI\u63A7\u4EF6\u7684\u7ED1\u5B9A\u7BA1\u7406\n"
            "- \u62A5\u8B66\u53D8\u91CF\u81EA\u52A8\u5173\u8054\u5230\u62A5\u8B66\u753B\u9762\n"
            "- \u591A\u54C1\u724CHMI\u683C\u5F0F\u5BFC\u51FA (.vtp/.hmi)\n"
            "- \u53D8\u91CF\u5730\u5740\u4E0E\u63A7\u4EF6\u7C7B\u578B\u5339\u914D\u6821\u9A8C"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet(
            "color: #9E9E9E; font-size: 10pt; padding: 12px;"
        )
        layout.addWidget(info_label)

        # 加载示例数据
        self._load_sample_data()

    def _load_sample_data(self):
        """加载示例映射数据用于演示"""
        samples = [
            ["bMotorRun", "%M0.0", "BOOL", "Indicator_Lamp", "Main_001",
             "\u8BFB\u5199", "\u8FD0\u884C\u6307\u793A\u706F"],
            ["bStartBtn", "%IX0.1", "BOOL", "Button_Start", "Main_002",
             "\u5199", "\u542F\u52A8\u6309\u94AE"],
            ["bStopBtn", "%IX0.2", "BOOL", "Button_Stop", "Main_002",
             "\u5199", "\u505C\u6B62\u6309\u94AE"],
            ["rSpeedAct", "%RW64", "REAL", "Numeric_Display", "Main_003",
             "\u8BFB", "\u5B9E\u9645\u901F\u5EA6\u663E\u793A"],
            ["bFault", "%M0.10", "BOOL", "Alarm_Banner", "Alarm_001",
             "\u8BFB\u5199", "\u6545\u969C\u62A5\u8B66"],
        ]

        self._table.setRowCount(len(samples))
        for row_idx, row_data in enumerate(samples):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                # 映射类型列着色
                if col_idx == 5:
                    type_colors = {
                        "\u8BFB": QColor("#E3F2FD"),
                        "\u5199": QColor("#FFF3E0"),
                        "\u8BFB\u5199": QColor("#E8F5E9"),
                    }
                    item.setBackground(type_colors.get(value, QColor("#FFFFFF")))
                self._table.setItem(row_idx, col_idx, item)

    def _on_add_mapping(self):
        """添加新映射行"""
        row_count = self._table.rowCount()
        self._table.insertRow(row_count)
        # 设置默认值
        defaults = ["", "", "", "", "", "\u8BFB", ""]
        for col_idx, val in enumerate(defaults):
            self._table.setItem(row_count, col_idx, QTableWidgetItem(val))

    def _on_import_variables(self):
        """从变量清单导入"""
        QMessageBox.information(
            self, "\u63D0\u793A",
            "\u53D8\u91CF\u5BFC\u5165\u529F\u80FD\u6B63\u5728\u5F00\u53D1\u4E2D..."
        )

    def _on_export_hmi(self):
        """导出HMI配置文件"""
        QMessageBox.information(
            self, "\u63D0\u793A",
            "HMI\u914D\u7F6E\u5BFC\u51FA\u529F\u80FD\u6B63\u5728\u5F00\u53D1\u4E2D..."
        )

    def _on_check_conflicts(self):
        """检查映射冲突"""
        QMessageBox.information(
            self, "\u63D0\u793A",
            "\u6620\u5C04\u51B2\u7A61\u68C0\u67E5\u529F\u80FD\u6B63\u5728\u5F00\u53D1\u4E2D..."
        )
