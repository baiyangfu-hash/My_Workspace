"""auto_pm.tests.application.test_change_transaction - 变更事务沙箱测试

覆盖 DEV-300 SRE 工程可靠性与 DEV-210 编程规范：
- 原文件快照备份与基线不可篡改
- 变更失败全量原子回滚（原文件内容还原、新建文件/目录物理清除）
- 正常退出自动提交（变更保留、快照目录清除）
- 上下文管理器异常自动回滚与正常提交
- 状态机防非法流转（已提交/已回滚状态不可再操作）
- 关键操作白盒审计日志记录
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from auto_pm.application.core.change_transaction import (
    ChangeTransaction,
    ChangeTransactionManager,
    TransactionStateError,
)
from auto_pm.contracts.workflow_dtos import TransactionStatus


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """创建临时工作空间目录"""
    ws = tmp_path / "workspace"
    ws.mkdir(parents=True, exist_ok=True)
    return ws


@pytest.fixture
def tm(workspace: Path) -> ChangeTransactionManager:
    """创建与临时工作空间绑定的 ChangeTransactionManager"""
    return ChangeTransactionManager(workspace_root=workspace)


class TestChangeTransactionBasics:
    """基础字段初始化与属性校验"""

    def test_begin_creates_active_transaction(self, tm: ChangeTransactionManager, workspace: Path) -> None:
        tx = tm.begin(project_id="PROJ-001", change_id="CHG-001")
        assert isinstance(tx, ChangeTransaction)
        assert tx.project_id == "PROJ-001"
        assert tx.change_id == "CHG-001"
        assert tx.status == TransactionStatus.ACTIVE
        assert tx.workspace_root == workspace.resolve()
        assert tx.backup_dir == (workspace / ".auto-pm" / "transactions" / tx.tx_id).resolve()
        assert tx.backups == {}
        assert tx.created_files == []

    def test_custom_tx_id_and_custom_backup_dir(self, workspace: Path, tmp_path: Path) -> None:
        custom_backup_base = tmp_path / "custom_backups"
        mgr = ChangeTransactionManager(workspace_root=workspace, backup_base_dir=custom_backup_base)
        tx = mgr.begin(project_id="PROJ-002", change_id="CHG-002", tx_id="TX-CUSTOM-999")
        assert tx.tx_id == "TX-CUSTOM-999"
        assert tx.backup_dir == (custom_backup_base / "TX-CUSTOM-999").resolve()


class TestChangeTransactionBackup:
    """快照备份功能测试"""

    def test_backup_file_creates_snapshot(self, tm: ChangeTransactionManager, workspace: Path) -> None:
        target_file = workspace / "src" / "main.py"
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text("print('version 1')", encoding="utf-8")

        tx = tm.begin("PROJ-001", "CHG-001")
        backup_path = tx.backup_file(target_file)

        assert backup_path.exists()
        assert backup_path.read_text(encoding="utf-8") == "print('version 1')"
        assert target_file in tx.backups
        assert tx.backups[target_file] == backup_path

    def test_backup_file_relative_path(self, tm: ChangeTransactionManager, workspace: Path) -> None:
        rel_path = Path("config") / "settings.json"
        target_file = workspace / rel_path
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text('{"debug": true}', encoding="utf-8")

        tx = tm.begin("PROJ-001", "CHG-001")
        backup_path = tx.backup_file(rel_path)

        assert backup_path.exists()
        assert backup_path.read_text(encoding="utf-8") == '{"debug": true}'
        assert target_file.resolve() in tx.backups

    def test_backup_file_preserves_baseline_on_multiple_calls(
        self, tm: ChangeTransactionManager, workspace: Path
    ) -> None:
        target_file = workspace / "module.py"
        target_file.write_text("baseline content", encoding="utf-8")

        tx = tm.begin("PROJ-001", "CHG-001")
        b1 = tx.backup_file(target_file)

        # 模拟工作流中间步骤修改了文件
        target_file.write_text("modified content", encoding="utf-8")

        # 再次调用备份不应覆盖原有的初始基线快照
        b2 = tx.backup_file(target_file)
        assert b1 == b2
        assert b2.read_text(encoding="utf-8") == "baseline content"

    def test_backup_nonexistent_file_raises_not_found(
        self, tm: ChangeTransactionManager, workspace: Path
    ) -> None:
        tx = tm.begin("PROJ-001", "CHG-001")
        with pytest.raises(FileNotFoundError):
            tx.backup_file(workspace / "not_found.py")

    def test_backup_file_outside_workspace(
        self, tm: ChangeTransactionManager, tmp_path: Path
    ) -> None:
        ext_file = tmp_path / "external" / "ext.txt"
        ext_file.parent.mkdir(parents=True, exist_ok=True)
        ext_file.write_text("external data", encoding="utf-8")

        tx = tm.begin("PROJ-001", "CHG-001")
        backup_path = tx.backup_file(ext_file)
        assert backup_path.exists()
        assert backup_path.read_text(encoding="utf-8") == "external data"


class TestChangeTransactionTrackCreated:
    """新建文件登记测试"""

    def test_track_created_file(self, tm: ChangeTransactionManager, workspace: Path) -> None:
        tx = tm.begin("PROJ-001", "CHG-001")
        new_file = workspace / "new_module.py"
        tx.track_created_file(new_file)
        assert new_file.resolve() in tx.created_files

        # 重复登记不重复添加
        tx.track_created_file(new_file)
        assert len(tx.created_files) == 1

    def test_track_created_relative_path(self, tm: ChangeTransactionManager, workspace: Path) -> None:
        tx = tm.begin("PROJ-001", "CHG-001")
        tx.track_created_file("docs/readme.md")
        assert (workspace / "docs" / "readme.md").resolve() in tx.created_files


class TestChangeTransactionRollback:
    """事务回滚与清理测试"""

    def test_rollback_restores_modified_and_removes_created_files(
        self, tm: ChangeTransactionManager, workspace: Path
    ) -> None:
        # 1. 准备已有文件
        orig_file1 = workspace / "file1.txt"
        orig_file1.write_text("orig1_initial", encoding="utf-8")
        orig_file2 = workspace / "sub" / "file2.txt"
        orig_file2.parent.mkdir(parents=True, exist_ok=True)
        orig_file2.write_text("orig2_initial", encoding="utf-8")

        # 2. 事务备份并修改
        tx = tm.begin("PROJ-001", "CHG-001")
        tx.backup_file(orig_file1)
        tx.backup_file(orig_file2)

        orig_file1.write_text("orig1_dirty", encoding="utf-8")
        orig_file2.write_text("orig2_dirty", encoding="utf-8")

        # 3. 事务新建文件及目录
        new_dir = workspace / "created_dir"
        new_dir.mkdir(parents=True, exist_ok=True)
        new_file = new_dir / "created.txt"
        new_file.write_text("created_content", encoding="utf-8")
        tx.track_created_file(new_file)
        tx.track_created_file(new_dir)

        assert tx.backup_dir.exists()

        # 4. 执行回滚
        with patch("auto_pm.application.core.change_transaction.audit_log") as mock_audit:
            tx.rollback(reason="Test failure")
            mock_audit.assert_called_once()
            call_kwargs = mock_audit.call_args[1]
            assert call_kwargs["tx_id"] == tx.tx_id
            assert call_kwargs["reason"] == "Test failure"
            assert call_kwargs["restored_count"] == 2
            assert call_kwargs["deleted_count"] == 2

        # 5. 校验还原结果
        assert orig_file1.read_text(encoding="utf-8") == "orig1_initial"
        assert orig_file2.read_text(encoding="utf-8") == "orig2_initial"
        assert not new_file.exists()
        assert not new_dir.exists()
        assert not tx.backup_dir.exists()
        assert tx.status == TransactionStatus.ROLLED_BACK


class TestChangeTransactionCommit:
    """事务提交测试"""

    def test_commit_cleans_backups_and_keeps_changes(
        self, tm: ChangeTransactionManager, workspace: Path
    ) -> None:
        orig_file = workspace / "script.py"
        orig_file.write_text("v1", encoding="utf-8")

        tx = tm.begin("PROJ-001", "CHG-001")
        tx.backup_file(orig_file)
        orig_file.write_text("v2", encoding="utf-8")

        new_file = workspace / "extra.py"
        new_file.write_text("new", encoding="utf-8")
        tx.track_created_file(new_file)

        assert tx.backup_dir.exists()

        with patch("auto_pm.application.core.change_transaction.audit_log") as mock_audit:
            tx.commit()
            mock_audit.assert_called_once()
            call_kwargs = mock_audit.call_args[1]
            assert call_kwargs["tx_id"] == tx.tx_id
            assert call_kwargs["backed_up_count"] == 1
            assert call_kwargs["created_count"] == 1

        assert orig_file.read_text(encoding="utf-8") == "v2"
        assert new_file.exists()
        assert not tx.backup_dir.exists()
        assert tx.status == TransactionStatus.COMMITTED


class TestChangeTransactionContextManager:
    """上下文管理器行为测试"""

    def test_context_manager_auto_commit_on_success(
        self, tm: ChangeTransactionManager, workspace: Path
    ) -> None:
        target = workspace / "doc.md"
        target.write_text("init", encoding="utf-8")

        with tm.transaction("PROJ-001", "CHG-001") as tx:
            tx.backup_file(target)
            target.write_text("updated", encoding="utf-8")
            assert tx.status == TransactionStatus.ACTIVE

        assert tx.status == TransactionStatus.COMMITTED
        assert target.read_text(encoding="utf-8") == "updated"
        assert not tx.backup_dir.exists()

    def test_context_manager_auto_rollback_on_exception(
        self, tm: ChangeTransactionManager, workspace: Path
    ) -> None:
        target = workspace / "doc.md"
        target.write_text("init", encoding="utf-8")
        new_file = workspace / "temp.txt"

        with pytest.raises(RuntimeError, match="Simulated Error"):
            with tm.transaction("PROJ-001", "CHG-001") as tx:
                tx.backup_file(target)
                target.write_text("dirty", encoding="utf-8")
                new_file.write_text("created", encoding="utf-8")
                tx.track_created_file(new_file)
                raise RuntimeError("Simulated Error")

        assert tx.status == TransactionStatus.ROLLED_BACK
        assert target.read_text(encoding="utf-8") == "init"
        assert not new_file.exists()
        assert not tx.backup_dir.exists()

    def test_context_manager_manual_commit_not_recommitted(
        self, tm: ChangeTransactionManager, workspace: Path
    ) -> None:
        target = workspace / "doc.md"
        target.write_text("init", encoding="utf-8")

        with tm.transaction("PROJ-001", "CHG-001") as tx:
            tx.backup_file(target)
            target.write_text("done", encoding="utf-8")
            tx.commit()
            assert tx.status == TransactionStatus.COMMITTED

        assert tx.status == TransactionStatus.COMMITTED


class TestChangeTransactionStateMachine:
    """状态机与防非法流转测试"""

    def test_cannot_operate_after_commit(self, tm: ChangeTransactionManager, workspace: Path) -> None:
        target = workspace / "file.txt"
        target.write_text("content", encoding="utf-8")

        tx = tm.begin("PROJ-001", "CHG-001")
        tx.commit()

        with pytest.raises(TransactionStateError):
            tx.commit()

        with pytest.raises(TransactionStateError):
            tx.rollback()

        with pytest.raises(TransactionStateError):
            tx.backup_file(target)

        with pytest.raises(TransactionStateError):
            tx.track_created_file(target)

        with pytest.raises(TransactionStateError):
            with tx:
                pass

    def test_cannot_operate_after_rollback(self, tm: ChangeTransactionManager, workspace: Path) -> None:
        target = workspace / "file.txt"
        target.write_text("content", encoding="utf-8")

        tx = tm.begin("PROJ-001", "CHG-001")
        tx.rollback()

        with pytest.raises(TransactionStateError):
            tx.rollback()

        with pytest.raises(TransactionStateError):
            tx.commit()

        with pytest.raises(TransactionStateError):
            tx.backup_file(target)

        with pytest.raises(TransactionStateError):
            tx.track_created_file(target)

        with pytest.raises(TransactionStateError):
            with tx:
                pass


class TestChangeTransactionErrorResilience:
    """DEV-300 故障隔离与异常容错测试"""

    def test_backup_file_os_error_raises_transaction_file_error(
        self, tm: ChangeTransactionManager, workspace: Path
    ) -> None:
        from auto_pm.application.core.change_transaction import TransactionFileError

        target = workspace / "dummy.txt"
        target.write_text("ok", encoding="utf-8")
        tx = tm.begin("PROJ-001", "CHG-001")

        with patch("shutil.copy2", side_effect=OSError("Disk write error")):
            with pytest.raises(TransactionFileError, match="创建文件快照失败"):
                tx.backup_file(target)

    def test_rollback_tolerates_individual_file_errors(
        self, tm: ChangeTransactionManager, workspace: Path
    ) -> None:
        target = workspace / "file.txt"
        target.write_text("v1", encoding="utf-8")
        created = workspace / "created.txt"
        created.write_text("new", encoding="utf-8")

        tx = tm.begin("PROJ-001", "CHG-001")
        tx.backup_file(target)
        tx.track_created_file(created)

        with patch("shutil.copy2", side_effect=OSError("Restore permission denied")), patch.object(
            Path, "unlink", side_effect=OSError("Delete permission denied")
        ):
            tx.rollback(reason="Test error resilience")

        # 事务仍正确流转为 ROLLED_BACK，不发生致命崩溃
        assert tx.status == TransactionStatus.ROLLED_BACK

    def test_cleanup_failure_handled_gracefully(
        self, tm: ChangeTransactionManager, workspace: Path
    ) -> None:
        tx = tm.begin("PROJ-001", "CHG-001")
        tx.backup_dir.mkdir(parents=True, exist_ok=True)
        with patch("shutil.rmtree", side_effect=OSError("Access denied")):
            tx.commit()
        assert tx.status == TransactionStatus.COMMITTED

        tx2 = tm.begin("PROJ-001", "CHG-002")
        tx2.backup_dir.mkdir(parents=True, exist_ok=True)
        with patch("shutil.rmtree", side_effect=OSError("Access denied")):
            tx2.rollback()
        assert tx2.status == TransactionStatus.ROLLED_BACK
