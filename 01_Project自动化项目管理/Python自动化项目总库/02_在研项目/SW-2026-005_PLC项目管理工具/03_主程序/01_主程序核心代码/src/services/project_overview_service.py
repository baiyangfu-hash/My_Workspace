"""项目总览 Service - 从立项表提取项目信息"""

from __future__ import annotations

import os

from src.models.change_request import ChangeSummary
from src.models.project_info import ProjectInfo
from src.parsers.chg_parser import ChgParser
from src.parsers.proj_parser import ProjParser
from src.utils.file_utils import get_mtime
from src.utils.logger import get_logger
from src.utils.path_resolver import (
    find_proj_file,
    get_project_id_from_path,
    scan_change_files,
)

log = get_logger(__name__)


class ProjectOverviewService:
    """项目总览 Service - 从立项表提取项目信息"""

    def __init__(self, workspace_root: str) -> None:
        """
        Args:
            workspace_root: 工作空间根目录绝对路径
                           (如 C:\\...\\0100_PLC自动化)
        """
        self.workspace_root = workspace_root
        self._parser = ProjParser()
        self._chg_parser = ChgParser()
        self._cache: dict[str, tuple[float, ProjectInfo]] = {}

    def get_workspace_projects(self) -> list[ProjectInfo]:
        """获取工作空间下所有项目概览信息

        扫描工作空间根目录下的子目录（最多1层直接子目录 + 1层嵌套），
        每个含立项表的目录视为一个项目。
        变更统计仅计数文件数，不解析内容（保证响应速度）。
        """
        projects: list[ProjectInfo] = []
        if not os.path.isdir(self.workspace_root):
            log.warning("工作空间目录不存在: %s", self.workspace_root)
            return projects

        log.info("扫描工作空间: %s", self.workspace_root)
        self._scan_dir(self.workspace_root, projects, depth=0, max_depth=1)
        log.info("扫描完成，共 %d 个项目", len(projects))
        return projects

    def get_project_detail(self, project_id: str) -> ProjectInfo | None:
        """获取单个项目完整信息"""
        project_path = self._find_project_path(project_id)
        if not project_path:
            log.warning("项目路径未找到: %s", project_id)
            return None

        proj_file = find_proj_file(project_path)
        if not proj_file:
            log.warning("立项表文件未找到: %s", project_path)
            return None

        info = self._get_or_parse(proj_file)
        info.project_path = project_path
        info.project_id = project_id
        self._fill_change_stats(info, project_path)
        log.info("获取项目详情: %s, 阶段=%s, 变更%d件", project_id, info.phase, info.change_count)
        return info

    def get_project_changes(self, project_id: str) -> list[ChangeSummary]:
        """获取项目的变更单摘要列表"""
        project_path = self._find_project_path(project_id)
        if not project_path:
            log.warning("获取变更单列表: 项目路径未找到 %s", project_id)
            return []

        change_files = scan_change_files(project_path)
        log.info("获取变更单列表: %s, 扫描到 %d 个文件", project_id, len(change_files))
        summaries: list[ChangeSummary] = []
        for cf in change_files:
            cr = self._chg_parser.parse(cf)
            summaries.append(self._chg_parser.to_summary(cr))
        return summaries

    def refresh(self, project_id: str | None = None) -> None:
        """强制刷新缓存

        Args:
            project_id: 指定项目则只刷新该项目，None 则刷新全部
        """
        if project_id is None:
            log.info("刷新全部缓存, 清除 %d 条", len(self._cache))
            self._cache.clear()
            return

        # 找到该项目的立项表并清除缓存
        project_path = self._find_project_path(project_id)
        if project_path:
            proj_file = find_proj_file(project_path)
            if proj_file and proj_file in self._cache:
                del self._cache[proj_file]
                log.info("刷新项目缓存: %s", project_id)
            else:
                log.debug("刷新项目缓存: %s, 无缓存条目", project_id)

    # ---- 内部方法 ----

    def _scan_dir(self, dir_path: str, results: list[ProjectInfo], depth: int, max_depth: int) -> None:
        """递归扫描目录，查找含立项表的项目目录"""
        try:
            entries = sorted(os.listdir(dir_path))
        except PermissionError:
            log.warning("无权限访问目录: %s", dir_path)
            return

        for name in entries:
            project_path = os.path.join(dir_path, name)
            if not os.path.isdir(project_path):
                continue
            # 跳过隐藏目录和通用规范目录
            if name.startswith(".") or name.startswith("00_"):
                log.debug("跳过目录: %s", name)
                continue

            proj_file = find_proj_file(project_path)
            if proj_file:
                info = self._get_or_parse(proj_file)
                info.project_path = project_path
                info.project_id = get_project_id_from_path(project_path)
                self._fill_change_stats_light(info, project_path)  # 轻量统计：仅计数不解析
                results.append(info)
                log.info("发现项目: %s (%s), 变更%d件/待处理%d件",
                         info.project_id, info.name, info.change_count, info.pending_change_count)
            elif depth < max_depth:
                # 无立项表，继续向下一层搜索
                log.debug("目录无立项表，继续递归: %s (depth=%d)", name, depth)
                self._scan_dir(project_path, results, depth + 1, max_depth)
            else:
                log.debug("目录无立项表，跳过: %s", name)

    def _find_project_path(self, project_id: str) -> str | None:
        """根据项目编号获取项目路径（支持多级目录）"""
        # 直接子目录匹配
        candidate = os.path.join(self.workspace_root, project_id)
        if os.path.isdir(candidate):
            return candidate
        # 递归查找（最多2层）
        return self._find_project_dir(self.workspace_root, project_id, depth=0, max_depth=2)

    def _find_project_dir(self, dir_path: str, project_id: str, depth: int, max_depth: int) -> str | None:
        """递归查找项目目录"""
        try:
            entries = os.listdir(dir_path)
        except PermissionError:
            return None
        for name in entries:
            sub_path = os.path.join(dir_path, name)
            if not os.path.isdir(sub_path):
                continue
            if name == project_id:
                return sub_path
            if depth < max_depth and not name.startswith(".") and not name.startswith("00_"):
                result = self._find_project_dir(sub_path, project_id, depth + 1, max_depth)
                if result:
                    return result
        return None

    def _get_or_parse(self, file_path: str) -> ProjectInfo:
        """获取缓存或解析立项表（基于 mtime 判断缓存有效性）"""
        current_mtime = get_mtime(file_path)
        if file_path in self._cache:
            cached_mtime, cached_data = self._cache[file_path]
            if cached_mtime == current_mtime:
                log.debug("缓存命中: %s", os.path.basename(file_path))
                return cached_data
            log.info("缓存失效(mtime变更), 重新解析: %s", os.path.basename(file_path))
        # 缓存未命中或文件已修改，重新解析
        log.info("解析立项表: %s", os.path.basename(file_path))
        data = self._parser.parse(file_path)
        self._cache[file_path] = (current_mtime, data)
        return data

    def _fill_change_stats(self, info: ProjectInfo, project_path: str) -> None:
        """填充变更统计数据"""
        change_files = scan_change_files(project_path)
        info.change_count = len(change_files)
        # 统计待处理变更数
        pending_count = 0
        for cf in change_files:
            cr = self._chg_parser.parse(cf)
            if cr.status in ("draft", "submitted", "under_review", "approved"):
                pending_count += 1
                log.debug("待处理变更: %s, 状态=%s", cr.change_number, cr.status)
        info.pending_change_count = pending_count

    def _fill_change_stats_light(self, info: ProjectInfo, project_path: str) -> None:
        """轻量变更统计：仅计数文件数，不解析内容（用于总览列表加速）"""
        change_files = scan_change_files(project_path)
        info.change_count = len(change_files)
        # 待处理数先设为0，详情页再精确统计
        info.pending_change_count = 0
