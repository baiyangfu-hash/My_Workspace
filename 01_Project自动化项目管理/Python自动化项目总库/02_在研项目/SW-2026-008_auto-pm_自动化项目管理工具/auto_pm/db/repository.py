"""数据访问层（Repository）

提供 projects / change_requests / scan_log 三张表的 CRUD 操作。
所有方法使用参数化查询防止 SQL 注入。
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any

from auto_pm.db.connection import DatabaseManager
from auto_pm.models import ChangeSummary, ProjectRecord


class ProjectRepository:
    """项目索引缓存 CRUD"""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def upsert(self, project: ProjectRecord) -> None:
        """插入或更新项目记录（UPSERT）"""
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO projects
                    (project_id, name, path, stack, version, description,
                     source, phase, business_line, extra, file_mtime, last_scanned)
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    name=excluded.name,
                    path=excluded.path,
                    stack=excluded.stack,
                    version=excluded.version,
                    description=excluded.description,
                    source=excluded.source,
                    phase=excluded.phase,
                    business_line=excluded.business_line,
                    extra=excluded.extra,
                    file_mtime=excluded.file_mtime,
                    last_scanned=excluded.last_scanned
                """,
                (
                    project.project_id,
                    project.name,
                    project.path,
                    project.stack,
                    project.version,
                    project.description,
                    project.source,
                    project.phase,
                    project.business_line,
                    json.dumps(project.extra, ensure_ascii=False),
                    project.file_mtime,
                    project.last_scanned,
                ),
            )
            conn.commit()

    def get_by_id(self, project_id: str) -> ProjectRecord | None:
        """按 project_id 查询项目"""
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
            return self._row_to_record(row) if row else None

    def list_all(self) -> list[ProjectRecord]:
        """列出所有项目（按 project_id 排序）"""
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM projects ORDER BY project_id").fetchall()
            return [self._row_to_record(row) for row in rows]

    def list_by_stack(self, stack: str) -> list[ProjectRecord]:
        """按技术栈筛选项目"""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM projects WHERE stack = ? ORDER BY project_id",
                (stack,),
            ).fetchall()
            return [self._row_to_record(row) for row in rows]

    def list_by_business_line(self, business_line: str) -> list[ProjectRecord]:
        """按业务线筛选项目

        Args:
            business_line: 业务线编码（SW/DJ/ZD/XT/WX）

        Returns:
            匹配业务线的项目列表，按 project_id 排序
        """
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM projects WHERE business_line = ? ORDER BY project_id",
                (business_line,),
            ).fetchall()
            return [self._row_to_record(row) for row in rows]

    def list_by_phase(self, phase: str) -> list[ProjectRecord]:
        """按阶段筛选项目

        Args:
            phase: 项目阶段（developing/commissioning/production/archived）

        Returns:
            匹配阶段的项目列表，按 project_id 排序
        """
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM projects WHERE phase = ? ORDER BY project_id",
                (phase,),
            ).fetchall()
            return [self._row_to_record(row) for row in rows]

    def delete(self, project_id: str) -> bool:
        """删除项目记录

        Returns:
            True 如果删除了记录，False 如果记录不存在
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
            conn.commit()
            return cursor.rowcount > 0

    def count(self) -> int:
        """项目总数"""
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) as cnt FROM projects").fetchone()
            return int(row["cnt"]) if row else 0

    def get_mtime(self, project_id: str) -> float:
        """获取项目的 file_mtime（增量扫描判据）

        Returns:
            file_mtime，如果项目不存在返回 0
        """
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT file_mtime FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
            return float(row["file_mtime"]) if row else 0

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> ProjectRecord:
        """将数据库行转换为 ProjectRecord"""
        extra: dict[str, Any] = json.loads(row["extra"]) if row["extra"] else {}
        columns = row.keys()
        business_line = row["business_line"] if "business_line" in columns else ""
        return ProjectRecord(
            project_id=row["project_id"],
            name=row["name"],
            path=row["path"],
            stack=row["stack"],
            version=row["version"],
            description=row["description"],
            source=row["source"],
            phase=row["phase"],
            business_line=business_line,
            extra=extra,
            file_mtime=row["file_mtime"],
            last_scanned=row["last_scanned"],
        )


class ChangeRequestRepository:
    """变更单索引缓存 CRUD"""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def upsert(self, change: ChangeSummary, file_path: str = "", file_mtime: float = 0) -> None:
        """插入或更新变更单记录"""
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO change_requests
                    (change_number, project_id, project_name, domain,
                     business_nature, impact_scope, status, applicant,
                     apply_date, title, file_path, file_mtime)
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(change_number) DO UPDATE SET
                    project_id=excluded.project_id,
                    project_name=excluded.project_name,
                    domain=excluded.domain,
                    business_nature=excluded.business_nature,
                    impact_scope=excluded.impact_scope,
                    status=excluded.status,
                    applicant=excluded.applicant,
                    apply_date=excluded.apply_date,
                    title=excluded.title,
                    file_path=excluded.file_path,
                    file_mtime=excluded.file_mtime
                """,
                (
                    change.change_number,
                    change.project_id,
                    change.project_name,
                    change.domain,
                    change.business_nature,
                    json.dumps(change.impact_scope, ensure_ascii=False),
                    change.status,
                    change.applicant,
                    change.apply_date,
                    change.title,
                    file_path,
                    file_mtime,
                ),
            )
            conn.commit()

    def list_by_project(self, project_id: str) -> list[ChangeSummary]:
        """按项目 ID 查询变更单列表"""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM change_requests WHERE project_id = ? ORDER BY change_number",
                (project_id,),
            ).fetchall()
            return [self._row_to_summary(row) for row in rows]

    def list_all(self) -> list[ChangeSummary]:
        """列出所有变更单"""
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM change_requests ORDER BY change_number").fetchall()
            return [self._row_to_summary(row) for row in rows]

    def count_by_project(self, project_id: str) -> int:
        """统计项目的变更单数"""
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(*) as cnt FROM change_requests WHERE project_id = ?",
                (project_id,),
            ).fetchone()
            return int(row["cnt"]) if row else 0

    def delete(self, change_number: str) -> bool:
        """删除变更单记录"""
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM change_requests WHERE change_number = ?", (change_number,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_by_project(self, project_id: str) -> int:
        """删除项目的所有变更单记录

        Returns:
            删除的记录数
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM change_requests WHERE project_id = ?", (project_id,))
            conn.commit()
            return cursor.rowcount

    @staticmethod
    def _row_to_summary(row: sqlite3.Row) -> ChangeSummary:
        """将数据库行转换为 ChangeSummary"""
        impact_scope: list[str] = json.loads(row["impact_scope"]) if row["impact_scope"] else []
        return ChangeSummary(
            change_number=row["change_number"],
            project_id=row["project_id"],
            project_name=row["project_name"],
            domain=row["domain"],
            business_nature=row["business_nature"],
            impact_scope=impact_scope,
            status=row["status"],
            applicant=row["applicant"],
            apply_date=row["apply_date"],
            title=row["title"],
        )


class ScanLogRepository:
    """扫描日志 CRUD"""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def insert(
        self,
        scan_type: str,
        projects_found: int,
        changes_found: int,
        duration_ms: int,
        status: str = "success",
        message: str = "",
    ) -> int:
        """插入扫描日志

        Returns:
            日志 ID
        """
        timestamp = datetime.now().isoformat()
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO scan_log
                    (scan_type, projects_found, changes_found, duration_ms,
                     status, message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (scan_type, projects_found, changes_found, duration_ms, status, message, timestamp),
            )
            conn.commit()
            return cursor.lastrowid or 0

    def get_latest(self) -> dict[str, Any] | None:
        """获取最近一次扫描日志"""
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM scan_log ORDER BY id DESC LIMIT 1").fetchone()
            return dict(row) if row else None
