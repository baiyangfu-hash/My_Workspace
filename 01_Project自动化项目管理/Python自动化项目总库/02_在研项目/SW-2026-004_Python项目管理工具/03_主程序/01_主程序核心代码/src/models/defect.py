# -*- coding: utf-8 -*-
"""
缺陷模型
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from src.models.base import BaseModel


class DefectStatus(enum.Enum):
    """缺陷状态枚举"""
    OPEN = "open"  # 打开
    IN_PROGRESS = "in_progress"  # 进行中
    FIXED = "fixed"  # 已修复
    VERIFIED = "verified"  # 已验证
    CLOSED = "closed"  # 已关闭
    REJECTED = "rejected"  # 已拒绝


class DefectPriority(enum.Enum):
    """缺陷优先级枚举"""
    HIGH = "high"  # 高
    MEDIUM = "medium"  # 中
    LOW = "low"  # 低


class DefectSeverity(enum.Enum):
    """缺陷严重程度枚举"""
    BLOCKER = "blocker"  # 阻塞
    CRITICAL = "critical"  # 严重
    MAJOR = "major"  # 主要
    MINOR = "minor"  # 次要
    TRIVIAL = "trivial"  # 轻微


class Defect(BaseModel):
    """缺陷模型"""
    __tablename__ = "defects"
    
    title = Column(String(255), nullable=False, comment="缺陷标题")
    description = Column(Text, nullable=False, comment="缺陷描述")
    status = Column(Enum(DefectStatus), default=DefectStatus.OPEN, nullable=False, comment="缺陷状态")
    priority = Column(Enum(DefectPriority), default=DefectPriority.MEDIUM, nullable=False, comment="缺陷优先级")
    severity = Column(Enum(DefectSeverity), default=DefectSeverity.MAJOR, nullable=False, comment="缺陷严重程度")
    reporter = Column(String(100), nullable=False, comment="报告人")
    assignee = Column(String(100), nullable=True, comment="负责人")
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, comment="关联项目ID")
    library_id = Column(Integer, ForeignKey("libraries.id"), nullable=True, comment="关联库ID")
    version = Column(String(50), nullable=True, comment="版本信息")
    environment = Column(String(255), nullable=True, comment="环境信息")
    steps_to_reproduce = Column(Text, nullable=True, comment="复现步骤")
    expected_behavior = Column(Text, nullable=True, comment="期望行为")
    actual_behavior = Column(Text, nullable=True, comment="实际行为")
    attachments = Column(Text, nullable=True, comment="附件信息")
    resolution = Column(Text, nullable=True, comment="解决方案")
    fix_version = Column(String(50), nullable=True, comment="修复版本")
    
    # 关系
    project = relationship("Project", backref="defects")
    library = relationship("Library", backref="defects")
