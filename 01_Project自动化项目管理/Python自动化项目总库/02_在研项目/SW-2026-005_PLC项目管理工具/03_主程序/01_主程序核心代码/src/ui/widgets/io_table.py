# -*- coding: utf-8 -*-
"""
IO分配表组件 (预留接口)

用于展示和管理PLC项目的IO地址分配信息，
支持从Excel导入/导出、冲突检测和可视化展示。

注意: 此模块为预留接口，待后续迭代实现。
"""
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QComboBox,
    QLineEdit,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class IOTableWidget(QWidget):
    """
    IO分配表组件 (预留)

    功能规划:
    - 表格化展示DI/DO/AI/AO点位信息
    - 支持按类型/模块/地址筛选排序
    - IO地址冲突检测与高亮警告
    - 从Excel模板导入/导出IO表
    - 与变量清单双向关联
    - 批量编辑和查找替换
    """

    # 表格列定义
    COLUMNS = [
        "序号", "类型", "地址", "符号名", "数据类型",
        "描述", "模块", "通道", "备注",
    ]

    # IO类型选项
    IO_TYPES = ["DI", "DO", "AI", "AO"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._io_data = []
        self._init_ui()

    def _init_ui(self):
        """初始化UI布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        # ===== 工具栏 =====
        toolbar = QHBoxLayout()

        # 类型筛选
        self._filter_type = QComboBox()
        self._filter_type.addItem("\u5168\u90E8")
        for io_type in self.IO_TYPES:
            self._filter_type.addItem(io_type)
        toolbar.addWidget(QLabel("\u7C7B\u578B:"))
        toolbar.addWidget(self._filter_type)

        # 搜索框
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText(
            "\u641C\u7D22\u5730\u5740/\u7B26\u53F7\u540D..."
        )
        self._search_edit.setMaximumWidth(200)
        toolbar.addWidget(self._search_edit)

        toolbar.addStretch()

        # 操作按钮
        btn_import = QPushButton("\u5BFC\u5165Excel")
        btn_import.clicked.connect(self._on_import)
        btn_export = QPushButton("\u5BFC\u51FAExcel")
        btn_export.clicked.connect(self._on_export)
        btn_add = QPushButton("\u002B \u6DFB\u52A0")
        btn_add.clicked.connect(self._on_add_row)
        btn_check = QPushButton("\u2705 \u68C0\u67E5\u51B2\u7A81")
        btn_check.clicked.connect(self._on_check_conflicts)

        toolbar.addWidget(btn_import)
        toolbar.addWidget(btn_export)
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_check)

        layout.addLayout(toolbar)

        # ===== 数据表格 =====
        self._table = QTableWidget()
        self._table.setColumnCount(len(self.COLUMNS))
        self._table.setHorizontalHeaderLabels(self.COLUMNS)
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive
        )
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(
            QTableWidget.SelectRows
        )
        self._table.setEditTriggers(
            QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed
        )

        # 设置列宽比例
        col_widths = [50, 45, 80, 140, 70, 180, 80, 50, 120]
        for i, width in enumerate(col_widths):
            self._table.setColumnWidth(i, width)

        layout.addWidget(self._table)

        # ===== 状态栏 =====
        self._status_label = QLabel(
            "\u26A1 IO\u5206\u914D\u8868 (\u9884\u7559)"
        )
        self._status_label.setStyleSheet(
            "font-size: 9pt; color: #9E9E9E;"
        )
        layout.addWidget(self._status_label)

        # 加载示例数据
        self._load_sample_data()

    def _load_sample_data(self):
        """加载示例IO数据用于演示"""
        sample_data = [
            [1, "DI", "%IX0.0", "bEmergencyStop", "BOOL",
             "急停按钮-常闭", "DI_Module_1", "CH0", ""],
            [2, "DI", "%IX0.1", "bStartButton", "BOOL",
             "启动按钮", "DI_Module_1", "CH1", ""],
            [3, "DI", "%IX0.2", "bStopButton", "BOOL",
             "停止按钮", "DI_Module_1", "CH2", ""],
            [4, "DO", "%QX0.0", "bMotorRun", "BOOL",
             "电机运行指示灯", "DO_Module_1", "CH0", ""],
            [5, "DO", "%QX0.1", "bFaultLamp", "BOOL",
             "故障报警灯", "DO_Module_1", "CH1", ""],
            [6, "AI", "%IW64", "rTemperature", "REAL",
             "温度传感器输入", "AI_Module_1", "CH0", "0-100°C"],
            [7, "AO", "%QW64", "anSpeedRef", "INT",
             "变频器速度给定", "AO_Module_1", "CH0", "0-100%"],
        ]

        self._table.setRowCount(len(sample_data))
        for row_idx, row_data in enumerate(sample_data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                if col_idx == 1:  # 类型列着色
                    type_colors = {
                        "DI": QColor("#E3F2FD"),
                        "DO": QColor("#FFF3E0"),
                        "AI": QColor("#E8F5E9"),
                        "AO": QColor("#FCE4EC"),
                    }
                    bg_color = type_colors.get(str(value), QColor("#FFFFFF"))
                    item.setBackground(bg_color)
                self._table.setItem(row_idx, col_idx, item)

        self._status_label.setText(
            f"\u26A1 IO\u5206\u914D\u8868 - \u5171 {len(sample_data)} \u6761\u8BB0\u5F55"
        )

    def _on_import(self):
        """导入Excel文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "\u5BFC\u5165IO\u5206\u914D\u8868", "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        if file_path:
            try:
                import openpyxl
                wb = openpyxl.load_workbook(file_path)
                ws = wb.active
                # TODO: 解析并填充表格
                QMessageBox.information(
                    self, "\u6210\u529F",
                    f"\u5BFC\u5165\u6210\u529F: {file_path}"
                )
                logger.info(f"IO表导入: {file_path}")
            except ImportError:
                QMessageBox.warning(
                    self, "\u63D0\u793A",
                    "\u9700\u8981\u5B89\u88C5openpyxl: pip install openpyxl"
                )
            except Exception as e:
                QMessageBox.critical(self, "\u9519\u8BEF", str(e))

    def _on_export(self):
        """导出到Excel文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "\u5BFC\u51FAIO\u5206\u914D\u8868", "IO_Allocation.xlsx",
            "Excel Files (*.xlsx);;All Files (*)"
        )
        if file_path:
            try:
                import openpyxl
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "IO_Allocation"

                # 写入表头
                for col_idx, header in enumerate(self.COLUMNS, 1):
                    ws.cell(row=1, column=col_idx, value=header)

                # 写入数据
                for row_idx in range(self._table.rowCount()):
                    for col_idx in range(self._table.columnCount()):
                        item = self._table.item(row_idx, col_idx)
                        value = item.text() if item else ""
                        ws.cell(row=row_idx + 2, column=col_idx + 1, value=value)

                wb.save(file_path)
                QMessageBox.information(
                    self, "\u6210\u529F",
                    f"\u5BFC\u51FA\u6210\u529F: {file_path}"
                )
                logger.info(f"IO表导出: {file_path}")
            except ImportError:
                QMessageBox.warning(
                    self, "\u63D0\u793A",
                    "\u9700\u8981\u5B89\u88C5openpyxl: pip install openpyxl"
                )
            except Exception as e:
                QMessageBox.critical(self, "\u9519\u8BEF", str(e))

    def _on_add_row(self):
        """添加新行"""
        row_count = self._table.rowCount()
        self._table.insertRow(row_count)
        self._table.setItem(row_count, 0, QTableWidgetItem(str(row_count + 1)))

    def _on_check_conflicts(self):
        """检查IO地址冲突"""
        address_set = set()
        conflicts = []

        for row in range(self._table.rowCount()):
            addr_item = self._table.item(row, 2)
            if addr_item:
                addr = addr_item.text().strip()
                if addr and addr in address_set:
                    conflicts.append((row + 1, addr))
                elif addr:
                    address_set.add(addr)

        if conflicts:
            details = "\n".join([
                f"  \u2022 \u884C{row}: {addr}" for row, addr in conflicts
            ])
            QMessageBox.warning(
                self, "\u26A0\uFE0F IO\u5730\u5740\u51B2\u7A81",
                f"\u53D1\u73B0 {len(conflicts)} \u5904\u5730\u5740\u51B2\u7A81:\n\n{details}"
            )
        else:
            QMessageBox.information(
                self, "\u2705 \u68C0\u67E5\u901A\u8FC7",
                "\u672A\u53D1\u73B0IO\u5730\u5740\u51B2\u7A61!"
            )
