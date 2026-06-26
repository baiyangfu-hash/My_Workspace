"""LedgerUpdater 单元测试"""

from __future__ import annotations

from auto_pm.change.ledger_updater import LedgerUpdater


class TestLedgerUpdaterUpdate:
    """LedgerUpdater.update 测试"""

    def test_update_appends_row(self, tmp_path: object) -> None:
        """update 在台帐变更单索引中追加一行"""
        tmp = tmp_path  # type: Path
        ledger = tmp / "01_版本变更台帐.md"
        ledger.write_text(
            "# 版本变更台帐\n\n"
            "## 变更单索引\n\n"
            "| 序号 | 变更编号 | 描述 |\n"
            "|------|----------|------|\n",
            encoding="utf-8",
        )

        updater = LedgerUpdater()
        updater.update(str(ledger), "CHG-PLC-2026-001", "修复阀门时序")

        content = ledger.read_text(encoding="utf-8")
        assert "CHG-PLC-2026-001" in content
        assert "修复阀门时序" in content

    def test_update_empty_file(self, tmp_path: object) -> None:
        """update 对空文件不写入"""
        tmp = tmp_path  # type: Path
        ledger = tmp / "empty.md"
        ledger.write_text("", encoding="utf-8")

        updater = LedgerUpdater()
        updater.update(str(ledger), "CHG-PLC-2026-001", "测试")

        content = ledger.read_text(encoding="utf-8")
        assert content == ""

    def test_update_nonexistent_file(self, tmp_path: object) -> None:
        """update 对不存在的文件不抛异常"""
        tmp = tmp_path  # type: Path
        updater = LedgerUpdater()
        # read_file 对不存在的文件返回空字符串，update 应安全退出
        updater.update(str(tmp / "nonexistent.md"), "CHG-PLC-2026-001", "测试")

    def test_update_no_index_table(self, tmp_path: object) -> None:
        """update 对无变更单索引表格的台帐不写入"""
        tmp = tmp_path  # type: Path
        ledger = tmp / "no_index.md"
        ledger.write_text("# 版本变更台帐\n\n无索引表格\n", encoding="utf-8")

        updater = LedgerUpdater()
        updater.update(str(ledger), "CHG-PLC-2026-001", "测试")

        content = ledger.read_text(encoding="utf-8")
        assert "CHG-PLC-2026-001" not in content

    def test_update_sequential_numbering(self, tmp_path: object) -> None:
        """update 连续追加时序号递增"""
        tmp = tmp_path  # type: Path
        ledger = tmp / "ledger.md"
        ledger.write_text(
            "# 版本变更台帐\n\n"
            "## 变更单索引\n\n"
            "| 序号 | 变更编号 | 描述 |\n"
            "|------|----------|------|\n"
            "| 001 | CHG-PLC-2026-001 | 修复1 |\n",
            encoding="utf-8",
        )

        updater = LedgerUpdater()
        updater.update(str(ledger), "CHG-DOCU-2026-002", "文档更新")

        content = ledger.read_text(encoding="utf-8")
        assert "002" in content
        assert "CHG-DOCU-2026-002" in content


class TestGetNextSequence:
    """LedgerUpdater._get_next_sequence 测试"""

    def test_empty_content(self) -> None:
        """空内容返回 1"""
        updater = LedgerUpdater()
        assert updater._get_next_sequence("") == 1

    def test_no_index(self) -> None:
        """无变更单索引返回 1"""
        updater = LedgerUpdater()
        content = "# 标题\n\n无索引\n"
        assert updater._get_next_sequence(content) == 1

    def test_with_existing_entries(self) -> None:
        """有已有条目时返回 max+1"""
        updater = LedgerUpdater()
        content = (
            "# 台帐\n\n"
            "## 变更单索引\n\n"
            "| 序号 | 变更编号 |\n"
            "|------|----------|\n"
            "| 001 | CHG-001 |\n"
            "| 003 | CHG-003 |\n"
        )
        assert updater._get_next_sequence(content) == 4

    def test_non_digit_sequence_ignored(self) -> None:
        """非数字序号被忽略"""
        updater = LedgerUpdater()
        content = (
            "# 台帐\n\n"
            "## 变更单索引\n\n"
            "| 序号 | 变更编号 |\n"
            "|------|----------|\n"
            "| abc | CHG-001 |\n"
        )
        assert updater._get_next_sequence(content) == 1


class TestInsertRowToIndexTable:
    """LedgerUpdater._insert_row_to_index_table 测试"""

    def test_insert_after_separator(self) -> None:
        """在分隔行后插入新行"""
        updater = LedgerUpdater()
        content = (
            "# 台帐\n\n"
            "## 变更单索引\n\n"
            "| 序号 | 变更编号 |\n"
            "|------|----------|\n"
        )
        new_row = "| 001 | CHG-001 | 测试 |\n"
        result = updater._insert_row_to_index_table(content, new_row)
        assert "CHG-001" in result
        # 新行应在分隔行之后
        lines = result.split("\n")
        found_sep = False
        for line in lines:
            if "---" in line:
                found_sep = True
            elif found_sep and "CHG-001" in line:
                break

    def test_no_index_section(self) -> None:
        """无变更单索引时不插入"""
        updater = LedgerUpdater()
        content = "# 台帐\n\n无索引\n"
        new_row = "| 001 | CHG-001 | 测试 |\n"
        result = updater._insert_row_to_index_table(content, new_row)
        assert "CHG-001" not in result


class TestLedgerUpdaterUpdateStatus:
    """LedgerUpdater.update_status 测试（TD-T10 修复）"""

    def test_update_status_updates_last_column(self, tmp_path: object) -> None:
        """update_status 更新指定变更单的状态列（最后一列）"""
        tmp = tmp_path  # type: Path
        ledger = tmp / "ledger.md"
        ledger.write_text(
            "# 版本变更台帐\n\n"
            "## 变更单索引\n\n"
            "| 序号 | 变更编号 | 领域 | 申请人 | 申请日期 | 变更描述 | 完成日期 | 状态 |\n"
            "|------|----------|------|--------|----------|----------|----------|------|\n"
            "| 001 | CHG-SCPT-2026-001 | SCPT | fubai | 2026-06-25 | 测试 | | 🔄待处理 |\n",
            encoding="utf-8",
        )

        updater = LedgerUpdater()
        updater.update_status(str(ledger), "CHG-SCPT-2026-001", "✅已关闭")

        content = ledger.read_text(encoding="utf-8")
        assert "✅已关闭" in content
        assert "🔄待处理" not in content
        # 其他列保持不变
        assert "CHG-SCPT-2026-001" in content
        assert "fubai" in content

    def test_update_status_not_found(self, tmp_path: object) -> None:
        """update_status 未找到 change_number 时不修改内容"""
        tmp = tmp_path  # type: Path
        ledger = tmp / "ledger.md"
        original = (
            "# 版本变更台帐\n\n"
            "## 变更单索引\n\n"
            "| 序号 | 变更编号 | 状态 |\n"
            "|------|----------|------|\n"
            "| 001 | CHG-SCPT-2026-001 | 🔄待处理 |\n"
        )
        ledger.write_text(original, encoding="utf-8")

        updater = LedgerUpdater()
        updater.update_status(str(ledger), "CHG-SCPT-2026-999", "✅已关闭")

        content = ledger.read_text(encoding="utf-8")
        assert content == original

    def test_update_status_empty_file(self, tmp_path: object) -> None:
        """update_status 对空文件不抛异常"""
        tmp = tmp_path  # type: Path
        ledger = tmp / "empty.md"
        ledger.write_text("", encoding="utf-8")

        updater = LedgerUpdater()
        updater.update_status(str(ledger), "CHG-SCPT-2026-001", "✅已关闭")

        content = ledger.read_text(encoding="utf-8")
        assert content == ""

    def test_update_status_multiple_rows_only_updates_target(self, tmp_path: object) -> None:
        """update_status 多行时只更新目标行"""
        tmp = tmp_path  # type: Path
        ledger = tmp / "ledger.md"
        ledger.write_text(
            "# 版本变更台帐\n\n"
            "## 变更单索引\n\n"
            "| 序号 | 变更编号 | 状态 |\n"
            "|------|----------|------|\n"
            "| 001 | CHG-SCPT-2026-001 | 🔄待处理 |\n"
            "| 002 | CHG-SCPT-2026-002 | 🔄待处理 |\n",
            encoding="utf-8",
        )

        updater = LedgerUpdater()
        updater.update_status(str(ledger), "CHG-SCPT-2026-002", "✅已关闭")

        content = ledger.read_text(encoding="utf-8")
        # 目标行已更新
        assert "CHG-SCPT-2026-002 | ✅已关闭" in content
        # 非目标行保持不变
        assert "CHG-SCPT-2026-001 | 🔄待处理" in content


class TestLedgerUpdaterRemove:
    """LedgerUpdater.remove 测试（TD-T10 修复）"""

    def test_remove_deletes_row(self, tmp_path: object) -> None:
        """remove 删除指定变更单的行"""
        tmp = tmp_path  # type: Path
        ledger = tmp / "ledger.md"
        ledger.write_text(
            "# 版本变更台帐\n\n"
            "## 变更单索引\n\n"
            "| 序号 | 变更编号 | 状态 |\n"
            "|------|----------|------|\n"
            "| 001 | CHG-SCPT-2026-001 | 🔄待处理 |\n"
            "| 002 | CHG-SCPT-2026-002 | 🔄待处理 |\n",
            encoding="utf-8",
        )

        updater = LedgerUpdater()
        updater.remove(str(ledger), "CHG-SCPT-2026-001")

        content = ledger.read_text(encoding="utf-8")
        assert "CHG-SCPT-2026-001" not in content
        assert "CHG-SCPT-2026-002" in content

    def test_remove_not_found(self, tmp_path: object) -> None:
        """remove 未找到 change_number 时不修改内容"""
        tmp = tmp_path  # type: Path
        ledger = tmp / "ledger.md"
        original = (
            "# 版本变更台帐\n\n"
            "## 变更单索引\n\n"
            "| 序号 | 变更编号 | 状态 |\n"
            "|------|----------|------|\n"
            "| 001 | CHG-SCPT-2026-001 | 🔄待处理 |\n"
        )
        ledger.write_text(original, encoding="utf-8")

        updater = LedgerUpdater()
        updater.remove(str(ledger), "CHG-SCPT-2026-999")

        content = ledger.read_text(encoding="utf-8")
        assert content == original

    def test_remove_empty_file(self, tmp_path: object) -> None:
        """remove 对空文件不抛异常"""
        tmp = tmp_path  # type: Path
        ledger = tmp / "empty.md"
        ledger.write_text("", encoding="utf-8")

        updater = LedgerUpdater()
        updater.remove(str(ledger), "CHG-SCPT-2026-001")

        content = ledger.read_text(encoding="utf-8")
        assert content == ""

    def test_remove_preserves_non_table_lines(self, tmp_path: object) -> None:
        """remove 只删除表格行，保留非表格行（如标题、说明）"""
        tmp = tmp_path  # type: Path
        ledger = tmp / "ledger.md"
        ledger.write_text(
            "# 版本变更台帐\n\n"
            "> 记录项目所有变更单的索引与状态\n\n"
            "## 变更单索引\n\n"
            "| 序号 | 变更编号 | 状态 |\n"
            "|------|----------|------|\n"
            "| 001 | CHG-SCPT-2026-001 | 🔄待处理 |\n",
            encoding="utf-8",
        )

        updater = LedgerUpdater()
        updater.remove(str(ledger), "CHG-SCPT-2026-001")

        content = ledger.read_text(encoding="utf-8")
        # 表格行已删除
        assert "CHG-SCPT-2026-001" not in content
        # 非表格行保留
        assert "# 版本变更台帐" in content
        assert "记录项目所有变更单的索引与状态" in content
        assert "## 变更单索引" in content
