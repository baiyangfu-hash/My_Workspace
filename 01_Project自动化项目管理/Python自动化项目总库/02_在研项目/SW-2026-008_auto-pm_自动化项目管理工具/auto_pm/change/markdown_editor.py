"""变更单 Markdown 内容编辑器（M3-Iter2 从 ChangeService 拆分）

负责变更单 .md 文件的内容级编辑：
- 审批/实施/验证表格追加行
- 状态字段更新
- 验证结论更新
- 字段值更新（背景/必要性/参考依据/预计日期/紧急程度）

ChangeService 通过组合方式使用本模块，保持向后兼容。
"""

from __future__ import annotations

import re

from auto_pm.change.models import URGENCY_LEVELS
from auto_pm.logging.logging import setup_logger as get_logger

log = get_logger(log_level="INFO", app_name="auto_pm")


class ChangeMarkdownEditor:
    """变更单 Markdown 内容编辑器

    所有方法都是纯函数式操作：输入 .md 内容字符串，返回修改后的字符串。
    不涉及文件 I/O，便于单测和复用。
    """

    def append_to_approval_table(self, content: str, row: str) -> str:
        """在审批流程表格末尾追加一行"""
        # 查找 §8.1 审批流程
        pattern = re.compile(
            r"(###\s*8\.1.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|\n)((?:\|[\s\-:|]+\|\n)?(?:\|.*\|\n)*)",
            re.DOTALL,
        )
        match = pattern.search(content)
        if match:
            return content[:match.end()] + row + content[match.end():]
        # 兜底：在 §8 章节末尾追加
        return content + "\n" + row

    def append_to_implementation_table(self, content: str, row: str) -> str:
        """在实施记录表格末尾追加一行"""
        pattern = re.compile(
            r"(##\s*9\..*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|\n)((?:\|[\s\-:|]+\|\n)?(?:\|.*\|\n)*)",
            re.DOTALL,
        )
        match = pattern.search(content)
        if match:
            return content[:match.end()] + row + content[match.end():]
        return content + "\n" + row

    def append_to_verification_table(self, content: str, row: str) -> str:
        """在验证表格 (§10.1) 末尾追加一行

        在 §10.2 节标题之前插入新行，避免正则匹配偏移。
        """
        # 定位 §10.1 起始位置
        sec_10_1 = re.search(r"^###\s*10\.1", content, re.MULTILINE)
        if not sec_10_1:
            return content + "\n" + row

        # 定位 §10.2 节标题，在其前插入
        remainder = content[sec_10_1.end():]
        next_section = re.search(r"^###\s*10\.2", remainder, re.MULTILINE)
        if next_section:
            insert_pos = sec_10_1.end() + next_section.start()
            return content[:insert_pos].rstrip() + "\n" + row + content[insert_pos:]

        # 无 §10.2：在 §10.1 区域末尾追加
        return content + "\n" + row

    def update_status_field(self, content: str, new_status: str) -> str:
        """更新 §3.4 申请信息表中的"变更状态"字段

        如果已有"变更状态"行，替换值；如果没有，在紧急程度行后追加。
        """
        # 替换已有的变更状态行
        pattern = re.compile(r"(\|\s*变更状态\s*\|\s*)\S+(\s*\|)")
        if pattern.search(content):
            return pattern.sub(r"\g<1>" + new_status + r"\2", content)
        # 没有变更状态行，在紧急程度行后追加
        urgency_pattern = re.compile(r"(\|\s*紧急程度\s*\|.*?\|)\n")
        match = urgency_pattern.search(content)
        if match:
            return content[:match.end()] + f"| 变更状态 | {new_status} |\n" + content[match.end():]
        # 兜底：在 §3.4 末尾追加
        return content + f"\n| 变更状态 | {new_status} |\n"

    def update_verification_conclusion(self, content: str, conclusion: str) -> str:
        """更新 §10.2 验证结论为指定值

        兼容三种格式：
        1. 原始模板格式: | 结论 | □ 全部通过,可关闭 □ 部分不通过,需返工 □ 需补充验证 |
        2. 已写入格式:    | **验证结论** | 全部通过 |
        3. § 符号变体:    ### §10.2 或 ### 10.2
        """
        lines = content.splitlines()
        in_section_10_2 = False
        found_conclusion_line = False
        result = []
        for line in lines:
            stripped = line.strip()
            # 匹配 ### 10.2 或 ### §10.2（兼容有无 § 符号）
            if re.match(r"^###\s*§?\s*10\.2\b", stripped):
                in_section_10_2 = True
                result.append(line)
                continue
            if in_section_10_2 and re.match(r"^###\s", stripped):
                in_section_10_2 = False

            if in_section_10_2 and not found_conclusion_line:
                # 格式A: 模板原始格式 | 结论 | □ ... |
                if re.match(r"^\|\s*结论\s*\|", stripped):
                    result.append(f"| **验证结论** | {conclusion} |")
                    found_conclusion_line = True
                    continue
                # 格式B: 已写入的 **验证结论** 格式
                if "**验证结论**" in stripped:
                    result.append(f"| **验证结论** | {conclusion} |")
                    found_conclusion_line = True
                    continue

            result.append(line)

        # 如果进入了 §10.2 但没找到结论行，在节标题后插入
        if in_section_10_2 and not found_conclusion_line:
            # 在 result 中找到 §10.2 标题行后插入
            for i, r in enumerate(result):
                if re.match(r"^###\s*§?\s*10\.2\b", r.strip()):
                    result.insert(i + 1, f"| **验证结论** | {conclusion} |")
                    break

        return "\n".join(result)

    def update_field(self, content: str, field: str, value: str) -> str:
        """根据字段名分发到对应的章节更新逻辑

        Args:
            content: .md 文件原始内容
            field: 字段名（background/necessity/references/planned_date/urgency）
            value: 新值

        Returns:
            更新后的 .md 内容（未匹配到则原样返回）
        """
        if field in ("background", "necessity", "references"):
            label_map = {
                "background": "变更背景",
                "necessity": "变更必要性",
                "references": "参考依据",
            }
            return self._update_text_block(content, label_map[field], value)
        if field == "planned_date":
            return self._update_table_field(content, "预计实施日期", value)
        if field == "urgency":
            return self._update_table_field(
                content, "紧急程度", self.render_urgency_value(value)
            )
        return content

    def _update_text_block(self, content: str, label: str, value: str) -> str:
        """更新 §4 中的文本块（**变更背景**：xxx）

        保留 ``**label**：`` 标记行，仅替换后续段落内容，
        直到遇到下一个 ``**...**`` 标记或 ``##`` 章节标题。
        """
        pattern = re.compile(
            rf"(\*\*{re.escape(label)}\*\*[：:]\s*\n)(.*?)(?=\n\*\*|\n##|\Z)",
            re.DOTALL,
        )
        match = pattern.search(content)
        if match:
            # 使用函数替换避免 value 中的反斜杠被当作反向引用
            return pattern.sub(lambda m: m.group(1) + value + "\n", content, count=1)
        log.warning("更新文本块: 未找到标签 '%s'，跳过", label)
        return content

    def _update_table_field(self, content: str, field_name: str, value: str) -> str:
        """更新 §3.4 表格中的字段值（| 字段名 | 值 |）

        仅替换值单元格，保留字段名和表格结构。
        """
        pattern = re.compile(
            rf"(\|\s*{re.escape(field_name)}\s*\|\s*)[^|]*(\s*\|)"
        )
        match = pattern.search(content)
        if match:
            return pattern.sub(
                lambda m: m.group(1) + value + m.group(2), content, count=1
            )
        log.warning("更新表格字段: 未找到字段 '%s'，跳过", field_name)
        return content

    @staticmethod
    def render_urgency_value(urgency: str) -> str:
        """渲染紧急程度为 ☑/□ 格式（与 ChgGenerator._render_urgency 对齐）"""
        parts = []
        for code, label in URGENCY_LEVELS.items():
            mark = "☑" if code == urgency else "□"
            parts.append(f"{mark}{label}")
        return " ".join(parts)
