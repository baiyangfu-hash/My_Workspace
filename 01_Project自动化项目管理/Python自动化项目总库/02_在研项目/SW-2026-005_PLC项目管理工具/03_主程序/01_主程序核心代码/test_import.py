#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简单测试脚本 - 诊断导入问题"""
import sys
import os

print(f"Python版本: {sys.version}")
print(f"当前目录: {os.getcwd()}")
print(f"Python路径: {sys.path[:5]}")

# 添加src路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)
print(f"\n添加的src路径: {src_path}")
print(f"src路径存在: {os.path.exists(src_path)}")

# 测试基础模块
print("\n=== 测试基础导入 ===")
try:
    import logging
    print("✅ logging 导入成功")
except Exception as e:
    print(f"❌ logging 导入失败: {e}")

try:
    from pathlib import Path
    print("✅ pathlib 导入成功")
except Exception as e:
    print(f"❌ pathlib 导入失败: {e}")

# 测试自定义模块
print("\n=== 测试自定义模块 ===")
try:
    from core.config import ConfigLoader
    print("✅ ConfigLoader 导入成功")
except Exception as e:
    print(f"❌ ConfigLoader 导入失败: {e}")

try:
    from utils.logger import setup_logger
    print("✅ setup_logger 导入成功")
except Exception as e:
    print(f"❌ setup_logger 导入失败: {e}")

try:
    logger = setup_logger(__name__)
    print(f"✅ Logger 创建成功: {logger.name}")
except Exception as e:
    print(f"❌ Logger 创建失败: {e}")

try:
    from core.app import Application
    print("✅ Application 导入成功")
except Exception as e:
    print(f"❌ Application 导入失败: {e}")

print("\n=== 测试完成 ===")
