# -*- coding: utf-8 -*-
"""
基本导入测试用例
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """测试基本导入"""
    # 测试核心模块导入
    try:
        from src.core.version import VERSION
        from src.core.spec_manager import SpecManager
        from src.gui.spec_sync_dialog import SpecSyncDialog
        from src.ui.widgets.spec_center import SpecCenterWidget
        from src.ui.main_window import MainWindow
        
        # 验证导入成功
        assert VERSION is not None
        assert SpecManager is not None
        assert SpecSyncDialog is not None
        assert SpecCenterWidget is not None
        assert MainWindow is not None
        
        print("✅ 所有模块导入成功")
    except ImportError as e:
        pytest.fail(f"导入失败: {e}")


def test_spec_manager_initialization():
    """测试规范管理器初始化"""
    try:
        from src.core.spec_manager import SpecManager
        manager = SpecManager()
        assert manager is not None
        print("✅ 规范管理器初始化成功")
    except Exception as e:
        pytest.fail(f"规范管理器初始化失败: {e}")


def test_version_info():
    """测试版本信息"""
    try:
        from src.core.version import VERSION, VERSION_INFO
        assert isinstance(VERSION, str)
        assert isinstance(VERSION_INFO, dict)
        assert 'major' in VERSION_INFO
        assert 'minor' in VERSION_INFO
        assert 'patch' in VERSION_INFO
        print(f"✅ 版本信息检查成功: {VERSION}")
    except Exception as e:
        pytest.fail(f"版本信息检查失败: {e}")


if __name__ == "__main__":
    test_imports()
    test_spec_manager_initialization()
    test_version_info()
    print("\n所有测试通过！")
