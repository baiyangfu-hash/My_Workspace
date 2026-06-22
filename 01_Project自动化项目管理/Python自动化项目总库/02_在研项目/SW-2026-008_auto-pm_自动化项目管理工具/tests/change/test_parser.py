"""ChgParser 单元测试"""

from __future__ import annotations

import os

import pytest

from auto_pm.change.parser import ChgParser
from auto_pm.utils.file_utils import write_file


class TestChgParser:
    """变更单解析器测试"""

    def test_parse_sample(self, sample_chg_content: str, tmp_dir: str) -> None:
        """测试解析样例变更单"""
        # 模拟 CHG-DOCU 目录结构
        chg_dir = os.path.join(tmp_dir, "CHG-DOCU")
        os.makedirs(chg_dir, exist_ok=True)
        file_path = os.path.join(chg_dir, "CHG-PLC-2026-001.md")
        write_file(file_path, sample_chg_content)

        parser = ChgParser()
        cr = parser.parse(file_path)

        assert cr.change_number == "CHG-PLC-2026-001"
        assert cr.project_id == "TEST-2026-001"
        assert cr.project_name == "TEST-2026-001 测试项目"
        assert cr.domain == "DOCU"  # 从路径提取
        assert cr.business_nature == "DEF"
        assert "LOCAL" in cr.impact_scope
        assert "MODULE" in cr.impact_scope
        assert cr.applicant == "张三"
        assert cr.apply_date == "2026-01-15"
        assert cr.planned_date == "2026-01-20"
        assert cr.urgency == "normal"
        assert cr.background != "待补充"
        assert cr.status == "approved"  # 有审批且通过

    def test_parse_real_file(self, chg_file: str) -> None:
        """测试解析真实变更单 CHG-DOCU-2026-001"""
        if not os.path.isfile(chg_file):
            pytest.skip("真实变更单文件不存在")

        parser = ChgParser()
        cr = parser.parse(chg_file)

        assert cr.change_number == "CHG-DOCU-2026-001"
        assert cr.domain == "DOCU"
        assert cr.business_nature == "DEF"
        assert "MODULE" in cr.impact_scope
        # 状态可能是 approved/completed/closed（取决于实施记录和验证）
        assert cr.status in ("approved", "implementing", "completed", "closed")

    def test_status_inference_draft(self, tmp_dir: str) -> None:
        """测试状态推断：无审批 → draft"""
        content = """# 变更单

## 3. 变更基本信息

### 3.0 编号与项目
| 字段 | 内容 |
|------|------|
| 变更编号 | CHG-PLC-2026-099 |

## 4. 变更原因

**变更背景**：
测试草稿
"""
        chg_dir = os.path.join(tmp_dir, "CHG-PLC")
        os.makedirs(chg_dir, exist_ok=True)
        file_path = os.path.join(chg_dir, "CHG-PLC-2026-099.md")
        write_file(file_path, content)

        parser = ChgParser()
        cr = parser.parse(file_path)

        assert cr.status == "draft"

    def test_status_inference_approved(self, tmp_dir: str) -> None:
        """测试状态推断：审批通过 → approved"""
        content = """# 变更单

## 3. 变更基本信息

### 3.0 编号与项目
| 字段 | 内容 |
|------|------|
| 变更编号 | CHG-PLC-2026-100 |

## 8. 变更审批

### 8.2 审批结论
| 结论 | ☑ 通过 |
"""
        chg_dir = os.path.join(tmp_dir, "CHG-PLC")
        os.makedirs(chg_dir, exist_ok=True)
        file_path = os.path.join(chg_dir, "CHG-PLC-2026-100.md")
        write_file(file_path, content)

        parser = ChgParser()
        cr = parser.parse(file_path)

        assert cr.status == "approved"

    def test_status_inference_rejected(self, tmp_dir: str) -> None:
        """测试状态推断：审批驳回 → rejected"""
        content = """# 变更单

## 3. 变更基本信息

### 3.0 编号与项目
| 字段 | 内容 |
|------|------|
| 变更编号 | CHG-PLC-2026-101 |

## 8. 变更审批

### 8.2 审批结论
| 结论 | □ 通过 ☑ 驳回(附原因) |
"""
        chg_dir = os.path.join(tmp_dir, "CHG-PLC")
        os.makedirs(chg_dir, exist_ok=True)
        file_path = os.path.join(chg_dir, "CHG-PLC-2026-101.md")
        write_file(file_path, content)

        parser = ChgParser()
        cr = parser.parse(file_path)

        assert cr.status == "rejected"

    def test_to_summary(self, sample_chg_content: str, tmp_dir: str) -> None:
        """测试转换为 ChangeSummary"""
        chg_dir = os.path.join(tmp_dir, "CHG-DOCU")
        os.makedirs(chg_dir, exist_ok=True)
        file_path = os.path.join(chg_dir, "CHG-PLC-2026-001.md")
        write_file(file_path, sample_chg_content)

        parser = ChgParser()
        cr = parser.parse(file_path)
        summary = parser.to_summary(cr)

        assert summary.change_number == cr.change_number
        assert summary.domain == cr.domain
        assert summary.status == cr.status
        assert len(summary.title) <= 53  # 50 + "..."

    def test_domain_extraction_from_path(self) -> None:
        """测试从路径提取领域"""
        parser = ChgParser()
        assert parser._extract_domain_from_path("/path/CHG-DOCU/CHG-DOCU-2026-001.md") == "DOCU"
        assert parser._extract_domain_from_path("/path/CHG-PLC/CHG-PLC-2026-001.md") == "PLC"

    def test_change_number_extraction(self) -> None:
        """测试变更编号提取"""
        parser = ChgParser()
        assert parser._extract_change_number("/path/CHG-DOCU-2026-001.md") == "CHG-DOCU-2026-001"
        assert parser._extract_change_number("/path/other.md") == ""

    def test_urgency_parsing(self, tmp_dir: str) -> None:
        """测试紧急程度解析"""
        content = """# 变更单

## 3. 变更基本信息

### 3.4 申请信息
| 字段 | 内容 |
|------|------|
| 变更申请人 | 张三 |
| 申请日期 | 2026-01-15 |
| 预计实施日期 | 2026-01-20 |
| 紧急程度 | □一般 ☑紧急 □非常紧急 |

## 8. 变更审批

### 8.2 审批结论
| 结论 | ☑ 通过 |
"""
        chg_dir = os.path.join(tmp_dir, "CHG-PLC")
        os.makedirs(chg_dir, exist_ok=True)
        file_path = os.path.join(chg_dir, "CHG-PLC-2026-200.md")
        write_file(file_path, content)

        parser = ChgParser()
        cr = parser.parse(file_path)

        assert cr.urgency == "urgent"
