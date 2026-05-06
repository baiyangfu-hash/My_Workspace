# -*- coding: utf-8 -*-
"""
模板服务单元测试

测试TemplateService的核心功能：
- 内置模板初始化
- 模板加载与查询
- 模板应用到目标路径
"""
import pytest
import json
from pathlib import Path

from src.services.template_service import TemplateService


class TestTemplateServiceInit:
    """模板服务初始化测试"""

    def test_initialize_builtin_templates(self):
        """测试内置模板初始化不报错"""
        TemplateService._initialized = False  # 重置以便重新初始化
        TemplateService.initialize_builtin_templates()
        assert TemplateService._initialized is True

    def test_initialize_idempotent(self):
        """测试重复初始化幂等性"""
        TemplateService.initialize_builtin_templates()
        count_before = len(TemplateService._templates)
        TemplateService.initialize_builtin_templates()
        count_after = len(TemplateService._templates)
        assert count_before == count_after


class TestTemplateRetrieval:
    """模板查询功能测试"""

    def test_get_template_m001(self):
        """测试获取M001模板"""
        TemplateService.initialize_builtin_templates()
        tpl = TemplateService.get_template("TPL-SINGLE-PLC-M001")
        assert tpl is not None
        assert tpl.get("name") != ""

    def test_get_template_s001(self):
        """测试获取S001模板"""
        TemplateService.initialize_builtin_templates()
        tpl = TemplateService.get_template("TPL-SINGLE-PLC-S001")
        assert tpl is not None

    def test_get_nonexistent_template(self):
        """测试获取不存在的模板"""
        TemplateService.initialize_builtin_templates()
        tpl = TemplateService.get_template("NONEXISTENT")
        assert tpl is None

    def test_get_all_templates(self):
        """测试获取所有模板列表"""
        TemplateService.initialize_builtin_templates()
        all_tpls = TemplateService.get_all_templates()
        assert isinstance(all_tpls, list)
        assert len(all_tpls) >= 2  # 至少M001和S001

    def test_get_template_metadata(self):
        """测试获取模板元数据摘要"""
        TemplateService.initialize_builtin_templates()
        metadata = TemplateService.get_template_metadata()

        assert isinstance(metadata, list)
        # 元数据不应包含完整的structure字段(太大)
        for meta in metadata:
            assert "id" in meta
            assert "name" in meta
            assert "version" in meta
            assert "is_builtin" in meta


class TestTemplateApplication:
    """模板应用功能测试"""

    def test_apply_m001_template(self, tmp_path):
        """测试应用M001模板到目标路径"""
        TemplateService.initialize_builtin_templates()
        target = tmp_path / "TestProject_M001"

        success, message = TemplateService.apply_template(
            "TPL-SINGLE-PLC-M001",
            str(target),
            variables={"project_name": "TestProject"},
        )

        assert success is True
        assert target.exists()
        # 验证关键目录已创建
        expected_dirs = [
            "00_项目基础信息",
            "01_项目文档",
            "03_PLC程序",
            "05_变量清单",
        ]
        for dir_name in expected_dirs:
            assert (target / dir_name).exists(), \
                f"Expected directory missing: {dir_name}"

    def test_apply_s001_template(self, tmp_path):
        """测试应用S001精简版模板"""
        TemplateService.initialize_builtin_templates()
        target = tmp_path / "TestProject_S001"

        success, message = TemplateService.apply_template(
            "TPL-SINGLE-PLC-S001",
            str(target),
        )

        assert success is True
        assert target.exists()

    def test_apply_nonexistent_template(self, tmp_path):
        """测试应用不存在的模板"""
        TemplateService.initialize_builtin_templates()
        target = tmp_path / "TestProject_Bad"

        success, message = TemplateService.apply_template(
            "BAD_TEMPLATE_ID",
            str(target),
        )

        assert success is False
        assert "不存在" in message
