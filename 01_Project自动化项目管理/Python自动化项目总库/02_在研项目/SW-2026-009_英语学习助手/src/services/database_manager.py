"""
数据库连接与事务管理器 - 提供线程安全的 SQLite 上下文管理
"""
import os
import sqlite3
import threading
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'app.db')

class DatabaseManager:
    """线程安全的 SQLite 数据库管理器"""
    _local = threading.local()

    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_tables()

    def get_connection(self):
        """获取当前线程的数据库连接"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    @contextmanager
    def session(self):
        """上下文管理器：自动提交与异常回滚"""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def init_tables(self):
        """初始化数据库表结构"""
        with self.session() as conn:
            cursor = conn.cursor()
            # 学习记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    word_id TEXT,
                    action TEXT NOT NULL,
                    result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 用户单词状态表（用于间隔重复）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT UNIQUE NOT NULL,
                    status TEXT DEFAULT 'new',
                    fsrs_state TEXT,
                    due_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 学习统计表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    new_words INTEGER DEFAULT 0,
                    review_words INTEGER DEFAULT 0,
                    study_minutes INTEGER DEFAULT 0,
                    correct_count INTEGER DEFAULT 0,
                    total_count INTEGER DEFAULT 0
                )
            ''')

    def close(self):
        """关闭当前线程连接"""
        if hasattr(self._local, 'conn') and self._local.conn is not None:
            self._local.conn.close()
            self._local.conn = None

_db_manager_instance = None

def get_db(db_path=None):
    """获取全局单例 DatabaseManager 实例"""
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager(db_path)
    return _db_manager_instance
