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

    UNIQUE_DOC_PATTERNS = {
        DocumentType.REQ: ["*REQ*.md", "*需求*.md"],
        DocumentType.DSN: ["*DSN*.md", "*设计*.md"],
        DocumentType.IFC: ["*IFC*.md", "*接口*.md"],
        DocumentType.UM: ["*UM*.md", "*手册*.md"],
        DocumentType.CHG: ["*CHG*.md", "*变更*.md"],
        DocumentType.ALM: ["*ALM*.md", "*报警*.md"],
        DocumentType.VAR: ["*VAR*.md", "*变量*.md"],
        DocumentType.IO: ["*IO*.md", "*IO分配*.md"],
        DocumentType.ARC: ["*ARC*.md", "*架构*.md"],
        DocumentType.TEST: ["*TEST*.md", "*测试*.md"],
        DocumentType.SUM: ["*SUM*.md", "*总结*.md"],
    }

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
        return cls.create_or_update_document(
            project_path=project_path,
            doc_type=doc_type,
            doc_name=doc_name,
            version=version,
            author=author,
            content=content,
        )

    @classmethod
    def create_or_update_document(
        cls,
        project_path: str,
        doc_type: DocumentType,
        doc_name: str = None,
        version: str = "V1.0.0",
        author: str = "",
        content: str = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        创建或更新项目文档

        优先更新现有权威文档，避免出现重复文档。
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
                DocumentType.SUM: "Summary",
            }

            target_dir = base / type_dirs.get(doc_type, ".")
            target_dir.mkdir(parents=True, exist_ok=True)

            # 文件名生成
            display_name = doc_name or DOCUMENT_TYPE_NAMES.get(doc_type, doc_type.name)
            safe_name = display_name.replace("/", "_").replace("\\", "_")
            existing_path = cls.find_authoritative_document(project_path, doc_type)
            file_path = (
                Path(existing_path)
                if existing_path
                else target_dir / f"{safe_name}_{version}.md"
            )

            # 内容处理
            if content is None:
                content = cls._get_template_content(doc_type, safe_name, version, author)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            action = "更新" if existing_path else "创建"
            logger.info(f"文档已{action}: {file_path} ({doc_type.value})")
            return str(file_path), None

        except Exception as e:
            logger.exception(f"文档创建失败: {e}")
            return None, str(e)

    @classmethod
    def find_authoritative_document(
        cls, project_path: str, doc_type: DocumentType
    ) -> Optional[str]:
        """查找同类型权威文档，避免重复创建"""
        project_root = Path(project_path)
        patterns = cls.UNIQUE_DOC_PATTERNS.get(doc_type, [])
        for pattern in patterns:
            matches = [
                path
                for path in project_root.rglob(pattern)
                if path.is_file()
                and ".trae" not in path.parts
                and ".plc-out" not in path.parts
            ]
            if matches:
                matches.sort(key=lambda path: len(path.parts))
                return str(matches[0])
        return None

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
            DocumentType.IFC: f"""# {title}

> 版本: {version} | 作者: {author} | 日期: {now}

## 1. 接口概述

### 1.1 范围
<!-- 描述本文档覆盖的接口范围与边界 -->

### 1.2 名词与缩写
| 缩写 | 全称 | 说明 |
|---|---|---|
| PLC | Programmable Logic Controller | 可编程逻辑控制器 |
| HMI | Human Machine Interface | 人机界面 |

## 2. 通信与协议

### 2.1 协议/链路
<!-- 例如 Profinet/ModbusTCP/OPC UA 等 -->

### 2.2 数据编码
<!-- 字节序、字符串编码、时间类型等 -->

## 3. 点表/信号定义

| 序号 | 名称 | 方向 | 数据类型 | 单位 | 取值范围 | 备注 |
|---|---|---|---|---|---|---|

## 4. 异常与超时

- 超时策略
- 重试策略
- 报警/告警联动
""",
            DocumentType.UM: f"""# {title}

> 版本: {version} | 作者: {author} | 日期: {now}

## 1. 简介

- 适用范围
- 读者对象

## 2. 快速开始

### 2.1 安装与启动

### 2.2 创建/打开项目

### 2.3 典型流程（建议演示）

1. 创建项目
2. 编辑/检查
3. 诊断
4. 生成交付文档

## 3. 功能说明

### 3.1 项目管理

### 3.2 规范检查

### 3.3 诊断分析

### 3.4 文档生成

### 3.5 测试管理

## 4. 常见问题

| 问题 | 原因 | 解决方法 |
|---|---|---|
""",
            DocumentType.CHG: f"""# {title}

> 版本: {version} | 作者: {author} | 日期: {now}

## 1. 变更摘要

| 变更编号 | 分类 | 标题 | 状态 |
|---|---|---|---|

## 2. 变更明细

### 2.1 变更原因

### 2.2 影响分析

### 2.3 验证方式

### 2.4 回退方案
""",
            DocumentType.ALM: f"""# {title}

> 版本: {version} | 作者: {author} | 日期: {now}

## 1. 报警码定义

| 报警码 | 严重等级 | 模块 | 描述 | 触发条件 | 复位条件 | 建议处理 |
|---|---|---|---|---|---|---|

## 2. 报警策略

- 去抖/延时策略
- 互锁与联动
- 报警历史与追溯
""",
            DocumentType.VAR: f"""# {title}

> 版本: {version} | 作者: {author} | 日期: {now}

## 1. 变量清单

| 名称 | 数据类型 | 作用域 | 初值 | 说明 | 备注 |
|---|---|---|---|---|---|

## 2. 变量命名规范

- 前缀规则
- 单位/量纲表达
- 保留字与禁用命名
""",
            DocumentType.IO: f"""# {title}

> 版本: {version} | 作者: {author} | 日期: {now}

## 1. IO分配表

| 点位 | 类型(DI/DO/AI/AO) | 地址 | 信号名称 | 设备/位置 | 备注 |
|---|---|---|---|---|---|

## 2. 说明

- 地址规划与预留策略
- 信号命名与跨系统一致性要求
""",
            DocumentType.ARC: f"""# {title}

> 版本: {version} | 作者: {author} | 日期: {now}

## 1. 架构概述

- 目标与范围
- 约束与假设

## 2. POU/模块划分

| 模块/POU | 职责 | 依赖 | 说明 |
|---|---|---|---|

## 3. 数据结构与变量域

- 全局变量
- 数据块(DB)组织

## 4. 关键流程

- 启动/初始化
- 主循环
- 故障处理
""",
            DocumentType.TEST: f"""# {title}

> 版本: {version} | 作者: {author} | 日期: {now}

## 1. 测试概述

- 测试范围
- 测试环境

## 2. 用例执行记录

| 用例ID | 用例名称 | 结果(PASS/FAIL) | 备注 |
|---|---|---|---|

## 3. 缺陷与结论

- 缺陷列表（如有）
- 测试结论
""",
            DocumentType.SUM: f"""# {title}

> 版本: {version} | 作者: {author} | 日期: {now}

## 1. 项目概况

- 项目背景与目标
- 交付范围

## 2. 实施总结

- 里程碑达成情况
- 关键问题与解决方案

## 3. 风险与经验

- 风险回顾
- 可复用经验

## 4. 后续建议
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
