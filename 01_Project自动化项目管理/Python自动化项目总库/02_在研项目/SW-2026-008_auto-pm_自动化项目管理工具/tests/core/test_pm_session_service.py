"""PM_SESSION 服务测试 - CHG-088 Stage 2

测试 PmSessionParser / PmSessionCheckService / PmSessionArchiveService / generate_view。
"""

from __future__ import annotations

from pathlib import Path

import pytest

from auto_pm.core.pm_session_service import (
    DEPRECATED_SECTIONS,
    MAX_FILE_LINES,
    MAX_FILE_SIZE_KB,
    REQUIRED_SECTIONS,
    ArchiveResult,
    CheckResult,
    PmSessionArchiveService,
    PmSessionCheckService,
    PmSessionParser,
    generate_view,
)

# ---------- Fixtures ----------

SAMPLE_PM_SESSION = """# PM_SESSION_TEST

## 0. Meta

- project_id: TEST-001
- last_updated: 2026-07-04

## 1. Positioning

- one_liner: 测试项目

## 2. Current Focus

- current_focus: 当前焦点

## 3. Status Summary

- in_progress: 测试中

## 4. Artifacts Index

- req: doc.md

## 5. Logs

- change_log: 测试日志

## 6. Implementation Log

- 2026-07-04 测试实施记录

## 8. Handoff Notes

- current_state: 测试状态

## 9. Next Actions

- [待启动] 测试下一步
"""


SAMPLE_WITH_SECTION_7 = """# PM_SESSION_TEST

## 0. Meta

- project_id: TEST-001

## 7. Verification Log

- 旧章节不应存在

## 8. Handoff Notes

- current_state: 测试
"""


@pytest.fixture
def sample_pm_session_file(tmp_path: Path) -> Path:
    """创建测试用 PM_SESSION 文件"""
    f = tmp_path / "PM_SESSION_TEST-001.md"
    f.write_text(SAMPLE_PM_SESSION, encoding="utf-8")
    return f


@pytest.fixture
def sample_with_section_7_file(tmp_path: Path) -> Path:
    """创建包含 §7 的测试文件（应触发 deprecated 警告）"""
    f = tmp_path / "PM_SESSION_TEST-002.md"
    f.write_text(SAMPLE_WITH_SECTION_7, encoding="utf-8")
    return f


# ---------- PmSessionParser 测试 ----------


class TestPmSessionParser:
    def test_parse_content_returns_all_sections(self) -> None:
        parser = PmSessionParser()
        result = parser.parse_content(SAMPLE_PM_SESSION)
        section_numbers = {s.number for s in result.sections}
        assert section_numbers == {"0", "1", "2", "3", "4", "5", "6", "8", "9"}

    def test_parse_content_extracts_section_titles(self) -> None:
        parser = PmSessionParser()
        result = parser.parse_content(SAMPLE_PM_SESSION)
        section_0 = result.get_section("0")
        assert section_0 is not None
        assert section_0.title == "Meta"
        section_2 = result.get_section("2")
        assert section_2 is not None
        assert "Current Focus" in section_2.title

    def test_parse_content_section_content(self) -> None:
        parser = PmSessionParser()
        result = parser.parse_content(SAMPLE_PM_SESSION)
        section_0 = result.get_section("0")
        assert section_0 is not None
        assert "project_id: TEST-001" in section_0.content
        assert "last_updated: 2026-07-04" in section_0.content

    def test_parse_content_line_numbers(self) -> None:
        parser = PmSessionParser()
        result = parser.parse_content(SAMPLE_PM_SESSION)
        section_0 = result.get_section("0")
        assert section_0 is not None
        assert section_0.start_line < section_0.end_line
        assert section_0.line_count > 0

    def test_parse_file(self, sample_pm_session_file: Path) -> None:
        parser = PmSessionParser()
        result = parser.parse_file(sample_pm_session_file)
        assert result.file_path == sample_pm_session_file
        assert result.total_lines > 0
        assert len(result.sections) == 9

    def test_parse_content_pre_header_lines(self) -> None:
        parser = PmSessionParser()
        result = parser.parse_content(SAMPLE_PM_SESSION)
        assert len(result.pre_header_lines) > 0
        assert result.pre_header_lines[0] == "# PM_SESSION_TEST"

    def test_get_section_nonexistent(self) -> None:
        parser = PmSessionParser()
        result = parser.parse_content(SAMPLE_PM_SESSION)
        assert result.get_section("99") is None

    def test_find_missing_required_empty(self) -> None:
        parser = PmSessionParser()
        result = parser.parse_content(SAMPLE_PM_SESSION)
        assert result.find_missing_required() == set()

    def test_find_missing_required_with_gaps(self) -> None:
        parser = PmSessionParser()
        result = parser.parse_content(SAMPLE_WITH_SECTION_7)
        # SAMPLE_WITH_SECTION_7 只有 §0 和 §7 和 §8
        missing = result.find_missing_required()
        assert "1" in missing
        assert "2" in missing
        assert "3" in missing
        assert "6" in missing
        assert "9" in missing

    def test_find_deprecated_present_empty(self) -> None:
        parser = PmSessionParser()
        result = parser.parse_content(SAMPLE_PM_SESSION)
        assert result.find_deprecated_present() == set()

    def test_find_deprecated_present_with_section_7(self) -> None:
        parser = PmSessionParser()
        result = parser.parse_content(SAMPLE_WITH_SECTION_7)
        assert "7" in result.find_deprecated_present()


# ---------- PmSessionCheckService 测试 ----------


class TestPmSessionCheckService:
    def test_check_healthy_file(self, sample_pm_session_file: Path) -> None:
        svc = PmSessionCheckService()
        result = svc.check(sample_pm_session_file)
        assert isinstance(result, CheckResult)
        assert result.is_healthy
        assert result.missing_required == set()
        assert result.deprecated_present == set()
        assert not result.is_oversized
        assert result.warnings == []

    def test_check_finds_missing_sections(self, sample_with_section_7_file: Path) -> None:
        svc = PmSessionCheckService()
        result = svc.check(sample_with_section_7_file)
        assert not result.is_healthy
        assert len(result.missing_required) > 0
        assert any("缺失必须章节" in w for w in result.warnings)

    def test_check_finds_deprecated_section(self, sample_with_section_7_file: Path) -> None:
        svc = PmSessionCheckService()
        result = svc.check(sample_with_section_7_file)
        assert "7" in result.deprecated_present
        assert any("已归档章节回归" in w for w in result.warnings)

    def test_check_oversized_file(self, tmp_path: Path) -> None:
        # 创建超大文件（> 150KB = 153600 字节）
        # 每个章节填充大量内容，确保总大小超过阈值
        big_content = "# PM_SESSION_BIG\n\n## 0. Meta\n\n- project_id: BIG\n\n"
        # §1-§6 各填充 30000 字节（180000 字节总计，超过 150KB）
        for i in range(1, 7):
            big_content += f"\n## {i}. Section {i}\n\n"
            # 每行约 100 字符，300 行约 30000 字节
            big_content += "\n".join(f"- line {i}-{j} " + "x" * 90 for j in range(300))
            big_content += "\n"
        # §8 和 §9
        big_content += "\n## 8. Handoff Notes\n\n- handoff\n\n## 9. Next Actions\n\n- next\n"
        big_file = tmp_path / "PM_SESSION_BIG.md"
        big_file.write_text(big_content, encoding="utf-8")

        svc = PmSessionCheckService()
        result = svc.check(big_file)
        assert result.is_oversized
        assert any("超过阈值" in w for w in result.warnings)

    def test_check_nonexistent_file(self, tmp_path: Path) -> None:
        svc = PmSessionCheckService()
        with pytest.raises(FileNotFoundError):
            svc.check(tmp_path / "nonexistent.md")


# ---------- PmSessionArchiveService 测试 ----------


class TestPmSessionArchiveService:
    def test_archive_section_creates_archive_file(self, tmp_path: Path) -> None:
        # 创建测试文件
        content = "# PM_SESSION_TEST\n\n## 6. Implementation Log\n\n"
        content += "\n".join(f"- line {i}" for i in range(50))
        content += "\n\n## 8. Handoff Notes\n\n- handoff\n"
        main_file = tmp_path / "PM_SESSION_TEST.md"
        main_file.write_text(content, encoding="utf-8")
        archive_file = tmp_path / "archive.md"

        svc = PmSessionArchiveService()
        result = svc.archive_section(
            main_file=main_file,
            archive_file=archive_file,
            section_number="6",
            keep_recent=0,
            create_backup=False,
        )

        assert isinstance(result, ArchiveResult)
        assert result.archive_file == archive_file
        assert result.archived_sections == ["6"]
        assert result.archived_line_count > 0
        assert result.main_file_lines_after < result.main_file_lines_before
        assert archive_file.exists()

    def test_archive_section_keep_recent(self, tmp_path: Path) -> None:
        content = "# PM_SESSION_TEST\n\n## 6. Implementation Log\n\n"
        content += "\n".join(f"- line {i}" for i in range(50))
        content += "\n\n## 8. Handoff Notes\n\n- handoff\n"
        main_file = tmp_path / "PM_SESSION_TEST.md"
        main_file.write_text(content, encoding="utf-8")
        archive_file = tmp_path / "archive.md"

        svc = PmSessionArchiveService()
        svc.archive_section(
            main_file=main_file,
            archive_file=archive_file,
            section_number="6",
            keep_recent=10,
            create_backup=False,
        )

        # 主文件应保留 §6 的 header + 10 行
        new_content = main_file.read_text(encoding="utf-8")
        assert "## 6. Implementation Log" in new_content
        assert "## 8. Handoff Notes" in new_content

    def test_archive_section_creates_backup(self, tmp_path: Path) -> None:
        content = "# PM_SESSION_TEST\n\n## 6. Log\n\n- x\n\n## 8. Handoff\n\n- y\n"
        main_file = tmp_path / "PM_SESSION_TEST.md"
        main_file.write_text(content, encoding="utf-8")
        archive_file = tmp_path / "archive.md"

        svc = PmSessionArchiveService()
        result = svc.archive_section(
            main_file=main_file,
            archive_file=archive_file,
            section_number="6",
            keep_recent=0,
            create_backup=True,
        )

        assert result.backup_file is not None
        assert result.backup_file.exists()

    def test_archive_section_appends_to_existing_archive(self, tmp_path: Path) -> None:
        content = "# PM_SESSION_TEST\n\n## 6. Log\n\n- x\n\n## 8. Handoff\n\n- y\n"
        main_file = tmp_path / "PM_SESSION_TEST.md"
        main_file.write_text(content, encoding="utf-8")
        archive_file = tmp_path / "archive.md"
        archive_file.write_text("# Existing Archive\n\n## old\n- old content\n", encoding="utf-8")

        svc = PmSessionArchiveService()
        svc.archive_section(
            main_file=main_file,
            archive_file=archive_file,
            section_number="6",
            keep_recent=0,
            create_backup=False,
        )

        archive_content = archive_file.read_text(encoding="utf-8")
        assert "Existing Archive" in archive_content
        assert "## 6. Log" in archive_content

    def test_archive_section_nonexistent_section(self, tmp_path: Path) -> None:
        content = "# PM_SESSION_TEST\n\n## 0. Meta\n\n- x\n"
        main_file = tmp_path / "PM_SESSION_TEST.md"
        main_file.write_text(content, encoding="utf-8")
        archive_file = tmp_path / "archive.md"

        svc = PmSessionArchiveService()
        with pytest.raises(ValueError, match="章节 §99"):
            svc.archive_section(
                main_file=main_file,
                archive_file=archive_file,
                section_number="99",
            )

    def test_archive_section_nonexistent_main_file(self, tmp_path: Path) -> None:
        svc = PmSessionArchiveService()
        with pytest.raises(FileNotFoundError):
            svc.archive_section(
                main_file=tmp_path / "nonexistent.md",
                archive_file=tmp_path / "archive.md",
                section_number="6",
            )

    def test_archive_section_keep_recent_ge_total(self, tmp_path: Path) -> None:
        """keep_recent >= 章节总行数时，应跳过归档"""
        content = "# PM_SESSION_TEST\n\n## 6. Log\n\n- x\n\n## 8. Handoff\n\n- y\n"
        main_file = tmp_path / "PM_SESSION_TEST.md"
        main_file.write_text(content, encoding="utf-8")
        archive_file = tmp_path / "archive.md"

        svc = PmSessionArchiveService()
        result = svc.archive_section(
            main_file=main_file,
            archive_file=archive_file,
            section_number="6",
            keep_recent=100,  # 远超章节行数
            create_backup=False,
        )

        assert result.archived_line_count == 0
        assert result.main_file_lines_after == result.main_file_lines_before


# ---------- generate_view 测试 ----------


class TestGenerateView:
    def test_generate_view_contains_header(self) -> None:
        parser = PmSessionParser()
        result = parser.parse_content(SAMPLE_PM_SESSION)
        view = generate_view(result)
        assert "PM_SESSION 只读视图" in view

    def test_generate_view_contains_section_2(self) -> None:
        parser = PmSessionParser()
        result = parser.parse_content(SAMPLE_PM_SESSION)
        view = generate_view(result)
        assert "§2" in view
        assert "Current Focus" in view
        assert "当前焦点" in view

    def test_generate_view_contains_section_3(self) -> None:
        parser = PmSessionParser()
        result = parser.parse_content(SAMPLE_PM_SESSION)
        view = generate_view(result)
        assert "§3" in view
        assert "Status Summary" in view

    def test_generate_view_contains_section_9(self) -> None:
        parser = PmSessionParser()
        result = parser.parse_content(SAMPLE_PM_SESSION)
        view = generate_view(result)
        assert "§9" in view
        assert "Next Actions" in view
        assert "待启动" in view

    def test_generate_view_does_not_contain_section_7(self) -> None:
        parser = PmSessionParser()
        result = parser.parse_content(SAMPLE_PM_SESSION)
        view = generate_view(result)
        assert "§7" not in view


# ---------- 常量测试 ----------


class TestConstants:
    def test_required_sections_excludes_7(self) -> None:
        assert "7" not in REQUIRED_SECTIONS
        assert "0" in REQUIRED_SECTIONS
        assert "9" in REQUIRED_SECTIONS

    def test_deprecated_sections_contains_7(self) -> None:
        assert "7" in DEPRECATED_SECTIONS

    def test_thresholds_reasonable(self) -> None:
        assert MAX_FILE_SIZE_KB > 0
        assert MAX_FILE_LINES > 0
        assert MAX_FILE_SIZE_KB >= 100  # 至少 100KB
        assert MAX_FILE_LINES >= 200  # 至少 200 行
