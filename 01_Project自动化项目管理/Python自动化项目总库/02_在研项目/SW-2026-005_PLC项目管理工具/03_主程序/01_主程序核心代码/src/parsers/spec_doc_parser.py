# -*- coding: utf-8 -*-
"""
规范文档解析器模块

专门用于解析Markdown格式的PLC编程规范文档，
提取规则定义、检查项和要求说明。
支持单文件解析和批量目录扫描。
"""
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class SpecRule:
    """
    从规范文档提取的单条规则数据类

    Attributes:
        rule_id: 规则标识符 (如 REQ-NAMING-001)
        title: 规则标题
        content: 规则详细内容
        category: 规则分类 (如 naming, structure, safety)
        priority: 优先级 (high/medium/low)
        severity: 建议的严重级别 (error/warning/info)
        tags: 标签列表
        source_file: 来源文件路径
        line_number: 在源文件中的起始行号
    """
    rule_id: str
    title: str
    content: str
    category: str = "general"
    priority: str = "medium"
    severity: str = "warning"
    tags: List[str] = field(default_factory=list)
    source_file: str = ""
    line_number: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "priority": self.priority,
            "severity": self.severity,
            "tags": self.tags,
            "source_file": str(self.source_file),
            "line_number": self.line_number,
        }


class SpecDocParser:
    """
    Markdown格式规范文档解析器

    功能:
    - 解析Markdown格式的PLC编程规范文档
    - 提取结构化的规则定义
    - 支持多种规则标记格式
    - 提供规范概要统计

    支持的规则格式示例:

    ### [REQ-NAMING-001] 变量命名规范
    **优先级**: high
    **严重级别**: error
    **标签**: naming, convention

    详细规则内容...

    或简化格式:

    #### RULE-001: 函数长度限制
    - 优先级: medium
    - 严重级别: warning

    规则描述...
    """

    # 正则表达式模式集合
    # 匹配标准规则标题: ### [RULE_ID] Title 或 ### RULE_ID: Title
    RE_RULE_HEADER = re.compile(
        r"^#{2,4}\s+"
        r"(?:\[([A-Za-z0-9_-]+)\]\s*|([A-Za-z0-9_-]+)\s*:\s*)"
        r"(.+?)$",
        re.MULTILINE,
    )

    # 匹配元数据行: **Key**: Value 或 - Key: Value
    RE_METADATA = re.compile(
        r"(?:^\*{2}|^-)\s*(优先级|严重级别|类别|标签|Priority|Severity|Category|Tags)"
        r"\*{0,2}\s*[:：]\s*(.+)$",
        re.MULTILINE | re.IGNORECASE,
    )

    # 匹配规则内容（到下一个同级或更高级标题为止）
    RE_SECTION_CONTENT = re.compile(
        r"(^#{2,4}\s+.+?$)(.*?)(?=\n#{2,4}\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )

    def __init__(self):
        """初始化解析器"""
        self._rules: List[SpecRule] = []
        self._parsed_files: List[str] = []
        self._parse_errors: List[Dict] = []

    def parse_file(self, file_path: str) -> List[SpecRule]:
        """
        解析单个规范文档文件

        Args:
            file_path: Markdown文件路径

        Returns:
            List[SpecRule]: 提取的规则列表

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件格式不支持
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"规范文件不存在: {file_path}")

        if path.suffix.lower() not in [".md", ".markdown", ".txt"]:
            raise ValueError(
                f"不支持的文件格式: {path.suffix}, "
                f"仅支持 .md/.markdown/.txt"
            )

        logger.info(f"开始解析规范文件: {file_path}")

        try:
            content = path.read_text(encoding="utf-8")
            rules = self._parse_content(content, str(path.absolute()))
            self._parsed_files.append(file_path)
            self._rules.extend(rules)

            logger.info(
                f"文件解析完成: {file_path}, "
                f"提取 {len(rules)} 条规则"
            )
            return rules

        except Exception as e:
            error_info = {
                "file": file_path,
                "error": str(e),
                "time": datetime.now().isoformat(),
            }
            self._parse_errors.append(error_info)
            logger.exception(f"解析文件出错: {file_path}, 错误: {e}")
            raise

    def parse_directory(
        self,
        directory: str,
        recursive: bool = True,
        pattern: str = "*.md",
    ) -> List[SpecRule]:
        """
        解析目录下的所有规范文档

        Args:
            directory: 目录路径
            recursive: 是否递归子目录
            pattern: 文件匹配模式 (glob风格)

        Returns:
            List[SpecRule]: 所有文件提取的规则列表
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")

        if not dir_path.is_dir():
            raise NotADirectoryError(f"路径不是目录: {directory}")

        logger.info(
            f"开始扫描规范目录: {directory} "
            f"(递归={recursive}, 模式={pattern})"
        )

        all_rules: List[SpecRule] = []

        if recursive:
            files = list(dir_path.rglob(pattern))
        else:
            files = list(dir_path.glob(pattern))

        # 过滤掉隐藏文件和非目标文件
        files = [
            f for f in files
            if not f.name.startswith(".")
            and f.suffix.lower() in [".md", ".markdown", ".txt"]
        ]

        logger.info(f"发现 {len(files)} 个规范文件")

        for file_path in sorted(files):
            try:
                rules = self.parse_file(str(file_path))
                all_rules.extend(rules)
            except Exception as e:
                logger.warning(
                    f"跳过文件 {file_path} (原因: {e})"
                )
                continue

        logger.info(
            f"目录解析完成: 共提取 {len(all_rules)} 条规则"
        )
        return all_rules

    def _parse_content(
        self, content: str, source_file: str = ""
    ) -> List[SpecRule]:
        """
        解析文档内容并提取规则

        Args:
            content: 文档文本内容
            source_file: 来源文件路径

        Returns:
            List[SpecRule]: 提取的规则列表
        """
        rules = []
        lines = content.splitlines()

        # 查找所有规则标题位置
        for match in self.RE_RULE_HEADER.finditer(content):
            rule_id_bracket = match.group(1)  # [ID] 格式
            rule_id_colon = match.group(2)     # ID: 格式
            title = match.group(3).strip()

            # 确定规则ID
            rule_id = rule_id_bracket or rule_id_colon
            if not rule_id:
                continue

            start_pos = match.start()
            line_num = content[:start_pos].count("\n") + 1

            # 提取该规则的内容块（到下一个同级标题或文件末尾）
            end_pos = self._find_section_end(content, start_pos)
            section_text = content[start_pos:end_pos]

            # 解析元数据和正文
            metadata = self._extract_metadata(section_text)
            body_content = self._extract_body(section_text)

            # 创建规则对象
            rule = SpecRule(
                rule_id=rule_id.strip(),
                title=title,
                content=body_content.strip(),
                category=metadata.get("category", "general").lower(),
                priority=metadata.get("priority", "medium").lower(),
                severity=metadata.get("severity", "warning").lower(),
                tags=self._parse_tags(metadata.get("tags", "")),
                source_file=source_file,
                line_number=line_num,
            )

            rules.append(rule)

        return rules

    def _find_section_end(
        self, content: str, start_pos: int
    ) -> int:
        """
        查找当前章节的结束位置

        结束条件: 遇到同级别或更高级别的标题，或到达文件末尾

        Args:
            content: 完整文档内容
            start_pos: 当前章节开始位置

        Returns:
            int: 章节结束位置
        """
        # 获取当前标题级别
        header_match = re.match(
            r"^(#{2,4})\s+", content[start_pos:], re.MULTILINE
        )
        if not header_match:
            return len(content)

        current_level = len(header_match.group(1))

        # 搜索下一个同级或更高级别标题
        pos = start_pos + header_match.end()
        while pos < len(content):
            next_header = re.match(
                r"^(#{2,4})\s+", content[pos:], re.MULTILINE
            )
            if next_header:
                next_level = len(next_header.group(1))
                if next_level <= current_level:
                    return pos
                pos += next_header.end()
            else:
                pos += 1

        return len(content)

    def _extract_metadata(self, section_text: str) -> Dict[str, str]:
        """
        从章节文本中提取元数据

        Args:
            section_text: 章节文本

        Returns:
            Dict: 元数据键值对
        """
        metadata = {}

        for match in self.RE_METADATA.finditer(section_text):
            key = match.group(1).strip().lower()
            value = match.group(2).strip()

            # 标准化键名映射
            key_mapping = {
                "优先级": "priority",
                "严重级别": "severity",
                "类别": "category",
                "标签": "tags",
            }
            normalized_key = key_mapping.get(key, key)
            metadata[normalized_key] = value

        return metadata

    def _extract_body(self, section_text: str) -> str:
        """
        提取规则正文内容（去除标题和元数据）

        Args:
            section_text: 章节文本

        Returns:
            str: 正文内容
        """
        lines = section_text.splitlines()[1:]  # 去除标题行
        body_lines = []
        in_metadata = False

        for line in lines:
            stripped = line.strip()

            # 跳过元数据行
            if self.RE_METADATA.match(line):
                continue

            # 跳过空行（但保留段落分隔）
            if not stripped:
                if body_lines and body_lines[-1].strip():
                    body_lines.append("")
                continue

            body_lines.append(line)

        return "\n".join(body_lines).strip()

    def _parse_tags(self, tags_string: str) -> List[str]:
        """
        解析标签字符串

        支持逗号、分号或空格分隔的多个标签

        Args:
            tags_string: 标签字符串

        Returns:
            List[str]: 清洗后的标签列表
        """
        if not tags_string:
            return []

        separators = [",", ";", "，", "；"]
        tags = tags_string

        for sep in separators:
            if sep in tags:
                tags = tags.replace(sep, ",")

        return [t.strip().lower() for t in tags.split(",") if t.strip()]

    def get_spec_summary(self) -> Dict[str, Any]:
        """
        获取当前已加载规范的概要统计

        Returns:
            Dict: 包含统计信息的字典:
                - total_rules: 总规则数
                - categories: 各类别规则数
                - priorities: 各优先级规则数
                - severities: 各严重级别规则数
                - parsed_files: 已解析的文件列表
                - parse_errors: 解析错误列表
        """
        from collections import Counter

        category_counts = Counter(r.category for r in self._rules)
        priority_counts = Counter(r.priority for r in self._rules)
        severity_counts = Counter(r.severity for r in self._rules)

        return {
            "total_rules": len(self._rules),
            "categories": dict(category_counts),
            "priorities": dict(priority_counts),
            "severities": dict(severity_counts),
            "parsed_files": self._parsed_files,
            "parse_errors": self._parse_errors,
            "load_time": datetime.now().isoformat(),
        }

    def get_rules_by_category(self, category: str) -> List[SpecRule]:
        """
        按类别获取规则

        Args:
            category: 类别名

        Returns:
            List[SpecRule]: 该类别下的规则列表
        """
        return [r for r in self._rules if r.category == category.lower()]

    def get_rule_by_id(self, rule_id: str) -> Optional[SpecRule]:
        """
        按ID查找规则

        Args:
            rule_id: 规则ID

        Returns:
            Optional[SpecRule]: 规则对象，不存在返回None
        """
        for rule in self._rules:
            if rule.rule_id.lower() == rule_id.lower():
                return rule
        return None

    def search_rules(self, keyword: str) -> List[SpecRule]:
        """
        搜索规则（在标题和内容中搜索关键词）

        Args:
            keyword: 搜索关键词

        Returns:
            List[SpecRule]: 匹配的规则列表
        """
        keyword_lower = keyword.lower()
        return [
            r for r in self._rules
            if keyword_lower in r.title.lower()
            or keyword_lower in r.content.lower()
        ]

    @property
    def rules(self) -> List[SpecRule]:
        """获取所有已解析的规则"""
        return self._rules.copy()

    @property
    def parsed_files_count(self) -> int:
        """获取已解析的文件数量"""
        return len(self._parsed_files)

    def clear(self) -> None:
        """清空所有已解析的数据"""
        self._rules.clear()
        self._parsed_files.clear()
        self._parse_errors.clear()
        logger.info("解析器数据已清空")

    def __len__(self) -> int:
        """返回规则总数"""
        return len(self._rules)
