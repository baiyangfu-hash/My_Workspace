# -*- coding: utf-8 -*-
"""
API服务测试脚本
"""
import sys
import os
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.api.client import AIAccessManager


def test_api_service():
    """测试API服务"""
    print("=" * 60)
    print("测试API服务")
    print("=" * 60)
    
    ai_manager = AIAccessManager()
    
    # 测试启动API服务
    print("\n1. 测试启动API服务:")
    start_result = ai_manager.start_api_service()
    print(start_result)
    
    # 等待服务启动
    time.sleep(2)
    
    # 测试API服务状态
    print("\n2. 测试API服务状态:")
    is_running = ai_manager.ensure_api_running()
    print(f"API服务运行状态: {is_running}")
    
    # 测试获取工具信息
    print("\n3. 测试获取工具信息:")
    tool_info = ai_manager.get_tool_info()
    print(tool_info)
    
    # 测试获取版本信息
    print("\n4. 测试获取版本信息:")
    version_info = ai_manager.get_version()
    print(version_info)
    
    # 测试获取规范信息
    print("\n5. 测试获取规范信息:")
    spec_info = ai_manager.get_spec_info()
    print(spec_info)
    
    # 测试检查规范更新
    print("\n6. 测试检查规范更新:")
    check_result = ai_manager.check_spec_updates(auto_sync=False)
    print(check_result)
    
    # 测试同步规范
    print("\n7. 测试同步规范:")
    sync_result = ai_manager.sync_specs()
    print(sync_result)
    
    # 测试停止API服务
    print("\n8. 测试停止API服务:")
    stop_result = ai_manager.stop_api_service()
    print(stop_result)
    
    # 测试API服务状态
    print("\n9. 测试API服务状态（停止后）:")
    is_running = ai_manager.ensure_api_running()
    print(f"API服务运行状态: {is_running}")
    
    print("\nAPI服务测试完成！")


def main():
    """主测试函数"""
    print("Python项目管理工具 - API服务测试")
    print("=" * 60)
    print(f"测试时间: {os.popen('date /t').read().strip()}")
    print(f"Python版本: {sys.version}")
    print("=" * 60)
    
    # 测试API服务
    test_api_service()
    
    print("\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
