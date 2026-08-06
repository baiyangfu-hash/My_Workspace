"""
数据库模块 - 管理 SQLite 数据库连接和表结构
"""
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'app.db')

class Database:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._init_tables()

    def _init_tables(self):
        """初始化数据库表"""
        # 学习记录表
        self.cursor.execute('''
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
        self.cursor.execute('''
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
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                new_words INTEGER DEFAULT 0,
                review_words INTEGER DEFAULT 0,
                study_minutes INTEGER DEFAULT 0,
                correct_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0
            )
        ''')

        self.conn.commit()

    def add_study_record(self, word, action, result=None, word_id=None):
        """添加学习记录"""
        self.cursor.execute(
            'INSERT INTO study_records (word, word_id, action, result) VALUES (?, ?, ?, ?)',
            (word, word_id, action, result)
        )
        self.conn.commit()

    def get_or_create_user_word(self, word):
        """获取或创建用户单词记录"""
        self.cursor.execute('SELECT * FROM user_words WHERE word = ?', (word,))
        row = self.cursor.fetchone()
        if row:
            return dict(row)
        self.cursor.execute(
            'INSERT INTO user_words (word, status) VALUES (?, ?)',
            (word, 'new')
        )
        self.conn.commit()
        return {'word': word, 'status': 'new', 'fsrs_state': None, 'due_date': None}

    def update_user_word(self, word, status=None, fsrs_state=None, due_date=None):
        """更新用户单词状态"""
        updates = []
        params = []
        if status is not None:
            updates.append('status = ?')
            params.append(status)
        if fsrs_state is not None:
            updates.append('fsrs_state = ?')
            params.append(fsrs_state)
        if due_date is not None:
            updates.append('due_date = ?')
            params.append(due_date)
        if not updates:
            return
        params.append(word)
        sql = f"UPDATE user_words SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE word = ?"
        self.cursor.execute(sql, params)
        self.conn.commit()

    def get_due_words(self, limit=50):
        """获取到期需要复习的单词"""
        now = datetime.now().isoformat()
        self.cursor.execute(
            'SELECT * FROM user_words WHERE due_date IS NULL OR due_date <= ? ORDER BY due_date LIMIT ?',
            (now, limit)
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_daily_stats(self, date=None):
        """获取每日统计"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('SELECT * FROM daily_stats WHERE date = ?', (date,))
        row = self.cursor.fetchone()
        if row:
            return dict(row)
        return {'date': date, 'new_words': 0, 'review_words': 0, 'study_minutes': 0, 'correct_count': 0, 'total_count': 0}

    def update_daily_stats(self, date=None, **kwargs):
        """更新每日统计"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('INSERT OR IGNORE INTO daily_stats (date) VALUES (?)', (date,))
        for key, value in kwargs.items():
            if key in ['new_words', 'review_words', 'study_minutes', 'correct_count', 'total_count']:
                self.cursor.execute(f'UPDATE daily_stats SET {key} = {key} + ? WHERE date = ?', (value, date))
        self.conn.commit()

    def close(self):
        self.conn.close()
