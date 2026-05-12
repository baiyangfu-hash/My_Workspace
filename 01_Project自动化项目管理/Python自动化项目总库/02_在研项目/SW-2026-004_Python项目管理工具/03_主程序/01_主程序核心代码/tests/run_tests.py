# -*- coding: utf-8 -*-
"""
简化版全量自动化测试脚本
"""
import pytest
import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests():
    """运行所有测试用例"""
    print("=" * 60)
    print("Python项目管理工具 - 全量自动化测试")
    print("=" * 60)
    print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n正在运行测试用例...\n")
    
    # 测试文件列表
    test_files = [
        "test_basic_imports.py"
    ]
    
    # 运行测试
    start_time = time.time()
    result = pytest.main(test_files + ["-v", "--tb=short"])
    end_time = time.time()
    
    print("\n" + "=" * 60)
    print(f"测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试总耗时: {end_time - start_time:.2f} 秒")
    print("=" * 60)
    
    if result == 0:
        print("✅ 所有测试用例通过！")
    else:
        print("❌ 部分测试用例失败！")
    
    return result


if __name__ == "__main__":
    result = run_all_tests()
    sys.exit(result)
