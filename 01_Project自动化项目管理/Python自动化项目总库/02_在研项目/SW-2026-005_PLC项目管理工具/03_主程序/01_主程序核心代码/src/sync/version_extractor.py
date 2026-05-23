# -*- coding: utf-8 -*-
"""
版本号提取器

从 .scl 文件头和 PRD(.md) 文档中提取版本号。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Tuple

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class VersionExtractor:
    """版本号提取器"""

    RE_SCL_VERSION_LINE = re.compile(
        r'版本号[：:]\s*V(\d+)\.(\d+)\.(\d+)'
    )
    RE_SCL_CHANGELOG_VERSION = re.compile(
        r'^\s*(?://|\(\*)\s*V(\d+)\.(\d+)\.(\d+)\s*[\(（:]'
    )
    RE_SCL_FILEHEADER_VERSION = re.compile(
        r'(?://|\*\s+).*\s+[\(（]V(\d+)\.(\d+)\.(\d+)[\)）]'
    )
    RE_FILENAME_VERSION = re.compile(
        r'[Vv](\d+)\.(\d+)\.(\d+)'
    )
    RE_MD_VERSION_LINE = re.compile(
        r'>\s*(?:版本|Version)[：:]\s*V(\d+)\.(\d+)\.(\d+)'
    )
    RE_MD_TABLE_VERSION = re.compile(
        r'\*\*(?:文档)?版本\*\*\s*\|\s*V(\d+)\.(\d+)\.(\d+)'
    )

    @classmethod
    def extract_scl_version(cls, file_path: str) -> Optional[str]:
        """
        从 .scl 文件头提取版本号

        策略:
        1. 匹配 "版本号：Vx.y.z" 格式（(* *)注释块，PickPlace/Conveyor样式）
        2. 匹配 OB1 样式：取 changelog 第一条最新版本
        3. 匹配文件头行 "(Vx.y.z)" 格式
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"文件不存在: {file_path}")
                return None

            content = path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()

            version = cls._try_version_label(lines[:30])
            if version:
                return version

            version = cls._try_changelog_first(lines[:60])
            if version:
                return version

            version = cls._try_fileheader(lines[:5])
            if version:
                return version

            logger.debug(f"未找到版本号: {file_path}")
            return None

        except Exception as e:
            logger.warning(f"版本提取失败 {file_path}: {e}")
            return None

    @classmethod
    def _try_version_label(cls, lines: list) -> Optional[str]:
        """匹配 '版本号：Vx.y.z' 格式"""
        for line in lines:
            m = cls.RE_SCL_VERSION_LINE.search(line)
            if m:
                return f"V{m.group(1)}.{m.group(2)}.{m.group(3)}"
        return None

    @classmethod
    def _try_changelog_first(cls, lines: list) -> Optional[str]:
        """匹配 changelog 区域第一条版本号（即最新版本）"""
        for line in lines:
            m = cls.RE_SCL_CHANGELOG_VERSION.match(line.strip())
            if m:
                return f"V{m.group(1)}.{m.group(2)}.{m.group(3)}"
        return None

    @classmethod
    def _try_fileheader(cls, lines: list) -> Optional[str]:
        """匹配文件头描述行 '(Vx.y.z)' 格式"""
        for line in lines:
            m = cls.RE_SCL_FILEHEADER_VERSION.search(line)
            if m:
                return f"V{m.group(1)}.{m.group(2)}.{m.group(3)}"
        return None

    @classmethod
    def extract_prd_version(cls, file_path: str) -> Optional[str]:
        """
        从 PRD 文档提取版本号

        策略:
        1. 先尝试从文件名提取 (IFC-FB1003-PickPlace-V7.0.0.md → V7.0.0)
        2. 再尝试从文件内容前 20 行匹配 "> 版本: Vx.y.z" 行
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None

            version = cls.extract_prd_version_from_filename(path.name)
            if version:
                return version

            content = path.read_text(encoding="utf-8", errors="ignore")
            for line in content.splitlines()[:20]:
                m = cls.RE_MD_VERSION_LINE.search(line)
                if m:
                    return f"V{m.group(1)}.{m.group(2)}.{m.group(3)}"
                m = cls.RE_MD_TABLE_VERSION.search(line)
                if m:
                    return f"V{m.group(1)}.{m.group(2)}.{m.group(3)}"

            return None

        except Exception as e:
            logger.warning(f"PRD版本提取失败 {file_path}: {e}")
            return None

    @classmethod
    def extract_prd_version_from_filename(cls, file_name: str) -> Optional[str]:
        """
        从文件名提取版本号
        "接口文档_IFC-FB1003-PickPlace-V7.0.0.md" → "V7.0.0"
        """
        matches = cls.RE_FILENAME_VERSION.findall(file_name)
        if not matches:
            return None
        last = matches[-1]
        return f"V{last[0]}.{last[1]}.{last[2]}"

    @classmethod
    def parse_version_tuple(cls, version_str: str) -> Tuple[int, int, int]:
        """将版本字符串解析为元组 ("V7.1.1" → (7, 1, 1))"""
        m = cls.RE_FILENAME_VERSION.search(version_str)
        if m:
            return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        return (0, 0, 0)

    @classmethod
    def compare_versions(cls, v1: str, v2: str) -> int:
        """
        比较两个版本号
        Returns: -1(v1<v2), 0(v1==v2), 1(v1>v2)
        """
        t1 = cls.parse_version_tuple(v1)
        t2 = cls.parse_version_tuple(v2)
        if t1 < t2:
            return -1
        if t1 > t2:
            return 1
        return 0