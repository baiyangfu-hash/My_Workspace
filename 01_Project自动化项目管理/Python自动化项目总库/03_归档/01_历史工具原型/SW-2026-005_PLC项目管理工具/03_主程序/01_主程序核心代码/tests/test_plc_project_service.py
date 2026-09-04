"""PlcProjectService 单元测试（V9 标准化管理）

测试范围：
- check_project / check_workspace: 结构检查
- repair_project / repair_workspace: 自动修复
- standardize_docs / standardize_workspace: 文档标准化
"""

from __future__ import annotations

import json
import os
import shutil

import pytest

from src.services.plc_project_service import (
    CheckResult,
    PlcProjectService,
    RepairResult,
    StandardizeResult,
    NAMING_RULES,
)


class TestCheckProject:
    """结构检查测试"""

    def test_check_project_standard(self, workspace_root: str) -> None:
        """测试标准项目检查（DJ-2026-005 已修复为PASS）"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        project_path = os.path.join(workspace_root, "DJ-2026-005")
        if not os.path.isdir(project_path):
            pytest.skip("DJ-2026-005 项目不存在")

        svc = PlcProjectService(workspace_root)
        result = svc.check_project(project_path)

        assert isinstance(result, CheckResult)
        assert result.project_type == "standard"
        # DJ-2026-005 已修复，应该全部通过
        assert result.all_pass is True
        assert result.fail_count == 0

    def test_check_project_syslib_fb(self, workspace_root: str) -> None:
        """测试 SysLib FB 项目检查"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        project_path = os.path.join(
            workspace_root, "01_SharedLibraries", "SysLib",
            "actuator", "FB_1011_CylinderControl"
        )
        if not os.path.isdir(project_path):
            pytest.skip("FB_1011_CylinderControl 项目不存在")

        svc = PlcProjectService(workspace_root)
        result = svc.check_project(project_path)

        assert result.project_type == "syslib_fb"
        # SysLib FB 项目不检查 .plc.json（应为 warn）
        plc_json_items = [i for i in result.items if i.item == ".plc.json"]
        if plc_json_items:
            assert plc_json_items[0].status == "warn"

    def test_check_workspace_depth4(self, workspace_root: str) -> None:
        """测试工作空间扫描深度4层，覆盖 SysLib/actuator/FB_xxx"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = PlcProjectService(workspace_root)
        results = svc.check_workspace(scan_depth=4)

        assert isinstance(results, list)
        assert len(results) > 0

        # 验证能扫描到 FB_ 开头的项目（三级嵌套）
        project_names = [os.path.basename(r.project_path) for r in results]
        fb_projects = [n for n in project_names if n.startswith("FB_")]
        assert len(fb_projects) > 0, f"未扫描到 FB_ 项目，实际: {project_names}"

    def test_check_workspace_default_depth(self, workspace_root: str) -> None:
        """测试默认扫描深度为4"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = PlcProjectService(workspace_root)
        # 不传 scan_depth，应使用默认值4
        results = svc.check_workspace()

        assert len(results) > 0


class TestRepairProject:
    """自动修复测试"""

    @pytest.fixture
    def tmp_project(self, tmp_dir: str) -> str:
        """创建临时项目目录（模拟缺失文件的项目）"""
        project_path = os.path.join(tmp_dir, "TEST-REPAIR-001")
        os.makedirs(project_path, exist_ok=True)
        return project_path

    def test_repair_missing_plc_json(self, tmp_project: str) -> None:
        """测试修复缺失的 .plc.json"""
        svc = PlcProjectService(os.path.dirname(tmp_project))
        result = svc.repair_project(tmp_project, dry_run=False)

        assert isinstance(result, RepairResult)
        # 应修复 .plc.json
        plc_json_actions = [a for a in result.actions if a.item == ".plc.json"]
        assert len(plc_json_actions) > 0
        assert plc_json_actions[0].status == "fixed"

        # 验证文件已创建
        plc_json_path = os.path.join(tmp_project, ".plc.json")
        assert os.path.isfile(plc_json_path)

        # 验证内容
        with open(plc_json_path, encoding="utf-8") as f:
            cfg = json.load(f)
        assert "name" in cfg
        assert "description" in cfg
        assert "version" in cfg

    def test_repair_missing_pm_session(self, tmp_project: str) -> None:
        """测试修复缺失的 PM_SESSION"""
        svc = PlcProjectService(os.path.dirname(tmp_project))
        result = svc.repair_project(tmp_project, dry_run=False)

        pm_actions = [a for a in result.actions if a.item == "PM_SESSION"]
        assert len(pm_actions) > 0
        assert pm_actions[0].status == "fixed"

        # 验证文件已创建
        project_id = "TEST-REPAIR-001"
        pm_path = os.path.join(tmp_project, f"PM_SESSION_{project_id}.md")
        assert os.path.isfile(pm_path)

    def test_repair_missing_prd_dir_and_docs(self, tmp_project: str) -> None:
        """测试修复缺失的 PRD 目录和文档"""
        svc = PlcProjectService(os.path.dirname(tmp_project))
        result = svc.repair_project(tmp_project, dry_run=False)

        # 应修复 PRD 目录
        prd_dir_actions = [a for a in result.actions if a.item == "PRD 目录"]
        assert len(prd_dir_actions) > 0
        assert prd_dir_actions[0].status == "fixed"

        # 应同时补全 PRD 四件套
        prd_doc_actions = [a for a in result.actions if a.item.startswith("PRD/")]
        assert len(prd_doc_actions) == 4  # REQ/INT/DSN/TEC

        # 验证目录和文件已创建
        prd_path = os.path.join(tmp_project, "PRD")
        assert os.path.isdir(prd_path)
        for doc_name in ["需求分析文档_REQ.md", "接口文档_INT.md",
                         "详细设计说明书_DSN.md", "技术方案文档_TEC.md"]:
            assert os.path.isfile(os.path.join(prd_path, doc_name))

    def test_repair_missing_std_dirs(self, tmp_project: str) -> None:
        """测试修复缺失的标准目录"""
        svc = PlcProjectService(os.path.dirname(tmp_project))
        result = svc.repair_project(tmp_project, dry_run=False)

        # 应修复标准目录
        dir_actions = [a for a in result.actions if a.item.startswith("目录 ")]
        assert len(dir_actions) > 0

        # 验证目录已创建
        for d in ["02_PLC程序/通用ST程序及变量表", "03_HMI设计",
                   "04_现场调试", "04_变更管理", "PRD"]:
            assert os.path.isdir(os.path.join(tmp_project, d))

    def test_repair_dry_run(self, tmp_project: str) -> None:
        """测试 dry-run 模式不实际执行"""
        svc = PlcProjectService(os.path.dirname(tmp_project))
        result = svc.repair_project(tmp_project, dry_run=True)

        # dry-run 模式所有操作应为 skipped
        assert result.fixed_count == 0
        assert result.skipped_count > 0

        # 验证文件未创建
        assert not os.path.isfile(os.path.join(tmp_project, ".plc.json"))

    def test_repair_all_pass_project(self, workspace_root: str) -> None:
        """测试修复已全部通过的项目（应无修复动作）"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        project_path = os.path.join(workspace_root, "DJ-2026-005")
        if not os.path.isdir(project_path):
            pytest.skip("DJ-2026-005 项目不存在")

        svc = PlcProjectService(workspace_root)
        result = svc.repair_project(project_path, dry_run=False)

        # 已全部通过，无 FAIL 项，无修复动作
        assert result.fixed_count == 0
        assert result.before_check.all_pass is True

    def test_repair_rename_without_confirm(self, tmp_project: str) -> None:
        """测试未确认时跳过重命名（破坏性操作）"""
        # 先创建一个命名不匹配的 PRD 文档
        prd_path = os.path.join(tmp_project, "PRD")
        os.makedirs(prd_path, exist_ok=True)
        # 创建非标准命名的文件
        non_std_file = os.path.join(prd_path, "接口文档_IFC-TEST-V1.0.0.md")
        with open(non_std_file, "w", encoding="utf-8") as f:
            f.write("# 测试接口文档")

        svc = PlcProjectService(os.path.dirname(tmp_project))
        # 不传 rename_confirm，重命名应被跳过
        result = svc.repair_project(tmp_project, dry_run=False, rename_confirm=False)

        # 应有 skipped 的重命名动作
        rename_actions = [a for a in result.actions if a.destructive]
        assert len(rename_actions) > 0
        assert all(a.status == "skipped" for a in rename_actions)

        # 原文件应仍存在
        assert os.path.isfile(non_std_file)


class TestStandardizeDocs:
    """文档标准化测试"""

    @pytest.fixture
    def tmp_project_with_prd(self, tmp_dir: str) -> str:
        """创建带 PRD 目录的临时项目"""
        project_path = os.path.join(tmp_dir, "TEST-STD-001")
        prd_path = os.path.join(project_path, "PRD")
        os.makedirs(prd_path, exist_ok=True)
        return project_path

    def test_standardize_detect_only(self, tmp_project_with_prd: str) -> None:
        """测试仅检测不执行"""
        prd_path = os.path.join(tmp_project_with_prd, "PRD")

        # 创建非标准命名的文件
        non_std_files = [
            "接口文档_IFC-TEST-V1.0.0.md",
            "详细设计说明书_DSN-TEST-V1.0.0.md",
        ]
        for filename in non_std_files:
            with open(os.path.join(prd_path, filename), "w", encoding="utf-8") as f:
                f.write(f"# {filename}")

        svc = PlcProjectService(os.path.dirname(tmp_project_with_prd))
        result = svc.standardize_docs(tmp_project_with_prd, apply=False)

        assert isinstance(result, StandardizeResult)
        assert len(result.plans) == 2
        assert result.applied_count == 0
        assert result.skipped_count == 2

        # 验证原文件仍存在
        for filename in non_std_files:
            assert os.path.isfile(os.path.join(prd_path, filename))

    def test_standardize_apply(self, tmp_project_with_prd: str) -> None:
        """测试执行重命名"""
        prd_path = os.path.join(tmp_project_with_prd, "PRD")

        # 创建非标准命名的文件
        non_std_file = os.path.join(prd_path, "接口文档_IFC-TEST-V1.0.0.md")
        with open(non_std_file, "w", encoding="utf-8") as f:
            f.write("# 测试接口文档")

        svc = PlcProjectService(os.path.dirname(tmp_project_with_prd))
        result = svc.standardize_docs(tmp_project_with_prd, apply=True)

        assert result.applied_count == 1
        assert len(result.plans) == 1

        # 验证文件已重命名
        assert not os.path.isfile(non_std_file)
        assert os.path.isfile(os.path.join(prd_path, "接口文档_INT.md"))

        # 验证备份已创建
        assert os.path.isfile(non_std_file + ".bak")

    def test_standardize_no_prd_dir(self, tmp_dir: str) -> None:
        """测试 PRD 目录不存在时的处理"""
        project_path = os.path.join(tmp_dir, "TEST-NOPRD-001")
        os.makedirs(project_path, exist_ok=True)

        svc = PlcProjectService(tmp_dir)
        result = svc.standardize_docs(project_path, apply=False)

        assert isinstance(result, StandardizeResult)
        assert len(result.plans) == 0
        assert result.applied_count == 0

    def test_standardize_already_standard(self, tmp_project_with_prd: str) -> None:
        """测试已是标准命名的文件不触发重命名"""
        prd_path = os.path.join(tmp_project_with_prd, "PRD")

        # 创建标准命名的文件
        std_file = os.path.join(prd_path, "接口文档_INT.md")
        with open(std_file, "w", encoding="utf-8") as f:
            f.write("# 标准接口文档")

        svc = PlcProjectService(os.path.dirname(tmp_project_with_prd))
        result = svc.standardize_docs(tmp_project_with_prd, apply=False)

        # 标准命名的文件不应出现在 plans 中
        assert len(result.plans) == 0

    def test_standardize_reference_update(self, tmp_project_with_prd: str) -> None:
        """测试重命名后更新关联引用"""
        prd_path = os.path.join(tmp_project_with_prd, "PRD")

        # 创建非标准命名的接口文档
        old_name = "接口文档_IFC-TEST-V1.0.0.md"
        with open(os.path.join(prd_path, old_name), "w", encoding="utf-8") as f:
            f.write("# 测试接口文档")

        # 创建引用该文件名的 DSN 文档
        dsn_content = f"# 详细设计\n\n参见 [{old_name}]({old_name})\n"
        with open(os.path.join(prd_path, "详细设计说明书_DSN.md"), "w", encoding="utf-8") as f:
            f.write(dsn_content)

        svc = PlcProjectService(os.path.dirname(tmp_project_with_prd))
        result = svc.standardize_docs(tmp_project_with_prd, apply=True)

        # 验证引用已更新
        assert len(result.reference_updates) > 0

        # 验证 DSN 文档内容已更新
        with open(os.path.join(prd_path, "详细设计说明书_DSN.md"), encoding="utf-8") as f:
            content = f.read()
        assert "接口文档_INT.md" in content
        assert old_name not in content


class TestNamingRules:
    """命名规范映射测试"""

    def test_naming_rules_completeness(self) -> None:
        """测试命名规范映射完整性"""
        assert len(NAMING_RULES) == 4  # REQ/INT/DSN/TEC

        for std_name, rule in NAMING_RULES.items():
            assert "doc_type" in rule
            assert "prefix" in rule
            assert "patterns" in rule
            assert len(rule["patterns"]) > 0
            assert rule["doc_type"] in ["REQ", "INT", "DSN", "TEC"]
