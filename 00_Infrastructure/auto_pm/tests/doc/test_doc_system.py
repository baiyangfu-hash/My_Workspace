from auto_pm.domain.doc.services import (
    INFRA_RUNTIME_RELATIVE,
    LEGACY_PROJECT_RELATIVE,
    DocCheckService,
    DocSyncService,
)
from auto_pm.infrastructure.doc.extractors.bridge_ast_extractor import BridgeAstExtractor
from auto_pm.infrastructure.doc.extractors.cli_ast_extractor import CliAstExtractor
from auto_pm.infrastructure.doc.extractors.gate_ast_extractor import GateAstExtractor
from auto_pm.infrastructure.doc.injector.marker_injector import MarkdownMarkerInjector


def test_cli_ast_extractor(tmp_path):
    cli_file = tmp_path / "test_cmd.py"
    cli_file.write_text('''
def cmd_run(arg1, arg2):
    """Run test command description."""
    pass
''', encoding="utf-8")
    cmds = CliAstExtractor.extract_from_directory(tmp_path)
    assert len(cmds) >= 1
    assert cmds[0].group == "test_cmd"
    assert "Run test command description" in cmds[0].doc


def test_bridge_ast_extractor(tmp_path):
    bridge_file = tmp_path / "system_bridge.py"
    bridge_file.write_text('''
class SystemBridge:
    def on_refresh(self, name):
        """Refresh system state."""
        pass
''', encoding="utf-8")
    methods = BridgeAstExtractor.extract_from_directory(tmp_path)
    assert len(methods) >= 1
    assert methods[0].bridge_name == "system_bridge"
    assert methods[0].method_name == "on_refresh"


def test_gate_ast_extractor(tmp_path):
    checker_file = tmp_path / "checker.py"
    checker_file.write_text('''
class Checker:
    def check_prds(self):
        """Check all PRD docs."""
        pass
''', encoding="utf-8")
    rules = GateAstExtractor.extract_from_checker(checker_file)
    assert len(rules) == 1
    assert rules[0].rule_id == "GATE-PRDS"


def test_marker_injector(tmp_path):
    doc_file = tmp_path / "test_doc.md"
    doc_file.write_text('''# Doc
<!-- AUTO_DOC_START: TEST_TAG -->
old content
<!-- AUTO_DOC_END: TEST_TAG -->
Footer
''', encoding="utf-8")
    ok, msg = MarkdownMarkerInjector.inject(doc_file, "TEST_TAG", "new injected table")
    assert ok is True
    content = doc_file.read_text(encoding="utf-8")
    assert "new injected table" in content
    assert "old content" not in content
    assert "Footer" in content


def test_doc_services_prefer_infra_runtime_with_legacy_docs(tmp_path):
    infra_root = tmp_path / INFRA_RUNTIME_RELATIVE
    legacy_root = tmp_path / LEGACY_PROJECT_RELATIVE
    (infra_root / "auto_pm").mkdir(parents=True)
    (legacy_root / "02_规划").mkdir(parents=True)
    (legacy_root / "06_交付物").mkdir(parents=True)

    sync_service = DocSyncService(tmp_path)
    check_service = DocCheckService(tmp_path)

    assert sync_service.source_root == infra_root
    assert sync_service.docs_root == legacy_root
    assert sync_service.app_root == infra_root
    assert check_service.source_root == infra_root
    assert check_service.docs_root == legacy_root
    assert check_service.app_root == infra_root


def test_doc_services_fall_back_to_legacy_runtime(tmp_path):
    legacy_root = tmp_path / LEGACY_PROJECT_RELATIVE
    (legacy_root / "auto_pm").mkdir(parents=True)
    (legacy_root / "PM_SESSION_SW-2026-008.md").write_text(
        "- version: V1.2.3\n",
        encoding="utf-8",
    )

    service = DocCheckService(tmp_path)

    assert service.source_root == legacy_root
    assert service.docs_root == legacy_root
    assert service.app_root == legacy_root


def test_doc_check_reads_project_version_from_pyproject(tmp_path):
    infra_root = tmp_path / INFRA_RUNTIME_RELATIVE
    legacy_root = tmp_path / LEGACY_PROJECT_RELATIVE
    (infra_root / "auto_pm").mkdir(parents=True)
    legacy_root.mkdir(parents=True)
    (infra_root / "pyproject.toml").write_text(
        """
[project]
version = "1.2.3"

[tool.ruff]
required-version = ">=0.8.4"
""",
        encoding="utf-8",
    )
    (legacy_root / "PM_SESSION_SW-2026-008.md").write_text(
        "- version: V1.2.3\n",
        encoding="utf-8",
    )

    results = DocCheckService(tmp_path).check_all()
    version_result = next(item for item in results if item.check_id == "DOC-004")

    assert "pyproject=1.2.3" in version_result.message
    assert "PM_SESSION=1.2.3" in version_result.message


def test_deadlink_checker_active_and_cold_isolation(tmp_path):
    from auto_pm.domain.doc.deadlink_checker import DeadLinkChecker

    lib_dir = tmp_path / "00_Obsidian_Base"
    active_dir = lib_dir / "01_域"
    cold_dir = lib_dir / "Archive_Cold"
    active_dir.mkdir(parents=True)
    cold_dir.mkdir(parents=True)

    # 目标文件
    (active_dir / "target.md").write_text("# Target Doc\n\n## Section One\nContent\n", encoding="utf-8")
    
    # 活跃区文件包含有效链接、代码块内忽略链接、同页锚点
    (active_dir / "active.md").write_text("""# Active Doc
[有效链接](target.md#section-one)
[[target]]
```markdown
[代码块内死链忽略](nonexistent.md)
```
`[行内代码死链忽略](nonexistent.md)`
""", encoding="utf-8")

    # 冷区文件包含死链（应被归类为 cold，不阻断门禁）
    (cold_dir / "cold.md").write_text("[冷区死链](ghost_doc.md)\n", encoding="utf-8")

    checker = DeadLinkChecker(lib_dir)
    report = checker.scan()

    assert report.passed is True
    assert len(report.active_deadlinks) == 0
    assert len(report.cold_deadlinks) == 1
    assert report.cold_deadlinks[0].target == "ghost_doc.md"


def test_index_coverage_checker_100_percent_and_missing(tmp_path):
    import json
    from auto_pm.domain.doc.index_coverage_checker import IndexCoverageChecker

    lib_dir = tmp_path / "00_Obsidian_Base"
    lib_dir.mkdir(parents=True)

    spec_file = lib_dir / "001_Test_STD.md"
    spec_file.write_text("# Test Spec\n", encoding="utf-8")

    reg_data = {
        "specs": {
            "STD-001": {
                "canonical_path": "00_Obsidian_Base/001_Test_STD.md",
                "lifecycle": "stable",
            }
        }
    }
    (lib_dir / "spec_registry.json").write_text(json.dumps(reg_data), encoding="utf-8")

    # 1. 覆盖率 100%
    (lib_dir / "00_INDEX_全局规范索引.md").write_text("- [STD-001 测试规范](001_Test_STD.md)\n", encoding="utf-8")
    checker = IndexCoverageChecker(lib_dir, repo_root=tmp_path)
    report = checker.check()
    assert report.passed is True
    assert report.total_specs == 1
    assert len(report.missing_specs) == 0

    # 2. 存在缺失
    (lib_dir / "00_INDEX_全局规范索引.md").write_text("- 无规范链接\n", encoding="utf-8")
    report_missing = checker.check()
    assert report_missing.passed is False
    assert "STD-001" in report_missing.missing_specs


def test_doc_check_cli_strict_option(tmp_path):
    from click.testing import CliRunner
    from auto_pm.ui.cli.doc import doc_group

    runner = CliRunner()
    result = runner.invoke(doc_group, ["check", "--help"])
    assert result.exit_code == 0
    assert "--strict" in result.output

