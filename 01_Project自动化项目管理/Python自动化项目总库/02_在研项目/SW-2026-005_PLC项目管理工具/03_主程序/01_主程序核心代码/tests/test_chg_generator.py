"""ChgGenerator 单元测试"""

from __future__ import annotations

import os
import tempfile

import pytest

from src.generators.chg_generator import ChgGenerator
from src.models.change_request import ChangeRequest
from src.utils.file_utils import write_file


class TestChgGenerator:
    """变更单生成器测试"""

    def test_render_basic(self) -> None:
        """测试基本渲染"""
        cr = ChangeRequest(
            change_number="CHG-PLC-2026-001",
            project_id="TEST-2026-001",
            project_name="测试项目",
            domain="PLC",
            business_nature="DEF",
            impact_scope=["LOCAL", "MODULE"],
            applicant="张三",
            apply_date="2026-01-15",
            planned_date="2026-01-20",
            urgency="normal",
            background="测试变更背景",
            necessity="测试变更必要性",
            references="测试参考依据",
        )

        gen = ChgGenerator()
        content = gen.render(cr)

        assert "CHG-PLC-2026-001" in content
        assert "TEST-2026-001" in content
        assert "张三" in content
        assert "测试变更背景" in content
        assert "☑ **PLC**" in content
        assert "☑ **DEF**" in content
        assert "☑ **LOCAL**" in content
        assert "☑ **MODULE**" in content

    def test_render_urgency_critical(self) -> None:
        """测试紧急程度渲染"""
        cr = ChangeRequest(
            change_number="CHG-PLC-2026-002",
            project_id="TEST-2026-001",
            domain="PLC",
            business_nature="EMRG",
            impact_scope=["SAFE"],
            applicant="李四",
            urgency="critical",
            background="紧急变更",
            necessity="必须立即处理",
        )

        gen = ChgGenerator()
        content = gen.render(cr)

        assert "☑非常紧急" in content
        assert "☑ **EMRG**" in content
        assert "☑ **SAFE**" in content

    def test_save(self, tmp_dir: str) -> None:
        """测试保存文件"""
        cr = ChangeRequest(
            change_number="CHG-DOCU-2026-001",
            project_id="TEST-2026-001",
            domain="DOCU",
            business_nature="OPT",
            impact_scope=["LOCAL"],
            applicant="王五",
            urgency="normal",
            background="优化文档",
            necessity="提升可读性",
        )

        gen = ChgGenerator()
        file_path = os.path.join(tmp_dir, "CHG-DOCU", "CHG-DOCU-2026-001.md")
        result = gen.save(cr, file_path)

        assert os.path.isfile(result)
        with open(result, encoding="utf-8") as f:
            content = f.read()
        assert "CHG-DOCU-2026-001" in content

    def test_render_contains_all_sections(self) -> None:
        """测试渲染结果包含所有章节"""
        cr = ChangeRequest(
            change_number="CHG-PLC-2026-003",
            project_id="TEST-2026-001",
            domain="PLC",
            business_nature="DEF",
            impact_scope=["LOCAL"],
            applicant="测试",
            urgency="normal",
            background="测试",
            necessity="测试",
        )

        gen = ChgGenerator()
        content = gen.render(cr)

        # 检查所有章节标题
        assert "## 1. 文档基础信息" in content
        assert "## 2. 版本变更记录" in content
        assert "## 3. 变更基本信息" in content
        assert "### 3.0 编号与项目" in content
        assert "### 3.1 技术领域" in content
        assert "### 3.2 业务性质" in content
        assert "### 3.3 影响范围" in content
        assert "### 3.4 申请信息" in content
        assert "## 4. 变更原因" in content
        assert "## 5. 变更内容" in content
        assert "## 8. 变更审批" in content
        assert "## 9. 变更实施记录" in content
        assert "## 10. 变更验证" in content
