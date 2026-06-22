"""项目扫描器 - 递归扫描工作空间，识别项目

从 ProjectService 提取的单一职责模块，负责：
- 递归扫描目录
- 识别项目（.copier-answers.yml / .plc.json / PM_SESSION_*.md）
- 读取项目元数据

ProjectService 通过组合方式使用本模块，保持向后兼容。
"""

from __future__ import annotations

import json
import os
import re
from typing import Optional

import yaml

from auto_pm.logging.logging import setup_logger
from auto_pm.models import ProjectInfo
from auto_pm.models.project import extract_business_line

log = setup_logger(log_level="INFO", app_name="auto_pm")


class ProjectScanner:
    """项目扫描器 - 递归扫描工作空间，识别项目"""

    # 项目识别标志文件
    COPIER_ANSWERS_FILE = ".copier-answers.yml"
    PLC_JSON_FILE = ".plc.json"
    PM_SESSION_PREFIX = "PM_SESSION_"

    # 项目编号正则：SW-2026-001, DJ-2026-010 等格式（前缀 2-4 位大写字母）
    _PROJECT_ID_RE = re.compile(r"^([A-Z]{2,4}-\d{4}-\d{3})")

    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = os.path.abspath(workspace_root)

    def scan(self, scan_depth: int = 4) -> list[ProjectInfo]:
        """扫描工作空间，返回所有项目

        Args:
            scan_depth: 最大扫描深度（默认4层）

        Returns:
            项目列表，按 project_id 排序
        """
        results: list[ProjectInfo] = []
        self._scan(self.workspace_root, results, depth=0, max_depth=scan_depth)
        results.sort(key=lambda p: p.project_id)
        log.info("扫描完成: 发现 %d 个项目", len(results))
        return results

    def try_identify_project(self, project_path: str) -> Optional[ProjectInfo]:
        """尝试识别目录是否为项目，并提取元数据

        优先级：.copier-answers.yml > .plc.json > PM_SESSION_*.md > 目录名
        """
        # 1. Copier 答案文件（最可靠）
        info = self.read_copier_answers(project_path)
        if info is not None:
            info.file_mtime = self.get_project_mtime(project_path)
            return info

        # 2. .plc.json（PLC 项目）
        info = self.read_plc_json(project_path)
        if info is not None:
            info.file_mtime = self.get_project_mtime(project_path)
            return info

        # 3. PM_SESSION_*.md
        info = self.read_pm_session(project_path)
        if info is not None:
            info.file_mtime = self.get_project_mtime(project_path)
            return info

        return None

    def read_copier_answers(self, project_path: str) -> Optional[ProjectInfo]:
        """从 .copier-answers.yml 读取项目元数据"""
        answers_path = os.path.join(project_path, self.COPIER_ANSWERS_FILE)
        if not os.path.isfile(answers_path):
            return None

        try:
            with open(answers_path, encoding="utf-8") as f:
                answers = yaml.safe_load(f) or {}
        except (yaml.YAMLError, OSError) as e:
            log.warning("读取 .copier-answers.yml 失败: %s: %s", project_path, e)
            return None

        project_id = answers.get("project_id", "")
        project_name = answers.get("project_name", "")

        # project_id 为空时，从目录名提取编号（如 SW-2026-008）
        if not project_id:
            project_id = self.extract_id_from_dirname(project_path)

        # 推断技术栈
        src_path = answers.get("_src_path", "")
        stack = self.infer_stack(src_path)

        # 业务线：优先从 answers 读取，否则从 project_id 提取
        business_line = answers.get("business_line", "") or extract_business_line(project_id)

        return ProjectInfo(
            project_id=project_id,
            name=project_name or answers.get("project_name", "") or os.path.basename(project_path),
            path=project_path,
            stack=stack,
            version=answers.get("version", ""),
            description=answers.get("description", ""),
            phase=answers.get("phase", ""),
            business_line=business_line,
            source="copier",
            extra=answers,
        )

    def read_plc_json(self, project_path: str) -> Optional[ProjectInfo]:
        """从 .plc.json 读取项目元数据"""
        plc_json_path = os.path.join(project_path, self.PLC_JSON_FILE)
        if not os.path.isfile(plc_json_path):
            return None

        try:
            with open(plc_json_path, encoding="utf-8") as f:
                cfg = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            log.warning("读取 .plc.json 失败: %s: %s", project_path, e)
            return None

        name = cfg.get("name", "")
        return ProjectInfo(
            project_id=name or os.path.basename(project_path),
            name=name or os.path.basename(project_path),
            path=project_path,
            stack="plc",
            version=cfg.get("version", ""),
            description=cfg.get("description", ""),
            phase=cfg.get("phase", ""),
            source="plc_json",
            extra=cfg,
        )

    def read_pm_session(self, project_path: str) -> Optional[ProjectInfo]:
        """从 PM_SESSION_*.md 文件名提取项目编号"""
        try:
            entries = os.listdir(project_path)
        except OSError:
            return None

        for entry in entries:
            if entry.startswith(self.PM_SESSION_PREFIX) and entry.endswith(".md"):
                # PM_SESSION_DJ-2026-010.md -> DJ-2026-010
                project_id = entry[len(self.PM_SESSION_PREFIX) : -len(".md")]
                return ProjectInfo(
                    project_id=project_id,
                    name=os.path.basename(project_path),
                    path=project_path,
                    stack="unknown",
                    source="pm_session",
                )
        return None

    @staticmethod
    def extract_id_from_dirname(project_path: str) -> str:
        """从目录名提取项目编号（如 SW-2026-008）"""
        dirname = os.path.basename(project_path)
        m = ProjectScanner._PROJECT_ID_RE.match(dirname)
        return m.group(1) if m else dirname

    @staticmethod
    def infer_stack(src_path: str) -> str:
        """根据模板源路径推断技术栈"""
        src_lower = src_path.lower()
        if "plc" in src_lower:
            return "plc"
        if "python" in src_lower:
            return "python"
        return "unknown"

    @staticmethod
    def get_project_mtime(project_path: str) -> float:
        """获取项目标志文件的 mtime（增量扫描判据）"""
        mtime = 0.0
        for marker in (".copier-answers.yml", ".plc.json"):
            path = os.path.join(project_path, marker)
            if os.path.isfile(path):
                mtime = max(mtime, os.path.getmtime(path))
        try:
            for entry in os.listdir(project_path):
                if entry.startswith("PM_SESSION_") and entry.endswith(".md"):
                    path = os.path.join(project_path, entry)
                    mtime = max(mtime, os.path.getmtime(path))
        except OSError:
            pass
        return mtime

    def _scan(
        self,
        path: str,
        results: list[ProjectInfo],
        depth: int,
        max_depth: int,
    ) -> None:
        """递归扫描目录，识别项目"""
        if depth > max_depth:
            return

        try:
            entries = os.listdir(path)
        except OSError:
            return

        for entry in entries:
            entry_path = os.path.join(path, entry)
            if not os.path.isdir(entry_path):
                continue
            if entry.startswith(".") or entry.startswith("__"):
                continue

            # 判断是否是项目目录
            info = self.try_identify_project(entry_path)
            if info is not None:
                results.append(info)
            else:
                # 非项目目录，继续递归
                self._scan(entry_path, results, depth + 1, max_depth)
