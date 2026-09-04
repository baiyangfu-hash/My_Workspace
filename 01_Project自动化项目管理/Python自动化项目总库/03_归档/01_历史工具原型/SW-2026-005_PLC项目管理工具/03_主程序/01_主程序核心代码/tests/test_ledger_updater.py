"""LedgerUpdater 单元测试"""

from __future__ import annotations

import os
import tempfile

import pytest

from src.generators.ledger_updater import LedgerUpdater
from src.utils.file_utils import write_file, read_file


class TestLedgerUpdater:
    """台帐更新器测试"""

    def test_update_adds_row(self, tmp_dir: str) -> None:
        """测试追加记录到台帐"""
        ledger_content = """# 版本变更台帐

## 变更单索引

| 编号 | 变更单链接 | 领域 | 性质 | 范围 | 标题 | 优先级 | 状态 |
|------|-----------|:----:|:----:|:----:|:-----|:------:|:----:|
| 001 | [→ CHG-DOCU-2026-001](./01_变更单/CHG-DOCU/CHG-DOCU-2026-001.md) | DOCU | DEF | MODULE | 测试标题 | P1 | ✅完成 |
"""
        ledger_path = os.path.join(tmp_dir, "01_版本变更台帐.md")
        write_file(ledger_path, ledger_content)

        updater = LedgerUpdater()
        updater.update(ledger_path, "CHG-PLC-2026-001", "PLC程序缺陷修复")

        updated = read_file(ledger_path)
        assert "CHG-PLC-2026-001" in updated
        assert "PLC程序缺陷修复" in updated
        # 新行应在 001 行之前（序号 002）
        assert "002" in updated

    def test_update_real_file(self, ledger_file: str) -> None:
        """测试更新真实台帐文件"""
        if not os.path.isfile(ledger_file):
            pytest.skip("真实台帐文件不存在")

        # 读取原始内容
        original = read_file(ledger_file)

        updater = LedgerUpdater()
        updater.update(ledger_file, "CHG-TEST-2026-999", "测试变更单（自动测试）")

        updated = read_file(ledger_file)
        assert "CHG-TEST-2026-999" in updated

        # 恢复原始内容
        write_file(ledger_file, original)

    def test_sequence_numbering(self, tmp_dir: str) -> None:
        """测试序号自动递增"""
        ledger_content = """# 版本变更台帐

## 变更单索引

| 编号 | 变更单链接 | 领域 | 性质 | 范围 | 标题 | 优先级 | 状态 |
|------|-----------|:----:|:----:|:----:|:-----|:------:|:----:|
| 002 | [→ CHG-DOCU-2026-002](./01_变更单/CHG-DOCU/CHG-DOCU-2026-002.md) | DOCU | OPT | MODULE | 标题2 | P2 | 🔄进行中 |
| 001 | [→ CHG-DOCU-2026-001](./01_变更单/CHG-DOCU/CHG-DOCU-2026-001.md) | DOCU | DEF | MODULE | 标题1 | P1 | ✅完成 |
"""
        ledger_path = os.path.join(tmp_dir, "01_版本变更台帐.md")
        write_file(ledger_path, ledger_content)

        updater = LedgerUpdater()
        seq = updater._get_next_sequence(read_file(ledger_path))

        assert seq == 3

    def test_empty_ledger(self, tmp_dir: str) -> None:
        """测试空台帐"""
        ledger_content = """# 版本变更台帐

## 变更单索引

| 编号 | 变更单链接 | 领域 | 性质 | 范围 | 标题 | 优先级 | 状态 |
|------|-----------|:----:|:----:|:----:|:-----|:------:|:----:|
"""
        ledger_path = os.path.join(tmp_dir, "01_版本变更台帐.md")
        write_file(ledger_path, ledger_content)

        updater = LedgerUpdater()
        seq = updater._get_next_sequence(read_file(ledger_path))

        assert seq == 1
