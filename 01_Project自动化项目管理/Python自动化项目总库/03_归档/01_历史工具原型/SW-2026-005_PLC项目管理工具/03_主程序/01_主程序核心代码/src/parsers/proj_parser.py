"""立项表 Markdown 解析器"""

from __future__ import annotations

import os
import re

from src.models.project_info import ProjectInfo, RiskItem
from src.utils.file_utils import read_file, get_mtime
from src.utils.logger import get_logger

log = get_logger(__name__)

# 占位符模式：匹配这些值的字段返回 "待补充"
_PLACEHOLDER_PATTERN = re.compile(r"（待[^）]*）|待补充|待扫描统计|待统计", re.DOTALL)


class ProjParser:
    """立项表 Markdown 解析器"""

    def parse(self, file_path: str) -> ProjectInfo:
        """解析立项表文件，返回 ProjectInfo"""
        content = read_file(file_path)
        if not content:
            log.warning("立项表文件为空或读取失败: %s", file_path)
            return ProjectInfo()

        info = ProjectInfo(
            proj_file_path=file_path,
            proj_file_mtime=get_mtime(file_path),
        )

        # 从文件路径提取 project_id
        info.project_id = self._extract_project_id(file_path)

        # 按章节拆分
        sections = self._split_sections(content)
        log.debug("立项表章节拆分: %s → %s", os.path.basename(file_path), list(sections.keys()))

        # 解析各章节
        if "3" in sections:
            self._parse_business_identity(sections["3"], info)
        else:
            log.warning("立项表缺少 §3 业务身份: %s", os.path.basename(file_path))
        if "4" in sections:
            self._parse_tech_environment(sections["4"], info)
        else:
            log.warning("立项表缺少 §4 技术环境: %s", os.path.basename(file_path))
        if "5" in sections:
            self._parse_engineering_scale(sections["5"], info)
        if "6" in sections:
            self._parse_engineering_status(sections["6"], info)
        else:
            log.warning("立项表缺少 §6 工程状态: %s", os.path.basename(file_path))
        if "7" in sections:
            self._parse_change_ledger(sections["7"], info)
        if "附录 A" in sections or "附录A" in sections:
            key = "附录 A" if "附录 A" in sections else "附录A"
            self._parse_appendix_a(sections[key], info)

        log.info("解析立项表完成: project_id=%s, name=%s, phase=%s",
                 info.project_id, info.name, info.phase)
        return info

    def _extract_project_id(self, file_path: str) -> str:
        """从文件路径或内容提取项目编号"""
        # 从文件名提取（如 003_DJ-2026-005_项目立项表_PROJ.md）
        basename = os.path.basename(file_path)
        match = re.search(r"([A-Z]+-\d{4}-\d{3})", basename)
        if match:
            return match.group(1)
        # 从各级父目录名提取（如 SW-2026-005_PLC项目管理工具）
        path = file_path
        for _ in range(5):  # 最多向上5级
            dir_name = os.path.basename(path)
            match = re.search(r"([A-Z]+-\d{4}-\d{3})", dir_name)
            if match:
                return match.group(1)
            parent = os.path.dirname(path)
            if parent == path:
                break
            path = parent
        return ""

    def _split_sections(self, content: str) -> dict[str, str]:
        """按 ## N. 标题 拆分章节"""
        sections: dict[str, str] = {}
        # 匹配 ## N. 标题 或 ## 附录 X: 标题
        pattern = re.compile(r"^##\s+(\d+|附录\s*A?)\s*[.：:]", re.MULTILINE)
        matches = list(pattern.finditer(content))

        for i, match in enumerate(matches):
            section_key = match.group(1).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            sections[section_key] = content[start:end]

        return sections

    def _parse_table(self, section_text: str) -> dict[str, str]:
        """解析 Markdown 表格为 {字段名: 值} 字典

        支持两列表格: | 字段 | 内容 |
        也兼容三列表格: | 字段 | 内容 | 备注 |
        """
        result: dict[str, str] = {}
        lines = section_text.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line.startswith("|"):
                continue
            # 跳过分隔行
            if re.match(r"^\|[\s\-:|]+\|$", line):
                continue
            # 跳过表头行（第一行）
            cells = [c.strip() for c in line.split("|")]
            # cells[0] 和 cells[-1] 为空（首尾 | 分割）
            cells = [c for c in cells if c != "" or (cells.index(c) > 0 and cells.index(c) < len(cells) - 1)]
            # 重新分割，更简洁
            parts = line.split("|")
            cells = [p.strip() for p in parts]
            # 过滤首尾空
            cells = [c for c in cells if c]

            if len(cells) < 2:
                continue

            key = self._clean_key(cells[0])
            value = self._clean_value(cells[1])
            if key:
                result[key] = value

        return result

    def _clean_key(self, key: str) -> str:
        """清理字段名：去除加粗标记等"""
        key = re.sub(r"\*\*", "", key)
        key = key.strip()
        return key

    def _clean_value(self, value: str) -> str:
        """清理字段值：去除加粗标记、占位符等"""
        # 去除加粗
        value = re.sub(r"\*\*", "", value)
        # 去除行内代码
        value = re.sub(r"`([^`]*)`", r"\1", value)
        # 去除链接，保留文本
        value = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", value)
        value = value.strip()

        # 占位符处理
        if _PLACEHOLDER_PATTERN.search(value):
            return "待补充"
        if value in ("（待补充）", "待补充", "-"):
            return "待补充"

        return value

    def _parse_business_identity(self, text: str, info: ProjectInfo) -> None:
        """解析 §3 业务身份"""
        table = self._parse_table(text)
        info.name = table.get("项目名称", info.name)
        info.business_desc = table.get("业务描述", info.business_desc)
        info.important_note = table.get("重要说明", info.important_note)
        info.process_scope = table.get("工艺范围", info.process_scope)
        info.customer = table.get("客户/产线", info.customer)

    def _parse_tech_environment(self, text: str, info: ProjectInfo) -> None:
        """解析 §4 技术环境 + 控制参数"""
        table = self._parse_table(text)
        info.platform = table.get("编程平台", info.platform)
        info.plc_model = table.get("PLC 型号", info.plc_model)
        info.hmi_model = table.get("HMI 型号", info.hmi_model)
        info.driver = table.get("驱动器", info.driver)
        info.communication = table.get("通信方式", info.communication)

        # 控制参数子表
        ctrl_table = self._parse_subsection_table(text, "控制参数")
        info.axes = ctrl_table.get("运动轴", info.axes)
        info.precision = ctrl_table.get("定位精度", info.precision)
        info.safety_protection = ctrl_table.get("安全保护", info.safety_protection)

    def _parse_engineering_scale(self, text: str, info: ProjectInfo) -> None:
        """解析 §5 工程规模"""
        table = self._parse_table(text)
        info.module_count = table.get("工艺模块数", info.module_count)
        # 备注列可能在第三列
        if "工艺模块数" in table:
            # 尝试从原始文本提取备注
            for line in text.split("\n"):
                if "工艺模块数" in line:
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 3:
                        info.module_names = self._clean_value(parts[2])
                    break

        # 项目范围（列表格式）
        info.project_scope = self._extract_list_items(text, "项目范围")

    def _parse_engineering_status(self, text: str, info: ProjectInfo) -> None:
        """解析 §6 工程状态"""
        table = self._parse_table(text)
        phase_raw = table.get("当前阶段", info.phase)
        # 提取英文阶段标识，如 commissioning / developing
        match = re.search(r"`(\w+)`", phase_raw)
        if match:
            info.phase = match.group(1)
        else:
            # 尝试从括号中提取，如 "开发中 (developing)"
            match = re.search(r"\((\w+)\)", phase_raw)
            if match:
                info.phase = match.group(1)
            else:
                info.phase = phase_raw
        info.start_date = table.get("开始日期", info.start_date)
        info.end_date = table.get("预计完成日期", info.end_date)
        info.duration_days = table.get("总工期", info.duration_days)

    def _parse_change_ledger(self, text: str, info: ProjectInfo) -> None:
        """解析 §7 变更台账（占位，实际数据从变更管理文件夹扫描）"""
        # §7 的值通常是"待从变更管理系统读取"，实际数据由 Service 层填充
        pass

    def _parse_appendix_a(self, text: str, info: ProjectInfo) -> None:
        """解析附录A"""
        # A.1 人力资源摘要
        info.team = self._extract_team_summary(text)
        # A.4 风险评估
        info.risks = self._extract_risks(text)

    def _extract_team_summary(self, text: str) -> str:
        """提取 A.1 人力资源摘要"""
        # 查找 A.1 子章节
        a1_match = re.search(r"A\.1\s*人力资源(.*?)(?=A\.\d|###|$)", text, re.DOTALL)
        if not a1_match:
            return "待补充"
        a1_text = a1_match.group(1)
        table = self._parse_table(a1_text)
        if not table:
            return "待补充"
        # 拼接角色和人员
        parts = []
        lines = a1_text.strip().split("\n")
        for line in lines:
            line = line.strip()
            if not line.startswith("|"):
                continue
            if re.match(r"^\|[\s\-:|]+\|$", line):
                continue
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= 2 and cells[0] not in ("角色", "字段"):
                role = re.sub(r"\*\*", "", cells[0])
                person = re.sub(r"\*\*", "", cells[1])
                parts.append(f"{role}: {person}")
        return "; ".join(parts) if parts else "待补充"

    def _extract_risks(self, text: str) -> list[RiskItem]:
        """提取 A.4 风险评估"""
        a4_match = re.search(r"A\.4\s*风险评估(.*?)(?=A\.\d|###|$)", text, re.DOTALL)
        if not a4_match:
            return []
        a4_text = a4_match.group(1)
        risks: list[RiskItem] = []
        lines = a4_text.strip().split("\n")
        for line in lines:
            line = line.strip()
            if not line.startswith("|"):
                continue
            if re.match(r"^\|[\s\-:|]+\|$", line):
                continue
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= 3 and cells[0] not in ("风险项", "字段"):
                risk_item = re.sub(r"\*\*", "", cells[0])
                level = re.sub(r"\*\*", "", cells[1])
                measure = re.sub(r"\*\*", "", cells[2])
                risks.append(RiskItem(risk_item=risk_item, level=level, measure=measure))
        return risks

    def _parse_subsection_table(self, text: str, subsection_title: str) -> dict[str, str]:
        """解析子章节表格（如 ### 控制参数）"""
        pattern = re.compile(
            rf"###\s*{re.escape(subsection_title)}\s*\n(.*?)(?=\n###|\n##|\Z)",
            re.DOTALL,
        )
        match = pattern.search(text)
        if not match:
            return {}
        return self._parse_table(match.group(1))

    def _extract_list_items(self, text: str, subsection_title: str) -> str:
        """提取子章节列表项（如 ### 项目范围 下的 - 项目1\n- 项目2）"""
        pattern = re.compile(
            rf"###\s*{re.escape(subsection_title)}\s*\n(.*?)(?=\n###|\n##|\Z)",
            re.DOTALL,
        )
        match = pattern.search(text)
        if not match:
            return "待补充"
        items = []
        for line in match.group(1).strip().split("\n"):
            line = line.strip()
            if line.startswith("- "):
                items.append(line[2:].strip())
        return "; ".join(items) if items else "待补充"
