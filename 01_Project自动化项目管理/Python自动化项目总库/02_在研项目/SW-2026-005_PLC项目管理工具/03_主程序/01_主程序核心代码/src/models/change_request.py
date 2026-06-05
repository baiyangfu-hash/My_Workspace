"""变更单数据模型 - 来源：CHG-*.md"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ChangeRequest:
    """变更单数据模型 - 来源：CHG-*.md"""

    # §3.0 编号与项目
    change_number: str = ""
    project_id: str = ""
    project_name: str = ""

    # §3.1 技术领域
    domain: str = ""

    # §3.2 业务性质
    business_nature: str = ""

    # §3.3 影响范围
    impact_scope: list[str] = field(default_factory=list)

    # §3.4 申请信息
    applicant: str = "待补充"
    apply_date: str = "待补充"
    planned_date: str = "待补充"
    urgency: str = "normal"

    # §4 变更原因
    background: str = "待补充"
    necessity: str = "待补充"
    references: str = "待补充"

    # 状态（从审批流程推断）
    status: str = "draft"

    # 章节内容（门禁校验用，记录各章节是否有实质内容）
    has_section_4: bool = False      # §4 变更原因
    has_section_7: bool = False      # §7 实施计划
    has_section_8_approval: bool = False  # §8.1 至少一条审批记录
    has_section_9: bool = False      # §9 实施记录
    has_section_10_verify: bool = False   # §10.1 至少一条验证项
    section_10_conclusion: str = ""  # §10.2 验证结论

    # 元数据
    file_path: str = ""
    file_mtime: float = 0.0


@dataclass
class ChangeSummary:
    """变更单列表项 - 轻量级"""
    change_number: str = ""
    project_id: str = ""
    domain: str = ""
    business_nature: str = ""
    impact_scope: list[str] = field(default_factory=list)
    status: str = "draft"
    applicant: str = "待补充"
    apply_date: str = "待补充"
    title: str = "待补充"
