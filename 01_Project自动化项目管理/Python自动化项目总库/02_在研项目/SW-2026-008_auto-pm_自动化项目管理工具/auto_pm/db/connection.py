"""SQLite 连接管理

DB 路径: <workspace_root>/.auto-pm/index.db
使用 WAL 模式提升并发读性能。
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from auto_pm.db.schema import INDEX_DDL, TABLE_DDL, migrate_schema
from auto_pm.logging.logging import setup_logger

log = setup_logger(log_level="INFO", app_name="auto_pm")


class DatabaseManager:
    """SQLite 连接管理器

    负责创建连接、初始化表结构、管理 DB 文件位置。
    """

    DB_DIR = ".auto-pm"
    DB_FILE = "index.db"

    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = os.path.abspath(workspace_root)
        self.db_dir = os.path.join(self.workspace_root, self.DB_DIR)
        self.db_path = os.path.join(self.db_dir, self.DB_FILE)

    def _ensure_dir(self) -> None:
        """确保 DB 目录存在"""
        Path(self.db_dir).mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """获取 SQLite 连接（WAL 模式，外键开启）

        Returns:
            sqlite3.Connection: 已配置的连接
        """
        self._ensure_dir()
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 行以 dict-like 方式访问
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def init_schema(self) -> None:
        """初始化表结构（幂等，重复调用安全）

        执行顺序：表创建 → schema 迁移（ALTER TABLE ADD COLUMN）→ 索引创建。
        迁移在索引创建前执行，确保新增列存在后再创建依赖该列的索引。
        """
        with self.get_connection() as conn:
            for ddl in TABLE_DDL:
                conn.execute(ddl)
            migrate_schema(conn)
            for ddl in INDEX_DDL:
                conn.execute(ddl)
            conn.commit()
        log.info("DB schema 已初始化: %s", self.db_path)

    def drop_all(self) -> None:
        """删除所有表（仅用于测试/重置）"""
        with self.get_connection() as conn:
            conn.execute("DROP TABLE IF EXISTS scan_log")
            conn.execute("DROP TABLE IF EXISTS change_requests")
            conn.execute("DROP TABLE IF EXISTS projects")
            conn.commit()
        log.info("DB 所有表已删除: %s", self.db_path)

    def exists(self) -> bool:
        """DB 文件是否存在"""
        return os.path.isfile(self.db_path)
