# -*- coding: utf-8 -*-
"""
Template数据模型 - 项目模板数据模型

定义项目模板的结构化配置格式，
用于驱动新项目的目录结构和初始文件生成。
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class TemplateFileItem:
    """模板中的单个文件项"""
    name: str = ""
    content: str = ""
    description: str = ""


@dataclass
class TemplateDirectoryItem:
    """模板中的目录项"""
    name: str = ""
    description: str = ""
    structure: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TemplateModel:
    """
    项目模板数据模型

    定义一个完整的项目结构模板，
    包含目录层次和默认文件内容。
    """

    id: str = ""
    name: str = ""
    version: str = "V1.0.0"
    description: str = ""
    business_lines: List[str] = field(default_factory=list)
    is_builtin: bool = True
    directories: List[TemplateDirectoryItem] = field(default_factory=list)
    files: List[TemplateFileItem] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)

    def to_structure_dict(self) -> Dict[str, Any]:
        """转换为可序列化的结构字典（供TemplateService使用）"""
        dir_structs = []
        for d in self.directories:
            d_dict = {
                "name": d.name,
                "description": d.description,
                "structure": d.structure,
            }
            dir_structs.append(d_dict)

        file_list = []
        for f in self.files:
            f_dict = {
                "name": f.name,
                "content": f.content,
                "description": f.description,
            }
            file_list.append(f_dict)

        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "business_lines": self.business_lines,
            "is_builtin": self.is_builtin,
            "directories": dir_structs,
            "files": file_list,
            "config": self.config,
        }
