# -*- coding: utf-8 -*-
"""
变更管理服务

以项目中的变更单目录为权威源，提供基础的扫描和创建能力。
"""
from __future__ import annotations

import re
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
            requests.append(
                ChangeRequest(
                    change_id=change_id,
                    category=category,
                    title=change_id,
                    project_path=project_path,
                    status=ChangeStatus.IN_PROGRESS.value,
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

    @staticmethod
    def _extract_category(change_id: str) -> str:
        """从变更编号中提取分类"""
        parts = change_id.split("-")
        return parts[1] if len(parts) >= 2 else ChangeCategory.DOCU.value

    @staticmethod
    def _get_next_change_index(change_root: Path, category: ChangeCategory) -> int:
        """获取下一个变更序号"""
        pattern = re.compile(rf"CHG-{category.value}-\d{{4}}-(\d{{3}})")
        max_index = 0
        for file_path in change_root.glob(f"CHG-{category.value}-*.md"):
            match = pattern.match(file_path.stem)
            if match:
                max_index = max(max_index, int(match.group(1)))
        return max_index + 1
