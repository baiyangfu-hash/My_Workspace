# -*- coding: utf-8 -*-
"""
全量自动化测试脚本
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

def run_specific_test(test_file):
    """运行指定的测试文件"""
    print("=" * 60)
    print(f"运行测试: {test_file}")
    print("=" * 60)
    
    start_time = time.time()
    result = pytest.main([test_file, "-v", "--tb=short"])
    end_time = time.time()
    
    print("\n" + "=" * 60)
    print(f"测试耗时: {end_time - start_time:.2f} 秒")
    print("=" * 60)
    
    if result == 0:
        print("✅ 测试通过！")
    else:
        print("❌ 测试失败！")
    
    return result


def show_menu():
    """显示测试菜单"""
    print("\n" + "=" * 60)
    print("Python项目管理工具 - 测试菜单")
    print("=" * 60)
    print("1. 运行所有测试")
    print("2. 运行基本导入测试")
    print("5. 退出")
    print("=" * 60)


if __name__ == "__main__":
    while True:
        show_menu()
        choice = input("请选择测试选项 (1-5): ")
        
        if choice == "1":
            run_all_tests()
        elif choice == "2":
            run_specific_test("test_basic_imports.py")
        elif choice == "5":
            print("退出测试...")
            break
        else:
            print("无效选项，请重新选择！")
        
        input("\n按回车键继续...")
