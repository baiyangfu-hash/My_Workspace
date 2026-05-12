# -*- coding: utf-8 -*-
"""
插件市场功能测试
"""
import unittest
import tempfile
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.core.plugin_metadata import PluginMetadata, PluginMetadataSchema, PluginPermission
from src.services.plugin_market_service import PluginMarketService, RemotePlugin


class TestPluginMetadata(unittest.TestCase):
    """插件元数据测试"""
    
    def test_create_metadata(self):
        """测试创建元数据"""
        metadata = PluginMetadata(
            plugin_id="test_plugin",
            plugin_name="测试插件",
            plugin_version="1.0.0",
            plugin_author="Test Author",
            plugin_description="这是一个测试插件"
        )
        
        self.assertEqual(metadata.plugin_id, "test_plugin")
        self.assertEqual(metadata.plugin_name, "测试插件")
        self.assertEqual(metadata.plugin_version, "1.0.0")
    
    def test_metadata_to_dict(self):
        """测试元数据转字典"""
        metadata = PluginMetadata(
            plugin_id="test_plugin",
            plugin_name="测试插件",
            plugin_version="1.0.0",
            plugin_author="Test Author",
            plugin_description="测试描述",
            tags=["工具", "测试"]
        )
        
        data = metadata.to_dict()
        
        self.assertEqual(data['plugin_id'], "test_plugin")
        self.assertEqual(data['tags'], ["工具", "测试"])
    
    def test_metadata_from_dict(self):
        """测试从字典创建元数据"""
        data = {
            'plugin_id': 'test_plugin',
            'plugin_name': '测试插件',
            'plugin_version': '1.0.0',
            'plugin_author': 'Test Author',
            'plugin_description': '测试描述',
            'tags': ['工具']
        }
        
        metadata = PluginMetadata.from_dict(data)
        
        self.assertEqual(metadata.plugin_id, "test_plugin")
        self.assertEqual(metadata.tags, ['工具'])
    
    def test_validate_metadata(self):
        """测试元数据验证"""
        valid_metadata = PluginMetadata(
            plugin_id="test_plugin",
            plugin_name="测试插件",
            plugin_version="1.0.0",
            plugin_author="Test Author",
            plugin_description="测试描述"
        )
        
        is_valid, errors = valid_metadata.validate()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_invalid_id(self):
        """测试无效插件ID验证"""
        invalid_metadata = PluginMetadata(
            plugin_id="123_invalid",
            plugin_name="测试插件",
            plugin_version="1.0.0",
            plugin_author="Test Author",
            plugin_description="测试描述"
        )
        
        is_valid, errors = invalid_metadata.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any("plugin_id" in e for e in errors))
    
    def test_validate_invalid_version(self):
        """测试无效版本号验证"""
        invalid_metadata = PluginMetadata(
            plugin_id="test_plugin",
            plugin_name="测试插件",
            plugin_version="1.0",
            plugin_author="Test Author",
            plugin_description="测试描述"
        )
        
        is_valid, errors = invalid_metadata.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any("version" in e.lower() for e in errors))
    
    def test_validate_empty_required_fields(self):
        """测试必填字段为空"""
        invalid_metadata = PluginMetadata(
            plugin_id="",
            plugin_name="",
            plugin_version="",
            plugin_author="",
            plugin_description=""
        )
        
        is_valid, errors = invalid_metadata.validate()
        self.assertFalse(is_valid)
        self.assertTrue(len(errors) >= 5)
    
    def test_validate_invalid_permission(self):
        """测试无效权限"""
        metadata = PluginMetadata(
            plugin_id="test_plugin",
            plugin_name="测试插件",
            plugin_version="1.0.0",
            plugin_author="Test Author",
            plugin_description="测试描述",
            permissions=["invalid_permission"]
        )
        
        is_valid, errors = metadata.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any("权限" in e for e in errors))
    
    def test_metadata_to_json(self):
        """测试元数据转JSON"""
        metadata = PluginMetadata(
            plugin_id="test_plugin",
            plugin_name="测试插件",
            plugin_version="1.0.0",
            plugin_author="Test Author",
            plugin_description="测试描述"
        )
        
        json_str = metadata.to_json()
        
        self.assertIn('"plugin_id": "test_plugin"', json_str)
        self.assertIn('"plugin_name": "测试插件"', json_str)
    
    def test_metadata_from_json_file(self):
        """测试从JSON文件加载元数据"""
        json_content = '''{
            "plugin_id": "test_plugin",
            "plugin_name": "测试插件",
            "plugin_version": "1.0.0",
            "plugin_author": "Test Author",
            "plugin_description": "测试描述"
        }'''
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json', delete=False) as f:
            f.write(json_content)
            temp_path = f.name
        
        try:
            metadata = PluginMetadata.from_json_file(temp_path)
            self.assertEqual(metadata.plugin_id, "test_plugin")
        finally:
            os.unlink(temp_path)


class TestPluginMetadataSchema(unittest.TestCase):
    """插件元数据Schema测试"""
    
    def test_get_schema(self):
        """测试获取Schema"""
        schema = PluginMetadataSchema.get_schema()
        
        self.assertIn('required', schema)
        self.assertIn('plugin_id', schema['required'])
        self.assertIn('properties', schema)
    
    def test_validate_valid_data(self):
        """测试验证有效数据"""
        data = {
            'plugin_id': 'test_plugin',
            'plugin_name': '测试插件',
            'plugin_version': '1.0.0',
            'plugin_author': 'Test Author',
            'plugin_description': '测试描述'
        }
        
        is_valid, errors = PluginMetadataSchema.validate(data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)


class TestPluginPermission(unittest.TestCase):
    """插件权限枚举测试"""
    
    def test_permission_values(self):
        """测试权限值"""
        self.assertEqual(PluginPermission.FILE_READ.value, "file_read")
        self.assertEqual(PluginPermission.FILE_WRITE.value, "file_write")
        self.assertEqual(PluginPermission.NETWORK_ACCESS.value, "network_access")
        self.assertEqual(PluginPermission.PROJECT_ACCESS.value, "project_access")
    
    def test_all_permissions_defined(self):
        """测试所有权限已定义"""
        permissions = [p.value for p in PluginPermission]
        self.assertIn("file_read", permissions)
        self.assertIn("file_write", permissions)
        self.assertIn("network_access", permissions)


class TestRemotePlugin(unittest.TestCase):
    """远程插件信息测试"""
    
    def test_create_remote_plugin(self):
        """测试创建远程插件"""
        plugin = RemotePlugin(
            plugin_id="test_plugin",
            name="测试插件",
            version="1.0.0",
            author="Test Author",
            description="测试描述",
            download_url="https://example.com/plugin.zip"
        )
        
        self.assertEqual(plugin.plugin_id, "test_plugin")
        self.assertEqual(plugin.installed, False)
        self.assertEqual(plugin.has_update, False)
    
    def test_remote_plugin_with_tags(self):
        """测试带标签的远程插件"""
        plugin = RemotePlugin(
            plugin_id="test_plugin",
            name="测试插件",
            version="1.0.0",
            author="Test Author",
            description="测试描述",
            download_url="",
            tags=["工具", "测试"]
        )
        
        self.assertEqual(plugin.tags, ["工具", "测试"])


class TestPluginMarketService(unittest.TestCase):
    """插件市场服务测试"""
    
    def setUp(self):
        self.service = PluginMarketService()
        self.demo_plugins = self.service._get_demo_plugins()
    
    def test_get_demo_plugins(self):
        """测试获取演示插件"""
        plugins = self.demo_plugins
        
        self.assertIsInstance(plugins, list)
        self.assertTrue(len(plugins) > 0)
        
        for plugin in plugins:
            self.assertIsInstance(plugin, RemotePlugin)
            self.assertIsNotNone(plugin.plugin_id)
            self.assertIsNotNone(plugin.name)
    
    def test_search_plugins(self):
        """测试搜索插件"""
        self.service._cache = self.demo_plugins
        
        results = self.service.search_plugins("Git")
        
        self.assertTrue(len(results) > 0)
        for plugin in results:
            self.assertTrue(
                "git" in plugin.name.lower() or
                "git" in plugin.description.lower() or
                any("git" in tag.lower() for tag in plugin.tags)
            )
    
    def test_get_plugin_detail(self):
        """测试获取插件详情"""
        self.service._cache = self.demo_plugins
        
        plugin = self.service.get_plugin_detail("code_check")
        
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.plugin_id, "code_check")
    
    def test_get_plugin_detail_not_found(self):
        """测试获取不存在的插件详情"""
        self.service._cache = self.demo_plugins
        
        plugin = self.service.get_plugin_detail("not_exist")
        
        self.assertIsNone(plugin)
    
    def test_compare_versions(self):
        """测试版本比较"""
        self.assertEqual(self.service._compare_versions("1.0.0", "1.0.0"), 0)
        self.assertEqual(self.service._compare_versions("1.1.0", "1.0.0"), 1)
        self.assertEqual(self.service._compare_versions("1.0.0", "1.1.0"), -1)
        self.assertEqual(self.service._compare_versions("2.0.0", "1.9.9"), 1)
        self.assertEqual(self.service._compare_versions("1.10.0", "1.9.0"), 1)
    
    def test_get_categories(self):
        """测试获取分类"""
        self.service._cache = self.demo_plugins
        
        categories = self.service.get_categories()
        
        self.assertIsInstance(categories, list)
        for cat in categories:
            self.assertIn('name', cat)
            self.assertIn('count', cat)
    
    def test_get_featured_plugins(self):
        """测试获取推荐插件"""
        self.service._cache = self.demo_plugins
        
        featured = self.service.get_featured_plugins(limit=3)
        
        self.assertEqual(len(featured), 3)
        for i in range(len(featured) - 1):
            self.assertGreaterEqual(featured[i].rating, featured[i+1].rating)
    
    def test_get_popular_plugins(self):
        """测试获取热门插件"""
        self.service._cache = self.demo_plugins
        
        popular = self.service.get_popular_plugins(limit=5)
        
        self.assertEqual(len(popular), 5)
        for i in range(len(popular) - 1):
            self.assertGreaterEqual(popular[i].download_count, popular[i+1].download_count)
    
    @patch('src.services.plugin_market_service.PluginDAO')
    def test_check_updates(self, mock_dao):
        """测试检查更新"""
        mock_dao.list.return_value = []
        self.service._cache = self.demo_plugins
        
        updates = self.service.check_updates()
        
        self.assertIsInstance(updates, list)


if __name__ == '__main__':
    unittest.main()
