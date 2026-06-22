"""变更单文件路径定位器（M3-Iter2 从 ChangeService 拆分）

负责：
- 项目路径解析（_get_project_path）
- 变更编号生成（_generate_change_number）
- 变更单文件路径计算（_get_change_file_path）
- 跨项目变更单文件查找（_find_change_file）
- 全工作空间变更单扫描（_scan_all_change_files）

ChangeService 通过组合方式使用本模块，保持向后兼容。

M3-Iter6：路径常量统一到 auto_pm.core.paths，消除硬编码。
"""

from __future__ import annotations

import datetime
import os
from typing import Optional

from auto_pm.change.parser import ChgParser
from auto_pm.change.path_resolver import (
    extract_domain_from_change_number,
    scan_change_files,
)
from auto_pm.core.paths import (
    CHANGE_REQUESTS_PLC_PATH,
    CHANGE_REQUESTS_PYTHON_PATH,
)
from auto_pm.logging.logging import setup_logger as get_logger
from auto_pm.models import ChangeSummary

log = get_logger(log_level="INFO", app_name="auto_pm")


class ChangeFileLocator:
    """变更单文件路径定位器

    封装变更单文件的路径约定（PLC / Python 两套目录结构）和查找逻辑。
    """

    # 变更单搜索路径（按优先级排列，与 path_resolver._CHANGE_SEARCH_PATHS 对齐）
    # M3-Iter6: 从 core.paths 读取，消除硬编码
    CHANGE_FILE_SEARCH_PATHS = [
        os.path.join(*CHANGE_REQUESTS_PLC_PATH),
        os.path.join(*CHANGE_REQUESTS_PYTHON_PATH),
    ]

    def __init__(self, workspace_root: str, parser: ChgParser) -> None:
        self.workspace_root = workspace_root
        self._parser = parser

    def get_project_path(self, project_id: str) -> Optional[str]:
        """根据项目编号获取项目路径

        项目目录命名约定为 ``{project_id}_{project_name}``（见 cmd_create），
        因此优先按 ``{project_id}_`` 前缀匹配；同时保留精确匹配以向后兼容。
        """
        # 1. 精确匹配（向后兼容：目录名 == project_id）
        candidate = os.path.join(self.workspace_root, project_id)
        if os.path.isdir(candidate):
            return candidate

        # 2. 前缀匹配: {project_id}_{project_name}
        if not os.path.isdir(self.workspace_root):
            return None
        prefix = project_id + "_"
        try:
            for name in os.listdir(self.workspace_root):
                if name.startswith(prefix) and os.path.isdir(
                    os.path.join(self.workspace_root, name)
                ):
                    return os.path.join(self.workspace_root, name)
        except OSError:
            pass
        return None

    def generate_change_number(self, project_path: str, domain: str) -> str:
        """生成变更编号 CHG-{DOMAIN}-{YYYY}-{XXX}

        扫描已有变更单，确定下一个序号
        """
        year = str(datetime.date.today().year)
        change_files = scan_change_files(project_path)

        # 找出同领域同年的最大序号
        max_seq = 0
        prefix = f"CHG-{domain}-{year}-"
        for cf in change_files:
            basename = os.path.splitext(os.path.basename(cf))[0]
            if basename.startswith(prefix):
                seq_str = basename[len(prefix):]
                try:
                    seq = int(seq_str)
                    max_seq = max(max_seq, seq)
                except ValueError:
                    pass

        next_seq = max_seq + 1
        result = f"CHG-{domain}-{year}-{next_seq:03d}"
        log.debug("生成变更编号: %s (已有同领域最大序号=%d)", result, max_seq)
        return result

    def get_change_file_path(self, project_path: str, change_number: str) -> str:
        """根据变更编号获取文件路径

        按优先级搜索多套目录约定（PLC / Python），命中已有目录返回，
        未命中时使用 PLC 约定路径（默认创建路径）。

        格式: {搜索路径}/CHG-{DOMAIN}/CHG-{DOMAIN}-{YYYY}-{XXX}.md
        """
        domain = extract_domain_from_change_number(change_number)
        # 优先匹配已有目录
        for rel_path in self.CHANGE_FILE_SEARCH_PATHS:
            base_dir = os.path.join(project_path, rel_path, f"CHG-{domain}")
            if os.path.isdir(base_dir):
                return os.path.join(base_dir, f"{change_number}.md")
        # 未匹配已有目录 → 使用 PLC 约定路径（默认创建路径）
        # M3-Iter6: 从 core.paths 读取，消除硬编码
        return os.path.join(
            project_path,
            *CHANGE_REQUESTS_PLC_PATH,
            f"CHG-{domain}",
            f"{change_number}.md",
        )

    def find_change_file(self, change_number: str) -> Optional[str]:
        """根据变更编号查找文件

        遍历工作空间下的项目，按 PLC / Python 两套路径约定搜索。
        """
        domain = extract_domain_from_change_number(change_number)
        if not domain:
            log.warning("查找变更单: 无法从编号提取领域 %s", change_number)
            return None

        # 遍历工作空间下的项目查找
        if not os.path.isdir(self.workspace_root):
            log.warning("查找变更单: 工作空间目录不存在 %s", self.workspace_root)
            return None

        for name in os.listdir(self.workspace_root):
            project_path = os.path.join(self.workspace_root, name)
            if not os.path.isdir(project_path):
                continue
            # 按优先级搜索 PLC / Python 两套路径
            for rel_path in self.CHANGE_FILE_SEARCH_PATHS:
                candidate = os.path.join(
                    project_path,
                    rel_path,
                    f"CHG-{domain}",
                    f"{change_number}.md",
                )
                if os.path.isfile(candidate):
                    return candidate

        return None

    def scan_all_change_files(self) -> list[ChangeSummary]:
        """扫描工作空间所有项目的变更单文件（无 DB 时的回退路径）

        遍历 workspace_root 下的每个项目目录，调用 scan_change_files
        解析所有 CHG-*.md 文件并转换为 ChangeSummary。
        """
        summaries: list[ChangeSummary] = []
        if not os.path.isdir(self.workspace_root):
            return summaries

        try:
            entries = os.listdir(self.workspace_root)
        except OSError:
            return summaries

        for name in entries:
            project_path = os.path.join(self.workspace_root, name)
            if not os.path.isdir(project_path):
                continue
            for cf in scan_change_files(project_path):
                try:
                    cr = self._parser.parse(cf)
                    summaries.append(self._parser.to_summary(cr))
                except Exception as e:
                    log.warning("解析变更单文件失败，跳过: %s: %s", cf, e)
        return summaries
