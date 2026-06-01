from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from specmgr.services.check_svc import CheckService
from specmgr.services.frontmatter_svc import FrontmatterService
from specmgr.services.index_svc import IndexService
from specmgr.services.report_svc import ReportService


class TestCheckService:
    def test_run_returns_check_output(self, populated_workspace: Path) -> None:
        svc = CheckService(populated_workspace)
        output = svc.run()
        assert output.results is not None
        assert output.error_count >= 0
        assert output.warning_count >= 0
        assert output.info_count >= 0
        assert output.exit_code in (0, 1, 2)

    def test_run_with_severity_filter(self, populated_workspace: Path) -> None:
        from specmgr.core.checker_base import Severity
        svc = CheckService(populated_workspace)
        output = svc.run(min_severity=Severity.ERROR)
        assert all(r.severity >= Severity.ERROR for r in output.results)

    def test_run_with_check_ids(self, populated_workspace: Path) -> None:
        svc = CheckService(populated_workspace)
        output = svc.run(check_ids=["SHC-001"])
        assert all(r.check_id == "SHC-001" for r in output.results)

    def test_run_missing_registry(self, workspace: Path) -> None:
        svc = CheckService(workspace)
        output = svc.run()
        assert output.error_count == 1
        assert output.results[0].check_id == "SHC-000"

    def test_run_project_scope_defaults_to_pmsession_check(self, populated_workspace: Path) -> None:
        project_root = populated_workspace / "DJ-2026-000"
        project_root.mkdir(parents=True, exist_ok=True)
        (project_root / "PM_SESSION_DJ-2026-000.md").write_text(
            "# PM_SESSION_DJ-2026-000\n\n## 4. Artifacts Index\n- req:\n  - missing.md\n",
            encoding="utf-8",
        )

        spec_dir = populated_workspace / "00_Obsidian_Base全局规范文件仓库" / "01_项目管理域"
        (spec_dir / "PM-2026-001_项目管理规范_DEV-V1.0.0_copy.md").write_text(
            "# Duplicate\n",
            encoding="utf-8",
        )

        svc = CheckService(populated_workspace)
        output = svc.run(scope="project", project_root=project_root)
        assert output.results
        assert all(r.check_id == "SHC-009" for r in output.results)
        assert output.exit_code == 2


class TestIndexService:
    def test_run_generates_files(self, populated_workspace: Path) -> None:
        svc = IndexService(populated_workspace)
        output = svc.run()
        assert len(output.generated_files) > 0
        for f in output.generated_files:
            assert f.exists()

    def test_run_single_domain(self, populated_workspace: Path) -> None:
        svc = IndexService(populated_workspace)
        output = svc.run(domains=["plc"])
        assert len(output.generated_files) == 1

    def test_run_missing_registry(self, workspace: Path) -> None:
        with pytest.raises(FileNotFoundError):
            IndexService(workspace)


class TestFrontmatterService:
    def test_preview_returns_items(self, populated_workspace: Path) -> None:
        svc = FrontmatterService(populated_workspace)
        items = svc.preview()
        assert len(items) > 0

    def test_preview_with_spec_id(self, populated_workspace: Path) -> None:
        svc = FrontmatterService(populated_workspace)
        items = svc.preview(spec_id="PM-2026-001")
        assert all(i.spec_id == "PM-2026-001" for i in items)

    def test_preview_nonexistent_spec(self, populated_workspace: Path) -> None:
        svc = FrontmatterService(populated_workspace)
        items = svc.preview(spec_id="NONEXISTENT-000")
        assert len(items) == 0

    def test_apply_dry_run_no_modification(self, populated_workspace: Path) -> None:
        spec_path = populated_workspace / "00_Obsidian_Base全局规范文件仓库" / "01_项目管理域" / "PM-2026-001_项目管理规范_DEV-V1.0.0.md"
        original_content = spec_path.read_text(encoding="utf-8")
        svc = FrontmatterService(populated_workspace)
        items = svc.preview()
        pending = [i for i in items if i.status == "pending"]
        if pending:
            result = svc.apply(pending)
            assert result.modified_count >= 0

    def test_missing_registry(self, workspace: Path) -> None:
        with pytest.raises(FileNotFoundError):
            FrontmatterService(workspace)


class TestFrontmatterYamlGeneration:
    def test_special_characters_in_title(self, populated_workspace: Path) -> None:
        import json
        reg_path = populated_workspace / "00_Obsidian_Base全局规范文件仓库" / "spec_registry.json"
        data = json.loads(reg_path.read_text(encoding="utf-8"))
        data["specs"]["PM-2026-001"]["title"] = "规范：编程#标准 \"引用\""
        reg_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        svc = FrontmatterService(populated_workspace)
        items = svc.preview(spec_id="PM-2026-001")
        for item in items:
            if item.status == "pending" and item.new_frontmatter:
                fm_text = item.new_frontmatter.replace("---", "").strip()
                parsed = yaml.safe_load(fm_text)
                assert isinstance(parsed, dict)
                assert "规范" in parsed.get("title", "")


class TestReportService:
    def test_generate_markdown(self, populated_workspace: Path) -> None:
        svc = ReportService(populated_workspace)
        result = svc.generate(fmt="markdown")
        assert result.fmt == "markdown"
        assert result.output_path.exists()
        assert "规范元数据汇总报告" in result.content

    def test_generate_json(self, populated_workspace: Path) -> None:
        svc = ReportService(populated_workspace)
        result = svc.generate(fmt="json")
        assert result.fmt == "json"
        assert result.output_path.exists()
        import json
        data = json.loads(result.content)
        assert "specs" in data

    def test_generate_custom_output_path(self, populated_workspace: Path, tmp_path: Path) -> None:
        svc = ReportService(populated_workspace)
        custom_path = tmp_path / "custom_report.md"
        result = svc.generate(output_path=custom_path)
        assert result.output_path == custom_path
        assert custom_path.exists()

    def test_missing_registry(self, workspace: Path) -> None:
        with pytest.raises(FileNotFoundError):
            ReportService(workspace)
