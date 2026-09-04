# -*- coding: utf-8 -*-
"""
测试规范同步功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.spec_manager import SpecManager
from src.gui.spec_sync_dialog import show_spec_sync_dialog


def test_spec_manager():
    """测试规范管理器"""
    print("=== 测试规范管理器 ===")
    
    try:
        spec_manager = SpecManager()
        
        # 测试获取规范列表
        specs = spec_manager.get_specs_list()
        print(f"规范数量: {len(specs)}")
        for spec in specs:
            print(f"- {spec['name']}: {spec['current_version']} -> {spec['latest_version']} ({spec['status']})")
        
        # 测试检查更新
        print("\n=== 检查更新 ===")
        results = spec_manager.check_updates()
        print(f"检查时间: {results.get('检查时间', 'N/A')}")
        print(f"可更新规范: {len(results.get('可更新规范', []))}")
        print(f"已最新规范: {len(results.get('已最新规范', []))}")
        
        # 测试获取更新摘要
        summary = spec_manager.get_update_summary()
        print("\n=== 更新摘要 ===")
        print(summary)
        
        print("\n=== 测试完成 ===")
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui():
    """测试GUI功能"""
    print("\n=== 测试GUI功能 ===")
    print("将打开规范同步对话框...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        show_spec_sync_dialog()
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"PyQt5 未安装: {e}")
        return False
    except Exception as e:
        print(f"GUI测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("开始测试规范同步功能...\n")
    
    # 测试规范管理器
    test_spec_manager()
    
    # 测试GUI（可选）
    # test_gui()
