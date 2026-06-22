"""PlcChecker 单元测试"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from auto_pm.plc.checker import PlcChecker

# ── Fixtures ──────────────────────────────────────────


@pytest.fixture
def full_project(tmp_path: Path) -> Path:
    """创建一个完整标准项目（所有检查项通过）"""
    project_dir = tmp_path / "DJ-2026-FULL_完整项目"
    project_dir.mkdir()

    # .plc.json（含 libraries）
    (project_dir / ".plc.json").write_text(
        json.dumps(
            {
                "name": "DJ-2026-FULL",
                "version": "V1.0.0",
                "description": "完整项目",
                "type": "standard",
                "libraries": ["../../../01_SharedLibraries/SysLib"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # PM_SESSION
    (project_dir / "PM_SESSION_DJ-2026-FULL.md").write_text(
        "# PM_SESSION_DJ-2026-FULL\n", encoding="utf-8"
    )

    # PRD 目录 + 标准文档
    prd_dir = project_dir / "PRD"
    prd_dir.mkdir()
    for doc in ["需求分析文档_REQ.md", "接口文档_INT.md", "详细设计说明书_DSN.md", "技术方案文档_TEC.md"]:
        (prd_dir / doc).write_text(f"# {doc}\n", encoding="utf-8")

    # 标准目录
    for d in ["02_PLC程序/通用ST程序及变量表", "03_HMI设计", "04_现场调试", "04_变更管理"]:
        (project_dir / d).mkdir(parents=True)

    return tmp_path


@pytest.fixture
def missing_prd_dir_project(tmp_path: Path) -> Path:
    """创建缺少 PRD 目录的项目"""
    project_dir = tmp_path / "DJ-2026-NOPRD_无PRD项目"
    project_dir.mkdir()

    (project_dir / ".plc.json").write_text(
        json.dumps(
            {
                "name": "DJ-2026-NOPRD",
                "version": "V1.0.0",
                "description": "无PRD项目",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (project_dir / "PM_SESSION_DJ-2026-NOPRD.md").write_text(
        "# PM_SESSION\n", encoding="utf-8"
    )

    return tmp_path


@pytest.fixture
def missing_std_dirs_project(tmp_path: Path) -> Path:
    """创建缺少标准目录的项目"""
    project_dir = tmp_path / "DJ-2026-NODIR_无标准目录"
    project_dir.mkdir()

    (project_dir / ".plc.json").write_text(
        json.dumps(
            {
                "name": "DJ-2026-NODIR",
                "version": "V1.0.0",
                "description": "无标准目录",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (project_dir / "PM_SESSION_DJ-2026-NODIR.md").write_text(
        "# PM_SESSION\n", encoding="utf-8"
    )
    # 有 PRD 但无标准目录
    (project_dir / "PRD").mkdir()

    return tmp_path


@pytest.fixture
def nonstandard_prd_project(tmp_path: Path) -> Path:
    """创建 PRD 文档命名不规范的项目"""
    project_dir = tmp_path / "DJ-2026-NSPRD_非标准PRD"
    project_dir.mkdir()

    (project_dir / ".plc.json").write_text(
        json.dumps(
            {
                "name": "DJ-2026-NSPRD",
                "version": "V1.0.0",
                "description": "非标准PRD",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (project_dir / "PM_SESSION_DJ-2026-NSPRD.md").write_text(
        "# PM_SESSION\n", encoding="utf-8"
    )

    prd_dir = project_dir / "PRD"
    prd_dir.mkdir()
    # 非标准命名：前缀"需求分析文档"匹配标准文档"需求分析文档_REQ.md"的前缀
    # checker 用 doc.split("_")[0] 作为前缀，"需求分析文档_REQ.md" → "需求分析文档"
    (prd_dir / "需求分析文档_REQ-001.md").write_text("# 需求\n", encoding="utf-8")

    for d in ["02_PLC程序/通用ST程序及变量表", "03_HMI设计", "04_现场调试", "04_变更管理"]:
        (project_dir / d).mkdir(parents=True)

    return tmp_path


@pytest.fixture
def invalid_plc_json_project(tmp_path: Path) -> Path:
    """创建 .plc.json 缺少必填字段的项目"""
    project_dir = tmp_path / "DJ-2026-INV_无效配置"
    project_dir.mkdir()

    # 缺少 description 和 version
    (project_dir / ".plc.json").write_text(
        json.dumps({"name": "DJ-2026-INV"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (project_dir / "PM_SESSION_DJ-2026-INV.md").write_text(
        "# PM_SESSION\n", encoding="utf-8"
    )

    return tmp_path


@pytest.fixture
def syslib_fb_project(tmp_path: Path) -> Path:
    """创建 SysLib FB 项目"""
    syslib_dir = tmp_path / "01_SharedLibraries" / "SysLib"
    fb_dir = syslib_dir / "FB_1011_测试功能块"
    fb_dir.mkdir(parents=True)

    return tmp_path


# ── 基础检查测试 ──────────────────────────────────────


class TestCheckProject:
    """单项目检查测试"""

    def test_check_project(self, tmp_workspace: Path) -> None:
        """测试检查模拟项目"""
        project_path = str(tmp_workspace / "DJ-2026-TEST_测试项目")
        checker = PlcChecker(str(tmp_workspace))
        result = checker.check_project(project_path)

        assert result.project_path == project_path
        # .plc.json 存在，应该 pass
        assert any(item.item == ".plc.json" and item.status == "pass" for item in result.items)

    def test_check_project_missing_plc_json(self, tmp_path: Path) -> None:
        """测试缺少 .plc.json 的项目"""
        project_dir = tmp_path / "DJ-2026-EMPTY_空项目"
        project_dir.mkdir()

        checker = PlcChecker(str(tmp_path))
        result = checker.check_project(str(project_dir))

        # 缺少 .plc.json 应该 fail
        assert any(
            item.item == ".plc.json" and item.status == "fail" for item in result.items
        )

    def test_check_all_pass(self, full_project: Path) -> None:
        """检查完整项目应全部通过"""
        project_path = str(full_project / "DJ-2026-FULL_完整项目")
        checker = PlcChecker(str(full_project))
        result = checker.check_project(project_path)

        # 不应有 fail 项
        fail_items = [item for item in result.items if item.status == "fail"]
        assert len(fail_items) == 0, f"Unexpected fails: {[i.item for i in fail_items]}"

    def test_check_missing_prd_directory(self, missing_prd_dir_project: Path) -> None:
        """检查缺少 PRD 目录的项目"""
        project_path = str(missing_prd_dir_project / "DJ-2026-NOPRD_无PRD项目")
        checker = PlcChecker(str(missing_prd_dir_project))
        result = checker.check_project(project_path)

        assert any(
            item.item == "PRD 目录" and item.status == "fail" for item in result.items
        )

    def test_check_missing_std_dirs(self, missing_std_dirs_project: Path) -> None:
        """检查缺少标准目录的项目"""
        project_path = str(missing_std_dirs_project / "DJ-2026-NODIR_无标准目录")
        checker = PlcChecker(str(missing_std_dirs_project))
        result = checker.check_project(project_path)

        fail_dirs = [
            item for item in result.items
            if item.item.startswith("目录 ") and item.status == "fail"
        ]
        assert len(fail_dirs) >= 1

    def test_check_nonstandard_prd_names(self, nonstandard_prd_project: Path) -> None:
        """检查 PRD 文档命名不规范应产生警告"""
        project_path = str(nonstandard_prd_project / "DJ-2026-NSPRD_非标准PRD")
        checker = PlcChecker(str(nonstandard_prd_project))
        result = checker.check_project(project_path)

        warn_items = [
            item for item in result.items
            if item.item.startswith("PRD/") and item.status == "warn"
        ]
        assert len(warn_items) >= 1

    def test_check_invalid_plc_json(self, invalid_plc_json_project: Path) -> None:
        """检查 .plc.json 缺少必填字段应 fail"""
        project_path = str(invalid_plc_json_project / "DJ-2026-INV_无效配置")
        checker = PlcChecker(str(invalid_plc_json_project))
        result = checker.check_project(project_path)

        assert any(
            item.item == ".plc.json" and item.status == "fail" for item in result.items
        )

    def test_check_syslib_fb_project(self, syslib_fb_project: Path) -> None:
        """检查 SysLib FB 项目类型"""
        fb_path = str(
            syslib_fb_project / "01_SharedLibraries" / "SysLib" / "FB_1011_测试功能块"
        )
        checker = PlcChecker(str(syslib_fb_project))
        result = checker.check_project(fb_path)

        assert result.project_type == "syslib_fb"
        # SysLib FB 项目 .plc.json 应为 warn 而非 fail
        plc_items = [i for i in result.items if i.item == ".plc.json"]
        if plc_items:
            assert plc_items[0].status == "warn"


# ── 工作空间批量检查测试 ──────────────────────────────


class TestCheckWorkspace:
    """工作空间批量检查测试"""

    def test_check_workspace(self, tmp_workspace: Path) -> None:
        """测试批量检查工作空间"""
        checker = PlcChecker(str(tmp_workspace))
        results = checker.check_workspace()

        assert len(results) == 1
        assert "DJ-2026-TEST" in results[0].project_path

    def test_check_workspace_multiple_projects(self, tmp_path: Path) -> None:
        """检查包含多个项目的工作空间"""
        # 项目1
        p1 = tmp_path / "DJ-2026-001_项目一"
        p1.mkdir()
        (p1 / ".plc.json").write_text(
            json.dumps({"name": "DJ-2026-001", "version": "V1.0.0", "description": "项目一"}, ensure_ascii=False),
            encoding="utf-8",
        )

        # 项目2
        p2 = tmp_path / "DJ-2026-002_项目二"
        p2.mkdir()
        (p2 / ".plc.json").write_text(
            json.dumps({"name": "DJ-2026-002", "version": "V1.0.0", "description": "项目二"}, ensure_ascii=False),
            encoding="utf-8",
        )

        checker = PlcChecker(str(tmp_path))
        results = checker.check_workspace()

        assert len(results) == 2
        project_ids = {r.project_path.split(os.sep)[-1].split("_")[0] for r in results}
        assert "DJ-2026-001" in project_ids
        assert "DJ-2026-002" in project_ids


# ── 边缘用例测试 ──────────────────────────────────────


class TestEdgeCases:
    """边缘用例测试"""

    def test_check_malformed_plc_json(self, tmp_path: Path) -> None:
        """检查 .plc.json 解析失败的情况"""
        project_dir = tmp_path / "DJ-2026-BAD_损坏配置"
        project_dir.mkdir()
        (project_dir / ".plc.json").write_text("{invalid json", encoding="utf-8")

        checker = PlcChecker(str(tmp_path))
        result = checker.check_project(str(project_dir))

        assert any(
            item.item == ".plc.json" and item.status == "fail" for item in result.items
        )

    def test_check_pm_session_name_mismatch(self, tmp_path: Path) -> None:
        """PM_SESSION 文件名不匹配时应产生警告"""
        project_dir = tmp_path / "DJ-2026-MM_名称不匹配"
        project_dir.mkdir()
        (project_dir / ".plc.json").write_text(
            json.dumps({"name": "DJ-2026-MM", "version": "V1.0.0", "description": "名称不匹配"}, ensure_ascii=False),
            encoding="utf-8",
        )
        # PM_SESSION 文件名与项目编号不匹配
        (project_dir / "PM_SESSION_WRONG-ID.md").write_text(
            "# PM_SESSION\n", encoding="utf-8"
        )

        checker = PlcChecker(str(tmp_path))
        result = checker.check_project(str(project_dir))

        pm_items = [i for i in result.items if i.item == "PM_SESSION"]
        assert len(pm_items) == 1
        assert pm_items[0].status == "warn"

    def test_check_project_no_plc_json_no_pm_session(self, tmp_path: Path) -> None:
        """既无 .plc.json 也无 PM_SESSION 的目录"""
        project_dir = tmp_path / "DJ-2026-BARE_裸项目"
        project_dir.mkdir()

        checker = PlcChecker(str(tmp_path))
        result = checker.check_project(str(project_dir))

        # 应有多个 fail 项
        assert result.fail_count >= 1

    def test_check_project_with_libraries_warn(self, tmp_path: Path) -> None:
        """libraries 字段为空时应产生警告"""
        project_dir = tmp_path / "DJ-2026-NOLIB_无库配置"
        project_dir.mkdir()
        (project_dir / ".plc.json").write_text(
            json.dumps(
                {"name": "DJ-2026-NOLIB", "version": "V1.0.0", "description": "无库配置"},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        checker = PlcChecker(str(tmp_path))
        result = checker.check_project(str(project_dir))

        # libraries 字段缺失应产生 warn
        lib_items = [i for i in result.items if "libraries" in i.item]
        assert any(i.status == "warn" for i in lib_items)
