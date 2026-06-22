"""项目核心模型（迁移自 core/project_service.py:ProjectInfo）

文件系统为单一真源，本模型为内存表示 + DB 缓存载体。
"""

from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from auto_pm.models.enums import ProjectPhase, ProjectSource, Stack

# 业务线类型（"" 表示未设置）
BusinessLine = Literal["SW", "DJ", "ZD", "XT", "WX", ""]

# 项目编号正则：SW-2026-001, DJ-2026-010 等格式（前缀 2-4 位大写字母）
_PROJECT_ID_RE = re.compile(r"^([A-Z]{2,4})-\d{4}-\d{3}")


def extract_business_line(project_id: str) -> str:
    """从项目编号提取业务线前缀（如 SW-2026-008 → SW）

    业务线编码：SW=软件 / DJ=单机 / ZD=整线 / XT=升级 / WX=维保。
    无法识别时返回空字符串。
    """
    if not project_id:
        return ""
    m = _PROJECT_ID_RE.match(project_id)
    return m.group(1) if m else ""


class Project(BaseModel):
    """项目元数据

    迁移自 ProjectInfo dataclass。字段保持兼容，新增 phase/business_line 字段。
    """

    project_id: str = Field(..., description="项目编号，如 SW-2026-008")
    name: str = Field(..., description="项目名称")
    path: str = Field(..., description="项目绝对路径")
    stack: Stack = Field("unknown", description="技术栈: plc/python/unknown")
    version: str = Field("", description="版本号")
    description: str = Field("", description="描述")
    source: ProjectSource = Field("", description="元数据来源: copier/plc_json/pm_session/dirname")
    phase: ProjectPhase = Field(
        "", description="项目阶段: developing/commissioning/production/archived"
    )
    business_line: BusinessLine = Field("", description="业务线: SW/DJ/ZD/XT/WX")
    extra: dict[str, Any] = Field(default_factory=dict, description="额外字段")
    file_mtime: float = Field(0.0, description="项目文件最近修改时间")

    model_config = ConfigDict(from_attributes=True)


class ProjectRecord(Project):
    """DB 缓存记录（扩展扫描元数据）

    用于 SQLite 索引缓存表，记录扫描时间戳以支持增量同步。
    """

    last_scanned: str = Field("", description="最后扫描时间 ISO8601")


# 兼容别名：现有代码中 ProjectInfo 仍可使用，指向 Project
ProjectInfo = Project
