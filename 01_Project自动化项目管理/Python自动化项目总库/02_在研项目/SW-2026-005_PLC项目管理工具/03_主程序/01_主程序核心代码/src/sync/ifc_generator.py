# -*- coding: utf-8 -*-
"""
IFC 接口文档半自动生成器

从 GlobalVars.db 中提取 STRUCT 变量定义，生成标准 Markdown 接口文档。
半自动模式：生成 → 人工审核补充(来源列/状态机/地址映射) → 替换正式文档。
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.sync.db_parser import DbParser, StructGroup, VarRecord
from src.sync.version_extractor import VersionExtractor
from src.sync.fb_registry import resolve_title_cn, resolve_file_prefix, resolve_struct_key
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class IfcGenerator:
    """IFC 接口文档半自动生成器"""

    @classmethod
    def generate(cls, db_path: str, fb_name: str,
                 output_dir: str = None) -> str:
        groups = DbParser.parse_db_file(db_path)
        if not groups:
            logger.error("DB 解析无结果")
            return ""

        matched = cls._match_groups(groups, fb_name)
        if not matched:
            logger.error(f"未找到匹配的结构体: {fb_name}")
            return ""

        db_version = VersionExtractor.extract_scl_version(db_path) or "V?.?.?"

        title = cls._resolve_title(fb_name)
        prefix = cls._resolve_file_prefix(fb_name)

        doc = cls._render_document(title, db_version, matched, prefix)

        out = Path(output_dir) if output_dir else Path(db_path).parent / "PRD"
        out.mkdir(parents=True, exist_ok=True)
        filename = f"接口文档_IFC-{prefix}-{db_version}-GENERATED.md"
        filepath = out / filename
        filepath.write_text(doc, encoding="utf-8")

        logger.info(f"IFC 文档已生成: {filepath}")
        return str(filepath)

    @classmethod
    def _match_groups(cls, groups: List[StructGroup], fb_name: str) -> List[StructGroup]:
        fb_lower = fb_name.lower()
        struct_key = resolve_struct_key(fb_name)
        if struct_key is not None:
            if struct_key == "__ALL__":
                return groups
            for g in groups:
                if g.name.lower() == struct_key:
                    return [g]
            return []
        return []

    @classmethod
    def _resolve_title(cls, fb_name: str) -> str:
        return resolve_title_cn(fb_name)

    @classmethod
    def _resolve_file_prefix(cls, fb_name: str) -> str:
        return resolve_file_prefix(fb_name)

    @classmethod
    def _render_document(cls, title: str, version: str,
                         groups: List[StructGroup], prefix: str) -> str:
        lines = []
        lines.append(f"# 接口文档 {title}")
        lines.append("")
        lines.append("## 0. 文档基础信息")
        lines.append("")
        lines.append("| 属性 | 值 |")
        lines.append("|------|-----|")
        lines.append(f"| **文档标题** | {title} 接口定义 |")
        lines.append(f"| **文档版本** | {version} |")
        lines.append(f"| **数据来源** | GlobalVars.db {version} |")
        lines.append(f"| **编制日期** | {datetime.now().strftime('%Y-%m-%d')} |")
        lines.append(f"| **生成方式** | 半自动(ifc_generator.py) — 需人工审核补充 |")
        lines.append("")

        lines.append("## 1. 功能概述")
        lines.append("")
        lines.append("> [待人工补充: 功能块总体描述]")
        lines.append("")

        total_input = sum(g.input_count for g in groups)
        total_output = sum(g.output_count for g in groups)

        for g in groups:
            lines.append(f"## 2. {g.name} 接口 ({g.input_count}输入 / {g.output_count}输出)")
            lines.append("")

            if g.description:
                lines.append(f"**说明**: {g.description}")
                lines.append("")

            input_vars = [v for v in g.variables
                          if v.name.startswith(("i_", "I_"))]
            output_vars = [v for v in g.variables
                           if v.name.startswith(("o_", "O_", "q_", "Q_"))]

            if input_vars:
                lines.append(f"### 2.1 VAR_INPUT ({len(input_vars)}个)")
                lines.append("")
                lines.append("| 名称 | 类型 | 默认值 | 说明 | 来源 |")
                lines.append("|------|------|--------|------|------|")
                for v in input_vars:
                    t = cls._short_type(v.type_)
                    lines.append(f"| {v.name} | {t} | {v.default or '-'} | {v.comment} | [待补充] |")
                lines.append("")

            if output_vars:
                lines.append(f"### 2.2 VAR_OUTPUT ({len(output_vars)}个)")
                lines.append("")
                lines.append("| 名称 | 类型 | 默认值 | 说明 | 目标 |")
                lines.append("|------|------|--------|------|------|")
                for v in output_vars:
                    t = cls._short_type(v.type_)
                    lines.append(f"| {v.name} | {t} | {v.default or '-'} | {v.comment} | [待补充] |")
                lines.append("")

        lines.append("---")
        lines.append("")
        lines.append(f"> **接口统计**: {total_input}输入 + {total_output}输出")
        lines.append(f"> **数据来源**: GlobalVars.db {version} → ifc_generator.py 自动生成")
        lines.append(f"> **⚠ 本文件由 IFC 生成器自动生成，请人工审核后替换正式文档**")
        lines.append("")
        lines.append("**人工审核清单**:")
        lines.append("- [ ] 补充 §1 功能概述")
        lines.append("- [ ] 补全所有 [待补充] 来源/目标列")
        lines.append("- [ ] 添加状态机步序常量表 (如有)")
        lines.append("- [ ] 添加地址映射信息 (D寄存器/Y地址)")
        lines.append("- [ ] 确认变量分类正确 (输入/输出)")
        lines.append("- [ ] 确认版本号与代码一致")

        return "\n".join(lines)

    @classmethod
    def _short_type(cls, type_: str) -> str:
        if "ARRAY" in type_.upper():
            return type_.strip()
        return type_.strip()