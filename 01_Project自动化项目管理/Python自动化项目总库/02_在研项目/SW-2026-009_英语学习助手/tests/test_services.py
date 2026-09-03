"""
服务层单元测试 - 验证 StudyService, DictionaryService, GrammarService, CourseService, DatabaseManager
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services import (
    DatabaseManager, get_db,
    StudyService, DictionaryService, GrammarService, CourseService
)

class TestServiceLayer(unittest.TestCase):
    def setUp(self):
        self.db_manager = get_db()

    def test_database_manager(self):
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row['name'] for row in cursor.fetchall()]
            self.assertIn('user_words', tables)
            self.assertIn('study_records', tables)
            self.assertIn('daily_stats', tables)

    def test_dictionary_service(self):
        service = DictionaryService()
        res = service.lookup("apple")
        self.assertIsNotNone(res)
        self.assertIn('cefr_level', res)
        self.assertEqual(res['cefr_level'], 'A1')

        # 边界与入参清洗测试（空格修剪、空字符串、None、非字符串等）
        # 1. 验证前后空格输入清洗 lookup('  apple  ')
        res_spaces = service.lookup("  apple  ")
        self.assertIsNotNone(res_spaces)
        self.assertEqual(res_spaces['word'], 'apple')
        self.assertEqual(res_spaces['cefr_level'], 'A1')

        # 2. 验证空字符串与仅空格输入安全返回 None，杜绝异常
        self.assertIsNone(service.lookup(""))
        self.assertIsNone(service.lookup("   \t\n  "))
        self.assertIsNone(service.lookup(None))
        self.assertIsNone(service.lookup(12345))

        # 3. 验证 query_word 接口及参数清洗
        q_res = service.query_word("  apple  ")
        self.assertIsNotNone(q_res)
        self.assertEqual(q_res['word'], 'apple')
        self.assertIsNone(service.query_word(""))
        self.assertIsNone(service.query_word("   "))
        self.assertIsNone(service.query_word(None))

        # 4. 验证 search 前缀搜索清洗
        search_res = service.search("  app  ")
        self.assertIsInstance(search_res, list)
        self.assertEqual(service.search(""), [])
        self.assertEqual(service.search("   "), [])
        self.assertEqual(service.search(None), [])

        # 5. 验证静态辅助方法 sanitize_word
        self.assertEqual(DictionaryService.sanitize_word("  hello  "), "hello")
        self.assertEqual(DictionaryService.sanitize_word(""), "")
        self.assertEqual(DictionaryService.sanitize_word("   "), "")
        self.assertEqual(DictionaryService.sanitize_word(None), "")
        self.assertEqual(DictionaryService.sanitize_word(123), "")

        service.close()

    def test_study_service(self):
        import time
        test_word = f"service_test_word_{time.time_ns()}"
        service = StudyService(self.db_manager)
        word_record = service.get_or_create_word(test_word)
        self.assertEqual(word_record['word'], test_word)
        self.assertEqual(word_record['status'], 'new')

        res = service.record_review(test_word, "good", study_minutes=5)
        self.assertEqual(res['word'], test_word)
        self.assertEqual(res['status'], 'review')

        stats = service.get_daily_stats()
        self.assertGreaterEqual(stats['study_minutes'], 5)

    def test_grammar_service(self):
        service = GrammarService()
        points = service.get_points_by_level("A1")
        self.assertGreater(len(points), 0)

        practice = service.generate_practice(points[0])
        self.assertGreaterEqual(len(practice), 1)

    def test_course_service(self):
        service = CourseService(self.db_manager)
        progress = service.get_user_progress()
        self.assertIn('current_level', progress)

        plan = service.generate_daily_plan()
        self.assertIn('tasks', plan)
        self.assertIn('estimated_minutes', plan)

if __name__ == '__main__':
    unittest.main()
