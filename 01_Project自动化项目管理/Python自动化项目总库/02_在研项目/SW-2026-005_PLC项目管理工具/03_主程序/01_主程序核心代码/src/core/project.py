# -*- coding: utf-8 -*-
"""
Project数据模型

定义PLC项目的核心数据结构和属性。
一个Project代表一个完整的PLC工程项目，包含项目基本信息、
文档列表、PLC配置、HMI配置等。
"""
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .constants import (
    BusinessLine,
    ProjectStatus,
    ProjectType,
    WorkflowStage,
    PLCBrand,
    HMIBrand,
    PROJECT_STATUS_DESC,
)


@dataclass
class Project:
    """
    PLC项目数据模型

    Attributes:
        project_id: 项目唯一标识符 (UUID格式)
        code: 项目编号 (如 SW-2026-005-001)
        name: 项目名称
        description: 项目描述
        business_line: 业务线类型
        status: 项目状态
        plc_brand: PLC品牌
        hmi_brand: HMI品牌
        manager: 项目负责人
        created_at: 创建时间
        updated_at: 更新时间
        path: 项目根路径
        template_id: 使用的模板ID
        documents: 关联文档列表
        extra: 扩展属性字典
    """

    project_id: str = ""
    code: str = ""
    name: str = ""
    description: str = ""
    business_line: BusinessLine = BusinessLine.DEVICE
    status: ProjectStatus = ProjectStatus.PLANNING
    plc_brand: PLCBrand = PLCBrand.CODESYS
    hmi_brand: HMIBrand = HMIBrand.WEINVIEW
    manager: str = ""
    created_at: str = ""
    updated_at: str = ""
    path: str = ""
    template_id: str = ""
    project_type: ProjectType = ProjectType.GENERIC
    workflow_stage: WorkflowStage = WorkflowStage.INITIATION
    artifact_roots: List[Dict[str, Any]] = field(default_factory=list)
    change_status_summary: Dict[str, int] = field(default_factory=dict)
    documents: List[Dict[str, Any]] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """初始化后处理 - 自动设置时间戳"""
        if not self.project_id:
            import uuid
            self.project_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.updated_at:
            self.updated_at = self.created_at

    @property
    def status_display(self) -> str:
        """获取状态的中文描述"""
        return PROJECT_STATUS_DESC.get(self.status, self.status.value)

    @property
    def full_code(self) -> str:
        """获取完整的项目编号"""
        if self.code:
            return self.code
        return f"{self.business_line.value}-{datetime.now().strftime('%Y%m')}-XXX"

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        data = asdict(self)
        data["business_line"] = self.business_line.value
        data["status"] = self.status.value
        data["project_type"] = self.project_type.value
        data["workflow_stage"] = self.workflow_stage.value
        data["plc_brand"] = self.plc_brand.value
        data["hmi_brand"] = self.hmi_brand.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """从字典反序列化"""
        if "business_line" in data and isinstance(data["business_line"], str):
            data["business_line"] = BusinessLine(data["business_line"])
        if "status" in data and isinstance(data["status"], str):
            data["status"] = ProjectStatus(data["status"])
        if "project_type" in data and isinstance(data["project_type"], str):
            data["project_type"] = ProjectType(data["project_type"])
        if "workflow_stage" in data and isinstance(data["workflow_stage"], str):
            data["workflow_stage"] = WorkflowStage(data["workflow_stage"])
        if "plc_brand" in data and isinstance(data["plc_brand"], str):
            data["plc_brand"] = PLCBrand(data["plc_brand"])
        if "hmi_brand" in data and isinstance(data["hmi_brand"], str):
            data["hmi_brand"] = HMIBrand(data["hmi_brand"])
        return cls(**data)

    def save_to_file(self, file_path: str):
        """保存项目信息到JSON文件"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, file_path: str) -> Optional["Project"]:
        """从JSON文件加载项目信息"""
        path = Path(file_path)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def touch(self):
        """更新时间戳"""
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_document(self, doc_type: str, doc_name: str, doc_path: str):
        """添加关联文档"""
        self.documents.append({
            "type": doc_type,
            "name": doc_name,
            "path": doc_path,
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        self.touch()
