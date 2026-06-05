"""变更单 Markdown 解析器"""

from __future__ import annotations

import os
import re

from src.models.change_request import ChangeRequest, ChangeSummary
from src.models.spec_constants import (
    REQUIRED_SUBSECTIONS,
    DOMAINS,
    BUSINESS_NATURES,
    IMPACT_SCOPES,
    ALL_STATUSES,
)
from src.utils.file_utils import read_file, get_mtime
from src.utils.logger import get_logger

log = get_logger(__name__)


class ChgParser:
    """变更单 Markdown 解析器"""

    def parse(self, file_path: str) -> ChangeRequest:
        """解析变更单文件，返回 ChangeRequest"""
        content = read_file(file_path)
        if not content:
            log.warning("变更单文件为空或读取失败: %s", file_path)
            return ChangeRequest()

        cr = ChangeRequest(
            file_path=file_path,
            file_mtime=get_mtime(file_path),
        )

        # 从文件路径提取 domain
        cr.domain = self._extract_domain_from_path(file_path)
        # 从文件名提取 change_number
        cr.change_number = self._extract_change_number(file_path)

        # 按章节拆分
        sections = self._split_sections(content)
        log.debug("变更单章节拆分: %s → %s", os.path.basename(file_path), list(sections.keys()))

        # 解析 §3 变更基本信息
        if "3" in sections:
            self._parse_change_info(sections["3"], cr)
        else:
            log.warning("变更单缺少§3变更基本信息章节: %s", cr.change_number)

        # 解析 §4 变更原因
        if "4" in sections:
            self._parse_change_reason(sections["4"], cr)

        # 状态确定：优先从 §3.4 "变更状态" 字段读取（流转时写入），回退到 §8 推断
        explicit_status = self._read_explicit_status(sections.get("3", ""))
        if explicit_status:
            cr.status = explicit_status
            log.debug("状态来源: §3.4 变更状态字段 → %s", explicit_status)
        else:
            # 回退：从 §8 审批章节推断
            if "8" in sections:
                cr.status = self._infer_status_from_approval(sections["8"])
            elif "7" in sections:
                cr.status = self._infer_status_from_approval(sections["7"])

            # 从 §9/§10 进一步推断
            if "9" in sections and cr.status in ("approved",):
                if self._has_implementation_records(sections["9"]):
                    cr.status = "implementing"
            if "10" in sections and cr.status == "implementing":
                if self._all_verification_passed(sections["10"]):
                    cr.status = "completed"
            log.debug("状态来源: §8推断 → %s", cr.status)

        # 如果 change_number 未从文件提取到，尝试从内容提取
        if not cr.change_number:
            cr.change_number = self._extract_change_number_from_content(content)

        # 如果 project_id 未从 §3 提取到，从 change_number 推断
        if not cr.project_id:
            cr.project_id = self._extract_project_id_from_content(content)

        # 填充章节内容标志（门禁校验用）
        self._fill_section_flags(cr, sections)

        # 规范结构校验：检查必填字段和合法枚举值
        violations = self._validate_spec_compliance(cr, sections)
        if violations:
            for v in violations:
                log.warning("规范校验违规 [%s]: %s", cr.change_number, v)

        log.info("解析变更单完成: %s, domain=%s, nature=%s, status=%s",
                 cr.change_number, cr.domain, cr.business_nature, cr.status)
        return cr

    def to_summary(self, cr: ChangeRequest) -> ChangeSummary:
        """将 ChangeRequest 转换为轻量级 ChangeSummary"""
        title = cr.background[:50] + "..." if len(cr.background) > 50 else cr.background
        return ChangeSummary(
            change_number=cr.change_number,
            project_id=cr.project_id,
            domain=cr.domain,
            business_nature=cr.business_nature,
            impact_scope=cr.impact_scope,
            status=cr.status,
            applicant=cr.applicant,
            apply_date=cr.apply_date,
            title=title,
        )

    # ---- 内部方法 ----

    def _split_sections(self, content: str) -> dict[str, str]:
        """按 ## N. 标题 拆分章节"""
        sections: dict[str, str] = {}
        pattern = re.compile(r"^##\s+(\d+)\s*[.、：:]", re.MULTILINE)
        matches = list(pattern.finditer(content))

        for i, match in enumerate(matches):
            section_key = match.group(1)
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            sections[section_key] = content[start:end]

        return sections

    def _parse_table(self, text: str) -> dict[str, str]:
        """解析 Markdown 表格为 {字段名: 值} 字典"""
        result: dict[str, str] = {}
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line.startswith("|"):
                continue
            if re.match(r"^\|[\s\-:|]+\|$", line):
                continue
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= 2:
                key = re.sub(r"\*\*", "", cells[0]).strip()
                value = re.sub(r"\*\*", "", cells[1]).strip()
                if key:
                    result[key] = value
        return result

    def _parse_change_info(self, text: str, cr: ChangeRequest) -> None:
        """解析 §3 变更基本信息（多级子表格式）"""
        # §3.0 编号与项目
        s30 = self._find_subsection(text, "3.0")
        if s30:
            table = self._parse_table(s30)
            cr.change_number = table.get("变更编号", cr.change_number)
            cr.project_name = table.get("项目名称", cr.project_name)
            cr.project_id = table.get("项目编号", cr.project_id)

        # §3.1 技术领域
        s31 = self._find_subsection(text, "3.1")
        if s31:
            cr.domain = self._extract_selected_option(s31) or cr.domain

        # §3.2 业务性质
        s32 = self._find_subsection(text, "3.2")
        if s32:
            cr.business_nature = self._extract_selected_option(s32) or cr.business_nature

        # §3.3 影响范围
        s33 = self._find_subsection(text, "3.3")
        if s33:
            cr.impact_scope = self._extract_selected_options(s33)

        # §3.4 申请信息
        s34 = self._find_subsection(text, "3.4")
        if s34:
            table = self._parse_table(s34)
            cr.applicant = table.get("变更申请人", cr.applicant)
            cr.apply_date = table.get("申请日期", cr.apply_date)
            cr.planned_date = table.get("预计实施日期", cr.planned_date)
            # 紧急程度 - 检查 ☑ 标记的位置
            urgency_raw = table.get("紧急程度", "")
            if "☑非常紧急" in urgency_raw or "☑ 非常紧急" in urgency_raw:
                cr.urgency = "critical"
            elif "☑紧急" in urgency_raw or "☑ 紧急" in urgency_raw:
                cr.urgency = "urgent"
            elif "☑一般" in urgency_raw or "☑ 一般" in urgency_raw:
                cr.urgency = "normal"
            elif "非常紧急" in urgency_raw and "☑" in urgency_raw.split("非常紧急")[0][-5:]:
                cr.urgency = "critical"
            elif "紧急" in urgency_raw and "☑" in urgency_raw.split("紧急")[0][-5:]:
                cr.urgency = "urgent"
            else:
                cr.urgency = "normal"

    def _parse_change_reason(self, text: str, cr: ChangeRequest) -> None:
        """解析 §4 变更原因（文本段落格式）"""
        cr.background = self._extract_text_block(text, "变更背景")
        cr.necessity = self._extract_text_block(text, "变更必要性")
        cr.references = self._extract_text_block(text, "参考依据")

    def _find_subsection(self, text: str, subsection_num: str) -> str | None:
        """查找子章节（如 ### 3.0 编号与项目）"""
        pattern = re.compile(
            rf"###\s*{re.escape(subsection_num)}\s*[.、：:]*(.*?)(?=\n###|\n##|\Z)",
            re.DOTALL,
        )
        match = pattern.search(text)
        if match:
            return match.group(0)
        return None

    def _extract_selected_option(self, text: str) -> str:
        """从选择表格中提取 ☑ 选中的选项代码

        例: ☑ **DOCU** 工程文档 → DOCU
        """
        for line in text.split("\n"):
            if "☑" in line:
                # 提取 **CODE** 格式
                match = re.search(r"☑\s*\*\*(\w+)\*\*", line)
                if match:
                    return match.group(1)
        return ""

    def _extract_selected_options(self, text: str) -> list[str]:
        """从多选表格中提取所有 ☑ 选中的选项代码"""
        options: list[str] = []
        for line in text.split("\n"):
            if "☑" in line:
                match = re.search(r"☑\s*\*\*(\w+)\*\*", line)
                if match:
                    options.append(match.group(1))
        return options

    def _extract_text_block(self, text: str, label: str) -> str:
        """提取文本块（如 **变更背景**：后面的内容）"""
        pattern = re.compile(
            rf"\*\*{re.escape(label)}\*\*[：:]\s*(.*?)(?=\n\*\*|\n##|\n###|\Z)",
            re.DOTALL,
        )
        match = pattern.search(text)
        if match:
            content = match.group(1).strip()
            # 清理列表编号
            content = re.sub(r"^\d+\.\s*", "- ", content, flags=re.MULTILINE)
            return content
        return "待补充"

    def _infer_status_from_approval(self, text: str) -> str:
        """从审批章节推断状态"""
        # 检查审批结论中的 ☑ 标记
        if "☑ 通过" in text or "☑通过" in text:
            log.debug("状态推断: 审批结论☑通过 → approved")
            return "approved"
        if "☑ 驳回" in text or "☑驳回" in text:
            log.debug("状态推断: 审批结论☑驳回 → rejected")
            return "rejected"
        if "☑ 拒绝" in text or "☑拒绝" in text:
            log.debug("状态推断: 审批结论☑拒绝 → rejected")
            return "rejected"
        # 检查审批流程中是否有已审批记录（有审批人+审批意见+日期）
        approval_rows = 0
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", line):
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if len(cells) >= 4 and cells[0] not in ("审批环节", "结论"):
                    if cells[2] and cells[3]:  # 有审批意见和日期
                        approval_rows += 1
        if approval_rows > 0:
            # 有审批记录但无明确结论 → 检查是否包含"同意"
            if "同意" in text:
                log.debug("状态推断: 有审批记录+同意 → approved")
                return "approved"
            log.debug("状态推断: 有审批记录无结论 → under_review")
            return "under_review"
        # 有审批章节但无记录
        if "审批" in text:
            log.debug("状态推断: 有审批章节无记录 → submitted")
            return "submitted"
        log.debug("状态推断: 无审批信息 → draft")
        return "draft"

    def _has_implementation_records(self, text: str) -> bool:
        """检查 §9 是否有实施记录"""
        # 查找表格中的数据行（排除表头和分隔行）
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", line):
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if len(cells) >= 2 and cells[0] not in ("实施日期", "序号"):
                    return True
        return False

    def _all_verification_passed(self, text: str) -> bool:
        """检查 §10 验证是否全部通过"""
        # 查找验证结论
        if "全部通过" in text:
            return True
        # 检查验证项表格中是否所有状态都是"通过"
        pass_count = 0
        total_count = 0
        for line in text.split("\n"):
            if "☑通过" in line or "✓通过" in line or "通过" in line:
                pass_count += 1
                total_count += 1
            elif line.startswith("|") and "状态" not in line and "验证项" not in line:
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if len(cells) >= 6:
                    total_count += 1
        return total_count > 0 and pass_count == total_count

    def _extract_domain_from_path(self, file_path: str) -> str:
        """从文件路径提取领域

        例: .../CHG-DOCU/CHG-DOCU-2026-001.md → DOCU
        """
        parts = file_path.replace("\\", "/").split("/")
        for part in parts:
            if part.startswith("CHG-") and part != os.path.basename(file_path).replace(".md", ""):
                # 目录名如 CHG-DOCU
                domain = part.replace("CHG-", "")
                if domain:
                    return domain
        return ""

    def _extract_change_number(self, file_path: str) -> str:
        """从文件名提取变更编号

        例: CHG-DOCU-2026-001.md → CHG-DOCU-2026-001
        """
        basename = os.path.splitext(os.path.basename(file_path))[0]
        if re.match(r"CHG-[A-Z]+-\d{4}-\d{3}", basename):
            return basename
        return ""

    def _extract_change_number_from_content(self, content: str) -> str:
        """从内容中提取变更编号"""
        match = re.search(r"CHG-[A-Z]+-\d{4}-\d{3}", content)
        return match.group(0) if match else ""

    def _extract_project_id_from_content(self, content: str) -> str:
        """从内容中提取项目编号（从§3.0编号与项目表格）"""
        match = re.search(r"项目编号[|：:]\s*([A-Z]+-\d{4}-\d{3})", content)
        return match.group(1) if match else ""

    def _read_explicit_status(self, section3_text: str) -> str:
        """从 §3.4 申请信息表中读取"变更状态"字段

        流转时写入此字段，解析时优先读取，确保状态持久化。
        返回空字符串表示无显式状态（回退到§8推断）。
        """
        match = re.search(r"\|\s*变更状态\s*\|\s*(\S+)\s*\|", section3_text)
        if match:
            status = match.group(1).strip()
            if status in ALL_STATUSES:
                return status
            log.debug("§3.4 变更状态值 '%s' 不在合法状态集中，忽略", status)
        return ""

    def _fill_section_flags(self, cr: ChangeRequest, sections: dict[str, str]) -> None:
        """填充章节内容标志（门禁校验用）

        检查各章节是否有实质内容（非空、非模板占位符）
        """
        # §4 变更原因：background 非空且非"待补充"
        cr.has_section_4 = bool(cr.background and cr.background != "待补充")

        # §7 实施计划：有至少一条数据行（表格中非表头/分隔符的行）
        if "7" in sections:
            cr.has_section_7 = self._has_table_data_rows(sections["7"])
        else:
            cr.has_section_7 = False

        # §8.1 审批记录：有至少一条审批数据行
        if "8" in sections:
            cr.has_section_8_approval = self._has_approval_records(sections["8"])
        else:
            cr.has_section_8_approval = False

        # §9 实施记录：有至少一条数据行
        if "9" in sections:
            cr.has_section_9 = self._has_table_data_rows(sections["9"])
        else:
            cr.has_section_9 = False

        # §10.1 验证项：有至少一条数据行
        # §10.2 验证结论
        if "10" in sections:
            cr.has_section_10_verify = self._has_verification_records(sections["10"])
            cr.section_10_conclusion = self._extract_verification_conclusion(sections["10"])
        else:
            cr.has_section_10_verify = False
            cr.section_10_conclusion = ""

    def _has_table_data_rows(self, text: str) -> bool:
        """检查章节中是否有表格数据行（排除表头和分隔符行）"""
        lines = text.strip().split("\n")
        data_rows = 0
        for line in lines:
            line = line.strip()
            if line.startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", line):
                # 排除标题行（包含 # 序号 等表头关键词）
                if re.match(r"^\|\s*#\s*\|", line):
                    continue
                # 排除空数据行（所有单元格都是空白或-）
                cells = [c.strip() for c in line.split("|")[1:-1]]
                if any(c and c != "-" for c in cells):
                    data_rows += 1
        return data_rows > 0

    def _has_approval_records(self, text: str) -> bool:
        """检查 §8 中是否有审批记录"""
        # 在 §8.1 审批流程表格中找数据行
        lines = text.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", line):
                cells = [c.strip() for c in line.split("|")[1:-1]]
                # 审批记录至少有一个非空单元格（排除表头行）
                if any(c for c in cells) and not re.match(r"^\|\s*审批环节\s*\|", line):
                    return True
        return False

    def _has_verification_records(self, text: str) -> bool:
        """检查 §10.1 中是否有验证项"""
        return self._has_table_data_rows(text)

    def _extract_verification_conclusion(self, text: str) -> str:
        """提取 §10.2 验证结论"""
        match = re.search(r"10\.2.*?\|.*结论.*?\|.*?☑.*?(\S+?)(?:\s*,|□|\|)", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # 简单匹配：查找 ☑ 标记
        if "☑通过" in text or "☑ 全部通过" in text:
            return "全部通过"
        return ""

    def _validate_spec_compliance(self, cr: ChangeRequest, sections: dict[str, str]) -> list[str]:
        """校验变更单是否符合 CHG-040 规范

        返回违规列表，空列表表示合规。
        不抛异常，仅记录警告，让解析继续完成。
        """
        violations: list[str] = []

        # 1. 必须有 §3 变更基本信息
        if "3" not in sections:
            violations.append("缺少 §3 变更基本信息章节")
        else:
            # §3 必须包含 3.0~3.4 子章节
            s3_text = sections["3"]
            for sub in REQUIRED_SUBSECTIONS:
                if not re.search(rf"###\s*{re.escape(sub)}", s3_text):
                    violations.append(f"缺少 §3 子章节 {sub}")

        # 2. 必须有 §4 变更原因
        if "4" not in sections:
            violations.append("缺少 §4 变更原因章节")

        # 3. 必须有 §8 变更审批
        if "8" not in sections:
            violations.append("缺少 §8 变更审批章节")

        # 4. 枚举值校验
        if cr.domain and cr.domain not in DOMAINS:
            violations.append(f"领域 '{cr.domain}' 不在规范允许值 {list(DOMAINS.keys())} 中")
        if cr.business_nature and cr.business_nature not in BUSINESS_NATURES:
            violations.append(f"业务性质 '{cr.business_nature}' 不在规范允许值 {list(BUSINESS_NATURES.keys())} 中")
        for scope in cr.impact_scope:
            if scope and scope not in IMPACT_SCOPES:
                violations.append(f"影响范围 '{scope}' 不在规范允许值 {list(IMPACT_SCOPES.keys())} 中")

        # 5. 必填字段校验
        if not cr.change_number:
            violations.append("变更编号为空")
        if not cr.project_id:
            violations.append("项目编号为空")

        return violations


