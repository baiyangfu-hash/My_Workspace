"""
入级测试引擎 - 10道题判断用户 CEFR 等级（A1/A2/B1）
高内聚低耦合：仅生成测试题和计算结果，不依赖 UI
"""
import os
import random
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'app.db')

# 入级测试题库，按等级分组
LEVEL_TEST_QUESTIONS = {
    "A1": [
        # 词汇
        {"type": "vocab", "question": "「breakfast」是什么意思？", "options": ["早餐", "午餐", "晚餐", "零食"], "answer": "早餐"},
        {"type": "vocab", "question": "「yesterday」是什么意思？", "options": ["今天", "明天", "昨天", "后天"], "answer": "昨天"},
        {"type": "vocab", "question": "「beautiful」是什么意思？", "options": ["丑陋的", "美丽的", "大的", "小的"], "answer": "美丽的"},
        {"type": "vocab", "question": "「hospital」是什么意思？", "options": ["学校", "医院", "酒店", "机场"], "answer": "医院"},
        # 语法
        {"type": "grammar", "question": "I ___ a student.", "options": ["am", "is", "are", "be"], "answer": "am"},
        {"type": "grammar", "question": "She ___ to school every day.", "options": ["go", "goes", "going", "went"], "answer": "goes"},
        {"type": "grammar", "question": "___ you like coffee?", "options": ["Do", "Does", "Are", "Is"], "answer": "Do"},
        {"type": "grammar", "question": "There ___ three books on the table.", "options": ["is", "am", "are", "be"], "answer": "are"},
        # 听力/阅读理解（文字版）
        {"type": "reading", "question": "阅读: 'My name is Tom. I am from China. I live in New York now.' Tom 来自哪里？", "options": ["纽约", "中国", "日本", "英国"], "answer": "中国"},
        {"type": "reading", "question": "阅读: 'The weather is nice today. Let\'s go to the park.' 天气怎么样？", "options": ["下雨", "很好", "很冷", "很热"], "answer": "很好"},
    ],
    "A2": [
        # 词汇
        {"type": "vocab", "question": "「reservation」是什么意思？", "options": ["保留", "预订", "恢复", "决心"], "answer": "预订"},
        {"type": "vocab", "question": "「environment」是什么意思？", "options": ["环境", "设备", "娱乐", "实验"], "answer": "环境"},
        {"type": "vocab", "question": "「accommodation」是什么意思？", "options": ["交通", "住宿", "陪同", "完成"], "answer": "住宿"},
        {"type": "vocab", "question": "「experience」是什么意思？", "options": ["实验", "经验", "表达", "扩展"], "answer": "经验"},
        # 语法
        {"type": "grammar", "question": "I ___ already ___ my homework.", "options": ["have...finished", "has...finished", "had...finish", "am...finishing"], "answer": "have...finished"},
        {"type": "grammar", "question": "She ___ to London last summer.", "options": ["goes", "went", "has gone", "is going"], "answer": "went"},
        {"type": "grammar", "question": "If it rains, we ___ stay home.", "options": ["will", "would", "can", "could"], "answer": "will"},
        {"type": "grammar", "question": "The book ___ by millions of people.", "options": ["reads", "is read", "reading", "read"], "answer": "is read"},
        # 阅读
        {"type": "reading", "question": "阅读: 'I\'ve been living here for 5 years. Before that, I lived in Tokyo.' 这个人现在住在哪里？", "options": ["东京", "这里（当前城市）", "纽约", "伦敦"], "answer": "这里（当前城市）"},
        {"type": "reading", "question": "阅读: 'You mustn\'t smoke here. It\'s not allowed.' 这句话的意思是？", "options": ["你必须在这里吸烟", "你不能在这里吸烟", "你应该在这里吸烟", "你可以在这里吸烟"], "answer": "你不能在这里吸烟"},
    ],
    "B1": [
        # 词汇
        {"type": "vocab", "question": "「comprehensive」是什么意思？", "options": ["综合的", "竞争的", "抱怨的", "妥协的"], "answer": "综合的"},
        {"type": "vocab", "question": "「nevertheless」是什么意思？", "options": ["因此", "然而", "尽管如此", "总之"], "answer": "尽管如此"},
        {"type": "vocab", "question": "「perspective」是什么意思？", "options": ["透视", "观点", "百分比", "说服"], "answer": "观点"},
        {"type": "vocab", "question": "「significant」是什么意思？", "options": ["沉默的", "重要的", "暗示的", "签名的"], "answer": "重要的"},
        # 语法
        {"type": "grammar", "question": "If I ___ you, I would accept the offer.", "options": ["am", "was", "were", "be"], "answer": "were"},
        {"type": "grammar", "question": "She told me that she ___ the report the day before.", "options": ["has finished", "had finished", "finished", "will finish"], "answer": "had finished"},
        {"type": "grammar", "question": "The man ___ is standing there is my boss.", "options": ["who", "which", "what", "whom"], "answer": "who"},
        {"type": "grammar", "question": "I wish I ___ harder when I was young.", "options": ["study", "studied", "had studied", "would study"], "answer": "had studied"},
        # 阅读
        {"type": "reading", "question": "阅读: 'Despite the economic downturn, the company managed to increase its revenue by 15%, largely due to its expansion into emerging markets.' 公司收入如何？", "options": ["下降了", "增长了15%", "没有变化", "增长了50%"], "answer": "增长了15%"},
        {"type": "reading", "question": "阅读: 'Not only did she win the competition, but she also broke the national record.' 她做了什么？", "options": ["只赢了比赛", "赢了比赛并打破了纪录", "只打破了纪录", "没有参加比赛"], "answer": "赢了比赛并打破了纪录"},
    ],
}


class LevelTestEngine:
    """入级测试引擎"""

    def __init__(self):
        self._ensure_db()

    def _ensure_db(self):
        """确保测试结果表存在"""
        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS level_test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_date TEXT,
                a1_score INTEGER DEFAULT 0,
                a1_total INTEGER DEFAULT 0,
                a2_score INTEGER DEFAULT 0,
                a2_total INTEGER DEFAULT 0,
                b1_score INTEGER DEFAULT 0,
                b1_total INTEGER DEFAULT 0,
                estimated_level TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def generate_test(self):
        """
        生成入级测试题（共 10 题）
        策略：先出 4 道 A1 题，再出 3 道 A2 题，最后出 3 道 B1 题
        根据答题情况判断等级
        """
        questions = []

        # A1 题 4 道
        a1_qs = random.sample(LEVEL_TEST_QUESTIONS["A1"], min(4, len(LEVEL_TEST_QUESTIONS["A1"])))
        for q in a1_qs:
            q['level'] = 'A1'
            questions.append(q)

        # A2 题 3 道
        a2_qs = random.sample(LEVEL_TEST_QUESTIONS["A2"], min(3, len(LEVEL_TEST_QUESTIONS["A2"])))
        for q in a2_qs:
            q['level'] = 'A2'
            questions.append(q)

        # B1 题 3 道
        b1_qs = random.sample(LEVEL_TEST_QUESTIONS["B1"], min(3, len(LEVEL_TEST_QUESTIONS["B1"])))
        for q in b1_qs:
            q['level'] = 'B1'
            questions.append(q)

        random.shuffle(questions)
        return questions

    def calculate_level(self, answers):
        """
        根据答题结果计算 CEFR 等级
        answers: list of {"level": "A1/A2/B1", "correct": True/False}
        返回: {"estimated_level": "A1/A2/B1", "scores": {...}, "details": "..."}
        """
        scores = {"A1": {"correct": 0, "total": 0}, "A2": {"correct": 0, "total": 0}, "B1": {"correct": 0, "total": 0}}

        for a in answers:
            level = a.get("level", "A1")
            if level in scores:
                scores[level]["total"] += 1
                if a.get("correct"):
                    scores[level]["correct"] += 1

        # 判断等级逻辑
        a1_rate = scores["A1"]["correct"] / max(scores["A1"]["total"], 1)
        a2_rate = scores["A2"]["correct"] / max(scores["A2"]["total"], 1)
        b1_rate = scores["B1"]["correct"] / max(scores["B1"]["total"], 1)

        if a1_rate < 0.5:
            estimated = "A1"
            detail = "基础词汇和语法需要加强，建议从 A1 开始系统学习"
        elif a2_rate < 0.5:
            estimated = "A1"
            detail = "A1 基础扎实，A2 内容需要学习，建议从 A1 巩固开始"
        elif a2_rate >= 0.8 and b1_rate >= 0.5:
            estimated = "B1"
            detail = "A2 内容掌握良好，可以直接从 B1 开始学习"
        elif a2_rate >= 0.5:
            estimated = "A2"
            detail = "A1 基础扎实，建议从 A2 开始学习"
        else:
            estimated = "A1"
            detail = "建议从 A1 开始巩固基础"

        result = {
            "estimated_level": estimated,
            "scores": scores,
            "detail": detail,
            "a1_rate": round(a1_rate * 100),
            "a2_rate": round(a2_rate * 100),
            "b1_rate": round(b1_rate * 100),
        }

        return result

    def save_result(self, result):
        """保存测试结果到数据库"""
        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO level_test_results (test_date, a1_score, a1_total, a2_score, a2_total, b1_score, b1_total, estimated_level, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime('%Y-%m-%d'),
            result['scores']['A1']['correct'],
            result['scores']['A1']['total'],
            result['scores']['A2']['correct'],
            result['scores']['A2']['total'],
            result['scores']['B1']['correct'],
            result['scores']['B1']['total'],
            result['estimated_level'],
            result['detail'],
        ))

        # 更新用户等级进度
        try:
            cursor.execute('''
                UPDATE user_level_progress SET current_level = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = (SELECT id FROM user_level_progress ORDER BY id DESC LIMIT 1)
            ''', (result['estimated_level'],))
        except sqlite3.OperationalError:
            pass

        conn.commit()
        conn.close()

    def get_latest_result(self):
        """获取最近一次测试结果"""
        if not os.path.exists(DB_PATH):
            return None
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM level_test_results ORDER BY created_at DESC LIMIT 1')
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.OperationalError:
            return None
        finally:
            conn.close()

    def has_taken_test(self):
        """是否已参加过测试"""
        return self.get_latest_result() is not None
