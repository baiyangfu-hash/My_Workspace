"""全局功能页 - 模板管理

展示所有可用 Copier 模板，每个模板一张卡片，显示图标/名称/版本/技术栈/使用项目数/描述。
提供"更新项目"按钮，对使用该模板的项目执行 Copier 增量更新。
"""

from __future__ import annotations

import os

import yaml
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from auto_pm.core.project_service import ProjectService
from auto_pm.core.template_service import TemplateService
from auto_pm.logging.logging import setup_logger

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["TemplatePage"]

# 技术栈 → (图标, 中文标签)
_STACK_ICON: dict[str, tuple[str, str]] = {
    "plc": ("🏭", "PLC"),
    "python": ("🐍", "Python"),
    "unknown": ("📦", "未分类"),
}

# 模板名前缀 → 技术栈
_TEMPLATE_STACK: dict[str, str] = {
    "plc": "plc",
    "python": "python",
}

_CARD_STYLE = """
QFrame#TemplateCard {
    border: 1px solid #d0d0d0;
    border-radius: 8px;
    background: #ffffff;
    padding: 4px;
}
QFrame#TemplateCard:hover {
    border: 1px solid #4a90d9;
    background: #f5f9ff;
}
QLabel#cardIcon { font-size: 20px; }
QLabel#cardTitle { font-size: 14px; font-weight: bold; color: #222; }
QLabel#cardMeta { font-size: 11px; color: #888; }
QLabel#cardDesc { font-size: 11px; color: #555; }
"""


def _infer_stack(template_name: str) -> str:
    """根据模板名推断技术栈"""
    name_lower = template_name.lower()
    for prefix, stack in _TEMPLATE_STACK.items():
        if prefix in name_lower:
            return stack
    return "unknown"


def _read_template_description(template_path: str) -> str:
    """从 copier.yml 首行注释提取模板描述

    copier.yml 首行通常为 `# Copier 模板配置 - PLC 标准项目（LSP-907）`，
    提取 `- ` 之后的内容作为描述。
    """
    copier_yml = os.path.join(template_path, "copier.yml")
    try:
        with open(copier_yml, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#"):
                    # 提取 ` - ` 之后的内容
                    if " - " in line:
                        return line.split(" - ", 1)[1].strip()
                    return line.lstrip("# ").strip()
                if line:  # 首个非空非注释行，停止
                    break
    except OSError as e:
        log.warning("读取 copier.yml 失败: %s: %s", template_path, e)
    return ""


def _read_template_version(template_path: str) -> str:
    """读取模板版本（copier.yml 无版本字段时返回默认 v1.0）"""
    copier_yml = os.path.join(template_path, "copier.yml")
    try:
        with open(copier_yml, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        version = data.get("_version", "")
        if version:
            return str(version)
    except (OSError, yaml.YAMLError) as e:
        log.warning("解析 copier.yml 版本失败: %s: %s", template_path, e)
    return "v1.0"


class TemplateCard(QFrame):
    """单个模板卡片

    展示模板图标/名称/版本/技术栈/使用项目数/描述，提供"更新项目"按钮。
    """

    updateRequested = Signal(str)

    def __init__(
        self,
        template_name: str,
        stack: str,
        version: str,
        usage_count: int,
        description: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._template_name = template_name
        self._stack = stack
        self.setObjectName("TemplateCard")
        self.setStyleSheet(_CARD_STYLE)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._build_ui(version, usage_count, description)

    def _build_ui(self, version: str, usage_count: int, description: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # 第一行：图标 + 模板名称（加粗）
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        icon, stack_label = _STACK_ICON.get(self._stack, _STACK_ICON["unknown"])
        self._icon_label = QLabel(icon)
        self._icon_label.setObjectName("cardIcon")
        top_row.addWidget(self._icon_label)

        self._title_label = QLabel(self._template_name)
        self._title_label.setObjectName("cardTitle")
        top_row.addWidget(self._title_label)
        top_row.addStretch(1)
        layout.addLayout(top_row)

        # 第二行：版本 | 技术栈 | 使用项目数
        self._meta_label = QLabel(
            f"{version} | 技术栈: {stack_label} | 使用项目: {usage_count}"
        )
        self._meta_label.setObjectName("cardMeta")
        layout.addWidget(self._meta_label)

        # 第三行：描述
        self._desc_label = QLabel(description or "—")
        self._desc_label.setObjectName("cardDesc")
        self._desc_label.setWordWrap(True)
        layout.addWidget(self._desc_label)

        # 第四行：更新项目按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self._update_btn = QPushButton("更新项目")
        self._update_btn.clicked.connect(self._on_update_clicked)
        btn_row.addWidget(self._update_btn)
        layout.addLayout(btn_row)

    def _on_update_clicked(self) -> None:
        self.updateRequested.emit(self._template_name)

    @property
    def template_name(self) -> str:
        return self._template_name

    @property
    def update_button(self) -> QPushButton:
        return self._update_btn


class TemplatePage(QWidget):
    """模板管理页

    列出所有可用 Copier 模板，每个模板一张卡片。
    点击"更新项目"按钮对该模板关联的所有项目执行 Copier 增量更新。
    """

    def __init__(
        self,
        template_service: TemplateService,
        project_service: ProjectService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._template_service = template_service
        self._project_service = project_service
        self._cards: dict[str, TemplateCard] = {}
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        title = QLabel("模板管理")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #222;")
        layout.addWidget(title)

        # 滚动区域包裹模板列表
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(10)
        self._list_layout.addStretch(1)

        scroll.setWidget(self._list_container)
        layout.addWidget(scroll, 1)

        # 空状态提示
        self._empty_hint = QLabel("暂无可用模板")
        self._empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_hint.setStyleSheet("color: #999; font-size: 14px;")
        self._empty_hint.setVisible(False)
        layout.addWidget(self._empty_hint)

    def refresh(self) -> None:
        """重新加载模板列表"""
        self._load_templates()

    def _load_templates(self) -> None:
        """加载模板列表并渲染卡片"""
        # 清空旧卡片
        for card in self._cards.values():
            card.deleteLater()
        self._cards.clear()

        templates = self._template_service.list_templates()
        if not templates:
            self._empty_hint.setVisible(True)
            return
        self._empty_hint.setVisible(False)

        # 统计各模板使用项目数
        usage_counts = self._count_template_usage()

        for name in templates:
            try:
                template_path = self._template_service.get_template_path(name)
            except FileNotFoundError:
                log.warning("模板路径不存在，跳过: %s", name)
                continue

            stack = _infer_stack(name)
            version = _read_template_version(template_path)
            description = _read_template_description(template_path)
            usage = usage_counts.get(name, 0)

            card = TemplateCard(
                template_name=name,
                stack=stack,
                version=version,
                usage_count=usage,
                description=description,
            )
            card.updateRequested.connect(self._on_update_template)
            # 插入到 stretch 之前
            self._list_layout.insertWidget(self._list_layout.count() - 1, card)
            self._cards[name] = card

    def _count_template_usage(self) -> dict[str, int]:
        """统计每个模板的使用项目数（按 _src_path 匹配）

        Returns:
            模板名 → 使用项目数
        """
        counts: dict[str, int] = {}
        try:
            projects = self._project_service.list_projects_cached()
        except Exception as e:
            log.warning("加载项目列表失败，使用项目数将全部为 0: %s", e)
            return counts

        for proj in projects:
            src_path = str(proj.extra.get("_src_path", ""))
            if not src_path:
                continue
            # src_path 形如 "templates/plc-standard"，提取末尾模板名
            template_name = os.path.basename(src_path)
            if template_name:
                counts[template_name] = counts.get(template_name, 0) + 1
        return counts

    def _on_update_template(self, template_name: str) -> None:
        """更新使用该模板的所有项目

        Args:
            template_name: 模板名称
        """
        # 找出使用该模板的所有项目
        projects_to_update: list[str] = []
        try:
            projects = self._project_service.list_projects_cached()
        except Exception as e:
            QMessageBox.warning(self, "更新项目", f"加载项目列表失败：{e}")
            return

        for proj in projects:
            src_path = str(proj.extra.get("_src_path", ""))
            if not src_path:
                continue
            if os.path.basename(src_path) == template_name:
                projects_to_update.append(proj.path)

        if not projects_to_update:
            QMessageBox.information(
                self,
                "更新项目",
                f"没有项目使用模板 {template_name}，无需更新。",
            )
            return

        reply = QMessageBox.question(
            self,
            "更新项目",
            f"将对 {len(projects_to_update)} 个使用模板 {template_name} 的项目执行增量更新，\n"
            "是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        success = 0
        failed = 0
        for project_path in projects_to_update:
            try:
                self._template_service.update_template(project_path)
                success += 1
                log.info("项目已更新: %s", project_path)
            except Exception as e:
                failed += 1
                log.error("更新项目失败: %s: %s", project_path, e)

        QMessageBox.information(
            self,
            "更新完成",
            f"更新完成：成功 {success} 个，失败 {failed} 个。",
        )
        self.refresh()
