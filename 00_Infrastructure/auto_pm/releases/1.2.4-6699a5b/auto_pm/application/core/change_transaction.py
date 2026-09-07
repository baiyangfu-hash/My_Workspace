"""auto_pm.application.core.change_transaction - 变更事务沙箱管理器

遵循 Clean Architecture 架构与 DEV-300 Google SRE 工程可靠性规范，
为 Cockpit OS 工作流执行阶段提供文件级事务沙箱、原文件快照备份、新建文件追踪、
异常原子回滚、正常提交清理及白盒审计记录能力。
"""

from __future__ import annotations

import hashlib
import logging
import shutil
import uuid
from contextlib import AbstractContextManager
from datetime import datetime
from pathlib import Path
from types import TracebackType

from auto_pm.contracts.workflow_dtos import TransactionStatus
from auto_pm.infrastructure.logging.audit import audit_log

logger = logging.getLogger(__name__)

__all__ = [
    "ChangeTransaction",
    "ChangeTransactionManager",
    "TransactionError",
    "TransactionFileError",
    "TransactionStateError",
]


class TransactionError(Exception):
    """事务基础异常"""


class TransactionStateError(TransactionError):
    """事务状态非法流转异常"""


class TransactionFileError(TransactionError):
    """事务文件 I/O 与备份恢复异常"""


class ChangeTransaction(AbstractContextManager["ChangeTransaction"]):
    """变更事务沙箱实例

    支持文件修改前快照备份、新建文件登记、发生错误时原子回滚与正常提交清理。
    """

    def __init__(
        self,
        tx_id: str,
        project_id: str,
        change_id: str,
        workspace_root: Path,
        backup_dir: Path,
    ) -> None:
        self.tx_id: str = tx_id
        self.project_id: str = project_id
        self.change_id: str = change_id
        self.status: TransactionStatus = TransactionStatus.ACTIVE
        self.workspace_root: Path = workspace_root
        self.backup_dir: Path = backup_dir
        self.backups: dict[Path, Path] = {}
        self.created_files: list[Path] = []

    def _resolve_path(self, path: str | Path) -> Path:
        """统一解析路径为绝对路径"""
        target = Path(path)
        if not target.is_absolute():
            return (self.workspace_root / target).resolve()
        return target.resolve()

    def backup_file(self, path: str | Path) -> Path:
        """为原文件在 backup_dir 创建快照副本。

        原文件必须存在。多次对同一文件备份时，保持首次基线快照不被覆盖。

        Args:
            path: 目标文件路径（可为绝对路径或相对于 workspace_root 的路径）

        Returns:
            备份文件在 backup_dir 中的绝对路径

        Raises:
            TransactionStateError: 事务不处于 ACTIVE 状态
            FileNotFoundError: 原文件不存在或不是普通文件
            TransactionFileError: 快照创建失败
        """
        if self.status != TransactionStatus.ACTIVE:
            raise TransactionStateError(
                f"事务 {self.tx_id} 当前状态为 {self.status.value}，禁止备份文件"
            )

        target = self._resolve_path(path)
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(f"原文件不存在，无法创建备份快照: {target}")

        # 若已备份，保留初始快照（基线版本）
        if target in self.backups:
            return self.backups[target]

        try:
            rel = target.relative_to(self.workspace_root)
            backup_path = (self.backup_dir / rel).resolve()
        except ValueError:
            h = hashlib.sha256(str(target).encode("utf-8")).hexdigest()[:8]
            backup_path = (self.backup_dir / f"{h}_{target.name}").resolve()

        try:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup_path)
        except OSError as exc:
            logger.error("创建文件快照失败 %s -> %s: %s", target, backup_path, exc, exc_info=True)
            raise TransactionFileError(f"创建文件快照失败: {target} -> {exc}") from exc

        self.backups[target] = backup_path
        return backup_path

    def track_created_file(self, path: str | Path) -> None:
        """登记事务过程中新建的文件。

        Args:
            path: 新建文件路径（可为绝对路径或相对于 workspace_root 的路径）

        Raises:
            TransactionStateError: 事务不处于 ACTIVE 状态
        """
        if self.status != TransactionStatus.ACTIVE:
            raise TransactionStateError(
                f"事务 {self.tx_id} 当前状态为 {self.status.value}，禁止登记新建文件"
            )

        target = self._resolve_path(path)
        if target not in self.created_files:
            self.created_files.append(target)

    def rollback(self, reason: str = "") -> None:
        """回滚事务：恢复所有备份的原文件，物理删除所有新建文件，清理快照目录并记录审计日志。

        Args:
            reason: 回滚原因说明

        Raises:
            TransactionStateError: 事务不处于 ACTIVE 状态
        """
        if self.status != TransactionStatus.ACTIVE:
            raise TransactionStateError(
                f"事务 {self.tx_id} 当前状态为 {self.status.value}，仅 ACTIVE 状态可执行 rollback"
            )

        errors: list[str] = []

        # 1. 恢复所有备份的原文件
        for orig_path, backup_path in self.backups.items():
            try:
                if backup_path.exists():
                    orig_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup_path, orig_path)
            except OSError as exc:
                logger.error(
                    "回滚恢复文件失败: %s -> %s: %s", backup_path, orig_path, exc, exc_info=True
                )
                errors.append(f"恢复文件失败 {orig_path}: {exc}")

        # 2. 物理删除所有新建文件（逆序清理，优先删除子层文件）
        for created_path in reversed(self.created_files):
            try:
                if created_path.is_file() or created_path.is_symlink():
                    created_path.unlink(missing_ok=True)
                elif created_path.is_dir():
                    shutil.rmtree(created_path, ignore_errors=True)
            except OSError as exc:
                logger.error("回滚清理新建文件失败 %s: %s", created_path, exc, exc_info=True)
                errors.append(f"删除新建文件失败 {created_path}: {exc}")

        # 3. 清理 backup_dir
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir, ignore_errors=True)
        except OSError as exc:
            logger.warning("清理快照目录失败 %s: %s", self.backup_dir, exc)

        # 4. 标记状态
        self.status = TransactionStatus.ROLLED_BACK

        # 5. 记录审计日志
        audit_log(
            "change_transaction_rollback",
            tx_id=self.tx_id,
            project_id=self.project_id,
            change_id=self.change_id,
            reason=reason,
            restored_count=len(self.backups),
            deleted_count=len(self.created_files),
            errors=errors,
        )

    def commit(self) -> None:
        """提交事务：清理快照目录并记录审计日志。

        Raises:
            TransactionStateError: 事务不处于 ACTIVE 状态
        """
        if self.status != TransactionStatus.ACTIVE:
            raise TransactionStateError(
                f"事务 {self.tx_id} 当前状态为 {self.status.value}，仅 ACTIVE 状态可执行 commit"
            )

        # 1. 清理 backup_dir
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir, ignore_errors=True)
        except OSError as exc:
            logger.warning("清理快照目录失败 %s: %s", self.backup_dir, exc)

        # 2. 标记状态
        self.status = TransactionStatus.COMMITTED

        # 3. 记录审计日志
        audit_log(
            "change_transaction_commit",
            tx_id=self.tx_id,
            project_id=self.project_id,
            change_id=self.change_id,
            backed_up_count=len(self.backups),
            created_count=len(self.created_files),
        )

    def __enter__(self) -> ChangeTransaction:
        if self.status != TransactionStatus.ACTIVE:
            raise TransactionStateError(
                f"事务 {self.tx_id} 当前状态为 {self.status.value}，无法进入上下文"
            )
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        if exc_type is not None:
            if self.status == TransactionStatus.ACTIVE:
                self.rollback(reason=str(exc_val))
            return False

        if self.status == TransactionStatus.ACTIVE:
            self.commit()
        return None


class ChangeTransactionManager:
    """变更事务管理器

    负责统一创建、管理和提供工作流上下文级沙箱事务。
    """

    def __init__(
        self,
        workspace_root: str | Path = ".",
        backup_base_dir: str | Path | None = None,
    ) -> None:
        self.workspace_root: Path = Path(workspace_root).resolve()
        if backup_base_dir is not None:
            self.backup_base_dir: Path = Path(backup_base_dir).resolve()
        else:
            self.backup_base_dir = (self.workspace_root / ".auto-pm" / "transactions").resolve()

    def begin(
        self,
        project_id: str,
        change_id: str,
        tx_id: str | None = None,
    ) -> ChangeTransaction:
        """开启并返回一个新的活动事务。

        Args:
            project_id: 项目 ID
            change_id: 变更单 ID
            tx_id: 可选事务 ID，缺省自动生成

        Returns:
            初始状态为 ACTIVE 的 ChangeTransaction 实例
        """
        if not tx_id:
            tx_id = f"TX-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
        backup_dir = self.backup_base_dir / tx_id
        return ChangeTransaction(
            tx_id=tx_id,
            project_id=project_id,
            change_id=change_id,
            workspace_root=self.workspace_root,
            backup_dir=backup_dir,
        )

    def transaction(
        self,
        project_id: str,
        change_id: str,
        tx_id: str | None = None,
    ) -> ChangeTransaction:
        """获取事务上下文管理器。

        Args:
            project_id: 项目 ID
            change_id: 变更单 ID
            tx_id: 可选事务 ID，缺省自动生成

        Returns:
            支持 with 语法的 ChangeTransaction 事务沙箱
        """
        return self.begin(project_id=project_id, change_id=change_id, tx_id=tx_id)
