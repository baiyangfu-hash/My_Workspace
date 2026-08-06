"""
服务层包 - 业务逻辑与数据访问封装
"""
from .course_service import CourseService
from .database_manager import DatabaseManager, get_db
from .dictionary_service import DictionaryService
from .grammar_service import GrammarService
from .study_service import StudyService

__all__ = [
    'DatabaseManager',
    'get_db',
    'StudyService',
    'DictionaryService',
    'GrammarService',
    'CourseService'
]
