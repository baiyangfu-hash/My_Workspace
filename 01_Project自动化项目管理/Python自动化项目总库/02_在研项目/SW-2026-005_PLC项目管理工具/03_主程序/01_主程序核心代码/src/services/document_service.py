# -*- coding: utf-8 -*-
"""
文档服务 - 管理项目文档的生命周期

提供文档的创建、编辑、版本管理和导出功能。
支持基于Markdown模板生成标准化工程文档。
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from src.core.constants import DocumentType, DOCUMENT_TYPE_NAMES
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DocumentService:
    """文档服务类 - 管理PLC项目全生命周期的工程文档"""

    @classmethod
    def create_document(
        cls,
        project_path: str,
        doc_type: DocumentType,
        doc_name: str = None,
        version: str = "V1.0.0",
        author: str = "",
        content: str = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        在项目中创建新文档

        Args:
            project_path: 项目根路径
            doc_type: 文档类型枚举
            doc_name: 自定义文档名称 (为None时使用默认名称)
            version: 文档版本号
            author: 文档作者
            content: 文档初始内容 (为None时使用模板)

        Returns:
            Tuple[str | None, str | None]: (文档路径, 错误信息)
        """
        try:
            base = Path(project_path) / "02_Documents"

            # 根据文档类型确定子目录
            type_dirs = {
                DocumentType.REQ: "Requirements",
                DocumentType.DSN: "Design",
                DocumentType.IFC: "Interface",
                DocumentType.UM: "UserManual",
                DocumentType.CHG: ".",          # 放在Documents根目录
                DocumentType.ALM: "../07_Alarms",
                DocumentType.VAR: "../05_Variables",
                DocumentType.IO: "../06_IO_Allocation",
                DocumentType.ARC: "Design",
                DocumentType.TEST: "../08_TestReports",
            }

            target_dir = base / type_dirs.get(doc_type, ".")
            target_dir.mkdir(parents=True, exist_ok=True)

            # 文件名生成
            display_name = doc_name or DOCUMENT_TYPE_NAMES.get(doc_type, doc_type.name)
            safe_name = display_name.replace("/", "_").replace("\\", "_")
            file_name = f"{safe_name}_{version}.md"
            file_path = target_dir / file_name

            # 内容处理
            if content is None:
                content = cls._get_template_content(doc_type, safe_name, version, author)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"文档已创建: {file_path} ({doc_type.value})")
            return str(file_path), None

        except Exception as e:
            logger.exception(f"文档创建失败: {e}")
            return None, str(e)

    @classmethod
    def _get_template_content(
        cls,
        doc_type: DocumentType,
        title: str,
        version: str,
        author: str,
    ) -> str:
        """根据文档类型获取模板内容"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        templates = {
            DocumentType.REQ: f"""# {title}

> 版本: {version} | 作者: {author} | 日期: {now}

## 1. 引言

### 1.1 编写目的
<!-- 说明本文档的编写目的和预期读者 -->

### 1.2 项目背景
<!-- 描述项目的来源、背景和业务需求 -->

### 1.3 术语定义
| 术语 | 全称 | 说明 |
|------|------|------|
| PLC | Programmable Logic Controller | 可编程逻辑控制器 |
| ST | Structured Text | 结构化文本语言 |
| HMI | Human Machine Interface | 人机界面 |

## 2. 功能需求

### 2.1 功能概述
<!-- 列出系统的主要功能点 -->

### 2.2 功能详细描述
<!-- 逐条描述每个功能的输入、处理、输出 -->

## 3. 非功能需求

### 3.1 性能要求
<!-- 响应时间、吞吐量等指标 -->

### 3.2 安全要求
<!-- 安全相关需求描述 -->

## 4. 接口需求

### 4.1 PLC接口
<!-- 与上位机/HMI的通信接口 -->

### 4.2 IO接口
<!-- 输入输出信号清单 -->
""",
            DocumentType.DSN: f"""# {title}

> 版本: {version} | 作者: {author} | 日期: {now}

## 1. 设计概述

### 1.1 系统架构
<!-- 整体架构设计说明 -->

### 1.2 技术选型
| 组件 | 选型 | 版本 |
|------|------|------|
| PLC品牌 | | |
| 编程软件 | | |
| 通信协议 | | |

## 2. 软件设计

### 2.1 POU结构设计
<!-- Program/Organization Unit 的层次结构 -->

### 2.2 主要功能块设计
<!-- 关键FB的设计说明 -->

### 2.3 变量设计
<!-- 全局变量和数据结构设计 -->

## 3. 硬件设计

### 3.1 IO分配表
<!-- DI/DO/AI/AO 详细分配 -->

### 3.2 网络拓扑
<!-- 网络连接关系图 -->
""",
        }

        return templates.get(doc_type, f"# {title}\n\n> 版本: {version}\n\n<!-- 请填写内容 -->")

    @classmethod
    def read_document(cls, file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """读取文档内容"""
        try:
            path = Path(file_path)
            if not path.exists():
                return None, "文件不存在"
            with open(path, "r", encoding="utf-8") as f:
                return f.read(), None
        except Exception as e:
            return None, str(e)

    @classmethod
    def save_document(cls, file_path: str, content: str) -> Tuple[bool, Optional[str]]:
        """保存文档内容"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, None
        except Exception as e:
            return False, str(e)

    @classmethod
    def list_documents(cls, project_path: str) -> List[Dict]:
        """列出项目下的所有文档"""
        docs_dir = Path(project_path) / "02_Documents"
        documents = []

        if not docs_dir.exists():
            return documents

        for md_file in docs_dir.rglob("*.md"):
            documents.append({
                "name": md_file.stem,
                "path": str(md_file),
                "relative_path": str(md_file.relative_to(docs_dir)),
                "size": md_file.stat().st_size,
                "modified": datetime.fromtimestamp(md_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            })

        return sorted(documents, key=lambda x: x["name"])
