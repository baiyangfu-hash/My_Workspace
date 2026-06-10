from __future__ import annotations

from pathlib import Path

from specmgr.core.checker_base import (
    CheckResult,
    DuplicateChecker,
    FrontmatterChecker,
    HealthChecker,
    IndexLinkChecker,
    ObsidianLinkChecker,
    PMSessionRefChecker,
    RulesPathChecker,
    Severity,
    UnlistedSpecChecker,
    VersionMismatchChecker,
)
from specmgr.core.config import WorkspaceConfig
from specmgr.core.registry import SpecRegistry
from specmgr.core.scanner import SpecScanner


class TestDuplicateChecker:
    def test_no_duplicates(self, populated_workspace: Path) -> None:
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace)
        checker = DuplicateChecker()
        results = checker.check(reg, scanner)
        shc001 = [r for r in results if r.check_id == "SHC-001"]
        assert len(shc001) == 0

    def test_with_duplicates(self, populated_workspace: Path) -> None:
        spec_dir = populated_workspace / "00_Obsidian_Base全局规范文件仓库" / "01_项目管理域"
        dup_file = spec_dir / "PM-2026-001_项目管理规范_DEV_copy.md"
        dup_file.write_text("# Duplicate\n", encoding="utf-8")
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace)
        checker = DuplicateChecker()
        results = checker.check(reg, scanner)
        shc001 = [r for r in results if r.check_id == "SHC-001"]
        assert len(shc001) >= 1
        assert shc001[0].severity == Severity.ERROR


class TestVersionMismatchChecker:
    def test_matching_versions(self, populated_workspace: Path) -> None:
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace)
        checker = VersionMismatchChecker()
        results = checker.check(reg, scanner)
        shc002 = [r for r in results if r.check_id == "SHC-002"]
        assert len(shc002) == 0

    def test_mismatched_versions(self, populated_workspace: Path) -> None:
        spec_path = populated_workspace / "00_Obsidian_Base全局规范文件仓库" / "01_项目管理域" / "PM-2026-001_项目管理规范_DEV.md"
        spec_path.write_text("# PM Spec\n\n版本: V9.9.9\n", encoding="utf-8")
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace)
        checker = VersionMismatchChecker()
        results = checker.check(reg, scanner)
        shc002 = [r for r in results if r.check_id == "SHC-002"]
        assert len(shc002) >= 1


class TestFrontmatterChecker:
    def test_existing_frontmatter(self, populated_workspace: Path) -> None:
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace)
        checker = FrontmatterChecker()
        results = checker.check(reg, scanner)
        shc007 = [r for r in results if r.check_id == "SHC-007"]
        assert all(r.severity == Severity.INFO for r in shc007)

    def test_missing_frontmatter(self, populated_workspace: Path) -> None:
        spec_path = populated_workspace / "00_Obsidian_Base全局规范文件仓库" / "01_项目管理域" / "PM-2026-001_项目管理规范_DEV.md"
        spec_path.write_text("# PM Spec without frontmatter\n\n版本: V1.0.0\n", encoding="utf-8")
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace)
        checker = FrontmatterChecker()
        results = checker.check(reg, scanner)
        shc007 = [r for r in results if r.check_id == "SHC-007"]
        assert len(shc007) >= 1
        assert shc007[0].severity == Severity.INFO


class TestUnlistedSpecChecker:
    def test_all_registered(self, populated_workspace: Path) -> None:
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace)
        checker = UnlistedSpecChecker()
        results = checker.check(reg, scanner)
        shc005 = [r for r in results if r.check_id == "SHC-005"]
        assert len(shc005) == 0

    def test_unlisted_spec(self, populated_workspace: Path) -> None:
        spec_dir = populated_workspace / "00_Obsidian_Base全局规范文件仓库" / "01_项目管理域"
        unlisted = spec_dir / "PM-9999-001_未注册规范_DEV.md"
        unlisted.write_text("# Unlisted\n", encoding="utf-8")
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace)
        checker = UnlistedSpecChecker()
        results = checker.check(reg, scanner)
        shc005 = [r for r in results if r.check_id == "SHC-005"]
        assert len(shc005) >= 1


class TestIndexLinkChecker:
    def test_index_with_valid_links(self, populated_workspace: Path) -> None:
        config = WorkspaceConfig(workspace=populated_workspace)
        for output_key, output_path in config.full_output_paths.items():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("# Index\n", encoding="utf-8")
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace, config)
        checker = IndexLinkChecker()
        results = checker.check(reg, scanner)
        shc004 = [r for r in results if r.check_id == "SHC-004"]
        assert len(shc004) == 0

    def test_index_with_broken_link(self, populated_workspace: Path) -> None:
        config = WorkspaceConfig(workspace=populated_workspace)
        index_path = config.full_output_paths.get("pm_index")
        if index_path:
            index_path.parent.mkdir(parents=True, exist_ok=True)
            index_path.write_text(
                "# Index\n\n| ID | File |\n|----|------|\n| PM-2026-001 | [PM-2026-001](nonexistent.md) |\n",
                encoding="utf-8",
            )
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace, config)
        checker = IndexLinkChecker()
        results = checker.check(reg, scanner)
        shc004 = [r for r in results if r.check_id == "SHC-004"]
        assert len(shc004) >= 1
        assert shc004[0].severity == Severity.ERROR


class TestObsidianLinkChecker:
    def test_no_broken_links(self, populated_workspace: Path) -> None:
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace)
        checker = ObsidianLinkChecker()
        results = checker.check(reg, scanner)
        shc006 = [r for r in results if r.check_id == "SHC-006"]
        assert len(shc006) == 0

    def test_broken_wikilink(self, populated_workspace: Path) -> None:
        spec_path = populated_workspace / "00_Obsidian_Base全局规范文件仓库" / "01_项目管理域" / "PM-2026-001_项目管理规范_DEV.md"
        spec_path.write_text(
            "---\nspec_id: PM-2026-001\n---\n\n# Title\n\nSee [[PM-9999-888_nonexistent]]\n",
            encoding="utf-8",
        )
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace)
        checker = ObsidianLinkChecker()
        results = checker.check(reg, scanner)
        shc006 = [r for r in results if r.check_id == "SHC-006"]
        assert len(shc006) >= 1


class TestRulesPathChecker:
    def test_no_rules_dir(self, populated_workspace: Path) -> None:
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace)
        checker = RulesPathChecker()
        results = checker.check(reg, scanner)
        shc008 = [r for r in results if r.check_id == "SHC-008"]
        assert len(shc008) == 0

    def test_rules_with_deprecated_ref(self, populated_workspace: Path) -> None:
        rules_dir = populated_workspace / ".trae" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        rule_file = rules_dir / "test_rule.md"
        rule_file.write_text("遵循规范 PM-2026-002", encoding="utf-8")
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace)
        checker = RulesPathChecker()
        results = checker.check(reg, scanner)
        shc008 = [r for r in results if r.check_id == "SHC-008"]
        assert len(shc008) >= 1
        assert any(r.severity == Severity.WARNING for r in shc008)


class TestPMSessionRefChecker:
    def test_project_scope_only_scans_project_root(self, populated_workspace: Path) -> None:
        project_a = populated_workspace / "DJ-2026-000"
        project_b = populated_workspace / "DJ-2026-001"
        project_a.mkdir(parents=True, exist_ok=True)
        project_b.mkdir(parents=True, exist_ok=True)

        (project_a / "PM_SESSION_DJ-2026-000.md").write_text(
            "# PM_SESSION_DJ-2026-000\n\n## 4. Artifacts Index\n- req:\n  - missing_a.md\n",
            encoding="utf-8",
        )
        (project_b / "PM_SESSION_DJ-2026-001.md").write_text(
            "# PM_SESSION_DJ-2026-001\n\n## 4. Artifacts Index\n- req:\n  - missing_b.md\n",
            encoding="utf-8",
        )

        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace, project_root=project_a)
        checker = PMSessionRefChecker()
        results = checker.check(reg, scanner)

        shc009 = [r for r in results if r.check_id == "SHC-009"]
        assert len(shc009) == 1
        assert "DJ-2026-000" in shc009[0].details
        assert "missing_a.md" in shc009[0].message


class TestHealthChecker:
    def test_run_all(self, populated_workspace: Path) -> None:
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace)
        checker = HealthChecker()
        results = checker.run_all(reg, scanner)
        assert isinstance(results, list)
        assert all(isinstance(r, CheckResult) for r in results)

    def test_run_by_id(self, populated_workspace: Path) -> None:
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace)
        checker = HealthChecker()
        results = checker.run_by_id("SHC-001", reg, scanner)
        assert all(r.check_id == "SHC-001" for r in results)

    def test_run_by_invalid_id(self, populated_workspace: Path) -> None:
        reg = SpecRegistry(populated_workspace)
        reg.load()
        scanner = SpecScanner(populated_workspace)
        checker = HealthChecker()
        results = checker.run_by_id("SHC-999", reg, scanner)
        assert len(results) == 0
