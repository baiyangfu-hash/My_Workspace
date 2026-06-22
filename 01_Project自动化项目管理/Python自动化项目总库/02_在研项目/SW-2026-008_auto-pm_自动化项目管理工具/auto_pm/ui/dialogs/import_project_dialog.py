"""导入项目对话框

选择已有项目目录导入到工作空间的 02_在研项目/ 下。
自动检测标志文件（.copier-answers.yml/.plc.json/PM_SESSION_*.md），
缺少 .copier-answers.yml 时可补全元数据。
成功后发射 projectImported(project_id) 信号。
"""

from __future__ import annotations

import os
import shutil

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from auto_pm.core.constants import BUSINESS_LINE_OPTIONS
from auto_pm.core.paths import WORKSPACE_PROJECTS_SUBDIR
from auto_pm.core.project_service import ProjectService
from auto_pm.logging.logging import setup_logger
from auto_pm.ui.project_list.project_card import extract_business_line

log = setup_logger(log_level="INFO", app_name="auto_pm")

# 项目目录子路径
# M3-Iter6: 从 core.paths 读取，消除硬编码
_PROJECTS_SUBDIR = WORKSPACE_PROJECTS_SUBDIR

# 业务线选项：(value, label)（M3-Iter7: 从 core.constants 读取）
_BUSINESS_LINE_OPTIONS = BUSINESS_LINE_OPTIONS

_DIALOG_STYLE = """
QDialog { background: #fafafa; }
QLabel#dialogTitle { font-size: 16px; font-weight: bold; color: #222; }
QLabel#pathDisplay {
    font-size: 12px; color: #333;
    background: #ecf0f1; padding: 6px 10px;
    border-radius: 4px; border: 1px solid #d0d0d0;
}
QLabel#detectStatus { font-size: 12px; color: #555; }
QLabel#detectOk { font-size: 12px; color: #27ae60; }
QLabel#detectWarn { font-size: 12px; color: #e67e22; }
QPushButton#retrofitBtn {
    padding: 4px 12px; border: 1px solid #e67e22;
    border-radius: 4px; background: #fef9f0; color: #e67e22;
    font-size: 12px;
}
QPushButton#retrofitBtn:hover { background: #fdf0e0; }
QPushButton#retrofitBtn:disabled { color: #bdc3c7; border-color: #ddd; background: #f5f5f5; }
"""


class ImportProjectDialog(QDialog):
    """导入项目对话框

    选择外部项目目录，复制到工作空间的 02_在研项目/ 下。
    成功后发射 projectImported(project_id)。
    """

    projectImported = Signal(str)

    def __init__(self, workspace_root: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._workspace_root = workspace_root
        self._source_path: str = ""
        self._build_ui()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle("导入项目")
        self.setMinimumWidth(560)
        self.setStyleSheet(_DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title = QLabel("导入已有项目")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        # 目录选择行
        dir_row = QHBoxLayout()
        dir_row.setSpacing(8)
        self._path_edit = QLineEdit()
        self._path_edit.setReadOnly(True)
        self._path_edit.setPlaceholderText("点击右侧按钮选择项目目录...")
        dir_row.addWidget(self._path_edit, 1)
        select_btn = QPushButton("选择目录")
        select_btn.clicked.connect(self._on_select_dir)
        dir_row.addWidget(select_btn)
        layout.addLayout(dir_row)

        # 检测状态
        self._detect_label = QLabel("尚未选择目录")
        self._detect_label.setObjectName("detectStatus")
        layout.addWidget(self._detect_label)

        # 补全元数据按钮
        self._retrofit_btn = QPushButton("补全元数据（创建 .copier-answers.yml）")
        self._retrofit_btn.setObjectName("retrofitBtn")
        self._retrofit_btn.setEnabled(False)
        self._retrofit_btn.clicked.connect(self._on_retrofit)
        layout.addWidget(self._retrofit_btn)

        # 项目信息表单
        form = QFormLayout()
        form.setSpacing(6)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._id_label = QLabel("—")
        form.addRow("项目编号:", self._id_label)

        self._name_label = QLabel("—")
        form.addRow("项目名称:", self._name_label)

        self._bl_combo = QComboBox()
        for value, label in _BUSINESS_LINE_OPTIONS:
            self._bl_combo.addItem(label, value)
        form.addRow("业务线:", self._bl_combo)

        layout.addLayout(form)

        # 导入路径预览
        self._dest_label = QLabel()
        self._dest_label.setObjectName("pathDisplay")
        self._dest_label.setWordWrap(True)
        self._dest_label.setText(f"导入路径: {_PROJECTS_SUBDIR}/<目录名>/")
        layout.addWidget(self._dest_label)

        # 按钮组
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._button_box.button(QDialogButtonBox.StandardButton.Ok).setText("导入")
        self._button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
        self._button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self._button_box.accepted.connect(self._on_accept)
        self._button_box.rejected.connect(self.reject)
        layout.addWidget(self._button_box)

    # ── 目录选择与检测 ────────────────────────────────────

    def _on_select_dir(self) -> None:
        """打开目录选择对话框"""
        path = QFileDialog.getExistingDirectory(
            self, "选择要导入的项目目录", ""
        )
        if not path:
            return
        self._source_path = path
        self._path_edit.setText(path)
        self._detect_project()

    def _detect_project(self) -> None:
        """检测选中目录的标志文件并更新 UI"""
        if not self._source_path or not os.path.isdir(self._source_path):
            return

        has_copier = os.path.isfile(
            os.path.join(self._source_path, ProjectService.COPIER_ANSWERS_FILE)
        )
        has_plc = os.path.isfile(
            os.path.join(self._source_path, ProjectService.PLC_JSON_FILE)
        )
        has_session = self._has_pm_session(self._source_path)

        markers: list[str] = []
        if has_copier:
            markers.append(".copier-answers.yml")
        if has_plc:
            markers.append(".plc.json")
        if has_session:
            markers.append("PM_SESSION_*.md")

        if markers:
            self._detect_label.setText(
                f"检测到标志文件: {', '.join(markers)}"
            )
            self._detect_label.setObjectName("detectOk")
        else:
            self._detect_label.setText(
                "未检测到标志文件（导入后可补全元数据）"
            )
            self._detect_label.setObjectName("detectWarn")

        self._detect_label.style().unpolish(self._detect_label)
        self._detect_label.style().polish(self._detect_label)

        # 补全按钮：缺少 .copier-answers.yml 时启用
        self._retrofit_btn.setEnabled(not has_copier)

        # 推断项目编号和名称
        project_id = ProjectService._extract_id_from_dirname(self._source_path)
        project_name = os.path.basename(self._source_path)
        self._id_label.setText(project_id)
        self._name_label.setText(project_name)

        # 联动业务线
        bl = extract_business_line(project_id)
        for i in range(self._bl_combo.count()):
            if self._bl_combo.itemData(i) == bl:
                self._bl_combo.setCurrentIndex(i)
                break

        # 更新导入路径预览
        dirname = os.path.basename(self._source_path)
        self._dest_label.setText(
            f"导入路径: {os.path.join(_PROJECTS_SUBDIR, dirname)}/"
        )

        self._button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)

    @staticmethod
    def _has_pm_session(path: str) -> bool:
        """检查目录下是否存在 PM_SESSION_*.md 文件"""
        try:
            for entry in os.listdir(path):
                if entry.startswith(ProjectService.PM_SESSION_PREFIX) and entry.endswith(
                    ".md"
                ):
                    return True
        except OSError:
            pass
        return False

    # ── 补全元数据 ────────────────────────────────────────

    def _on_retrofit(self) -> None:
        """补全 .copier-answers.yml 元数据文件"""
        if not self._source_path:
            return

        try:
            svc = ProjectService(self._workspace_root)
            svc.retrofit_project_by_path(self._source_path)
            QMessageBox.information(
                self,
                "补全成功",
                f"已在源目录创建 .copier-answers.yml:\n{self._source_path}",
            )
            self._retrofit_btn.setEnabled(False)
            self._detect_project()
        except FileExistsError:
            QMessageBox.information(
                self, "已存在", ".copier-answers.yml 已存在，无需补全。"
            )
            self._retrofit_btn.setEnabled(False)
        except Exception as e:
            log.error("补全元数据失败: %s", e, exc_info=True)
            QMessageBox.critical(self, "补全失败", f"补全元数据时出错:\n{e}")

    # ── 导入 ──────────────────────────────────────────────

    def _on_accept(self) -> None:
        """导入按钮：复制目录到工作空间"""
        if not self._source_path:
            return

        dirname = os.path.basename(self._source_path)
        dest_path = os.path.join(
            self._workspace_root, _PROJECTS_SUBDIR, dirname
        )

        if os.path.exists(dest_path):
            QMessageBox.critical(
                self, "路径已存在", f"目标路径已存在:\n{dest_path}"
            )
            return

        try:
            os.makedirs(
                os.path.join(self._workspace_root, _PROJECTS_SUBDIR),
                exist_ok=True,
            )
            shutil.copytree(self._source_path, dest_path)
            log.info("项目已导入: %s -> %s", self._source_path, dest_path)

            # 导入后补全 .copier-answers.yml（如果仍缺少）
            try:
                svc = ProjectService(self._workspace_root)
                svc.retrofit_project_by_path(dest_path)
            except FileExistsError:
                pass  # 已有 .copier-answers.yml，正常
            except Exception as e:
                log.warning("导入后补全元数据失败: %s", e)

            project_id = ProjectService._extract_id_from_dirname(dest_path)
            self.projectImported.emit(project_id)
            self.accept()
        except Exception as e:
            log.error("导入项目失败: %s", e, exc_info=True)
            QMessageBox.critical(self, "导入失败", f"导入项目时出错:\n{e}")
