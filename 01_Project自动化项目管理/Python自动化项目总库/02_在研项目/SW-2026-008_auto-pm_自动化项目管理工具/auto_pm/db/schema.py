"""SQLite 表结构定义（DDL）

五张表（V0.3.0 M2 扩展）：
- projects: 项目索引缓存
- change_requests: 变更单索引
- impact_analysis: 变更影响分析持久化（M2-1 新增）
- approval_history: 审批流转历史持久化（M2-1 新增）
- scan_log: 扫描日志
"""

from __future__ import annotations

import sqlite3

# 项目索引缓存表
DDL_PROJECTS = """
CREATE TABLE IF NOT EXISTS projects (
    project_id       TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    path             TEXT NOT NULL,
    stack            TEXT NOT NULL DEFAULT 'unknown',
    version          TEXT NOT NULL DEFAULT '',
    description      TEXT NOT NULL DEFAULT '',
    source           TEXT NOT NULL DEFAULT '',
    phase            TEXT NOT NULL DEFAULT '',
    business_line    TEXT NOT NULL DEFAULT '',
    extra            TEXT NOT NULL DEFAULT '{}',
    file_mtime       REAL NOT NULL DEFAULT 0,
    last_scanned     TEXT NOT NULL DEFAULT '',
    scanner_version  TEXT NOT NULL DEFAULT ''
);
"""

# 项目索引（加速按技术栈/阶段/业务线筛选）
DDL_INDEX_PROJECTS_STACK = """
CREATE INDEX IF NOT EXISTS idx_projects_stack ON projects(stack);
"""
DDL_INDEX_PROJECTS_PHASE = """
CREATE INDEX IF NOT EXISTS idx_projects_phase ON projects(phase);
"""
DDL_INDEX_PROJECTS_BUSINESS_LINE = """
CREATE INDEX IF NOT EXISTS idx_projects_business_line ON projects(business_line);
"""

# 变更单索引表
DDL_CHANGE_REQUESTS = """
CREATE TABLE IF NOT EXISTS change_requests (
    change_number   TEXT PRIMARY KEY,
    project_id      TEXT NOT NULL,
    project_name    TEXT NOT NULL DEFAULT '',
    domain          TEXT NOT NULL DEFAULT '',
    business_nature TEXT NOT NULL DEFAULT '',
    impact_scope    TEXT NOT NULL DEFAULT '[]',
    status          TEXT NOT NULL DEFAULT 'draft',
    applicant       TEXT NOT NULL DEFAULT '待补充',
    apply_date      TEXT NOT NULL DEFAULT '待补充',
    title           TEXT NOT NULL DEFAULT '待补充',
    file_path       TEXT NOT NULL DEFAULT '',
    file_mtime      REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);
"""

# 变更单索引（加速按项目/状态查询）
DDL_INDEX_CHANGES_PROJECT = """
CREATE INDEX IF NOT EXISTS idx_changes_project ON change_requests(project_id);
"""
DDL_INDEX_CHANGES_STATUS = """
CREATE INDEX IF NOT EXISTS idx_changes_status ON change_requests(status);
"""

# 变更影响分析持久化表（M2-1 新增）
# 存储 §6 影响分析的完整结构化数据，供 GUI 传播链视图和影响分析编辑使用
DDL_IMPACT_ANALYSIS = """
CREATE TABLE IF NOT EXISTS impact_analysis (
    change_number     TEXT PRIMARY KEY,
    risk_level        TEXT NOT NULL DEFAULT '',
    mitigation        TEXT NOT NULL DEFAULT '',
    constraint_impacts TEXT NOT NULL DEFAULT '{}',
    domain_impacts    TEXT NOT NULL DEFAULT '{}',
    propagation_chain TEXT NOT NULL DEFAULT '',
    related_changes   TEXT NOT NULL DEFAULT '[]',
    updated_at        TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (change_number) REFERENCES change_requests(change_number) ON DELETE CASCADE
);
"""

# 审批流转历史持久化表（M2-1 新增）
# 每次 transition_status 流转都追加一条记录，供 GUI 审批时间线使用
DDL_APPROVAL_HISTORY = """
CREATE TABLE IF NOT EXISTS approval_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    change_number   TEXT NOT NULL,
    from_status     TEXT NOT NULL DEFAULT '',
    to_status       TEXT NOT NULL,
    approver        TEXT NOT NULL DEFAULT '',
    comment         TEXT NOT NULL DEFAULT '',
    transition_date TEXT NOT NULL,
    FOREIGN KEY (change_number) REFERENCES change_requests(change_number) ON DELETE CASCADE
);
"""

# 审批历史索引（加速按变更单号查询流转记录）
DDL_INDEX_APPROVAL_HISTORY_CHANGE = """
CREATE INDEX IF NOT EXISTS idx_approval_history_change ON approval_history(change_number);
"""

# 扫描日志表
DDL_SCAN_LOG = """
CREATE TABLE IF NOT EXISTS scan_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_type       TEXT NOT NULL,
    projects_found  INTEGER NOT NULL DEFAULT 0,
    changes_found   INTEGER NOT NULL DEFAULT 0,
    duration_ms     INTEGER NOT NULL DEFAULT 0,
    status          TEXT NOT NULL DEFAULT 'success',
    message         TEXT NOT NULL DEFAULT '',
    timestamp       TEXT NOT NULL
);
"""

# 表创建 DDL（必须先于索引执行，迁移在表创建后、索引创建前插入）
TABLE_DDL: list[str] = [
    DDL_PROJECTS,
    DDL_CHANGE_REQUESTS,
    DDL_IMPACT_ANALYSIS,
    DDL_APPROVAL_HISTORY,
    DDL_SCAN_LOG,
]

# 索引创建 DDL（在 migrate_schema 之后执行，确保新增列已存在）
INDEX_DDL: list[str] = [
    DDL_INDEX_PROJECTS_STACK,
    DDL_INDEX_PROJECTS_PHASE,
    DDL_INDEX_PROJECTS_BUSINESS_LINE,
    DDL_INDEX_CHANGES_PROJECT,
    DDL_INDEX_CHANGES_STATUS,
    DDL_INDEX_APPROVAL_HISTORY_CHANGE,
]

# 所有 DDL（按依赖顺序，向后兼容）
ALL_DDL: list[str] = [*TABLE_DDL, *INDEX_DDL]


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    """检查表中是否存在指定列"""
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row[1] == column for row in rows)


def migrate_schema(conn: sqlite3.Connection) -> None:
    """执行 schema 迁移（幂等，重复调用安全）

    处理旧版 DB 升级到新版的列变更：
    - projects 表新增 business_line 列（V2.0 阶段 F 引入）
    - projects 表新增 scanner_version 列（CHG-085：scanner 逻辑变更时强制重扫）
    """
    if not _column_exists(conn, "projects", "business_line"):
        conn.execute("ALTER TABLE projects ADD COLUMN business_line TEXT NOT NULL DEFAULT ''")
    if not _column_exists(conn, "projects", "scanner_version"):
        conn.execute("ALTER TABLE projects ADD COLUMN scanner_version TEXT NOT NULL DEFAULT ''")
    conn.commit()
