"""变更单 Markdown 文件生成器"""

from __future__ import annotations

import datetime

from src.models.change_request import ChangeRequest
from src.models.spec_constants import (
    DOMAINS,
    BUSINESS_NATURES,
    IMPACT_SCOPES,
    URGENCY_LEVELS,
    DOMAIN_DESCRIPTIONS,
    BUSINESS_NATURE_DESCRIPTIONS,
    IMPACT_SCOPE_DESCRIPTIONS,
)
from src.utils.file_utils import write_file
from src.utils.logger import get_logger

log = get_logger(__name__)


class ChgGenerator:
    """变更单 Markdown 文件生成器"""

    def render(self, cr: ChangeRequest) -> str:
        """渲染变更单 Markdown 内容"""
        log.info("渲染变更单: %s, domain=%s, nature=%s",
                 cr.change_number, cr.domain, cr.business_nature)
        today = datetime.date.today().isoformat()

        # 影响范围选择行
        scope_lines = self._render_scope_options(cr.impact_scope)
        # 领域选择行
        domain_lines = self._render_domain_options(cr.domain)
        # 业务性质选择行
        nature_lines = self._render_nature_options(cr.business_nature)
        # 紧急程度
        urgency_lines = self._render_urgency(cr.urgency)

        content = f"""# 变更单

## 1. 文档基础信息

**文档标题**：变更单
**文档版本**：V1.0.0
**编制日期**：{today}
**编制人**：{cr.applicant}
**审核人**：

## 2. 版本变更记录

| 版本号 | 变更内容 | 变更人 | 变更日期 | 详细说明 |
|--------|----------|--------|----------|----------|
| V1.0.0 | 初始版本 | {cr.applicant} | {today} | 变更单创建 |

## 3. 变更基本信息

### 3.0 编号与项目
| 字段 | 内容 |
|------|------|
| 变更编号 | {cr.change_number} |
| 项目名称 | {cr.project_name} |
| 项目编号 | {cr.project_id} |

### 3.1 技术领域（必选）
{domain_lines}

### 3.2 业务性质（必选）
{nature_lines}

### 3.3 影响范围（可多选）
{scope_lines}

### 3.4 申请信息
| 字段 | 内容 |
|------|------|
| 变更申请人 | {cr.applicant} |
| 申请日期 | {cr.apply_date} |
| 预计实施日期 | {cr.planned_date} |
| 紧急程度 | {urgency_lines} |
| 变更状态 | {cr.status} |

## 4. 变更原因

**变更背景**：
{cr.background}

**变更必要性**：
{cr.necessity}

**参考依据**：
{cr.references}

## 5. 变更内容

### 5.1 变更前（当前状态）

| 项目 | 当前值/描述 |
|------|-----------|
| 涉及文件/交付物 | （待填写） |
| 关键参数/配置 | （待填写） |

### 5.2 变更后（目标状态）

| 项目 | 目标值/描述 |
|------|-----------|
| 涉及文件/交付物 | （待填写） |
| 关键参数/配置 | （待填写） |

## 6. 变更影响分析

（待填写）

## 7. 变更实施计划

| 序号 | 任务描述 | 负责人(角色) | 开始日期 | 完成日期 | 前置依赖 | 备注 |
|------|----------|-------------|----------|----------|----------|------|
| | | | | | | |

## 8. 变更审批

### 8.1 审批流程（按影响范围分级）

| 审批环节 | 审批人 | 审批意见 | 审批日期 | 签字/电子签章 |
|----------|--------|----------|----------|---------------|
| | | | | |

### 8.2 审批结论
| 结论 | □ 通过 □ 有条件通过(附条件) □ 驳回(附原因) □ 拒绝(附原因) |
|------|----------------------------------------------------------|

## 9. 变更实施记录

| 实施日期 | 实施人 | 实施任务 | 实施内容摘要 | 实施结果 | 备注 |
|----------|--------|----------|-------------|----------|------|
| | | | | | |

## 10. 变更验证

### 10.1 验证项清单

| # | 验证项 | 验证标准 | 预期结果 | 实际结果 | 状态 | 验证人 | 验证日期 |
|---|--------|----------|----------|----------|------|--------|----------|
| | | | | | | | |

### 10.2 验证结论
| 结论 | □ 全部通过,可关闭 □ 部分不通过,需返工 □ 需补充验证 |
|------|-------------------------------------------------------|

## 11. 附录

（待填写）

---

**文档版本**：V1.0.0
**编制日期**：{today}
**编制人**：{cr.applicant}
**审核人**：
"""
        return content

    def save(self, cr: ChangeRequest, file_path: str) -> str:
        """保存变更单到文件，返回文件路径"""
        content = self.render(cr)
        write_file(file_path, content)
        log.info("变更单已保存: %s → %s", cr.change_number, file_path)
        return file_path

    # ---- 内部方法 ----

    def _render_domain_options(self, selected: str) -> str:
        """渲染领域选择表格"""
        lines = ["| 领域 | 选择 | 说明 |", "|------|------|------|"]
        for code, name in DOMAINS.items():
            desc = DOMAIN_DESCRIPTIONS.get(code, "")
            check = "**选中**" if code == selected else "-"
            mark = "☑" if code == selected else "□"
            lines.append(f"| {mark} **{code}** {name} | {check} | {desc} |")
        return "\n".join(lines)

    def _render_nature_options(self, selected: str) -> str:
        """渲染业务性质选择表格"""
        lines = ["| 性质 | 选择 | 典型场景 |", "|------|------|----------|"]
        for code, name in BUSINESS_NATURES.items():
            desc = BUSINESS_NATURE_DESCRIPTIONS.get(code, "")
            check = "**选中**" if code == selected else "-"
            mark = "☑" if code == selected else "□"
            lines.append(f"| {mark} **{code}** {name} | {check} | {desc} |")
        return "\n".join(lines)

    def _render_scope_options(self, selected_scopes: list[str]) -> str:
        """渲染影响范围选择表格"""
        lines = ["| 范围 | 选择 | 审批要求 |", "|------|------|----------|"]
        for code, name in IMPACT_SCOPES.items():
            desc = IMPACT_SCOPE_DESCRIPTIONS.get(code, "")
            is_selected = code in selected_scopes
            check = "**选中**" if is_selected else "-"
            mark = "☑" if is_selected else "□"
            lines.append(f"| {mark} **{code}** {name} | {check} | {desc} |")
        return "\n".join(lines)

    def _render_urgency(self, urgency: str) -> str:
        """渲染紧急程度"""
        parts = []
        for code, label in URGENCY_LEVELS.items():
            mark = "☑" if code == urgency else "□"
            parts.append(f"{mark}{label}")
        return " ".join(parts)
