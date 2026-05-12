# -*- coding: utf-8 -*-
"""
API客户端测试脚本
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.api.client import APIClient, CLIClient, AIAccessManager


def test_cli_client():
    """测试CLI客户端"""
    print("=" * 60)
    print("测试CLI客户端")
    print("=" * 60)
    
    cli_client = CLIClient(main_script="main.py")
    
    # 测试版本信息
    print("\n1. 测试版本信息:")
    result = cli_client.version()
    print(result)
    
    # 测试工具信息
    print("\n2. 测试工具信息:")
    result = cli_client.info()
    print(result)
    
    # 测试规范信息
    print("\n3. 测试规范信息:")
    result = cli_client.spec_info()
    print(result)
    
    # 测试检查规范更新
    print("\n4. 测试检查规范更新:")
    result = cli_client.check_spec(auto_sync=False)
    print(result)
    
    print("\nCLI客户端测试完成！")


def test_ai_access_manager():
    """测试AI访问管理器"""
    print("\n" + "=" * 60)
    print("测试AI访问管理器")
    print("=" * 60)
    
    ai_manager = AIAccessManager()
    
    # 测试获取工具信息
    print("\n1. 测试获取工具信息:")
    result = ai_manager.get_tool_info()
    print(result)
    
    # 测试获取版本信息
    print("\n2. 测试获取版本信息:")
    result = ai_manager.get_version()
    print(result)
    
    # 测试获取规范信息
    print("\n3. 测试获取规范信息:")
    result = ai_manager.get_spec_info()
    print(result)
    
    # 测试检查规范更新
    print("\n4. 测试检查规范更新:")
    result = ai_manager.check_spec_updates(auto_sync=False)
    print(result)
    
    print("\nAI访问管理器测试完成！")


def main():
    """主测试函数"""
    print("Python项目管理工具 - API客户端测试")
    print("=" * 60)
    print(f"测试时间: {os.popen('date /t').read().strip()}")
    print(f"Python版本: {sys.version}")
    print("=" * 60)
    
    # 测试CLI客户端
    test_cli_client()
    
    # 测试AI访问管理器
    test_ai_access_manager()
    
    print("\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
