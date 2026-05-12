# -*- coding: utf-8 -*-
"""
测试测试环境
"""
import unittest

class TestTestEnvironment(unittest.TestCase):
    """测试测试环境"""
    
    def test_basic(self):
        """测试基本功能"""
        print("测试环境正常")
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main(verbosity=2)
