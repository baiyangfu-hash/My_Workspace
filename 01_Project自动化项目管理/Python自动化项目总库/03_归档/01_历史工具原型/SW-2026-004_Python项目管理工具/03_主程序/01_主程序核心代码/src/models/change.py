# -*- coding: utf-8 -*-
"""
变更记录数据模型 (V2.1.0 - 支持二维分类: 领域×性质×范围)
"""
from sqlalchemy import Column, String, Text, Enum, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Tuple, Optional

from .base import BaseModel
from src.core.constants import (
    ChangeStatus, Domain, Nature, Scope,
    DOMAIN_NAMES, NATURE_NAMES, SCOPE_NAMES,
    CHANGE_TYPE_TO_DOMAIN_MAP, IMPACT_LEVEL_TO_SCOPE_MAP,
)


class Change(BaseModel):
    """变更单模型 (V2.1.0 - 工程变更管理)"""
    __tablename__ = "changes"

    # === 基础信息 ===
    change_id = Column(String(32), unique=True, nullable=False, comment="变更单ID (CHG-[DOMAIN]-[YYYY]-[XXX])")
    project_id = Column(String(32), ForeignKey("projects.project_id"), nullable=False, comment="所属项目ID")
    title = Column(String(200), nullable=False, comment="变更标题")

    # === V2.1.0 二维分类 (替代原type字段) ===
    domain = Column(Enum(Domain), nullable=False, default=Domain.PLC, comment="技术领域(WHO)")
    nature = Column(Enum(Nature), nullable=False, default=Nature.OPT, comment="业务性质(WHY)")
    scope = Column(Enum(Scope), nullable=False, default=Scope.LOCAL, comment="影响范围(WHERE)")
    priority = Column(String(10), default="P2", comment="优先级 P0/P1/P2/P3")

    # === V1.x 兼容字段 (保留) ===
    type = Column(String(50), nullable=True, comment="变更类型(V1.x遗留, 建议使用domain+nature)")
    impact = Column(Text, nullable=True, comment="影响范围(V1.x遗留, 建议使用scope)")
    description = Column(Text, comment="详细描述")

    # === 变更内容 ===
    reason = Column(Text, comment="变更原因(§4)")
    content_before = Column(Text, comment="变更前状态(§5.1)")
    content_after = Column(Text, comment="变更后状态(§5.2)")

    # === 影响分析 ===
    impact_analysis = Column(Text, comment="影响分析结果(§6 补充说明)")

    # === V2.1.0 传播链与关联 ===
    related_changes = Column(JSON, default=list, comment="关联变更单ID列表 [str]")
    propagation_chain = Column(Text, comment="传播链描述(ASCII图+关联编号)")

    # === V2.1.0 分级审批 ===
    approval_level = Column(String(30), comment="审批层级(自动按scope匹配)")
    reviewer = Column(String(50), comment="复审人(SYS/CROSS/SAFE时需要)")

    # === 状态与人员 ===
    status = Column(Enum(ChangeStatus), default=ChangeStatus.DRAFT, comment="变更状态")
    proposer = Column(String(50), comment="提出人")
    approver = Column(String(50), comment="审批人")
    implementer = Column(String(50), comment="实施人")
    attachment = Column(JSON, default=list, comment="附件列表")

    # === 时间戳 ===
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, onupdate=datetime.now, comment="更新时间")
    approved_at = Column(DateTime, comment="审批时间")
    implemented_at = Column(DateTime, comment="实施时间")
    completed_at = Column(DateTime, comment="完成时间")

    # 关系
    project = relationship("Project", backref="changes")

    def __repr__(self) -> str:
        return f"<Change {self.change_id} [{self.domain.value}/{self.nature.value}] {self.title}>"

    @staticmethod
    def generate_change_id(domain: Domain, year: int, sequence: int) -> str:
        """V2.1.0命名规则: CHG-[DOMAIN]-[YYYY]-[XXX]"""
        return f"CHG-{domain.value}-{year}-{sequence:03d}"

    @staticmethod
    def migrate_from_v1(old_type: str, old_level: Optional[str] = None) -> Tuple[Domain, Nature]:
        """
        V1.x → V2.1.0 迁移辅助方法
        将旧的type字符串映射为新的Domain+Nature组合
        """
        domain = CHANGE_TYPE_TO_DOMAIN_MAP.get(old_type, Domain.SCPT)

        nature_map = {
            "功能变更": Nature.REQ, "需求变更": Nature.REQ,
            "Bug修复": Nature.DEF, "缺陷修复": Nature.DEF,
            "设计变更": Nature.OPT, "技术变更": Nature.OPT,
            "优化改进": Nature.OPT, "性能变更": Nature.OPT,
            "资源变更": Nature.CFG, "配置变更": Nature.CFG,
            "进度变更": Nature.CFG, "其他变更": Nature.CFG,
            "安全变更": Nature.EMRG, "紧急变更": Nature.EMRG,
        }
        nature = nature_map.get(old_type, Nature.OPT)

        if old_level:
            scope = IMPACT_LEVEL_TO_SCOPE_MAP.get(old_level.upper(), Scope.LOCAL)
        else:
            scope = Scope.LOCAL

        return domain, nature

    def get_approval_level_name(self) -> str:
        """获取当前scope对应的审批层级名称"""
        from src.core.constants import SCOPE_APPROVAL_MAP
        level = SCOPE_APPROVAL_MAP.get(self.scope)
        return level.value if level else "项目经理"

    def needs_reviewer(self) -> bool:
        """检查是否需要复审人(SYSTEM/CROSS/SAFE级必须)"""
        return self.scope in [Scope.SYSTEM, Scope.CROSS, Scope.SAFE]

    def get_scope_display(self) -> str:
        """获取带警告标记的范围显示名"""
        name = SCOPE_NAMES.get(self.scope, str(self.scope.value))
        warning = " ⚠️" if self.needs_reviewer() else ""
        return f"{name}{warning}"

    def to_v2_dict(self) -> dict:
        """导出为V2.1.0格式的字典(用于模板渲染)"""
        return {
            "change_id": self.change_id,
            "title": self.title,
            "domain": self.domain.value,
            "domain_name": DOMAIN_NAMES.get(self.domain, ""),
            "nature": self.nature.value,
            "nature_name": NATURE_NAMES.get(self.nature, ""),
            "scope": self.scope.value,
            "scope_display": self.get_scope_display(),
            "priority": self.priority,
            "reason": self.reason or "",
            "content_before": self.content_before or "",
            "content_after": self.content_after or "",
            "related_changes": self.related_changes or [],
            "propagation_chain": self.propagation_chain or "",
            "approval_level": self.get_approval_level_name(),
            "reviewer": self.reviewer or "",
            "status": self.status.value,
            "proposer": self.proposer or "",
            "approver": self.approver or "",
            "implementer": self.implementer or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else "",
        }
