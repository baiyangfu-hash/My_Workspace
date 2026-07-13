"""PLC-HMI 概念映射：SFB 库函数（路径工具（工作空间路径解析/标准化））

像 PLC 的 SFB/SFC 系统函数，被 FB 功能块（application/*_facade.py）调用，
不直接暴露给 HMI 画面。

--- 原始注释 ---

统一路径约定常量（M3-Iter6）

集中定义工作空间和项目内的目录结构约定，消除散落在各模块的硬编码路径。

目录约定来源：
- LSP-907 907_项目配置规范_LSP §3.1：PLC 项目目录结构
- CHG-040 §2：变更管理目录结构
- 210/211/220：Python 项目目录结构
"""

from __future__ import annotations

import os
from typing import Final

# ── 工作空间级目录 ─────────────────────────────────────────

#: 工作空间下存放"在研项目"的子目录
WORKSPACE_PROJECTS_SUBDIR: Final[str] = "02_在研项目"


# ── 项目级目录（PLC 项目，LSP-907 §3.1） ────────────────────

#: PLC 项目根目录下的标准子目录（LSP-907 §3.1）
PLC_STD_DIRS: Final[list[str]] = [
    "02_PLC程序/通用ST程序及变量表",
    "03_HMI设计",
    "04_现场调试",
    "04_变更管理",
    "PRD",
]

#: PRD 文档目录名
PRD_DIR: Final[str] = "PRD"


# ── 变更管理目录（CHG-040 §2） ─────────────────────────────

#: 变更单存放目录（PLC 项目约定）
CHANGE_REQUESTS_PLC_PATH: Final[list[str]] = [
    "00_项目管理", "04_变更管理", "01_变更单"
]

#: 变更单存放目录（Python/通用项目约定）
CHANGE_REQUESTS_PYTHON_PATH: Final[list[str]] = [
    "01_项目文档", "03_执行过程", "02_变更管理", "01_变更单"
]

#: 变更记录存放目录（PLC 项目约定）
CHANGE_RECORDS_PLC_PATH: Final[list[str]] = [
    "00_项目管理", "04_变更管理", "04_变更记录"
]

#: 变更记录存放目录（Python/通用项目约定）
CHANGE_RECORDS_PYTHON_PATH: Final[list[str]] = [
    "01_项目文档", "03_执行过程", "02_变更管理", "04_变更记录"
]

#: 立项与需求目录（PLC 项目约定）
PROJECT_INIT_PLC_PATH: Final[list[str]] = [
    "00_项目管理", "01_立项与需求"
]


# ── PRD 文档命名（LSP-907 + SysLib FB 标准） ───────────────

#: 标准 PRD 文档列表
STD_PRD_DOCS: Final[list[str]] = [
    "需求分析文档_REQ.md",
    "接口文档_INT.md",
    "详细设计说明书_DSN.md",
    "技术方案文档_TEC.md",
]


# ── 便捷函数 ───────────────────────────────────────────────

def join_path(*parts: str) -> str:
    """跨平台拼接路径（os.path.join 的语义化包装）"""
    return os.path.join(*parts)


def get_projects_subdir(workspace_root: str) -> str:
    """获取工作空间下的"在研项目"目录路径"""
    return os.path.join(workspace_root, WORKSPACE_PROJECTS_SUBDIR)


def get_change_requests_paths(project_path: str) -> list[str]:
    """获取变更单存放目录的所有候选路径（按优先级）

    PLC 约定优先，Python 约定次之。
    """
    return [
        os.path.join(project_path, *CHANGE_REQUESTS_PLC_PATH),
        os.path.join(project_path, *CHANGE_REQUESTS_PYTHON_PATH),
    ]


def get_change_records_paths(project_path: str) -> list[str]:
    """获取变更记录存放目录的所有候选路径（按优先级）"""
    return [
        os.path.join(project_path, *CHANGE_RECORDS_PLC_PATH),
        os.path.join(project_path, *CHANGE_RECORDS_PYTHON_PATH),
    ]


def get_prd_dir(project_path: str) -> str:
    """获取 PRD 文档目录路径"""
    return os.path.join(project_path, PRD_DIR)
