"""ProjParser 单元测试"""

from __future__ import annotations

import os
import tempfile

import pytest

from src.parsers.proj_parser import ProjParser
from src.utils.file_utils import write_file


class TestProjParser:
    """立项表解析器测试"""

    def test_parse_sample(self, sample_proj_content: str, tmp_dir: str) -> None:
        """测试解析样例立项表"""
        file_path = os.path.join(tmp_dir, "003_TEST-2026-001_项目立项表_PROJ.md")
        write_file(file_path, sample_proj_content)

        parser = ProjParser()
        info = parser.parse(file_path)

        assert info.name == "TEST-2026-001 测试项目 V1.0.0"
        assert info.business_desc == "这是一个测试项目"
        assert info.important_note == "仅用于测试"
        assert info.process_scope == "测试 / 验证"
        assert info.customer == "待补充"
        assert info.platform == "测试平台"
        assert info.plc_model == "测试PLC"
        assert info.axes == "X1 单轴"
        assert info.precision == "±0.5mm"
        assert info.safety_protection == "急停保护"
        assert info.module_count == "2"
        assert info.phase == "developing"
        assert info.start_date == "2026-01-01"
        assert info.end_date == "2026-06-30"
        assert info.duration_days == "180 天"
        assert info.proj_file_path == file_path

    def test_parse_real_file(self, proj_file: str) -> None:
        """测试解析真实立项表 DJ-2026-005"""
        if not os.path.isfile(proj_file):
            pytest.skip("真实立项表文件不存在")

        parser = ProjParser()
        info = parser.parse(proj_file)

        assert info.name != "待补充"
        assert "DJ-2026-005" in info.name or "边框缓存机" in info.name
        assert info.platform != "待补充"
        assert info.plc_model != "待补充"
        assert info.phase != "待补充"
        assert len(info.risks) > 0

    def test_parse_empty_file(self, tmp_dir: str) -> None:
        """测试解析空文件"""
        file_path = os.path.join(tmp_dir, "empty.md")
        write_file(file_path, "")

        parser = ProjParser()
        info = parser.parse(file_path)

        assert info.name == "待补充"
        assert info.phase == "待补充"

    def test_placeholder_handling(self, tmp_dir: str) -> None:
        """测试占位符处理"""
        content = """# 测试

## 3. 业务身份

| 字段 | 内容 |
|------|------|
| **项目名称** | （待补充） |
| **业务描述** | （待扫描统计） |
| **客户/产线** | （待从变更管理系统读取） |
"""
        file_path = os.path.join(tmp_dir, "placeholder.md")
        write_file(file_path, content)

        parser = ProjParser()
        info = parser.parse(file_path)

        assert info.name == "待补充"
        assert info.business_desc == "待补充"
        assert info.customer == "待补充"

    def test_section_split(self, sample_proj_content: str, tmp_dir: str) -> None:
        """测试章节拆分"""
        file_path = os.path.join(tmp_dir, "sections.md")
        write_file(file_path, sample_proj_content)

        parser = ProjParser()
        sections = parser._split_sections(sample_proj_content)

        assert "3" in sections
        assert "4" in sections
        assert "5" in sections
        assert "6" in sections
        assert "7" in sections

    def test_table_parse(self) -> None:
        """测试表格解析"""
        parser = ProjParser()
        table_text = """
| 字段 | 内容 |
|------|------|
| **项目名称** | 测试项目 |
| **业务描述** | 这是一个测试 |
"""
        result = parser._parse_table(table_text)
        assert result["项目名称"] == "测试项目"
        assert result["业务描述"] == "这是一个测试"

    def test_risk_extraction(self, sample_proj_content: str) -> None:
        """测试风险评估提取"""
        parser = ProjParser()
        sections = parser._split_sections(sample_proj_content)
        key = "附录 A" if "附录 A" in sections else "附录A"
        if key in sections:
            risks = parser._extract_risks(sections[key])
            assert len(risks) >= 1
            assert risks[0].risk_item != ""
            assert risks[0].level != ""

    def test_project_scope_extraction(self, sample_proj_content: str) -> None:
        """测试项目范围提取"""
        parser = ProjParser()
        sections = parser._split_sections(sample_proj_content)
        if "5" in sections:
            scope = parser._extract_list_items(sections["5"], "项目范围")
            assert "PLC 程序开发" in scope
