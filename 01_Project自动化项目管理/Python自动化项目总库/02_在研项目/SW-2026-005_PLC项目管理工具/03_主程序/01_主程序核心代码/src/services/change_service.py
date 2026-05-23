# -*- coding: utf-8 -*-
"""
变更管理服务

以项目中的变更单目录为权威源，提供扫描、创建、状态流转和审核能力。
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from src.core.constants import ChangeCategory, ChangeStatus
from src.models.change_request import ChangeRequest
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ChangeService:
    """基础变更管理服务"""

    CHANGE_ROOT = Path("00_项目管理") / "04_变更管理" / "01_变更单"

    @classmethod
    def list_change_requests(cls, project_path: str) -> List[ChangeRequest]:
        """扫描项目中的变更单"""
        root = Path(project_path) / cls.CHANGE_ROOT
        if not root.exists():
            return []

        requests: List[ChangeRequest] = []
        for file_path in root.rglob("CHG-*.md"):
            change_id = file_path.stem
            category = cls._extract_category(change_id)
            status = cls._read_status(file_path)
            requests.append(
                ChangeRequest(
                    change_id=change_id,
                    category=category,
                    title=change_id,
                    project_path=project_path,
                    status=status,
                    affected_paths=[str(file_path.relative_to(Path(project_path)))],
                )
            )

        return sorted(requests, key=lambda item: item.change_id)

    @classmethod
    def create_change_request(
        cls,
        project_path: str,
        category: ChangeCategory,
        title: str,
        description: str = "",
    ) -> Tuple[Optional[ChangeRequest], Optional[str]]:
        """创建基础变更单"""
        change_root = Path(project_path) / cls.CHANGE_ROOT / f"CHG-{category.value}"
        change_root.mkdir(parents=True, exist_ok=True)

        next_index = cls._get_next_change_index(change_root, category)
        change_id = f"CHG-{category.value}-2026-{next_index:03d}"
        file_path = change_root / f"{change_id}.md"

        content = (
            f"# {change_id}\n\n"
            f"## 标题\n{title}\n\n"
            f"## 描述\n{description or '待补充'}\n\n"
            f"## 状态\n{ChangeStatus.DRAFT.value}\n"
        )
        file_path.write_text(content, encoding="utf-8")

        request = ChangeRequest(
            change_id=change_id,
            category=category.value,
            title=title,
            project_path=project_path,
            status=ChangeStatus.DRAFT.value,
            description=description,
            affected_paths=[str(file_path.relative_to(Path(project_path)))],
        )
        logger.info(f"变更单已创建: {change_id}")
        return request, None

    @classmethod
    def update_status(
        cls, project_path: str, change_id: str, new_status: ChangeStatus
    ) -> bool:
        """
        更新变更单状态

        Args:
            project_path: 项目根目录
            change_id: 变更单编号
            new_status: 目标状态

        Returns:
            True=更新成功, False=更新失败(无效转换/文件不存在)
        """
        file_path = cls._find_change_file(project_path, change_id)
        if not file_path:
            logger.warning(f"变更单不存在: {change_id}")
            return False

        current_status = cls._read_status(file_path)
        current_enum = cls._status_from_value(current_status)

        if current_enum is None:
            logger.warning(f"无法解析当前状态: {current_status}")
            return False

        valid_next = ChangeStatus.valid_transitions(current_enum)
        if new_status not in valid_next:
            logger.warning(
                f"无效状态转换: {current_enum.value} -> {new_status.value}"
            )
            return False

        cls._write_status(file_path, new_status.value)
        logger.info(f"变更单状态已更新: {change_id} -> {new_status.value}")
        return True

    @classmethod
    def approve_change_request(
        cls, project_path: str, change_id: str, approver: str = ""
    ) -> bool:
        """
        审核通过变更单

        将状态从 REVIEW 转为 APPROVED，并记录审核人。

        Args:
            project_path: 项目根目录
            change_id: 变更单编号
            approver: 审核人

        Returns:
            True=审核成功, False=审核失败
        """
        file_path = cls._find_change_file(project_path, change_id)
        if not file_path:
            logger.warning(f"变更单不存在: {change_id}")
            return False

        current_status = cls._read_status(file_path)
        current_enum = cls._status_from_value(current_status)

        if current_enum is None:
            logger.warning(f"无法解析当前状态: {current_status}")
            return False

        if ChangeStatus.APPROVED not in ChangeStatus.valid_transitions(current_enum):
            logger.warning(f"变更单不可审核: {change_id} (当前: {current_status})")
            return False

        cls._write_status(file_path, ChangeStatus.APPROVED.value)

        if approver:
            try:
                content = file_path.read_text(encoding="utf-8")
                approval_line = (
                    f"\n## 审核\n"
                    f"- 审核人: {approver}\n"
                    f"- 审核时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"- 审核结果: 通过\n"
                )
                content += approval_line
                file_path.write_text(content, encoding="utf-8")
            except Exception as e:
                logger.warning(f"写入审核信息失败: {e}")

        logger.info(f"变更单已审核通过: {change_id} (审核人: {approver or '未指定'})")
        return True

    @classmethod
    def _find_change_file(cls, project_path: str, change_id: str) -> Optional[Path]:
        root = Path(project_path) / cls.CHANGE_ROOT
        if not root.exists():
            return None
        for fp in root.rglob(f"{change_id}.md"):
            return fp
        return None

    @staticmethod
    def _read_status(file_path: Path) -> str:
        try:
            content = file_path.read_text(encoding="utf-8")
            in_status_section = False
            for line in content.splitlines():
                stripped = line.strip()
                if stripped == "## 状态":
                    in_status_section = True
                    continue
                if in_status_section:
                    if stripped.startswith("## "):
                        break
                    if stripped:
                        return stripped
        except Exception:
            pass
        return ChangeStatus.DRAFT.value

    @staticmethod
    def _write_status(file_path: Path, new_status: str):
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            in_status_section = False
            for i, line in enumerate(lines):
                if line.strip() == "## 状态":
                    in_status_section = True
                    continue
                if in_status_section and line.strip() and not line.startswith("#"):
                    lines[i] = new_status
                    break
                if in_status_section and line.startswith("## "):
                    break
            file_path.write_text("\n".join(lines), encoding="utf-8")
        except Exception as e:
            logger.error(f"写入状态失败: {e}")

    @staticmethod
    def _status_from_value(value: str) -> Optional[ChangeStatus]:
        for status in ChangeStatus:
            if status.value == value:
                return status
        return None

    @staticmethod
    def _extract_category(change_id: str) -> str:
        parts = change_id.split("-")
        return parts[1] if len(parts) >= 2 else ChangeCategory.DOCU.value

    @staticmethod
    def _get_next_change_index(change_root: Path, category: ChangeCategory) -> int:
        pattern = re.compile(rf"CHG-{category.value}-\d{{4}}-(\d{{3}})")
        max_index = 0
        for file_path in change_root.glob(f"CHG-{category.value}-*.md"):
            match = pattern.match(file_path.stem)
            if match:
                max_index = max(max_index, int(match.group(1)))
        return max_index + 1
