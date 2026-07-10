"""统一路径约定测试（M3-Iter6）

验证 auto_pm.core.paths 模块的常量和便捷函数。
"""

from __future__ import annotations

import os
from pathlib import Path

from auto_pm.core.paths import (
    CHANGE_RECORDS_PLC_PATH,
    CHANGE_RECORDS_PYTHON_PATH,
    CHANGE_REQUESTS_PLC_PATH,
    CHANGE_REQUESTS_PYTHON_PATH,
    PLC_STD_DIRS,
    PRD_DIR,
    STD_PRD_DOCS,
    WORKSPACE_PROJECTS_SUBDIR,
    get_change_records_paths,
    get_change_requests_paths,
    get_prd_dir,
    get_projects_subdir,
)


class TestPathConstants:
    """路径常量定义测试"""

    def test_workspace_projects_subdir(self) -> None:
        """工作空间项目子目录常量"""
        assert WORKSPACE_PROJECTS_SUBDIR == "02_在研项目"

    def test_plc_std_dirs(self) -> None:
        """PLC 标准目录列表"""
        assert "PRD" in PLC_STD_DIRS
        assert "03_HMI设计" in PLC_STD_DIRS
        assert "04_现场调试" in PLC_STD_DIRS

    def test_prd_dir(self) -> None:
        """PRD 目录名常量"""
        assert PRD_DIR == "PRD"

    def test_std_prd_docs(self) -> None:
        """标准 PRD 文档列表"""
        assert "需求分析文档_REQ.md" in STD_PRD_DOCS
        assert "接口文档_INT.md" in STD_PRD_DOCS
        assert "详细设计说明书_DSN.md" in STD_PRD_DOCS
        assert "技术方案文档_TEC.md" in STD_PRD_DOCS

    def test_change_requests_paths(self) -> None:
        """变更单存放路径常量"""
        assert CHANGE_REQUESTS_PLC_PATH == ["00_项目管理", "04_变更管理", "01_变更单"]
        assert CHANGE_REQUESTS_PYTHON_PATH == [
            "01_项目文档", "03_执行过程", "02_变更管理", "01_变更单"
        ]

    def test_change_records_paths(self) -> None:
        """变更记录存放路径常量"""
        assert CHANGE_RECORDS_PLC_PATH == ["00_项目管理", "04_变更管理", "04_变更记录"]
        assert CHANGE_RECORDS_PYTHON_PATH == [
            "01_项目文档", "03_执行过程", "02_变更管理", "04_变更记录"
        ]


class TestPathHelpers:
    """便捷函数测试"""

    def test_get_projects_subdir(self, tmp_path: Path) -> None:
        """获取工作空间下的项目目录路径"""
        result = get_projects_subdir(str(tmp_path))
        expected = os.path.join(str(tmp_path), "02_在研项目")
        assert result == expected

    def test_get_change_requests_paths(self, tmp_path: Path) -> None:
        """获取变更单存放目录候选路径"""
        paths = get_change_requests_paths(str(tmp_path))
        assert len(paths) == 2
        # PLC 路径优先
        assert "00_项目管理" in paths[0]
        assert "01_项目文档" in paths[1]

    def test_get_change_records_paths(self, tmp_path: Path) -> None:
        """获取变更记录存放目录候选路径"""
        paths = get_change_records_paths(str(tmp_path))
        assert len(paths) == 2
        assert "04_变更记录" in paths[0]
        assert "04_变更记录" in paths[1]

    def test_get_prd_dir(self, tmp_path: Path) -> None:
        """获取 PRD 目录路径"""
        result = get_prd_dir(str(tmp_path))
        expected = os.path.join(str(tmp_path), "PRD")
        assert result == expected


class TestNoHardcodedPaths:
    """验证关键模块不再使用硬编码路径"""

    def test_file_locator_uses_constants(self) -> None:
        """ChangeFileLocator 使用 paths 常量而非硬编码"""
        from auto_pm.change.file_locator import ChangeFileLocator

        # CHANGE_FILE_SEARCH_PATHS 应从 paths 常量构造
        assert len(ChangeFileLocator.CHANGE_FILE_SEARCH_PATHS) == 2
        # 验证路径内容正确
        plc_path = os.path.join(*CHANGE_REQUESTS_PLC_PATH)
        python_path = os.path.join(*CHANGE_REQUESTS_PYTHON_PATH)
        assert plc_path in ChangeFileLocator.CHANGE_FILE_SEARCH_PATHS
        assert python_path in ChangeFileLocator.CHANGE_FILE_SEARCH_PATHS
