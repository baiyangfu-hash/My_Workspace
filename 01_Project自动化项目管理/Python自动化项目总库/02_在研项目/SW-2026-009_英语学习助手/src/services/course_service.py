"""
课程服务模块 - 封装课程路线图、每日学习计划与等级大纲生成逻辑
"""
from typing import Any

from course_manager import CourseManager

VALID_CEFR_LEVELS = ("A1", "A2", "B1", "B2", "C1", "C2")


class CourseService:
    VALID_CEFR_LEVELS = VALID_CEFR_LEVELS

    def __init__(self, db_manager=None):
        self.course_manager = CourseManager()

    @staticmethod
    def sanitize_level(level: Any, default: str = "A1") -> str:
        """清洗并校验 CEFR 等级入参，兜底保障零崩溃 (DEV-300)"""
        if level is None or not isinstance(level, str):
            return default
        clean = str(level).strip().upper()
        if clean in VALID_CEFR_LEVELS:
            return clean
        return default

    def get_user_progress(self):
        """获取当前用户学习进度与等级"""
        return self.course_manager.get_user_progress()

    def generate_daily_plan(self):
        """生成今日推荐学习计划"""
        return self.course_manager.get_daily_plan()

    def get_roadmap(self):
        """获取 6 个月阶段性路线图"""
        return self.course_manager.get_roadmap()

    def update_progress(self, vocab_count=0, grammar_count=0):
        """更新学习进度"""
        return self.course_manager.update_progress(vocab_count, grammar_count)

    def set_user_level(self, level: Any):
        """设置当前用户等级 (A1, A2, B1, B2, C1, C2)"""
        clean_level = self.sanitize_level(level)
        return self.course_manager.set_user_level(clean_level)

