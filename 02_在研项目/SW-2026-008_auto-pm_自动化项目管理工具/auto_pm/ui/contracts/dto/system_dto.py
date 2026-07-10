"""System 相关 DTO 定义

M4 第 2 批新增：SystemFacade 6 方法返回带类型 DTO。
list_templates 返回 list[str]、get_template_path 返回 str，无需 DTO。
get_template_detail 从现有 Facade 代码提取 6 个具体字段。
pm_session 2 方法用 dict 字段包装（TODO: Service 结构明确后细化字段）。
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PmSessionViewDTO:
    """PM_SESSION 视图（对应 get_pm_session_view 返回，M4 第 2 批新增）"""
    data: dict[str, Any]  # pm_session_service.generate_view 返回


@dataclass(frozen=True)
class PmSessionCheckResultDTO:
    """PM_SESSION 检查结果（对应 run_pm_session_check 返回，M4 第 2 批新增）"""
    data: dict[str, Any]  # pm_session_service.check 返回


@dataclass(frozen=True)
class TemplateDetailDTO:
    """模板详情（对应 get_template_detail 返回，M4 第 2 批新增）"""
    name: str
    version: str
    description: str
    stack: str
    usage_count: int
    path: str


@dataclass(frozen=True)
class ApplyTemplateResultDTO:
    """模板应用结果（对应 apply_template 返回，M4 第 2 批新增）"""
    project_id: str
    template_name: str
    result: dict[str, Any]  # template_service.apply_template 返回
