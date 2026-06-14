# -*- coding: utf-8 -*-
"""
常量定义（统一入口）

子模块拆分:
  - _business_constants: 项目/业务线/模板/插件/检查结果相关枚举与映射
  - _change_constants: 变更管理相关枚举与映射（V2.1.0 Domain/Nature/Scope/ApprovalLevel）
  - _template_constants: 默认项目结构模板数据（DEFAULT_TEMPLATES）

所有现有 `from src.core.constants import ...` 无需修改。
"""

# 从子模块 re-export 所有公开名称
from ._business_constants import (  # noqa: F401
    BusinessLine,
    ProjectStatus,
    TemplateType,
    PluginStatus,
    CheckResult,
    BUSINESS_LINE_DESC,
    BUSINESS_LINE_TEMPLATES,
    PROJECT_STATUS_COLOR,
)

from ._change_constants import (  # noqa: F401
    ChangeStatus,
    ChangeType,
    ImpactLevel,
    Domain,
    DOMAIN_NAMES,
    Nature,
    NATURE_NAMES,
    Scope,
    SCOPE_NAMES,
    ApprovalLevel,
    SCOPE_APPROVAL_MAP,
    CHANGE_TYPE_TO_DOMAIN_MAP,
    IMPACT_LEVEL_TO_SCOPE_MAP,
)

from ._template_constants import (  # noqa: F401
    DEFAULT_TEMPLATES,
)
