"""
语法服务模块 - 封装语法知识点查询与自动出题生成逻辑
"""
from grammar_engine import GrammarEngine
from grammar_practice import GrammarPracticeEngine


class GrammarService:
    def __init__(self):
        self.grammar_engine = GrammarEngine()
        self.practice_engine = GrammarPracticeEngine()

    def get_points_by_level(self, level):
        """按 CEFR 等级（A1/A2/B1）获取语法点列表"""
        return self.grammar_engine.get_points_by_level(level)

    def get_point_by_id(self, point_id):
        """根据 ID 获取语法点详情"""
        return self.grammar_engine.get_point_by_id(point_id)

    def generate_practice(self, point):
        """自动为语法点生成练习题"""
        return self.practice_engine.generate_exercises(point)

