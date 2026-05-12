# -*- coding: utf-8 -*-
"""
测试导入和基本功能
"""
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("测试导入...")

try:
    from src.services.change_service import ChangeService
    print("✓ 成功导入 ChangeService")
except Exception as e:
    print(f"✗ 导入 ChangeService 失败: {e}")

try:
    from src.models.change import Change
    print("✓ 成功导入 Change 模型")
except Exception as e:
    print(f"✗ 导入 Change 模型失败: {e}")

try:
    from src.core.constants import ChangeStatus
    print("✓ 成功导入 ChangeStatus")
except Exception as e:
    print(f"✗ 导入 ChangeStatus 失败: {e}")

print("\n测试基本功能...")

try:
    # 测试变更状态枚举
    print(f"变更状态: {[status.name for status in ChangeStatus]}")
    print("✓ 成功访问 ChangeStatus")
except Exception as e:
    print(f"✗ 测试 ChangeStatus 失败: {e}")

print("\n测试完成")
