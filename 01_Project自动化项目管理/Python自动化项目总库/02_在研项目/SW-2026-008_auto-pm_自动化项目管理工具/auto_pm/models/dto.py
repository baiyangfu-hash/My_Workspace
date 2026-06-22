"""GUI / API 层 DTO

供 PySide6 视图层和 CLI 使用，与核心模型分离，避免内部字段暴露给前端。
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from auto_pm.models.change import ChangeSummary
from auto_pm.models.enums import Stack
from auto_pm.models.project import BusinessLine, Project

T = TypeVar("T")


class ProjectListItem(BaseModel):
    """项目列表项（轻量，左侧列表用）"""

    project_id: str = Field(..., description="项目编号")
    name: str = Field(..., description="项目名称")
    stack: Stack = Field(..., description="技术栈")
    version: str = Field("", description="版本号")
    phase: str = Field("", description="阶段")
    change_count: int = Field(0, description="关联变更单数（JOIN 查询）")

    model_config = ConfigDict(from_attributes=True)


class ProjectCardDTO(BaseModel):
    """项目卡片 DTO（PySide6 项目列表卡片用）

    包含卡片展示所需的全部字段：编号、名称、技术栈、阶段、版本、业务线、变更数、路径、
    最近修改时间、描述摘要。
    """

    project_id: str = Field(..., description="项目编号")
    name: str = Field(..., description="项目名称")
    stack: Stack = Field(..., description="技术栈: plc/python/unknown")
    phase: str = Field("", description="项目阶段")
    version: str = Field("", description="版本号")
    business_line: BusinessLine = Field("", description="业务线: SW/DJ/ZD/XT/WX")
    change_count: int = Field(0, description="关联变更单数")
    path: str = Field("", description="项目绝对路径")
    file_mtime: float = Field(0.0, description="项目文件最近修改时间(时间戳)")
    description: str = Field("", description="项目描述摘要")

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailDTO(BaseModel):
    """项目详情 DTO（PySide6 项目工作区详情页用）

    包含完整 Project 字段 + 关联变更单列表，供详情视图渲染。
    """

    project_id: str = Field(..., description="项目编号")
    name: str = Field(..., description="项目名称")
    path: str = Field(..., description="项目绝对路径")
    stack: Stack = Field(..., description="技术栈")
    version: str = Field("", description="版本号")
    description: str = Field("", description="描述")
    source: str = Field("", description="元数据来源")
    phase: str = Field("", description="项目阶段")
    business_line: BusinessLine = Field("", description="业务线")
    extra: dict[str, object] = Field(default_factory=dict, description="额外字段")
    changes: list[ChangeSummary] = Field(default_factory=list, description="关联变更单列表")
    change_count: int = Field(0, description="关联变更单数")

    model_config = ConfigDict(from_attributes=True)


class ProjectDetail(BaseModel):
    """项目详情（右侧面板用）"""

    project: Project = Field(..., description="项目完整信息")
    changes: list[ChangeSummary] = Field(default_factory=list, description="关联变更单列表")
    doc_count: int = Field(0, description="文档数")
    last_check: str = Field("", description="最后规范检查结果")

    model_config = ConfigDict(from_attributes=True)


class ProjectCreateRequest(BaseModel):
    """创建项目请求（新建项目弹窗）"""

    project_id: str = Field(..., pattern=r"^[A-Z]+-\d{4}-\d{3}$", description="项目编号")
    project_name: str = Field(..., min_length=1, description="项目名称")
    stack: Stack = Field(..., description="技术栈: plc/python")
    template: str = Field("plc-standard", description="模板名")
    description: str = Field("", description="描述")
    author: str = Field("", description="作者")


class ProjectUpdateRequest(BaseModel):
    """更新项目元数据请求"""

    phase: str | None = Field(None, description="阶段")
    description: str | None = Field(None, description="描述")
    version: str | None = Field(None, description="版本号")


class ScanResult(BaseModel):
    """扫描结果"""

    scan_type: str = Field(..., description="扫描类型: full/incremental")
    projects_found: int = Field(0, description="发现项目数")
    changes_found: int = Field(0, description="发现变更单数")
    duration_ms: int = Field(0, description="耗时(毫秒)")
    status: str = Field("success", description="状态: success/failed")
    message: str = Field("", description="附加消息")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应（pywebview JS bridge 返回格式）"""

    success: bool = Field(True, description="是否成功")
    data: T | None = Field(None, description="响应数据")
    error: str | None = Field(None, description="错误信息")
    message: str = Field("", description="附加消息")
    timestamp: str = Field("", description="时间戳 ISO8601")
