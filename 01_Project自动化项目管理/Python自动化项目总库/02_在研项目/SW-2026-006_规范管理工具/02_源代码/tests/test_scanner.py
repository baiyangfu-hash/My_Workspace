from __future__ import annotations

from pathlib import Path

from specmgr.core.scanner import SpecScanner


class TestSpecScannerScanAll:
    def test_scan_finds_spec_files(self, populated_workspace: Path) -> None:
        scanner = SpecScanner(populated_workspace)
        result = scanner.scan_all()
        assert len(result) >= 3
        assert "PM-2026-001" in result
        assert "PLC-2026-001" in result
        assert "CODE-210" in result

    def test_scan_empty_workspace(self, workspace: Path) -> None:
        scanner = SpecScanner(workspace)
        result = scanner.scan_all()
        assert len(result) == 0

    def test_scan_ignores_non_spec_files(self, populated_workspace: Path) -> None:
        non_spec = populated_workspace / "00_Obsidian_Base全局规范文件仓库" / "01_项目管理域" / "random_notes.md"
        non_spec.write_text("# Random Notes", encoding="utf-8")
        scanner = SpecScanner(populated_workspace)
        result = scanner.scan_all()
        assert "random" not in result


class TestSpecScannerExtractVersion:
    def test_extract_version_chinese(self, populated_workspace: Path) -> None:
        scanner = SpecScanner(populated_workspace)
        spec_path = populated_workspace / "00_Obsidian_Base全局规范文件仓库" / "01_项目管理域" / "PM-2026-001_项目管理规范_DEV-V1.0.0.md"
        version = scanner.extract_version(spec_path)
        assert version is not None
        assert "1.0.0" in version

    def test_extract_version_no_version(self, workspace: Path) -> None:
        spec_dir = workspace / "00_Obsidian_Base全局规范文件仓库" / "01_项目管理域"
        spec_dir.mkdir(parents=True, exist_ok=True)
        f = spec_dir / "PM-2026-099_无版本规范_DEV.md"
        f.write_text("# No version here\n", encoding="utf-8")
        scanner = SpecScanner(workspace)
        assert scanner.extract_version(f) is None


class TestSpecScannerExtractFrontmatter:
    def test_extract_existing_frontmatter(self, populated_workspace: Path) -> None:
        scanner = SpecScanner(populated_workspace)
        spec_path = populated_workspace / "00_Obsidian_Base全局规范文件仓库" / "01_项目管理域" / "PM-2026-001_项目管理规范_DEV-V1.0.0.md"
        fm = scanner.extract_frontmatter(spec_path)
        assert fm is not None
        assert isinstance(fm, dict)
        assert fm.get("spec_id") == "PM-2026-001"

    def test_extract_no_frontmatter(self, workspace: Path) -> None:
        spec_dir = workspace / "00_Obsidian_Base全局规范文件仓库" / "01_项目管理域"
        spec_dir.mkdir(parents=True, exist_ok=True)
        f = spec_dir / "PM-2026-099_无frontmatter_DEV.md"
        f.write_text("# No frontmatter\n\nSome content\n", encoding="utf-8")
        scanner = SpecScanner(workspace)
        assert scanner.extract_frontmatter(f) is None

    def test_extract_invalid_yaml_frontmatter(self, workspace: Path) -> None:
        spec_dir = workspace / "00_Obsidian_Base全局规范文件仓库" / "01_项目管理域"
        spec_dir.mkdir(parents=True, exist_ok=True)
        f = spec_dir / "PM-2026-099_无效YAML_DEV.md"
        f.write_text("---\n: invalid: yaml: [\n---\n\n# Content\n", encoding="utf-8")
        scanner = SpecScanner(workspace)
        assert scanner.extract_frontmatter(f) is None


class TestSpecScannerFindDuplicates:
    def test_no_duplicates(self, populated_workspace: Path) -> None:
        scanner = SpecScanner(populated_workspace)
        dups = scanner.find_duplicates()
        assert len(dups) == 0

    def test_with_duplicates(self, populated_workspace: Path) -> None:
        spec_dir = populated_workspace / "00_Obsidian_Base全局规范文件仓库" / "01_项目管理域"
        dup_file = spec_dir / "PM-2026-001_项目管理规范_DEV-V1.0.0_copy.md"
        dup_file.write_text("# Duplicate\n", encoding="utf-8")
        scanner = SpecScanner(populated_workspace)
        dups = scanner.find_duplicates()
        assert "PM-2026-001" in dups
        assert len(dups["PM-2026-001"]) >= 2
