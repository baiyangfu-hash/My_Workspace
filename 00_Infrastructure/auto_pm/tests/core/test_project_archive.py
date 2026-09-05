"""ProjectArchiveService 与 CLI 归档恢复功能测试"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from auto_pm.core.project_archive_service import (
    DirtyWorkspaceBlockingError,
    OpenChangesBlockingError,
    ProjectArchiveError,
    ProjectArchiveService,
    ProtectionViolationError,
)
from auto_pm.core.project_scanner import ProjectScanner
from auto_pm.core.project_service import ProjectService
from click.testing import CliRunner

from auto_pm.app_context import AppContext
from auto_pm.ui.cli.project import project_group


@pytest.fixture
def test_workspace(tmp_path: Path) -> Path:
    """初始化用于测试的工作空间目录结构"""
    ws = tmp_path / "workspace"
    ws.mkdir()
    # 创建 PLC 目录与归档目录
    (ws / "0100_PLC自动化").mkdir()
    # 创建 Python 在研与归档目录
    py_base = ws / "01_Project自动化项目管理" / "Python自动化项目总库"
    (py_base / "02_在研项目").mkdir(parents=True)
    (py_base / "03_归档").mkdir(parents=True)
    # 创建其它通用目录
    (ws / "0100_项目").mkdir()
    return ws


def _create_dummy_project(
    proj_dir: Path,
    project_id: str,
    project_name: str,
    stack: str = "python",
    phase: str = "developing",
) -> Path:
    """辅助方法：在指定路径创建合规的项目目录"""
    proj_dir.mkdir(parents=True, exist_ok=True)
    pm_session = proj_dir / f"PM_SESSION_{project_id}.md"
    session_content = f"""---
project_id: {project_id}
phase: {phase}
---
# PM_SESSION_{project_id}

## 0. Meta
| 字段 | 内容 |
| --- | --- |
| 项目编号 | {project_id} |
| 项目名称 | {project_name} |
| 阶段 | {phase} |
"""
    pm_session.write_text(session_content, encoding="utf-8")

    copier_file = proj_dir / ".copier-answers.yml"
    copier_content = f"""_commit: HEAD
_src_path: templates/copier-python-template
project_id: {project_id}
project_name: {project_name}
phase: {phase}
stack: {stack}
"""
    copier_file.write_text(copier_content, encoding="utf-8")
    return proj_dir


# ── 1. 领域就近路由测试 ─────────────────────────────────────


class TestResolveArchivePath:
    def test_plc_domain_routing(self, test_workspace: Path) -> None:
        """测试 PLC 项目路由到 0100_PLC自动化/_archive"""
        svc = ProjectArchiveService(str(test_workspace))
        src = test_workspace / "0100_PLC自动化" / "DJ-2026-001_Demo"
        dest = svc.resolve_archive_path(str(src))
        expected = test_workspace / "0100_PLC自动化" / "_archive" / "DJ-2026-001_Demo"
        assert Path(dest) == expected

    def test_python_domain_routing(self, test_workspace: Path) -> None:
        """测试 Python 在研项目路由到 03_归档"""
        svc = ProjectArchiveService(str(test_workspace))
        src = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "02_在研项目"
            / "SW-2026-001_Tool"
        )
        dest = svc.resolve_archive_path(str(src))
        expected = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "03_归档"
            / "SW-2026-001_Tool"
        )
        assert Path(dest) == expected

    def test_generic_domain_routing(self, test_workspace: Path) -> None:
        """测试其他项目路由到上级目录下的 _archive"""
        svc = ProjectArchiveService(str(test_workspace))
        src = test_workspace / "0100_项目" / "SW-2026-002_Other"
        dest = svc.resolve_archive_path(str(src))
        expected = test_workspace / "0100_项目" / "_archive" / "SW-2026-002_Other"
        assert Path(dest) == expected

    def test_reverse_routing(self, test_workspace: Path) -> None:
        """测试逆向路由推导恢复目标路径"""
        svc = ProjectArchiveService(str(test_workspace))

        # PLC 逆向
        plc_arch = test_workspace / "0100_PLC自动化" / "_archive" / "DJ-2026-001_Demo"
        plc_restore = svc.resolve_restore_path(str(plc_arch))
        assert Path(plc_restore) == test_workspace / "0100_PLC自动化" / "DJ-2026-001_Demo"

        # Python 逆向
        py_arch = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "03_归档"
            / "SW-2026-001_Tool"
        )
        py_restore = svc.resolve_restore_path(str(py_arch))
        expected_py = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "02_在研项目"
            / "SW-2026-001_Tool"
        )
        assert Path(py_restore) == expected_py


# ── 2. 三道硬门禁拦截测试 ───────────────────────────────────


class TestArchiveGates:
    def test_gate3_protected_projects(self, test_workspace: Path) -> None:
        """Gate 3: 受保护母体项目 (SW-2026-008, SYS-2026-001) 严禁归档"""
        svc = ProjectArchiveService(str(test_workspace))
        proj_dir = test_workspace / "SW-2026-008_auto-pm"
        proj_dir.mkdir(exist_ok=True)

        with pytest.raises(ProtectionViolationError, match="核心母体/系统级受保护项目严禁归档"):
            svc.check_archive_gates("SW-2026-008", str(proj_dir))

        with pytest.raises(ProtectionViolationError, match="核心母体/系统级受保护项目严禁归档"):
            svc.check_archive_gates("SYS-2026-001", str(proj_dir))

    def test_gate3_missing_pm_session(self, test_workspace: Path) -> None:
        """Gate 3: 缺少 PM_SESSION_*.md 管理资产文件合规阻断"""
        svc = ProjectArchiveService(str(test_workspace))
        proj_dir = test_workspace / "0100_项目" / "SW-2026-099_NoMeta"
        proj_dir.mkdir(parents=True)
        # 仅放代码，无 PM_SESSION
        (proj_dir / "app.py").write_text("print('hello')", encoding="utf-8")

        with pytest.raises(ProjectArchiveError, match="缺少 PM_SESSION_\\*\\.md"):
            svc.check_archive_gates("SW-2026-099", str(proj_dir))

    def test_gate1_open_changes_blocked(self, test_workspace: Path) -> None:
        """Gate 1: 未闭环变更单拦截"""
        proj_dir = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "02_在研项目"
            / "SW-2026-010_Test"
        )
        _create_dummy_project(proj_dir, "SW-2026-010", "Test")

        # 模拟在监控/变更管理下创建一个未闭环的变更单
        chg_dir = proj_dir / "04_监控" / "01_变更管理" / "01_变更单" / "CHG-SCPT"
        chg_dir.mkdir(parents=True)
        chg_file = chg_dir / "CHG-SCPT-2026-001.md"
        chg_content = """# 变更单
### 3.0 编号与项目
| 字段 | 内容 |
| 变更编号 | CHG-SCPT-2026-001 |
| 项目编号 | SW-2026-010 |

### 3.4 申请信息
| 变更状态 | implementing |
"""
        chg_file.write_text(chg_content, encoding="utf-8")

        svc = ProjectArchiveService(str(test_workspace))
        with pytest.raises(OpenChangesBlockingError, match="未闭环变更单"):
            svc.check_archive_gates("SW-2026-010", str(proj_dir))

    def test_gate2_dirty_workspace_blocked(self, test_workspace: Path) -> None:
        """Gate 2: Git 工作区脏状态拦截与 force 绕过"""
        proj_dir = test_workspace / "0100_项目" / "SW-2026-020_GitTest"
        _create_dummy_project(proj_dir, "SW-2026-020", "GitTest")

        # 初始化独立 git repo 并制造 dirty 状态
        try:
            subprocess.run(["git", "init"], cwd=proj_dir, check=True, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=proj_dir, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "init"],
                cwd=proj_dir,
                check=True,
                capture_output=True,
                env={**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_COMMITTER_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t.com", "GIT_COMMITTER_EMAIL": "t@t.com"},
            )
            # 添加未暂存修改
            (proj_dir / "dirty.txt").write_text("dirty content", encoding="utf-8")
        except Exception:
            pytest.skip("本地 Git 环境不可用，跳过测试")

        svc = ProjectArchiveService(str(test_workspace))
        with pytest.raises(DirtyWorkspaceBlockingError, match="未提交变更或未追踪文件"):
            svc.check_archive_gates("SW-2026-020", str(proj_dir), force=False)

        # force=True 允许绕过
        svc.check_archive_gates("SW-2026-020", str(proj_dir), force=True)


# ── 3. 完整归档流程与台账自动化测试 ─────────────────────────


class TestArchiveExecutionAndLedger:
    def test_archive_success_and_ledger(self, test_workspace: Path) -> None:
        """测试正常项目的物理移动、台账记录与 PM_SESSION phase 变更"""
        proj_dir = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "02_在研项目"
            / "SW-2026-030_Demo"
        )
        _create_dummy_project(proj_dir, "SW-2026-030", "Demo")

        svc = ProjectArchiveService(str(test_workspace))
        result = svc.archive_project(
            project_id="SW-2026-030",
            reason="项目结项",
            operator="tester",
            force=True,
        )

        assert result["success"] is True
        assert result["project_id"] == "SW-2026-030"
        archive_path = Path(result["archive_path"])
        assert archive_path.exists()
        assert not proj_dir.exists()

        # 验证 PM_SESSION phase 已变为 archived
        session_file = archive_path / "PM_SESSION_SW-2026-030.md"
        assert "phase: archived" in session_file.read_text(encoding="utf-8")

        # 验证台账文件已初始化并写入记录
        archive_dir = archive_path.parent
        ledger_file = archive_dir / "00_历史项目归档台账.md"
        assert ledger_file.is_file()
        ledger_text = ledger_file.read_text(encoding="utf-8")
        assert "| 序号 | 归档编号 | 项目编号 |" in ledger_text
        assert "SW-2026-030" in ledger_text
        assert "已归档" in ledger_text
        assert "tester" in ledger_text
        assert "项目结项" in ledger_text
        assert result["archive_code"].startswith("ARC-")

    def test_archive_sequence_increment(self, test_workspace: Path) -> None:
        """测试多次归档时流水号自动递增"""
        svc = ProjectArchiveService(str(test_workspace))
        base_dir = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "02_在研项目"
        )
        _create_dummy_project(base_dir / "SW-2026-031_A", "SW-2026-031", "A")
        _create_dummy_project(base_dir / "SW-2026-032_B", "SW-2026-032", "B")


        res1 = svc.archive_project("SW-2026-031", force=True)
        res2 = svc.archive_project("SW-2026-032", force=True)

        assert res1["archive_code"] != res2["archive_code"]
        seq1 = int(res1["archive_code"].split("-")[-1])
        seq2 = int(res2["archive_code"].split("-")[-1])
        assert seq2 == seq1 + 1

    def test_archive_target_exists_raises(self, test_workspace: Path) -> None:
        """目标归档目录已存在同名项目时抛出 FileExistsError"""
        proj_dir = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "02_在研项目"
            / "SW-2026-033_Dup"
        )
        _create_dummy_project(proj_dir, "SW-2026-033", "Dup")

        dest_dir = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "03_归档"
            / "SW-2026-033_Dup"
        )
        dest_dir.mkdir(parents=True)

        svc = ProjectArchiveService(str(test_workspace))
        with pytest.raises(FileExistsError, match="已存在同名项目"):
            svc.archive_project("SW-2026-033", force=True)


# ── 4. 逆向恢复与冲突防护测试 ───────────────────────────────


class TestRestoreExecution:
    def test_restore_success_and_ledger_status(self, test_workspace: Path) -> None:
        """测试从归档目录成功恢复回在研目录，台账更新为已恢复，phase 变为 developing"""
        base_dir = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "02_在研项目"
        )
        proj_dir = base_dir / "SW-2026-040_Restorable"
        _create_dummy_project(proj_dir, "SW-2026-040", "Restorable")

        svc = ProjectArchiveService(str(test_workspace))
        arch_res = svc.archive_project("SW-2026-040", force=True)
        arch_path = Path(arch_res["archive_path"])
        assert not proj_dir.exists()

        # 执行恢复
        restore_res = svc.restore_project("SW-2026-040", operator="tester")
        assert restore_res["success"] is True
        restored_path = Path(restore_res["restored_path"])
        assert restored_path.exists()
        assert not arch_path.exists()

        # 检查 PM_SESSION phase 恢复为 developing
        session_text = (restored_path / "PM_SESSION_SW-2026-040.md").read_text(encoding="utf-8")
        assert "phase: developing" in session_text

        # 检查台账中状态变更为 已恢复
        ledger_text = (arch_path.parent / "00_历史项目归档台账.md").read_text(encoding="utf-8")
        assert "SW-2026-040" in ledger_text
        assert "已恢复" in ledger_text

    def test_restore_conflict_raises(self, test_workspace: Path) -> None:
        """当目标在研路径已存在同名项目时阻断并抛出 FileExistsError"""
        base_dir = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "02_在研项目"
        )
        proj_dir = base_dir / "SW-2026-041_Conflict"
        _create_dummy_project(proj_dir, "SW-2026-041", "Conflict")

        svc = ProjectArchiveService(str(test_workspace))
        svc.archive_project("SW-2026-041", force=True)

        # 模拟在在研路径重新创建了同名目录
        proj_dir.mkdir(parents=True)

        with pytest.raises(FileExistsError, match="已存在同名目录"):
            svc.restore_project("SW-2026-041")


# ── 5. ProjectScanner 与 ProjectService 归档支持测试 ──────────


class TestScannerAndServiceArchived:
    def test_scanner_isolation(self, test_workspace: Path) -> None:
        """验证 scan() 不包含归档项目，而 scan_archived() 只包含归档项目"""
        base_dev = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "02_在研项目"
        )
        base_arch = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "03_归档"
        )
        _create_dummy_project(base_dev / "SW-2026-050_Active", "SW-2026-050", "Active")
        _create_dummy_project(base_arch / "SW-2026-051_Old", "SW-2026-051", "Old", phase="archived")

        scanner = ProjectScanner(str(test_workspace))
        active_projects = scanner.scan()
        archived_projects = scanner.scan_archived()

        active_ids = [p.project_id for p in active_projects]
        archived_ids = [p.project_id for p in archived_projects]

        assert "SW-2026-050" in active_ids
        assert "SW-2026-051" not in active_ids

        assert "SW-2026-051" in archived_ids
        assert "SW-2026-050" not in archived_ids

    def test_project_service_facade(self, test_workspace: Path) -> None:
        """验证 ProjectService 包装的 archive_project / restore_project / list_archived_projects"""
        svc = ProjectService(str(test_workspace))
        base_dev = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "02_在研项目"
        )
        _create_dummy_project(base_dev / "SW-2026-060_Fac", "SW-2026-060", "Fac")

        # 归档
        res = svc.archive_project("SW-2026-060", force=True)
        assert res["success"] is True

        # 列出归档
        archived = svc.list_archived_projects()
        assert any(p.project_id == "SW-2026-060" for p in archived)

        # 恢复
        res_rst = svc.restore_project("SW-2026-060")
        assert res_rst["success"] is True

    def test_project_service_delete_warning(self, test_workspace: Path) -> None:
        """验证 delete_project 若未传 force=True 抛出包含推荐归档的异常"""
        svc = ProjectService(str(test_workspace))
        base_dev = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "02_在研项目"
        )
        _create_dummy_project(base_dev / "SW-2026-070_Del", "SW-2026-070", "Del")

        with pytest.raises(RuntimeError, match="推荐使用 archive_project"):
            svc.delete_project("SW-2026-070", force=False)

        # 显式 force=True 执行硬删除
        svc.delete_project("SW-2026-070", force=True)
        assert svc.get_project("SW-2026-070") is None


# ── 6. CLI 命令行调用测试 ───────────────────────────────────


class TestCliProjectArchiveCommands:
    def test_cli_archive_and_restore(self, test_workspace: Path) -> None:
        """测试 CLI auto-pm project archive 与 auto-pm project restore 命令"""
        runner = CliRunner()
        base_dev = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "02_在研项目"
        )
        _create_dummy_project(base_dev / "SW-2026-080_Cli", "SW-2026-080", "Cli")

        ctx_obj = AppContext(workspace_root=str(test_workspace))

        # 1. 归档
        result = runner.invoke(
            project_group,
            ["archive", "SW-2026-080", "--reason", "CLI归档测试", "--force"],
            obj=ctx_obj,
        )
        assert result.exit_code == 0
        assert "项目归档成功: SW-2026-080" in result.output

        # 2. list 默认不包含归档
        list_res = runner.invoke(project_group, ["list"], obj=ctx_obj)
        assert "SW-2026-080" not in list_res.output

        # 3. list --archived-only 与 --include-archived 包含归档
        list_arch_res = runner.invoke(
            project_group, ["list", "--archived-only", "--json"], obj=ctx_obj
        )
        assert "SW-2026-080" in list_arch_res.output

        list_all_res = runner.invoke(
            project_group, ["list", "--include-archived", "--json"], obj=ctx_obj
        )
        assert "SW-2026-080" in list_all_res.output

        # 4. 恢复
        restore_res = runner.invoke(
            project_group,
            ["restore", "SW-2026-080"],
            obj=ctx_obj,
        )
        assert restore_res.exit_code == 0
        assert "SW-2026-080" in restore_res.output

        # 恢复后在默认 list 重新出现
        list_after_res = runner.invoke(project_group, ["list", "--json"], obj=ctx_obj)
        assert "SW-2026-080" in list_after_res.output

    def test_cli_delete_warning(self, test_workspace: Path) -> None:
        """测试 CLI delete 命令的归档推荐警告"""
        runner = CliRunner()
        base_dev = (
            test_workspace
            / "01_Project自动化项目管理"
            / "Python自动化项目总库"
            / "02_在研项目"
        )
        _create_dummy_project(base_dev / "SW-2026-081_Warn", "SW-2026-081", "Warn")

        ctx_obj = AppContext(workspace_root=str(test_workspace))
        result = runner.invoke(project_group, ["delete", "SW-2026-081"], obj=ctx_obj)
        assert result.exit_code != 0
        cleaned_output = result.output.replace("\n", "").replace("\r", "")
        assert "auto-pm project archive" in cleaned_output

