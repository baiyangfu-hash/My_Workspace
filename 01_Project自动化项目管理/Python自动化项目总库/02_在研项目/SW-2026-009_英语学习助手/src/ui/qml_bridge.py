"""
QML Bridge 模块 - 连接 Python 后端服务 (Course, Study, Dictionary, Grammar, TTS) 与 QML 前端 UI
"""
import json
import os
import sys

from PySide6.QtCore import QObject, Signal, Slot

# 确保 src 目录在 Python path
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from dialogs_data import get_all_dialogs
from services import CourseService, DictionaryService, GrammarService, StudyService, get_db
from tts_engine import TTSEngine
from us_travel_dialogs import DIALOGS as US_TRAVEL_DIALOGS


class QmlBridge(QObject):
    """QML 与 Python 业务逻辑的通信桥梁"""

    progressUpdated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = get_db()
        self.course_svc = CourseService(self.db_manager)
        self.study_svc = StudyService(self.db_manager)
        self.dict_svc = DictionaryService()
        self.grammar_svc = GrammarService()
        self.tts = TTSEngine()

    @Slot(result=str)
    def getUserProgressJson(self) -> str:
        """获取当前用户学习进度"""
        try:
            progress = self.course_svc.get_user_progress()
            return json.dumps(progress, ensure_ascii=False)
        except Exception:
            return json.dumps({"current_level": "A1", "vocab_mastered": 60, "total_vocab": 500}, ensure_ascii=False)

    @Slot(str, result=str)
    def setUserLevelJson(self, level: str) -> str:
        """设置/更新当前用户的 CEFR 目标等级 (A1, A2, B1, B2, C1, C2)"""
        try:
            res = self.course_svc.set_user_level(level)
            self.progressUpdated.emit()
            return json.dumps(res, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @Slot(result=str)
    def getDailyPlanJson(self) -> str:
        """获取今日推荐学习计划"""
        try:
            plan = self.course_svc.generate_daily_plan()
            return json.dumps(plan, ensure_ascii=False)
        except Exception:
            return json.dumps({}, ensure_ascii=False)

    @Slot(result=str)
    def getRoadmapJson(self) -> str:
        """获取 6 个月路线图"""
        try:
            roadmap = self.course_svc.get_roadmap()
            return json.dumps(roadmap, ensure_ascii=False)
        except Exception:
            return json.dumps([], ensure_ascii=False)

    @Slot(result=str)
    def getScenariosJson(self) -> str:
        """获取出差与生活场景对话列表 (支持 27+ 场景)"""
        try:
            scenarios = []
            for key, data in US_TRAVEL_DIALOGS.items():
                scenarios.append({
                    "id": key,
                    "title": data.get("title", key),
                    "title_en": data.get("title_en", ""),
                    "category": data.get("category", "日常交流"),
                    "level": data.get("difficulty", "初级"),
                    "lines_count": len(data.get("lines", []))
                })

            # 基础对话降级合并 (base_dialogs 是 list)
            base_list = get_all_dialogs()
            for item in base_list:
                key = item.get("id")
                if key and key not in US_TRAVEL_DIALOGS:
                    scenarios.append({
                        "id": key,
                        "title": item.get("title", key),
                        "title_en": item.get("title_en", ""),
                        "category": item.get("category", "基础对话"),
                        "level": item.get("difficulty", "初级"),
                        "lines_count": item.get("line_count", 0)
                    })
            return json.dumps(scenarios, ensure_ascii=False)
        except Exception as e:
            print(f"Error in getScenariosJson: {e}")
            return json.dumps([], ensure_ascii=False)

    @Slot(str, result=str)
    def getScenarioDetailJson(self, identifier: str) -> str:
        """获取特定场景的完整对话流（支持 ID 或 标题 查找）"""
        try:
            if not identifier:
                identifier = list(US_TRAVEL_DIALOGS.keys())[0]

            # 1. 尝试按 key 查找
            if identifier in US_TRAVEL_DIALOGS:
                return json.dumps(US_TRAVEL_DIALOGS[identifier], ensure_ascii=False)

            # 2. 尝试按 title 查找
            for k, data in US_TRAVEL_DIALOGS.items():
                if data.get("title") == identifier or data.get("title_en") == identifier:
                    return json.dumps(data, ensure_ascii=False)

            # 3. 基础对话字典查找
            from dialogs_data import get_dialog
            base_detail = get_dialog(identifier)
            if base_detail:
                return json.dumps(base_detail, ensure_ascii=False)

            # 4. 兜底返回第一个
            first_key = list(US_TRAVEL_DIALOGS.keys())[0]
            return json.dumps(US_TRAVEL_DIALOGS[first_key], ensure_ascii=False)
        except Exception as e:
            print(f"Error in getScenarioDetailJson: {e}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @Slot(str, result=str)
    def lookupWordJson(self, word: str) -> str:
        """离线词典精准查询"""
        try:
            result = self.dict_svc.lookup(word)
            if result:
                return json.dumps(result, ensure_ascii=False)
            return json.dumps({"word": word, "translation": "未找到相关词条", "cefr_level": "None"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"word": word, "translation": str(e), "cefr_level": "None"}, ensure_ascii=False)

    @Slot(str, str, int, result=str)
    def recordReviewJson(self, word: str, rating: str, study_minutes: int = 2) -> str:
        """记录 FSRS 单词复习"""
        try:
            res = self.study_svc.record_review(word, rating, study_minutes)
            self.progressUpdated.emit()
            return json.dumps(res, ensure_ascii=False)
        except Exception:
            return json.dumps({"word": word, "status": "review"}, ensure_ascii=False)

    @Slot(result=str)
    def getRandomVocabCardJson(self) -> str:
        """获取随机背词卡片"""
        try:
            words = self.dict_svc.get_random_words(1)
            if words:
                w = words[0]
                return json.dumps({
                    "word": w.get("word", "itinerary"),
                    "phonetic": w.get("phonetic", "/aɪˈtɪnəreri/"),
                    "translation": w.get("translation", "n. 旅行日程；行程单"),
                    "pos": w.get("pos", "n."),
                    "definition": w.get("definition", "a planned route or journey."),
                    "example": "Here is your itinerary for the business trip.",
                    "cefr_level": w.get("cefr_level", "A1")
                }, ensure_ascii=False)
        except Exception:
            pass
        return json.dumps({
            "word": "itinerary",
            "phonetic": "/aɪˈtɪnəreri/",
            "translation": "n. 旅行日程；行程单",
            "pos": "n.",
            "definition": "a planned route or journey.",
            "example": "Here is your business trip itinerary for Chicago.",
            "cefr_level": "A1"
        }, ensure_ascii=False)

    @Slot(str, result=str)
    def getGrammarPointsJson(self, level: str = "A1") -> str:
        """获取指定 CEFR 等级的语法知识点列表"""
        try:
            points = self.grammar_svc.get_points_by_level(level)
            return json.dumps(points, ensure_ascii=False)
        except Exception:
            return json.dumps([], ensure_ascii=False)

    @Slot(str)
    def speakText(self, text: str) -> None:
        """使用本地 SAPI5 TTS 朗读英文文本"""
        if text:
            self.tts.speak(text)
