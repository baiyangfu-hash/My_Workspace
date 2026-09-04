# -*- coding: utf-8 -*-
"""
迁移副本：运行多个 unittest 测试套件（延迟导入实际测试用例）
改造要点：将导入与执行放入 `main()`，以便导入模块时不会加载重度依赖。
"""
import sys
import os
import unittest


def main():
    # 将原来在文件顶部插入 sys.path 的逻辑移到这里
    base = os.path.dirname(__file__)
    sys.path.insert(0, os.path.join(base, 'src'))

    # 延迟导入测试用例，避免在 import 时触发
    try:
        from tests.test_change_impact import TestChangeImpactAnalysis
        from tests.test_change_approval import TestChangeApprovalProcess
        from tests.test_change_document import TestChangeDocumentManagement
        from tests.test_change_statistics import TestChangeStatistics
        from tests.test_change_notification import TestChangeNotification
        from tests.test_change_performance import TestChangePerformance
    except Exception as e:
        print(f"无法导入测试用例: {e}")
        return False

    # 运行所有测试
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestChangeImpactAnalysis)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestChangeApprovalProcess)
    suite3 = unittest.TestLoader().loadTestsFromTestCase(TestChangeDocumentManagement)
    suite4 = unittest.TestLoader().loadTestsFromTestCase(TestChangeStatistics)
    suite5 = unittest.TestLoader().loadTestsFromTestCase(TestChangeNotification)
    suite6 = unittest.TestLoader().loadTestsFromTestCase(TestChangePerformance)

    result1 = unittest.TextTestRunner(verbosity=2).run(suite1)
    result2 = unittest.TextTestRunner(verbosity=2).run(suite2)
    result3 = unittest.TextTestRunner(verbosity=2).run(suite3)
    result4 = unittest.TextTestRunner(verbosity=2).run(suite4)
    result5 = unittest.TextTestRunner(verbosity=2).run(suite5)
    result6 = unittest.TextTestRunner(verbosity=2).run(suite6)

    all_passed = all(r.wasSuccessful() for r in [result1, result2, result3, result4, result5, result6])
    return all_passed


if __name__ == '__main__':
    ok = main()
    sys.exit(0 if ok else 1)
