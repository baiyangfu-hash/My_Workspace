# -*- coding: utf-8 -*-
"""
简单测试脚本
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

# 测试项目管理服务
print("测试项目管理服务...")
try:
    from src.services.project_service import ProjectService
    print("项目管理服务加载成功")
    
    # 测试项目列表
    projects, total = ProjectService.list_projects(size=10)
    print(f"项目数量: {total}")
    
    # 测试项目统计
    stats = ProjectService.get_statistics()
    print(f"项目统计: {stats}")
    
except Exception as e:
    print(f"项目管理服务测试失败: {e}")

# 测试统计服务
print("\n测试统计服务...")
try:
    from src.services.statistics_service import StatisticsService
    print("统计服务加载成功")
    
    # 测试系统概览
    overview = StatisticsService.get_overview()
    print(f"系统概览: {overview}")
    
except Exception as e:
    print(f"统计服务测试失败: {e}")

# 测试总库管理服务
print("\n测试总库管理服务...")
try:
    from src.services.library_service import LibraryService
    print("总库管理服务加载成功")
    
    # 测试总库列表
    libraries = LibraryService.list_libraries()
    print(f"总库数量: {len(libraries)}")
    
except Exception as e:
    print(f"总库管理服务测试失败: {e}")

print("\n测试完成")
