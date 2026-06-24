"""全局功能页 - 系统设置

展示工作空间路径、扫描深度、数据库缓存统计，提供清除缓存/重建索引功能。
"""

from __future__ import annotations

import os

from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from auto_pm.change.change_service import ChangeService
from auto_pm.core.project_service import ProjectService
from auto_pm.db.connection import DatabaseManager
from auto_pm.logging.logging import setup_logger

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["SettingsPage"]


class SettingsPage(QWidget):
    """系统设置页

    通用设置：工作空间路径、扫描深度。
    数据库：缓存路径、项目/变更记录数、上次同步时间、清除缓存/重建索引。
    """

    def __init__(
        self,
        project_service: ProjectService,
        change_service: ChangeService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._project_service = project_service
        self._change_service = change_service
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        title = QLabel("系统设置")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #222;")
        layout.addWidget(title)

        layout.addWidget(self._build_general_group())
        layout.addWidget(self._build_db_group())
        layout.addStretch(1)

    def _build_general_group(self) -> QGroupBox:
        """通用设置区"""
        group = QGroupBox("通用")
        v = QVBoxLayout(group)
        v.setSpacing(8)

        # 工作空间路径
        ws_row = QHBoxLayout()
        ws_row.addWidget(QLabel("工作空间路径:"))
        self._workspace_edit = QLineEdit(self._project_service.workspace_root)
        self._workspace_edit.setReadOnly(True)
        ws_row.addWidget(self._workspace_edit, 1)

        browse_btn = QPushButton("📂")
        browse_btn.setToolTip("选择工作空间目录")
        browse_btn.setFixedWidth(32)
        browse_btn.clicked.connect(self._on_browse_workspace)
        ws_row.addWidget(browse_btn)
        v.addLayout(ws_row)

        # 扫描深度
        depth_row = QHBoxLayout()
        depth_row.addWidget(QLabel("扫描深度:"))
        self._depth_spin = QSpinBox()
        self._depth_spin.setRange(1, 10)
        self._depth_spin.setValue(4)
        depth_row.addWidget(self._depth_spin)
        depth_row.addStretch(1)
        v.addLayout(depth_row)

        return group

    def _build_db_group(self) -> QGroupBox:
        """数据库区"""
        group = QGroupBox("数据库")
        v = QVBoxLayout(group)
        v.setSpacing(8)

        # 缓存路径
        self._db_path_label = QLabel("缓存路径: —")
        self._db_path_label.setWordWrap(True)
        v.addWidget(self._db_path_label)

        # 项目记录数
        self._project_count_label = QLabel("项目记录: 0 条")
        v.addWidget(self._project_count_label)

        # 变更记录数
        self._change_count_label = QLabel("变更记录: 0 条")
        v.addWidget(self._change_count_label)

        # 上次同步时间
        self._last_sync_label = QLabel("上次同步: —")
        v.addWidget(self._last_sync_label)

        # 操作按钮
        btn_row = QHBoxLayout()
        self._clear_cache_btn = QPushButton("清除缓存")
        self._clear_cache_btn.clicked.connect(self._on_clear_cache)
        btn_row.addWidget(self._clear_cache_btn)

        self._rebuild_btn = QPushButton("重建索引")
        self._rebuild_btn.clicked.connect(self._on_rebuild_index)
        btn_row.addWidget(self._rebuild_btn)

        btn_row.addStretch(1)
        v.addLayout(btn_row)

        return group

    # ── 数据加载 ──────────────────────────────────────────

    def refresh(self) -> None:
        """重新加载统计"""
        self._load_db_stats()

    def _load_db_stats(self) -> None:
        """加载数据库统计信息"""
        db = self._project_service.db
        if db is None:
            self._db_path_label.setText("缓存路径: 未连接")
            self._project_count_label.setText("项目记录: —")
            self._change_count_label.setText("变更记录: —")
            self._last_sync_label.setText("上次同步: —")
            return

        # 缓存路径
        self._db_path_label.setText(f"缓存路径: {db.db_path}")

        # 项目记录数
        project_count = 0
        try:
            if self._project_service._repo is not None:
                project_count = self._project_service._repo.count()
            else:
                project_count = len(self._project_service.list_projects_cached())
        except Exception as e:
            log.warning("统计项目数失败: %s", e)
        self._project_count_label.setText(f"项目记录: {project_count} 条")

        # 变更记录数
        change_count = 0
        try:
            change_count = len(self._change_service.list_all_changes())
        except Exception as e:
            log.warning("统计变更数失败: %s", e)
        self._change_count_label.setText(f"变更记录: {change_count} 条")

        # 上次同步时间
        self._last_sync_label.setText(f"上次同步: {self._get_last_sync_time(db)}")

    def _get_last_sync_time(self, db: DatabaseManager) -> str:
        """获取上次同步时间

        M3-Iter5：通过 ProjectService.get_last_sync_time() 访问，
        不再直接使用 ScanLogRepository（保持分层架构）。

        Args:
            db: DatabaseManager 实例

        Returns:
            格式化的同步时间 YYYY-MM-DD HH:MM，无记录时返回 '—'
        """
        try:
            from auto_pm.core.project_service import ProjectService

            svc = ProjectService(self._project_service.workspace_root, db=db)
            return svc.get_last_sync_time()
        except Exception as e:
            log.warning("获取扫描时间失败: %s", e)
            return "—"

    # ── 交互 ─────────────────────────────────────────────

    def _on_browse_workspace(self) -> None:
        """选择工作空间目录（仅展示，不实际切换）"""
        current = self._workspace_edit.text() or ""
        path = QFileDialog.getExistingDirectory(
            self, "选择工作空间目录", current
        )
        if path:
            self._workspace_edit.setText(path)

    def _on_clear_cache(self) -> None:
        """清除缓存（删除 DB 文件）"""
        db = self._project_service.db
        if db is None:
            QMessageBox.information(self, "清除缓存", "DB 未初始化，无需清除。")
            return

        reply = QMessageBox.question(
            self,
            "清除缓存",
            f"将删除缓存文件：{db.db_path}\n删除后需重建索引恢复数据，是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # 关闭现有连接后删除文件
            db_path = db.db_path
            # 删除 DB 文件及 WAL/SHM 辅助文件
            for suffix in ("", "-wal", "-shm"):
                file_path = db_path + suffix
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    log.info("已删除缓存文件: %s", file_path)

            # 重新初始化 schema
            db.init_schema()
            QMessageBox.information(self, "清除缓存", "缓存已清除并重新初始化。")
            self.refresh()
        except Exception as e:
            log.error("清除缓存失败: %s", e)
            QMessageBox.warning(self, "清除缓存", f"清除缓存失败：{e}")

    def _on_rebuild_index(self) -> None:
        """重建索引（强制全量扫描同步到 DB 缓存）"""
        db = self._project_service.db
        if db is None:
            QMessageBox.warning(self, "重建索引", "DB 未初始化，无法重建索引。")
            return

        reply = QMessageBox.question(
            self,
            "重建索引",
            "将强制全量扫描工作空间并重建索引，可能耗时较长，是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            result = self._project_service.sync_to_cache(force_full=True)
            projects_found = result.get("projects_found", 0)
            changes_found = result.get("changes_found", 0)
            QMessageBox.information(
                self,
                "重建索引",
                f"重建完成：发现 {projects_found} 个项目，{changes_found} 条变更单。",
            )
            self.refresh()
        except Exception as e:
            log.error("重建索引失败: %s", e)
            QMessageBox.warning(self, "重建索引", f"重建索引失败：{e}")

    # ── 属性（便于测试访问） ─────────────────────────────

    @property
    def workspace_edit(self) -> QLineEdit:
        return self._workspace_edit

    @property
    def depth_spin(self) -> QSpinBox:
        return self._depth_spin

    @property
    def clear_cache_button(self) -> QPushButton:
        return self._clear_cache_btn

    @property
    def rebuild_button(self) -> QPushButton:
        return self._rebuild_btn

    @property
    def db_path_label(self) -> QLabel:
        return self._db_path_label

    @property
    def project_count_label(self) -> QLabel:
        return self._project_count_label

    @property
    def change_count_label(self) -> QLabel:
        return self._change_count_label

    @property
    def last_sync_label(self) -> QLabel:
        return self._last_sync_label
