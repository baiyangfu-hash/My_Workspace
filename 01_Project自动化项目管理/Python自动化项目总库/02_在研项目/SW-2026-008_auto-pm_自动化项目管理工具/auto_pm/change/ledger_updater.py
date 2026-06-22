"""版本变更台帐更新器"""

from __future__ import annotations

import re

from auto_pm.logging.logging import setup_logger as get_logger
from auto_pm.utils.file_utils import read_file, write_file

log = get_logger(log_level="INFO", app_name="auto_pm")


class LedgerUpdater:
    """版本变更台帐更新器"""

    def update(self, ledger_path: str, change_number: str, desc: str) -> None:
        """在台帐的变更单索引部分追加一条记录

        Args:
            ledger_path: 台帐文件路径
            change_number: 变更编号 (如 CHG-DOCU-2026-001)
            desc: 变更描述
        """
        content = read_file(ledger_path)
        if not content:
            log.warning("台帐文件为空或读取失败: %s", ledger_path)
            return

        # 提取领域
        domain = ""
        parts = change_number.split("-")
        if len(parts) >= 2:
            domain = parts[1]

        # 生成新的序号
        seq = self._get_next_sequence(content)

        # 生成变更单链接
        link = f"[→ {change_number}](./01_变更单/CHG-{domain}/{change_number}.md)"

        # 构造新行
        new_row = f"| {seq:03d} | {link} | {domain} | | | {desc} | | 🔄待处理 |\n"

        # 在变更单索引表格中插入
        updated = self._insert_row_to_index_table(content, new_row)
        if updated != content:
            write_file(ledger_path, updated)
            log.info("台帐已更新: 追加 %s (序号%03d)", change_number, seq)
        else:
            log.warning("台帐更新失败: 未找到变更单索引表格 %s", ledger_path)

    def _get_next_sequence(self, content: str) -> int:
        """获取变更单索引中的下一个序号"""
        max_seq = 0
        # 查找变更单索引表格中的序号
        in_index = False
        for line in content.split("\n"):
            line = line.strip()
            if "变更单索引" in line:
                in_index = True
                continue
            if in_index and line.startswith("|"):
                if re.match(r"^\|[\s\-:|]+\|$", line):
                    continue
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if cells and cells[0].isdigit():
                    try:
                        seq = int(cells[0])
                        max_seq = max(max_seq, seq)
                    except ValueError:
                        pass
            elif in_index and not line.startswith("|") and line:
                in_index = False
        return max_seq + 1

    def _insert_row_to_index_table(self, content: str, new_row: str) -> str:
        """在变更单索引表格中插入新行（在表头和分隔行之后）"""
        lines = content.split("\n")
        result_lines: list[str] = []
        in_index = False
        header_found = False
        inserted = False

        for i, line in enumerate(lines):
            result_lines.append(line)

            if "变更单索引" in line:
                in_index = True
                header_found = False
                continue

            if in_index and not inserted:
                stripped = line.strip()
                if stripped.startswith("|"):
                    if re.match(r"^\|[\s\-:|]+\|$", stripped):
                        # 分隔行，在之后插入
                        header_found = True
                        result_lines.append(new_row)
                        inserted = True
                    elif not header_found:
                        # 表头行，继续
                        pass
                elif stripped and not stripped.startswith("|"):
                    # 索引表格结束
                    in_index = False

        return "\n".join(result_lines)
