"""
学习激励系统 - 积分、连胜天数、等级徽章
高内聚低耦合：仅管理激励数据，不依赖 UI
"""
import os
import sqlite3
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'app.db')

# 等级徽章定义
BADGES = {
    "first_study": {"name": "初学者", "icon": "🌱", "description": "完成第一次学习", "condition": "total_days >= 1"},
    "week_streak": {"name": "坚持一周", "icon": "🔥", "description": "连续学习 7 天", "condition": "streak_days >= 7"},
    "month_streak": {"name": "坚持一月", "icon": "⚡", "description": "连续学习 30 天", "condition": "streak_days >= 30"},
    "vocab_100": {"name": "百词斩", "icon": "📚", "description": "掌握 100 个单词", "condition": "vocab_mastered >= 100"},
    "vocab_500": {"name": "词汇达人", "icon": "🎓", "description": "掌握 500 个单词", "condition": "vocab_mastered >= 500"},
    "vocab_1500": {"name": "A2 达标", "icon": "🏆", "description": "掌握 1500 个单词（A2）", "condition": "vocab_mastered >= 1500"},
    "grammar_10": {"name": "语法入门", "icon": "📖", "description": "学习 10 个语法点", "condition": "grammar_completed >= 10"},
    "grammar_50": {"name": "语法达人", "icon": "📝", "description": "学习 50 个语法点", "condition": "grammar_completed >= 50"},
    "grammar_all": {"name": "语法大师", "icon": "👑", "description": "学习全部 113 个语法点", "condition": "grammar_completed >= 113"},
    "daily_30min": {"name": "勤奋学习", "icon": "⏰", "description": "单日学习 30 分钟", "condition": "daily_minutes >= 30"},
    "perfect_day": {"name": "完美一天", "icon": "⭐", "description": "单日正确率 100%（至少 10 题）", "condition": "perfect_day"},
    "level_a2": {"name": "A2 达成", "icon": "🥈", "description": "通过 A2 等级", "condition": "level >= A2"},
    "level_b1": {"name": "B1 达成", "icon": "🥇", "description": "通过 B1 等级", "condition": "level >= B1"},
}

# 积分规则
POINTS_RULES = {
    "new_word": 5,       # 学习一个新词
    "review_word": 2,    # 复习一个单词
    "correct_answer": 3, # 答对一题
    "grammar_point": 10,  # 学习一个语法点
    "dialog_read": 8,     # 阅读一个对话
    "dictation": 5,       # 完成一次听写
    "daily_bonus": 20,    # 每日登录奖励
    "streak_bonus_7": 50,  # 连续 7 天奖励
    "streak_bonus_30": 200, # 连续 30 天奖励
}


class StudyTracker:
    """学习激励系统"""

    def __init__(self):
        self._ensure_db()

    def _ensure_db(self):
        """确保激励相关表存在"""
        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 积分记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS points_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                action TEXT NOT NULL,
                points INTEGER DEFAULT 0,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_points_date ON points_log(date)')

        # 徽章表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                badge_id TEXT UNIQUE NOT NULL,
                earned_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 每日汇总
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summary (
                date TEXT PRIMARY KEY,
                total_points INTEGER DEFAULT 0,
                new_words INTEGER DEFAULT 0,
                review_words INTEGER DEFAULT 0,
                correct_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0,
                study_minutes INTEGER DEFAULT 0,
                grammar_completed INTEGER DEFAULT 0,
                dialogs_read INTEGER DEFAULT 0
            )
        ''')

        conn.commit()
        conn.close()

    def add_points(self, action, count=1):
        """添加积分"""
        if action not in POINTS_RULES:
            return 0
        points = POINTS_RULES[action] * count
        today = datetime.now().strftime('%Y-%m-%d')

        if not os.path.exists(DB_PATH):
            return points

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO points_log (date, action, points, description) VALUES (?, ?, ?, ?)',
            (today, action, points, f"{action} x{count}")
        )

        # 更新每日汇总
        cursor.execute('''
            INSERT INTO daily_summary (date, total_points) VALUES (?, ?)
            ON CONFLICT(date) DO UPDATE SET total_points = total_points + ?
        ''', (today, points, points))

        conn.commit()
        conn.close()
        return points

    def get_today_points(self):
        """获取今日积分"""
        if not os.path.exists(DB_PATH):
            return 0
        today = datetime.now().strftime('%Y-%m-%d')
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT COALESCE(SUM(points), 0) FROM points_log WHERE date = ?', (today,))
            return cursor.fetchone()[0]
        except sqlite3.OperationalError:
            return 0
        finally:
            conn.close()

    def get_week_points(self):
        """获取本周积分"""
        if not os.path.exists(DB_PATH):
            return 0
        today = datetime.now()
        week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT COALESCE(SUM(points), 0) FROM points_log WHERE date >= ?', (week_start,))
            return cursor.fetchone()[0]
        except sqlite3.OperationalError:
            return 0
        finally:
            conn.close()

    def get_streak_days(self):
        """获取连续学习天数"""
        if not os.path.exists(DB_PATH):
            return 0
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT DISTINCT date FROM points_log ORDER BY date DESC')
            dates = [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            dates = []
        conn.close()

        if not dates:
            return 0

        streak = 0
        today = datetime.now().strftime('%Y-%m-%d')
        check_date = today

        for _ in range(365):
            if check_date in dates:
                streak += 1
                # 前一天
                d = datetime.strptime(check_date, '%Y-%m-%d') - timedelta(days=1)
                check_date = d.strftime('%Y-%m-%d')
            else:
                break

        return streak

    def check_and_award_badges(self, user_stats=None):
        """检查并颁发新徽章"""
        if not os.path.exists(DB_PATH):
            return []

        if user_stats is None:
            user_stats = {}

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 获取已有徽章
        cursor.execute('SELECT badge_id FROM badges')
        earned = {row[0] for row in cursor.fetchall()}

        new_badges = []
        stats = {
            "total_days": user_stats.get("total_days", 0),
            "streak_days": self.get_streak_days(),
            "vocab_mastered": user_stats.get("vocab_mastered", 0),
            "grammar_completed": user_stats.get("grammar_completed", 0),
            "daily_minutes": user_stats.get("study_minutes", 0),
            "perfect_day": user_stats.get("perfect_day", False),
            "level": user_stats.get("current_level", "A1"),
        }

        for badge_id, badge_info in BADGES.items():
            if badge_id in earned:
                continue
            if self._evaluate_condition(badge_info['condition'], stats):
                today = datetime.now().strftime('%Y-%m-%d')
                cursor.execute(
                    'INSERT OR IGNORE INTO badges (badge_id, earned_date) VALUES (?, ?)',
                    (badge_id, today)
                )
                new_badges.append({
                    "badge_id": badge_id,
                    "name": badge_info["name"],
                    "icon": badge_info["icon"],
                    "description": badge_info["description"],
                })

        conn.commit()
        conn.close()
        return new_badges

    def _evaluate_condition(self, condition, stats):
        """评估徽章条件"""
        try:
            if ">=" in condition:
                key, val = condition.split(">=")
                key = key.strip()
                val = int(val.strip())
                return stats.get(key, 0) >= val
            elif "==" in condition:
                key, val = condition.split("==")
                return str(stats.get(key.strip(), "")) == val.strip()
            elif condition == "perfect_day":
                return stats.get("perfect_day", False)
            elif condition.startswith("level >="):
                level = condition.split(">=")[1].strip()
                level_order = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5}
                current_order = level_order.get(stats.get("level", "A1"), 0)
                target_order = level_order.get(level, 0)
                return current_order >= target_order
        except Exception:
            pass
        return False

    def get_all_badges(self):
        """获取所有徽章（含已获得和未获得）"""
        earned = self.get_earned_badges()
        earned_ids = {b['badge_id'] for b in earned}

        all_badges = []
        for badge_id, info in BADGES.items():
            all_badges.append({
                "badge_id": badge_id,
                "name": info["name"],
                "icon": info["icon"],
                "description": info["description"],
                "earned": badge_id in earned_ids,
                "earned_date": next((b['earned_date'] for b in earned if b['badge_id'] == badge_id), None),
            })
        return all_badges

    def get_earned_badges(self):
        """获取已获得的徽章"""
        if not os.path.exists(DB_PATH):
            return []
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT badge_id, earned_date FROM badges ORDER BY earned_date')
            rows = cursor.fetchall()
            result = []
            for row in rows:
                info = BADGES.get(row['badge_id'], {})
                result.append({
                    "badge_id": row['badge_id'],
                    "name": info.get("name", ""),
                    "icon": info.get("icon", ""),
                    "description": info.get("description", ""),
                    "earned_date": row['earned_date'],
                })
            return result
        except sqlite3.OperationalError:
            return []
        finally:
            conn.close()

    def get_points_history(self, days=7):
        """获取最近 N 天的积分历史"""
        if not os.path.exists(DB_PATH):
            return []
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT date, COALESCE(SUM(points), 0) as total
                FROM points_log
                WHERE date >= date('now', ?)
                GROUP BY date
                ORDER BY date
            ''', (f'-{days} days',))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            return []
        finally:
            conn.close()
