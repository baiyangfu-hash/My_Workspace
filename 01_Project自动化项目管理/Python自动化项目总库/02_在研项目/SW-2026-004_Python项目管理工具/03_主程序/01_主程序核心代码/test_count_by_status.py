#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试总库管理模块的项目数统计功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dao.project_dao import ProjectDAO
from src.models.project import ProjectStatus

def test_count_by_status():
    """测试 count_by_status 方法"""
    print("=== 测试总库管理模块项目数统计 ===")
    
    # 测试统计所有项目
    total_count = ProjectDAO.count_by_status(None)
    print(f"所有项目数: {total_count}")
    
    # 测试按状态统计
    for status in ProjectStatus:
        count = ProjectDAO.count_by_status(status)
        print(f"{status.value} 状态项目数: {count}")
    
    print("=== 测试完成 ===")

if __name__ == "__main__":
    test_count_by_status()