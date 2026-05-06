# -*- coding: utf-8 -*-
"""
新建项目向导对话框

提供专业的多步骤向导界面，用于创建符合 TPL-SINGLE-PLC-M001 规范的标准PLC项目。
包含4个步骤: 选择父目录 -> 填写基本信息 -> 选择模板 -> 确认创建
"""
import json
import re
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QTextEdit,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QProgressBar,
    QFrame,
    QScrollArea,
    QWidget,
    QMessageBox,
    QFileDialog,
    QSizePolicy,
    QStackedWidget,
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon

from src.core.constants import (
    PLCBrand,
    HMIBrand,
    PLC_BRAND_DESCRIPTIONS,
    HMI_BRAND_DESCRIPTIONS,
    TEMPLATE_METADATA,
    TEMPLATE_FILES,
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# ============================================================
# 常量定义
# ============================================================
DEFAULT_PARENT_DIR = r"d:\BaiduSyncdisk\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\0100_项目" + "\\"

# 项目编号正则: DJ-YYYY-NNN
RE_PROJECT_ID = re.compile(r"^DJ-\d{4}-\d{3}$")

# 设备类型选项
DEVICE_TYPES = [
    ("输送设备", "conveyor"),
    ("装配设备", "assembly"),
    ("检测设备", "inspection"),
    ("包装设备", "packaging"),
    ("加工设备", "processing"),
    ("其他", "other"),
]

# IO规模选项 (value, label, description, recommended_template)
IO_SCALES = [
    ("small", "小型 (<50点)", "推荐使用 S001 精简版模板", "TPL-SINGLE-PLC-S001"),
    ("medium", "中型 (50-100点)", "推荐使用 M001 完整版模板", "TPL-SINGLE-PLC-M001"),
    ("large", "大型 (>100点)", "强制使用 M001 完整版模板", "TPL-SINGLE-PLC-M001"),
]

# 模板详细信息
TEMPLATE_DETAILS = {
    "TPL-SINGLE-PLC-M001": {
        "name": "TPL-SINGLE-PLC-M001",
        "display_name": "完整版",
        "description": "包含完整14大模块的标准单机PLC项目模板",
        "features": [
            "11个标准目录结构",
            "20+种文档模板占位文件",
            "完整的PLC程序框架(Pou/Gvl/Dut/Visu)",
            "HMI配置目录",
            "变量清单与IO分配表",
            "报警定义与测试报告",
        ],
        "suitable_for": "中大型项目 (IO>=50)",
        "directory_count": 11,
        "document_count": 20,
    },
    "TPL-SINGLE-PLC-S001": {
        "name": "TPL-SINGLE-PLC-S001",
        "display_name": "精简版",
        "description": "精简版单机PLC项目模板，适用于小型快速交付项目",
        "features": [
            "4个核心目录结构",
            "必要文档占位文件",
            "基础PLC程序框架(Pou/Gvl)",
            "HMI配置目录",
            "变量与IO表目录",
        ],
        "suitable_for": "小型快速交付项目 (IO<50)",
        "directory_count": 4,
        "document_count": 6,
    },
}


class StepIndicator(QWidget):
    """步骤指示器组件 - 显示当前进度"""

    def __init__(self, total_steps: int = 4, parent=None):
        super().__init__(parent)
        self._total_steps = total_steps
        self._current_step = 0
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._step_labels = []
        step_titles = ["选择目录", "基本信息", "选择模板", "确认创建"]

        for i in range(self._total_steps):
            # 步骤圆圈
            circle = QLabel(f"{i + 1}")
            circle.setFixedSize(28, 28)
            circle.setAlignment(Qt.AlignCenter)
            circle.setStyleSheet("""
                QLabel {
                    background-color: #E0E0E0;
                    color: #757575;
                    border-radius: 14px;
                    font-size: 10pt;
                    font-weight: bold;
                }
            """)
            self._step_labels.append(("circle", circle))
            layout.addWidget(circle)

            # 连接线（最后一个步骤不需要）
            if i < self._total_steps - 1:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setFixedHeight(2)
                line.setStyleSheet("background-color: #E0E0E0;")
                self._step_labels.append(("line", line))
                layout.addWidget(line, 1)

            # 步骤标题
            title = QLabel(step_titles[i] if i < len(step_titles) else f"Step {i+1}")
            title.setStyleSheet("""
                QLabel {
                    color: #9E9E9E;
                    font-size: 9pt;
                    padding: 0 4px;
                }
            """)
            self._step_labels.append(("title", title))
            layout.addWidget(title)

            # 间距
            if i < self._total_steps - 1:
                spacer = QWidget()
                spacer.setMinimumWidth(20)
                layout.addWidget(spacer, 1)

        layout.addStretch()

    def set_current_step(self, step: int):
        """设置当前激活的步骤 (0-based)"""
        self._current_step = step

        active_style_circle = """
            QLabel {
                background-color: #1976D2;
                color: white;
                border-radius: 14px;
                font-size: 10pt;
                font-weight: bold;
            }
        """
        completed_style_circle = """
            QLabel {
                background-color: #4CAF50;
                color: white;
                border-radius: 14px;
                font-size: 10pt;
                font-weight: bold;
            }
        """
        active_style_title = "QLabel { color: #1976D2; font-size: 9pt; font-weight: bold; padding: 0 4px; }"
        completed_style_title = "QLabel { color: #4CAF50; font-size: 9pt; padding: 0 4px; }"
        active_style_line = "background-color: #1976D2;"
        completed_style_line = "background-color: #4CAF50;"

        for item_type, widget in self._step_labels:
            if item_type == "circle":
                idx = self._step_labels.index((item_type, widget)) // 3
                if idx < step:
                    widget.setStyleSheet(completed_style_circle)
                elif idx == step:
                    widget.setStyleSheet(active_style_circle)
                else:
                    widget.setStyleSheet("""
                        QLabel {
                            background-color: #E0E0E0;
                            color: #757575;
                            border-radius: 14px;
                            font-size: 10pt;
                            font-weight: bold;
                        }
                    """)
            elif item_type == "title":
                idx = self._step_labels.index((item_type, widget)) // 3
                if idx < step:
                    widget.setStyleSheet(completed_style_title)
                elif idx == step:
                    widget.setStyleSheet(active_style_title)
                else:
                    widget.setStyleSheet("""
                        QLabel { color: #9E9E9E; font-size: 9pt; padding: 0 4px; }
                    """)
            elif item_type == "line":
                idx = self._step_labels.index((item_type, widget)) // 3
                if idx < step:
                    widget.setStyleSheet(completed_style_line)
                else:
                    widget.setStyleSheet("background-color: #E0E0E0;")


class StepPage(QWidget):
    """向导步骤页基类"""

    def __init__(self, parent=None):
        super().__init__(parent)

    def validate(self) -> tuple:
        """验证当前页面数据, 返回 (is_valid: bool, error_message: str)"""
        return True, ""

    def collect_data(self) -> dict:
        """收集当前页面数据"""
        return {}


class DirectorySelectPage(StepPage):
    """Step 1: 选择父目录"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # 标题说明
        title = QLabel("选择项目的父级存储目录")
        title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #212121;")
        layout.addWidget(title)

        desc = QLabel(
            "项目将在此目录下创建以 \"项目编号_项目名称\" 命名的子文件夹。\n"
            "请确保所选目录存在且具有写入权限。"
        )
        desc.setStyleSheet("color: #616161; font-size: 9pt;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(12)

        # 目录选择区域
        path_frame = QFrame()
        path_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        path_layout = QVBoxLayout(path_frame)
        path_layout.setContentsMargins(16, 12, 16, 12)

        # 当前路径显示
        path_row = QHBoxLayout()
        path_label = QLabel("目标父目录:")
        path_label.setStyleSheet("font-weight: bold; color: #424242;")
        path_row.addWidget(path_label)

        self._edit_path = QLineEdit()
        self._edit_path.setText(DEFAULT_PARENT_DIR)
        self._edit_path.setMinimumHeight(32)
        self._edit_path.setStyleSheet("""
            QLineEdit {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: white;
                font-size: 10pt;
            }
            QLineEdit:focus { border-color: #1976D2; }
            QLineEdit:read-only {
                background-color: #FAFAFA;
                color: #424242;
            }
        """)
        path_row.addWidget(self._edit_path)

        self._btn_browse = QPushButton("浏览...")
        self._btn_browse.setFixedHeight(32)
        self._btn_browse.setCursor(Qt.PointingHandCursor)
        self._btn_browse.setStyleSheet("""
            QPushButton {
                background-color: #E3F2FD;
                color: #1976D2;
                border: 1px solid #BBDEFB;
                border-radius: 4px;
                padding: 0 16px;
                font-size: 9pt;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #BBDEFB; }
        """)
        self._btn_browse.clicked.connect(self._on_browse)
        path_row.addWidget(self._btn_browse)

        path_layout.addLayout(path_row)

        # 路径预览
        preview_label = QLabel("路径预览:")
        preview_label.setStyleSheet("font-weight: bold; color: #424242; margin-top: 8px;")
        path_layout.addWidget(preview_label)

        self._preview_label = QLabel()
        self._preview_label.setStyleSheet(
            "color: #1976D2; font-size: 10pt; "
            "background-color: white; padding: 8px; border-radius: 4px;"
        )
        self._preview_label.setWordWrap(True)
        self._update_preview()
        path_layout.addWidget(self._preview_label)

        # 验证状态
        self._validation_label = QLabel()
        self._validation_label.setStyleSheet("color: #4CAF50; font-size: 9pt; margin-top: 4px;")
        path_layout.addWidget(self._validation_label)

        layout.addWidget(path_frame)
        layout.addStretch()

        # 绑定信号
        self._edit_path.textChanged.connect(self._on_path_changed)

    def _on_browse(self):
        """打开目录选择对话框"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择项目父目录",
            self._edit_path.text() or DEFAULT_PARENT_DIR,
            QFileDialog.ShowDirsOnly,
        )
        if dir_path:
            self._edit_path.setText(dir_path)

    def _on_path_changed(self, text: str):
        """路径变化时更新预览和验证"""
        self._update_preview()
        self._validate_directory()

    def _update_preview(self):
        """更新路径预览"""
        base_path = self._edit_path.text().strip() or "[未设置]"
        example_name = "DJ-2026-006_示例项目"
        full_path = str(Path(base_path) / example_name)
        self._preview_label.setText(full_path)

    def _validate_directory(self):
        """验证目录是否有效"""
        path_str = self._edit_path.text().strip()
        if not path_str:
            self._validation_label.setText("")
            self._validation_label.setStyleSheet("color: #9E9E9E; font-size: 9pt;")
            return

        path = Path(path_str)
        if not path.exists():
            self._validation_label.setText("X 目录不存在")
            self._validation_label.setStyleSheet("color: #F44336; font-size: 9pt; font-weight: bold;")
        elif not path.is_dir():
            self._validation_label.setText("X 路径不是目录")
            self._validation_label.setStyleSheet("color: #F44336; font-size: 9pt; font-weight: bold;")
        else:
            try:
                test_file = path / ".write_test"
                test_file.touch()
                test_file.unlink()
                self._validation_label.setText("OK 目录可读写")
                self._validation_label.setStyleSheet("color: #4CAF50; font-size: 9pt; font-weight: bold;")
            except OSError:
                self._validation_label.setText("X 目录不可写")
                self._validation_label.setStyleSheet("color: #F44336; font-size: 9pt; font-weight: bold;")

    def validate(self) -> tuple:
        """验证目录选择"""
        path_str = self._edit_path.text().strip()
        if not path_str:
            return False, "请选择或输入项目父目录"

        path = Path(path_str)
        if not path.exists():
            return False, f"目录不存在: {path_str}"
        if not path.is_dir():
            return False, f"路径不是有效目录: {path_str}"

        # 测试写入权限
        try:
            test_file = path / ".write_test"
            test_file.touch()
            test_file.unlink()
        except OSError:
            return False, f"目录没有写入权限: {path_str}"

        return True, ""

    def collect_data(self) -> dict:
        """收集目录数据"""
        return {"parent_dir": self._edit_path.text().strip()}

    def get_parent_dir(self) -> str:
        """获取选择的父目录路径"""
        return self._edit_path.text().strip()


class BasicInfoPage(StepPage):
    """Step 2: 填写项目基本信息"""

    # 定义信号: 数据变化时通知外部
    data_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._io_scale = "medium"  # 默认中型
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 标题
        title = QLabel("填写项目基本信息")
        title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #212121;")
        layout.addWidget(title)

        desc = QLabel("请准确填写以下信息，带 * 的字段为必填项。")
        desc.setStyleSheet("color: #616161; font-size: 9pt;")
        layout.addWidget(desc)

        # 可滚动表单区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(12)

        # ---- 项目编号 ----
        id_group = self._create_form_group("项目编号", required=True)
        self._edit_project_id = QLineEdit()
        self._edit_project_id.setPlaceholderText("例如: DJ-2026-006")
        self._edit_project_id.setMinimumHeight(34)
        self._setup_input_style(self._edit_project_id)
        self._edit_project_id.textChanged.connect(self._on_project_id_changed)
        id_group.layout().addWidget(self._edit_project_id)

        self._id_hint = QLabel("格式: DJ-YYYY-NNN (如 DJ-2026-006)")
        self._id_hint.setStyleSheet("color: #9E9E9E; font-size: 8pt; margin-left: 4px;")
        id_group.layout().addWidget(self._id_hint)

        self._id_validation = QLabel()
        self._id_validation.setStyleSheet("font-size: 8pt; margin-left: 4px;")
        id_group.layout().addWidget(self._id_validation)

        form_layout.addWidget(id_group)

        # ---- 项目名称 ----
        name_group = self._create_form_group("项目名称", required=True)
        self._edit_project_name = QLineEdit()
        self._edit_project_name.setPlaceholderText("例如: 边框缓存机、打胶机送料机构")
        self._edit_project_name.setMinimumHeight(34)
        self._setup_input_style(self._edit_project_name)
        # 项目名称改变时，如果编号为空则自动生成
        self._edit_project_name.textChanged.connect(self._on_project_name_changed)
        name_group.layout().addWidget(self._edit_project_name)

        self._name_validation = QLabel()
        self._name_validation.setStyleSheet("font-size: 8pt; margin-left: 4px;")
        name_group.layout().addWidget(self._name_validation)

        form_layout.addWidget(name_group)

        # ---- 设备类型 & PLC品牌 (同一行) ----
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(12)

        device_group = self._create_form_group("设备类型", required=True)
        self._combo_device_type = QComboBox()
        self._combo_device_type.setMinimumHeight(34)
        for display, value in DEVICE_TYPES:
            self._combo_device_type.addItem(display, value)
        self._setup_combo_style(self._combo_device_type)
        device_group.layout().addWidget(self._combo_device_type)
        row1_layout.addWidget(device_group)

        plc_group = self._create_form_group("PLC品牌", required=True)
        self._combo_plc_brand = QComboBox()
        self._combo_plc_brand.setMinimumHeight(34)
        for brand in PLCBrand:
            desc = PLC_BRAND_DESCRIPTIONS.get(brand, brand.value)
            self._combo_plc_brand.addItem(f"{brand.value} ({desc})", brand)
        self._setup_combo_style(self._combo_plc_brand)
        plc_group.layout().addWidget(self._combo_plc_brand)
        row1_layout.addWidget(plc_group)

        form_layout.addLayout(row1_layout)

        # ---- HMI品牌 ----
        hmi_group = self._create_form_group("HMI品牌", required=False)
        self._combo_hmi_brand = QComboBox()
        self._combo_hmi_brand.setMinimumHeight(34)
        self._combo_hmi_brand.addItem("-- 不使用HMI --", None)
        for brand in HMIBrand:
            desc = HMI_BRAND_DESCRIPTIONS.get(brand, brand.value)
            self._combo_hmi_brand.addItem(f"{brand.value} ({desc})", brand)
        self._setup_combo_style(self._combo_hmi_brand)
        hmi_group.layout().addWidget(self._combo_hmi_brand)
        form_layout.addWidget(hmi_group)

        # ---- IO点数估算 ----
        io_group = self._create_form_group("IO点数估算", required=True)
        io_layout = QVBoxLayout(io_group)
        io_layout.setSpacing(6)

        self._io_button_group = QButtonGroup(self)
        for value, label, description, _ in IO_SCALES:
            rb_layout = QHBoxLayout()
            rb = QRadioButton(label)
            rb.setCursor(Qt.PointingHandCursor)
            rb.setStyleSheet("""
                QRadioButton {
                    font-size: 10pt;
                    spacing: 6px;
                    color: #424242;
                }
                QRadioButton::indicator {
                    width: 16px;
                    height: 16px;
                }
                QRadioButton::indicator:unchecked {
                    border: 2px solid #BDBDBD;
                    border-radius: 8px;
                    background: white;
                }
                QRadioButton::indicator:checked {
                    border: 2px solid #1976D2;
                    border-radius: 8px;
                    background: #1976D2;
                }
            """)
            self._io_button_group.addButton(rb)
            # 用 objectName 存储 value
            rb.setObjectName(value)
            if value == "medium":
                rb.setChecked(True)

            hint = QLabel(description)
            hint.setStyleSheet("color: #757575; font-size: 8pt;")

            rb_layout.addWidget(rb)
            rb_layout.addWidget(hint)
            rb_layout.addStretch()
            io_layout.addLayout(rb_layout)

        form_layout.addWidget(io_group)

        # ---- 项目负责人 (可选) ----
        owner_group = self._create_form_group("项目负责人", required=False)
        self._edit_owner = QLineEdit()
        self._edit_owner.setPlaceholderText("可选，项目负责人姓名")
        self._edit_owner.setMinimumHeight(34)
        self._setup_input_style(self._edit_owner)
        owner_group.layout().addWidget(self._edit_owner)
        form_layout.addWidget(owner_group)

        # ---- 项目描述 (可选) ----
        desc_group = self._create_form_group("项目描述", required=False)
        self._edit_description = QTextEdit()
        self._edit_description.setPlaceholderText("可选，简要描述项目背景、目标和特殊要求...")
        self._edit_description.setMaximumHeight(80)
        self._edit_description.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: white;
                font-size: 10pt;
            }
            QTextEdit:focus { border-color: #1976D2; }
        """)
        desc_group.layout().addWidget(self._edit_description)
        form_layout.addWidget(desc_group)

        form_layout.addStretch()
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)

        # 绑定信号
        self._io_button_group.buttonClicked.connect(self._on_io_scale_changed)
        self._edit_project_id.editingFinished.connect(self._validate_project_id)
        self._edit_project_name.editingFinished.connect(self._validate_project_name)

    def _create_form_group(self, label_text: str, required: bool = False) -> QFrame:
        """创建表单组容器"""
        frame = QFrame()
        vlayout = QVBoxLayout(frame)
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.setSpacing(4)

        # 标签行
        hlayout = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("font-weight: bold; color: #424242; font-size: 10pt;")
        hlayout.addWidget(label)

        if required:
            star = QLabel("*")
            star.setStyleSheet("color: #F44336; font-weight: bold; font-size: 12pt;")
            hlayout.addWidget(star)

        hlayout.addStretch()
        vlayout.addLayout(hlayout)

        return frame

    def _setup_input_style(self, edit: QLineEdit):
        """设置输入框统一样式"""
        edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: white;
                font-size: 10pt;
            }
            QLineEdit:focus { border-color: #1976D2; }
        """)

    def _setup_combo_style(self, combo: QComboBox):
        """设置下拉框统一样式"""
        combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: white;
                font-size: 10pt;
            }
            QComboBox:focus { border-color: #1976D2; }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #757575;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #E0E0E0;
                selection-background-color: #E3F2FD;
                selection-color: #1976D2;
            }
        """)

    def _on_project_name_changed(self, text: str):
        """
        项目名称变化时自动生成项目编号
        
        当用户输入项目名称且编号为空时，
        自动生成 DJ-YYYY-NNN 格式编号。
        用户仍可手动编辑修改编号。
        """
        text = text.strip()
        current_id = self._edit_project_id.text().strip()
        
        # 只有当名称有效(>=2字符)且编号为空时才自动生成
        if len(text) >= 2 and not current_id:
            auto_id = self._generate_auto_project_id()
            if auto_id:
                # 使用 blockSignals 避免触发校验
                self._edit_project_id.blockSignals(True)
                self._edit_project_id.setText(auto_id)
                self._edit_project_id.blockSignals(False)
                logger.debug(f"自动生成项目编号: {auto_id}")
    
    def _generate_auto_project_id(self) -> str:
        """
        自动生成项目编号
        
        规则:
        - 格式: DJ-YYYY-NNN
        - YYYY = 当前年份
        - NNN = 现有项目中最大编号 + 1 (从父目录扫描)
        
        Returns:
            str: 生成的项目编号, 如 "DJ-2026-006"
        """
        from datetime import datetime as dt
        year = dt.now().strftime("%Y")
        
        # 通过对话框获取已收集的父目录 (优先) 或使用默认值
        parent_dir_str = None
        dialog = self.window()
        if hasattr(dialog, '_project_data') and 'parent_dir' in dialog._project_data:
            parent_dir_str = dialog._project_data.get('parent_dir', '').strip()
        
        if not parent_dir_str:
            parent_dir_str = DEFAULT_PARENT_DIR
        
        parent_dir = Path(parent_dir_str)
        
        max_num = 0
        prefix = f"DJ-{year}-"
        
        # 扫描父目录下已有的 DJ-* 项目目录
        try:
            for item in parent_dir.iterdir():
                if item.is_dir() and item.name.startswith(prefix):
                    num_str = item.name[len(prefix):]
                    if num_str.isdigit():
                        num = int(num_str)
                        if num > max_num:
                            max_num = num
        except Exception:
            pass
        
        new_num = max_num + 1
        return f"{prefix}{new_num:03d}"

    def _on_project_id_changed(self, text: str):
        """项目编号输入变化时实时校验"""
        text = text.strip()
        if not text:
            self._id_validation.setText("")
            self._id_validation.setStyleSheet("font-size: 8pt; margin-left: 4px;")
            return

        if RE_PROJECT_ID.match(text):
            self._id_validation.setText("OK 格式正确")
            self._id_validation.setStyleSheet(
                "font-size: 8pt; margin-left: 4px; color: #4CAF50; font-weight: bold;"
            )
        else:
            self._id_validation.setText(
                "X 格式错误，应为 DJ-YYYY-NNN (如 DJ-2026-006)"
            )
            self._id_validation.setStyleSheet(
                "font-size: 8pt; margin-left: 4px; color: #F44336;"
            )

    def _validate_project_id(self):
        """失去焦点时验证项目编号"""
        self._on_project_id_changed(self._edit_project_id.text())

    def _validate_project_name(self):
        """失去焦点时验证项目名称"""
        name = self._edit_project_name.text().strip()
        if not name:
            self._name_validation.setText("")
            self._name_validation.setStyleSheet("font-size: 8pt; margin-left: 4px;")
        elif len(name) < 2:
            self._name_validation.setText("X 项目名称至少需要2个字符")
            self._name_validation.setStyleSheet(
                "font-size: 8pt; margin-left: 4px; color: #F44336;"
            )
        else:
            self._name_validation.setText("OK")
            self._name_validation.setStyleSheet(
                "font-size: 8pt; margin-left: 4px; color: #4CAF50; font-weight: bold;"
            )

    def _on_io_scale_changed(self, button: QRadioButton):
        """IO规模选择变化"""
        self._io_scale = button.objectName()
        # 发出数据变化信号，供向导更新模板推荐
        self.data_changed.emit(self.collect_data())

    def validate(self) -> tuple:
        """验证所有必填字段"""
        # 验证项目编号
        project_id = self._edit_project_id.text().strip()
        if not project_id:
            return False, "请输入项目编号"
        if not RE_PROJECT_ID.match(project_id):
            return False, (
                f"项目编号格式错误: '{project_id}'\n"
                f"正确格式: DJ-YYYY-NNN (如 DJ-2026-006)"
            )

        # 验证项目名称
        project_name = self._edit_project_name.text().strip()
        if not project_name:
            return False, "请输入项目名称"
        if len(project_name) < 2:
            return False, "项目名称至少需要2个字符"

        # 验证设备类型
        if self._combo_device_type.currentIndex() < 0:
            return False, "请选择设备类型"

        # 验证PLC品牌
        if self._combo_plc_brand.currentIndex() < 0:
            return False, "请选择PLC品牌"

        return True, ""

    def collect_data(self) -> dict:
        """收集所有表单数据"""
        return {
            "project_id": self._edit_project_id.text().strip(),
            "project_name": self._edit_project_name.text().strip(),
            "device_type": self._combo_device_type.currentData(),
            "device_type_display": self._combo_device_type.currentText(),
            "plc_brand": self._combo_plc_brand.currentData(),
            "plc_brand_display": PLC_BRAND_DESCRIPTIONS.get(
                self._combo_plc_brand.currentData(), ""
            ),
            "hmi_brand": self._combo_hmi_brand.currentData(),
            "hmi_brand_display": (
                HMI_BRAND_DESCRIPTIONS.get(self._combo_hmi_brand.currentData(), "")
                if self._combo_hmi_brand.currentData()
                else "--"
            ),
            "io_scale": self._io_scale,
            "owner": self._edit_owner.text().strip(),
            "description": self._edit_description.toPlainText().strip(),
        }

    @property
    def recommended_template(self) -> str:
        """根据IO规模返回推荐的模板ID"""
        for value, _, _, template_id in IO_SCALES:
            if value == self._io_scale:
                return template_id
        return "TPL-SINGLE-PLC-M001"


class TemplateSelectPage(StepPage):
    """Step 3: 选择模板变体"""

    # 信号: 模板选择变化
    template_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_template = "TPL-SINGLE-PLC-M001"
        self._recommended_template = "TPL-SINGLE-PLC-M001"
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # 标题
        title = QLabel("选择项目模板")
        title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #212121;")
        layout.addWidget(title)

        # 推荐提示
        self._recommend_label = QLabel()
        self._recommend_label.setStyleSheet(
            "color: #1976D2; font-size: 10pt; font-weight: bold; "
            "background-color: #E3F2FD; padding: 8px 12px; border-radius: 4px;"
        )
        self._recommend_label.setWordWrap(True)
        layout.addWidget(self._recommend_label)

        # 模板卡片容器
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        # M001 完整版卡片
        m001_card = self._create_template_card(
            TEMPLATE_DETAILS["TPL-SINGLE-PLC-M001"],
            "TPL-SINGLE-PLC-M001",
        )
        cards_layout.addWidget(m001_card)

        # S001 精简版卡片
        s001_card = self._create_template_card(
            TEMPLATE_DETAILS["TPL-SINGLE-PLC-S001"],
            "TPL-SINGLE-PLC-S001",
        )
        cards_layout.addWidget(s001_card)

        layout.addLayout(cards_layout)
        layout.addStretch()

        # 更新初始推荐状态
        self._update_recommendation("TPL-SINGLE-PLC-M001")

    def _create_template_card(self, details: dict, template_id: str) -> QFrame:
        """创建模板选择卡片"""
        card = QFrame()
        card.setCursor(Qt.PointingHandCursor)
        card.setProperty("templateId", template_id)
        card.setFixedSize(320, 280)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)

        # 卡片头部: 图标 + 名称 + 类型标签
        header_layout = QHBoxLayout()

        icon_label = QLabel("\U0001F4E6" if template_id.endswith("M001") else "\U0001F4CB")
        icon_label.setStyleSheet("font-size: 24pt;")
        header_layout.addWidget(icon_label)

        name_layout = QVBoxLayout()
        name_label = QLabel(details["name"])
        name_label.setStyleSheet("font-size: 11pt; font-weight: bold; color: #212121;")
        name_layout.addWidget(name_label)

        type_tag = QLabel(details["display_name"])
        type_tag.setStyleSheet(
            "font-size: 9pt; color: white; background-color: #1976D2; "
            "padding: 2px 8px; border-radius: 10px;"
        )
        type_tag.setAlignment(Qt.AlignCenter)
        type_tag.setFixedWidth(60)
        name_layout.addWidget(type_tag)

        header_layout.addLayout(name_layout)
        header_layout.addStretch()
        card_layout.addLayout(header_layout)

        # 描述
        desc_label = QLabel(details["description"])
        desc_label.setStyleSheet("color: #616161; font-size: 9pt;")
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #E0E0E0;")
        card_layout.addWidget(line)

        # 特性列表
        features_text = "\n".join([f"  • {f}" for f in details["features"]])
        features_label = QLabel(features_text)
        features_label.setStyleSheet("color: #424242; font-size: 9pt;")
        features_label.setWordWrap(True)
        card_layout.addWidget(features_label)

        # 适用场景
        suitable_label = QLabel(f"适用: {details['suitable_for']}")
        suitable_label.setStyleSheet(
            "color: #1976D2; font-size: 9pt; font-weight: bold; "
            "background-color: #E3F2FD; padding: 4px 8px; border-radius: 4px;"
        )
        card_layout.addWidget(suitable_label)

        card_layout.addStretch()

        # 点击事件
        card.mousePressEvent = lambda event, tid=template_id: self._select_template(tid)

        # 引用以便后续样式更新
        card._template_id = template_id

        return card

    def _select_template(self, template_id: str):
        """选择模板"""
        self._selected_template = template_id
        self._update_card_styles()
        self.template_selected.emit(template_id)

    def _update_card_styles(self):
        """更新卡片选中/未选中样式"""
        # 遍历所有卡片更新样式
        parent = self.parent() or self
        for child in self.findChildren(QFrame):
            if hasattr(child, '_template_id'):
                tid = child._template_id
                if tid == self._selected_template:
                    child.setStyleSheet("""
                        QFrame {
                            background-color: #E3F2FD;
                            border: 2px solid #1976D2;
                            border-radius: 8px;
                        }
                    """)
                elif tid == self._recommended_template and tid != self._selected_template:
                    child.setStyleSheet("""
                        QFrame {
                            background-color: #FFF8E1;
                            border: 2px dashed #FFC107;
                            border-radius: 8px;
                        }
                    """)
                else:
                    child.setStyleSheet("""
                        QFrame {
                            background-color: #FAFAFA;
                            border: 1px solid #E0E0E0;
                            border-radius: 8px;
                        }
                    """)
                    child.hover_style_set = False

    def set_recommended_template(self, template_id: str):
        """设置推荐的模板（由BasicInfoPage的IO规模决定）"""
        self._recommended_template = template_id
        # 如果用户还没有手动选择过，则自动选中的推荐模板
        self._selected_template = template_id
        self._update_recommendation(template_id)
        self._update_card_styles()

    def _update_recommendation(self, template_id: str):
        """更新推荐提示文字"""
        details = TEMPLATE_DETAILS.get(template_id, {})
        rec_text = f"根据IO规模推荐: {details.get('display_name', template_id)} - {details.get('description', '')}"
        self._recommend_label.setText(rec_text)

    def validate(self) -> tuple:
        """模板选择总是有效的"""
        return True, ""

    def collect_data(self) -> dict:
        """收集模板选择数据"""
        details = TEMPLATE_DETAILS.get(self._selected_template, {})
        return {
            "template_id": self._selected_template,
            "template_display_name": details.get("display_name", ""),
            "template_description": details.get("description", ""),
            "directory_count": details.get("directory_count", 0),
            "document_count": details.get("document_count", 0),
        }


class ConfirmPage(StepPage):
    """Step 4: 确认并创建"""

    create_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._project_info = {}
        self._is_creating = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 标题
        title = QLabel("项目创建确认")
        title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #212121;")
        layout.addWidget(title)

        # 信息摘要面板
        self._summary_frame = QFrame()
        self._summary_frame.setStyleSheet("""
            QFrame {
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 4px;
            }
        """)
        summary_layout = QVBoxLayout(self._summary_frame)
        summary_layout.setContentsMargins(16, 12, 16, 12)
        summary_layout.setSpacing(6)

        self._summary_content = QLabel()
        self._summary_content.setStyleSheet("""
            QLabel {
                font-family: 'Consolas', 'Microsoft YaHei Mono', monospace;
                font-size: 10pt;
                color: #424242;
                line-height: 1.5;
            }
        """)
        self._summary_content.setWordWrap(True)
        summary_layout.addWidget(self._summary_content)

        layout.addWidget(self._summary_frame)

        # 进度条区域
        progress_container = QWidget()
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 8, 0, 0)

        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        self._progress_bar.setMinimumHeight(24)
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: #F5F5F5;
                text-align: center;
                font-size: 9pt;
                color: #1976D2;
            }
            QProgressBar::chunk {
                background-color: #1976D2;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self._progress_bar)

        self._status_label = QLabel()
        self._status_label.setStyleSheet("color: #616161; font-size: 9pt;")
        self._status_label.setVisible(False)
        progress_layout.addWidget(self._status_label)

        layout.addWidget(progress_container)
        layout.addStretch()

    def update_summary(self, info: dict):
        """更新确认摘要信息"""
        self._project_info = info

        # 构建格式化的摘要文本
        lines = []
        lines.append("<b style='color:#1976D2'>  项目创建确认</b>")
        lines.append("<hr style='border:none;border-top:1px solid #E0E0E0;margin:4px 0;'>")
        lines.append(f"  <b>项目编号:</b> {info.get('project_id', '-')}")
        lines.append(f"  <b>项目名称:</b> {info.get('project_name', '-')}")
        lines.append(f"  <b>设备类型:</b> {info.get('device_type_display', '-')}")
        lines.append(f"  <b>PLC品牌:</b> {info.get('plc_brand_display', '-')}")
        lines.append(f"  <b>HMI品牌:</b> {info.get('hmi_brand_display', '--')}")

        # IO规模显示名
        io_scale_map = {"small": "小型 (<50点)", "medium": "中型 (50-100点)", "large": "大型 (>100点)"}
        lines.append(f"  <b>IO规模:</b> {io_scale_map.get(info.get('io_scale', ''), '-')}")

        tpl_display = info.get('template_display_name', '')
        tpl_id = info.get('template_id', '')
        lines.append(f"  <b>模板:</b> {tpl_id} ({tpl_display})")
        lines.append("")
        lines.append(f"  <b>创建位置:</b>")
        lines.append(f"  <span style='color:#1976D2'>{info.get('full_path', '-')}</span>")
        lines.append("")
        lines.append(f"  <b>将要创建:</b>")
        lines.append(f"  &bull; {info.get('directory_count', 0)} 个标准目录")
        lines.append(f"  &bull; {info.get('document_count', 0)}+ 个文档模板占位文件")
        lines.append(f"  &bull; .plc_project.json 元数据文件")

        self._summary_content.setText("<br>".join(lines))

    def show_progress(self, visible: bool = True):
        """显示/隐藏进度条"""
        self._progress_bar.setVisible(visible)
        self._status_label.setVisible(visible)

    def set_progress(self, value: int, status: str = ""):
        """更新进度"""
        self._progress_bar.setValue(value)
        if status:
            self._status_label.setText(status)

    def set_creating_state(self, is_creating: bool):
        """设置正在创建状态"""
        self._is_creating = is_creating

    def set_status(self, message: str, error: bool = False):
        """设置状态文本"""
        if error:
            self._status_label.setStyleSheet("color: #F44336; font-size: 9pt; font-weight: bold;")
        else:
            self._status_label.setStyleSheet("color: #616161; font-size: 9pt;")
        self._status_label.setText(message)
        self._status_label.setVisible(True)

    def validate(self) -> tuple:
        """确认页总是有效的"""
        return True, ""

    def collect_data(self) -> dict:
        """确认页不额外收集数据"""
        return {}


class NewProjectDialog(QDialog):
    """
    新建项目向导对话框

    提供专业的4步向导界面用于创建符合 TPL-SINGLE-PLC 规范的标准PLC项目。

    步骤流程:
        Step 1: 选择父目录 - 选择项目存储位置
        Step 2: 填写基本信息 - 编号/名称/设备类型/PLC/HMI/IO规模等
        Step 3: 选择模板变体 - M001完整版 或 S001精简版
        Step 4: 确认创建 - 显示摘要并执行创建
    """

    # 总步数
    TOTAL_STEPS = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("\u002B 新建PLC项目向导")
        self.setMinimumSize(720, 580)
        self.setModal(True)
        self.resize(780, 620)

        # 数据存储
        self._project_data = {}
        self._created_project_path = None
        self._current_step = 0

        # 初始化UI
        self._init_ui()
        self._connect_signals()
        self._update_navigation()

    def _init_ui(self):
        """初始化对话框UI布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ===== 顶部步骤指示器 =====
        self._step_indicator = StepIndicator(total_steps=self.TOTAL_STEPS)
        self._step_indicator.setStyleSheet("""
            StepIndicator {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E0E0E0;
                padding: 16px 24px;
            }
        """)
        main_layout.addWidget(self._step_indicator)

        # ===== 中间内容区域 (QStackedWidget) =====
        self._stacked_widget = QStackedWidget()
        self._stacked_widget.setStyleSheet("""
            QStackedWidget {
                background-color: #FFFFFF;
            }
        """)
        main_layout.addWidget(self._stacked_widget, 1)

        # 创建各步骤页面
        self._page_directory = DirectorySelectPage()
        self._page_basic_info = BasicInfoPage()
        self._page_template = TemplateSelectPage()
        self._page_confirm = ConfirmPage()

        self._stacked_widget.addWidget(self._page_directory)   # Index 0
        self._stacked_widget.addWidget(self._page_basic_info)   # Index 1
        self._stacked_widget.addWidget(self._page_template)     # Index 2
        self._stacked_widget.addWidget(self._page_confirm)      # Index 3

        # ===== 底部按钮栏 =====
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet("""
            QFrame {
                background-color: #FAFAFA;
                border-top: 1px solid #E0E0E0;
                padding: 8px 16px;
            }
        """)
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(16, 10, 16, 10)

        # 上一步按钮
        self._btn_prev = QPushButton("\u25C0 上一步")
        self._btn_prev.setFixedHeight(36)
        self._btn_prev.setMinimumWidth(90)
        self._btn_prev.setCursor(Qt.PointingHandCursor)
        self._btn_prev.setEnabled(False)

        # 取消按钮
        self._btn_cancel = QPushButton("取消")
        self._btn_cancel.setFixedHeight(36)
        self._btn_cancel.setMinimumWidth(90)
        self._btn_cancel.setCursor(Qt.PointingHandCursor)

        # 弹簧
        bottom_layout.addStretch()

        # 下一步按钮
        self._btn_next = QPushButton("下一步 \u25B6")
        self._btn_next.setFixedHeight(36)
        self._btn_next.setMinimumWidth(100)
        self._btn_next.setCursor(Qt.PointingHandCursor)
        self._btn_next.setDefault(True)

        # 创建项目按钮 (在最后一步替换"下一步")
        self._btn_create = QPushButton("\u27A4 创建项目")
        self._btn_create.setFixedHeight(36)
        self._btn_create.setMinimumWidth(110)
        self._btn_create.setCursor(Qt.PointingHandCursor)
        self._btn_create.setVisible(False)
        self._btn_create.setDefault(True)

        # 设置按钮样式
        btn_nav_style = """
            QPushButton {
                background-color: #E0E0E0;
                color: #424242;
                border: none;
                border-radius: 4px;
                font-size: 10pt;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #BDBDBD; }
            QPushButton:pressed { background-color: #9E9E9E; }
            QPushButton:disabled { background-color: #F5F5F5; color: #BDBDBD; }
        """

        btn_primary_style = """
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 10pt;
                font-weight: bold;
                padding: 0 24px;
            }
            QPushButton:hover { background-color: #1565C0; }
            QPushButton:pressed { background-color: #0D47A1; }
            QPushButton:disabled { background-color: #BDBDBD; color: #757575; }
        """

        btn_create_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 10pt;
                font-weight: bold;
                padding: 0 24px;
            }
            QPushButton:hover { background-color: #43A047; }
            QPushButton:pressed { background-color: #388E3C; }
            QPushButton:disabled { background-color: #BDBDBD; color: #757575; }
        """

        btn_cancel_style = """
            QPushButton {
                background-color: transparent;
                color: #757575;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                font-size: 10pt;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #F5F5F5; color: #424242; }
        """

        self._btn_prev.setStyleSheet(btn_nav_style)
        self._btn_next.setStyleSheet(btn_primary_style)
        self._btn_create.setStyleSheet(btn_create_style)
        self._btn_cancel.setStyleSheet(btn_cancel_style)

        bottom_layout.addWidget(self._btn_prev)
        bottom_layout.addWidget(self._btn_cancel)
        bottom_layout.addWidget(self._btn_next)
        bottom_layout.addWidget(self._btn_create)

        main_layout.addWidget(bottom_frame)

    def _connect_signals(self):
        """连接信号槽"""
        self._btn_prev.clicked.connect(self._on_previous)
        self._btn_next.clicked.connect(self._on_next)
        self._btn_cancel.clicked.connect(self.reject)
        self._btn_create.clicked.connect(self._on_create)

        # BasicInfoPage 数据变化 -> 更新模板推荐
        self._page_basic_info.data_changed.connect(self._on_basic_info_changed)

        # ConfirmPage 创建请求
        self._page_confirm.create_requested.connect(self._execute_create)

    def _update_navigation(self):
        """更新导航按钮状态"""
        is_first = self._current_step == 0
        is_last = self._current_step == self.TOTAL_STEPS - 1

        self._btn_prev.setEnabled(not is_first)
        self._btn_next.setVisible(not is_last)
        self._btn_create.setVisible(is_last)

        # 更新步骤指示器
        self._step_indicator.set_current_step(self._current_step)

        # 切换到对应页面
        self._stacked_widget.setCurrentIndex(self._current_step)

    def _on_previous(self):
        """上一步"""
        if self._current_step > 0:
            # 先保存当前页数据
            self._save_current_page_data()
            self._current_step -= 1
            self._update_navigation()

    def _on_next(self):
        """下一步 - 包含验证逻辑"""
        current_page = self._stacked_widget.currentWidget()

        # 验证当前页
        is_valid, error_msg = current_page.validate()
        if not is_valid:
            QMessageBox.warning(
                self,
                "\u26A0\uFE0F 输入验证失败",
                error_msg,
                QMessageBox.Ok,
            )
            return

        # 保存当前页数据
        page_data = current_page.collect_data()
        self._project_data.update(page_data)

        # 特殊处理: 从Step 2进入Step 3时更新模板推荐
        if self._current_step == 1:
            recommended = self._page_basic_info.recommended_template
            self._page_template.set_recommended_template(recommended)

        # 特殊处理: 进入Step 4时更新确认摘要
        if self._current_step == 2:
            self._update_confirm_summary()

        if self._current_step < self.TOTAL_STEPS - 1:
            self._current_step += 1
            self._update_navigation()

    def _save_current_page_data(self):
        """保存当前页面的数据"""
        current_page = self._stacked_widget.currentWidget()
        if current_page:
            page_data = current_page.collect_data()
            self._project_data.update(page_data)

    def _on_basic_info_changed(self, data: dict):
        """BasicInfoPage数据变化时的回调"""
        # 可以在这里做额外的联动逻辑
        pass

    def _update_confirm_summary(self):
        """更新确认页的摘要信息"""
        # 合集所有已收集的数据
        summary_info = self._project_data.copy()

        # 构建完整路径
        parent_dir = summary_info.get("parent_dir", "")
        project_id = summary_info.get("project_id", "")
        project_name = summary_info.get("project_name", "")
        if parent_dir and project_id and project_name:
            full_path = str(Path(parent_dir) / f"{project_id}_{project_name}") + "\\"
        else:
            full_path = "[未确定]"
        summary_info["full_path"] = full_path

        self._page_confirm.update_summary(summary_info)

    def _on_create(self):
        """点击创建按钮 - 最终确认并执行创建"""
        reply = QMessageBox.question(
            self,
            "\u2753 确认创建项目",
            f"确定要创建项目吗?\n\n"
            f"项目: {self._project_data.get('project_id', '')}_{self._project_data.get('project_name', '')}\n"
            f"位置: {self._project_data.get('parent_dir', '')}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if reply == QMessageBox.Yes:
            self._execute_create()

    def _execute_create(self):
        """执行实际的项目创建操作"""
        try:
            # 显示进度条
            self._page_confirm.show_progress(True)
            self._page_confirm.set_creating_state(True)
            self._btn_create.setEnabled(False)
            self._btn_prev.setEnabled(False)
            self._btn_cancel.setEnabled(False)

            # 收集最终数据
            self._save_current_page_data()
            all_data = self._project_data.copy()

            # Step 1: 验证数据完整性
            self._page_confirm.set_progress(10, "正在验证数据...")
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()

            project_id = all_data.get("project_id", "").strip()
            project_name = all_data.get("project_name", "").strip()
            parent_dir = all_data.get("parent_dir", "").strip()

            if not all([project_id, project_name, parent_dir]):
                raise ValueError("缺少必要的项目信息")

            # Step 2: 构建项目根目录路径
            self._page_confirm.set_progress(20, "正在构建项目路径...")
            QApplication.processEvents()

            project_root = Path(parent_dir) / f"{project_id}_{project_name}"

            if project_root.exists():
                reply = QMessageBox.question(
                    self,
                    "目录已存在",
                    f"项目目录已存在:\n{project_root}\n\n是否覆盖现有内容?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply != QMessageBox.Yes:
                    self._reset_create_ui()
                    return

            # Step 3: 加载模板
            self._page_confirm.set_progress(30, "正在加载模板...")
            QApplication.processEvents()

            template_id = all_data.get("template_id", "TPL-SINGLE-PLC-M001")
            from src.services.template_service import TemplateService
            template = TemplateService.get_template(template_id)
            if not template:
                raise ValueError(f"模板未找到: {template_id}")

            # Step 4: 创建目录结构
            self._page_confirm.set_progress(40, "正在创建目录结构...")
            QApplication.processEvents()

            structure = template.get("structure", {})
            directories = structure.get("directories", [])
            total_dirs = len(directories)

            self._create_directories_recursive(project_root, directories)

            self._page_confirm.set_progress(
                60 + min(20, total_dirs),
                f"已创建 {total_dirs} 个标准目录..."
            )
            QApplication.processEvents()

            # Step 5: 创建文档占位文件
            self._page_confirm.set_progress(75, "正在生成文档占位文件...")
            QApplication.processEvents()

            doc_count = self._create_placeholder_files(project_root, template_id)

            # Step 6: 创建元数据JSON
            self._page_confirm.set_progress(85, "正在写入项目元数据...")
            QApplication.processEvents()

            metadata = {
                "project_id": project_id,
                "name": project_name,
                "device_type": all_data.get("device_type", ""),
                "device_type_display": all_data.get("device_type_display", ""),
                "plc_brand": all_data.get("plc_brand").value if all_data.get("plc_brand") else "",
                "plc_brand_display": all_data.get("plc_brand_display", ""),
                "hmi_brand": all_data.get("hmi_brand").value if all_data.get("hmi_brand") else "",
                "hmi_brand_display": all_data.get("hmi_brand_display", ""),
                "io_scale": all_data.get("io_scale", ""),
                "template": template_id,
                "template_display_name": all_data.get("template_display_name", ""),
                "owner": all_data.get("owner", ""),
                "description": all_data.get("description", ""),
                "status": "planning",
                "created_at": datetime.now().isoformat(),
                "version": "1.0.0",
            }

            meta_path = project_root / ".plc_project.json"
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            # 完成
            self._page_confirm.set_progress(100, "项目创建完成!")
            QApplication.processEvents()

            self._created_project_path = project_root
            self._project_data["project_path"] = str(project_root)

            logger.info(
                f"项目创建成功: {project_id}_{project_name} @ {project_root}"
            )

            # 延迟关闭，让用户看到完成状态
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(800, self.accept)

        except Exception as e:
            logger.exception(f"项目创建失败: {e}")
            self._page_confirm.set_status(f"创建失败: {e}", error=True)
            QMessageBox.critical(
                self,
                "\u274C 创建失败",
                f"项目创建过程中发生错误:\n\n{str(e)}",
                QMessageBox.Ok,
            )
            self._reset_create_ui()

    def _create_directories_recursive(self, base_path: Path, directories: list):
        """递归创建目录结构"""
        for dir_info in directories:
            dir_name = dir_info.get("name", "")
            if not dir_name:
                continue

            dir_path = base_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)

            # 创建 .gitkeep 保持空目录
            gitkeep = dir_path / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.touch()

            # 递归处理嵌套结构
            if "structure" in dir_info:
                self._create_directories_recursive(dir_path, dir_info["structure"])

    def _create_placeholder_files(self, project_root: Path, template_id: str) -> int:
        """创建文档占位文件"""
        count = 0

        # 根据 template_id 创建不同的占位文件
        if template_id == "TPL-SINGLE-PLC-M001":
            # M001 完整版的占位文件
            placeholder_files = [
                ("00_项目基础信息/README.md", "# 项目基础信息\n\n待补充...\n"),
                ("02_发布说明/RELEASE_NOTES.md", "# 版本发布说明\n\n## V1.0.0\n\n- 初始版本\n"),
                ("05_变量清单/VAR_LIST.md", "# 变量清单\n\n待定义...\n"),
                ("06_IO分配表/IO_ALLOCATION.md", "# IO分配表\n\n待定义...\n"),
                ("07_报警定义/ALARM_CODES.md", "# 报警码定义\n\n待定义...\n"),
                ("08_测试报告/TEST_REPORT.md", "# 测试报告\n\n待补充...\n"),
            ]
        else:
            # S001 精简版的占位文件
            placeholder_files = [
                ("01_Documents/README.md", "# 项目文档\n\n待补充...\n"),
                ("04_Variables/VAR_LIST.md", "# 变量清单\n\n待定义...\n"),
            ]

        for rel_path, content in placeholder_files:
            file_path = project_root / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if not file_path.exists():
                file_path.write_text(content, encoding="utf-8")
                count += 1

        return count

    def _reset_create_ui(self):
        """重置创建UI状态"""
        self._page_confirm.show_progress(False)
        self._page_confirm.set_creating_state(False)
        self._btn_create.setEnabled(True)

        if self._current_step == self.TOTAL_STEPS - 1:
            self._btn_prev.setEnabled(True)
        self._btn_cancel.setEnabled(True)

    def get_project_data(self) -> dict:
        """获取用户填写的完整项目数据"""
        return self._project_data.copy()

    def get_created_project_path(self) -> str:
        """获取创建成功后的项目根路径"""
        return str(self._created_project_path) if self._created_project_path else None

    def keyPressEvent(self, event):
        """键盘事件处理 - 支持Enter/Escape快捷键"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if self._current_step < self.TOTAL_STEPS - 1:
                self._on_next()
            elif self._btn_create.isVisible() and self._btn_create.isEnabled():
                self._on_create()
        elif event.key() == Qt.Key_Escape:
            if not self._page_confirm._is_creating:
                self.reject()
        else:
            super().keyPressEvent(event)
