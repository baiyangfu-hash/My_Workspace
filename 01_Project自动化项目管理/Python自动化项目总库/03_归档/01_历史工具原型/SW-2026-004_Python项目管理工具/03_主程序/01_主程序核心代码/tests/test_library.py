# -*- coding: utf-8 -*-
"""
总库管理功能测试
"""
import unittest
import tempfile
import os
from pathlib import Path

from src.services.library_service import LibraryService
from src.services.project_service import ProjectService
from src.services.library_change_service import LibraryChangeService
from src.services.library_dashboard_service import LibraryDashboardService
from src.services.library_report_service import LibraryReportService
from src.core.constants import BusinessLine

class TestLibraryService(unittest.TestCase):
    """总库服务测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时目录作为总库根路径
        self.temp_dir = tempfile.mkdtemp()
        self.library_id = None
        self.project_id = None
    
    def tearDown(self):
        """清理测试环境"""
        # 清理临时目录
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # 删除创建的总库
        if self.library_id:
            LibraryService.delete_library(self.library_id, hard_delete=True)
        
        # 删除创建的项目
        if self.project_id:
            ProjectService.delete_project(self.project_id, hard_delete=True, delete_local_files=True)
    
    def test_create_library(self):
        """测试创建总库"""
        library, error = LibraryService.create_library(
            name="测试总库",
            root_path=self.temp_dir,
            description="用于测试的总库"
        )
        
        self.assertIsNone(error)
        self.assertIsNotNone(library)
        self.assertEqual(library.name, "测试总库")
        self.assertEqual(library.description, "用于测试的总库")
        self.assertEqual(library.root_path, self.temp_dir)
        
        self.library_id = library.library_id
    
    def test_get_library(self):
        """测试获取总库"""
        # 先创建总库
        library, error = LibraryService.create_library(
            name="测试总库",
            root_path=self.temp_dir
        )
        self.assertIsNone(error)
        self.library_id = library.library_id
        
        # 获取总库
        retrieved_library = LibraryService.get_library(library.library_id)
        self.assertIsNotNone(retrieved_library)
        self.assertEqual(retrieved_library.library_id, library.library_id)
        self.assertEqual(retrieved_library.name, library.name)
    
    def test_update_library(self):
        """测试更新总库"""
        # 先创建总库
        library, error = LibraryService.create_library(
            name="测试总库",
            root_path=self.temp_dir
        )
        self.assertIsNone(error)
        self.library_id = library.library_id
        
        # 更新总库
        updated_library, update_error = LibraryService.update_library(
            library.library_id,
            {"name": "更新后的总库", "description": "更新后的描述"}
        )
        
        self.assertIsNone(update_error)
        self.assertIsNotNone(updated_library)
        self.assertEqual(updated_library.name, "更新后的总库")
        self.assertEqual(updated_library.description, "更新后的描述")
    
    def test_delete_library(self):
        """测试删除总库"""
        # 先创建总库
        library, error = LibraryService.create_library(
            name="测试总库",
            root_path=self.temp_dir
        )
        self.assertIsNone(error)
        self.library_id = library.library_id
        
        # 删除总库
        success, delete_error = LibraryService.delete_library(library.library_id)
        self.assertIsNone(delete_error)
        self.assertTrue(success)
        
        # 验证总库已删除
        deleted_library = LibraryService.get_library(library.library_id)
        self.assertIsNone(deleted_library)
    
    def test_add_project_to_library(self):
        """测试添加项目到总库"""
        # 先创建总库
        library, error = LibraryService.create_library(
            name="测试总库",
            root_path=self.temp_dir
        )
        self.assertIsNone(error)
        self.library_id = library.library_id
        
        # 创建测试项目
        project, project_error = ProjectService.create_project(
            business_line=BusinessLine.SW.value,
            name="测试项目",
            template_id="TPL-DEFAULT-001",
            custom_path=os.path.join(self.temp_dir, "test_project")
        )
        self.assertIsNone(project_error)
        self.project_id = project.project_id
        
        # 添加项目到总库
        add_success, add_error = LibraryService.add_project_to_library(
            library_id=library.library_id,
            project_id=project.project_id
        )
        
        self.assertIsNone(add_error)
        self.assertTrue(add_success)
        
        # 验证项目已添加到总库
        projects, total = LibraryService.list_library_projects(library.library_id)
        self.assertEqual(total, 1)
        self.assertEqual(projects[0].project_id, project.project_id)
    
    def test_remove_project_from_library(self):
        """测试从总库中移除项目"""
        # 先创建总库和项目
        library, error = LibraryService.create_library(
            name="测试总库",
            root_path=self.temp_dir
        )
        self.assertIsNone(error)
        self.library_id = library.library_id
        
        project, project_error = ProjectService.create_project(
            business_line=BusinessLine.SW.value,
            name="测试项目",
            template_id="TPL-DEFAULT-001",
            custom_path=os.path.join(self.temp_dir, "test_project")
        )
        self.assertIsNone(project_error)
        self.project_id = project.project_id
        
        # 添加项目到总库
        add_success, add_error = LibraryService.add_project_to_library(
            library_id=library.library_id,
            project_id=project.project_id
        )
        self.assertIsNone(add_error)
        self.assertTrue(add_success)
        
        # 从总库中移除项目
        remove_success, remove_error = LibraryService.remove_project_from_library(
            library_id=library.library_id,
            project_id=project.project_id
        )
        
        self.assertIsNone(remove_error)
        self.assertTrue(remove_success)
        
        # 验证项目已从总库中移除
        projects, total = LibraryService.list_library_projects(library.library_id)
        self.assertEqual(total, 0)
    
    def test_create_category(self):
        """测试创建分类"""
        # 先创建总库
        library, error = LibraryService.create_library(
            name="测试总库",
            root_path=self.temp_dir
        )
        self.assertIsNone(error)
        self.library_id = library.library_id
        
        # 创建分类
        category, category_error = LibraryService.create_category(
            library_id=library.library_id,
            name="测试分类",
            description="用于测试的分类"
        )
        
        self.assertIsNone(category_error)
        self.assertIsNotNone(category)
        self.assertEqual(category.name, "测试分类")
        self.assertEqual(category.description, "用于测试的分类")
        
        # 验证分类已创建
        categories = LibraryService.list_categories(library.library_id)
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].category_id, category.category_id)

class TestLibraryChangeService(unittest.TestCase):
    """总库变更服务测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时目录作为总库根路径
        self.temp_dir = tempfile.mkdtemp()
        self.library_id = None
        self.change_id = None
    
    def tearDown(self):
        """清理测试环境"""
        # 清理临时目录
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # 删除创建的总库
        if self.library_id:
            LibraryService.delete_library(self.library_id, hard_delete=True)
    
    def test_create_change(self):
        """测试创建总库变更"""
        # 先创建总库
        library, error = LibraryService.create_library(
            name="测试总库",
            root_path=self.temp_dir
        )
        self.assertIsNone(error)
        self.library_id = library.library_id
        
        # 创建变更
        change, change_error = LibraryChangeService.create_change(
            library_id=library.library_id,
            change_type="ADD",
            title="测试变更",
            description="用于测试的变更",
            requested_by="测试用户"
        )
        
        self.assertIsNone(change_error)
        self.assertIsNotNone(change)
        self.assertEqual(change.title, "测试变更")
        self.assertEqual(change.description, "用于测试的变更")
        self.assertEqual(change.requested_by, "测试用户")
        
        self.change_id = change.change_id
    
    def test_approve_change(self):
        """测试审批总库变更"""
        # 先创建总库和变更
        library, error = LibraryService.create_library(
            name="测试总库",
            root_path=self.temp_dir
        )
        self.assertIsNone(error)
        self.library_id = library.library_id
        
        change, change_error = LibraryChangeService.create_change(
            library_id=library.library_id,
            change_type="ADD",
            title="测试变更"
        )
        self.assertIsNone(change_error)
        self.change_id = change.change_id
        
        # 审批变更
        approve_success, approve_error = LibraryChangeService.approve_change(
            change.change_id,
            approved_by="审批人"
        )
        
        self.assertIsNone(approve_error)
        self.assertTrue(approve_success)
        
        # 验证变更状态已更新
        updated_change = LibraryChangeService.get_change(change.change_id)
        self.assertEqual(updated_change.status.value, "APPROVED")
        self.assertEqual(updated_change.approved_by, "审批人")
    
    def test_reject_change(self):
        """测试拒绝总库变更"""
        # 先创建总库和变更
        library, error = LibraryService.create_library(
            name="测试总库",
            root_path=self.temp_dir
        )
        self.assertIsNone(error)
        self.library_id = library.library_id
        
        change, change_error = LibraryChangeService.create_change(
            library_id=library.library_id,
            change_type="ADD",
            title="测试变更"
        )
        self.assertIsNone(change_error)
        self.change_id = change.change_id
        
        # 拒绝变更
        reject_success, reject_error = LibraryChangeService.reject_change(
            change.change_id,
            rejected_by="审批人",
            comments="拒绝原因"
        )
        
        self.assertIsNone(reject_error)
        self.assertTrue(reject_success)
        
        # 验证变更状态已更新
        updated_change = LibraryChangeService.get_change(change.change_id)
        self.assertEqual(updated_change.status.value, "REJECTED")
        self.assertEqual(updated_change.approved_by, "审批人")

class TestLibraryDashboardService(unittest.TestCase):
    """总库仪表盘服务测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时目录作为总库根路径
        self.temp_dir = tempfile.mkdtemp()
        self.library_id = None
    
    def tearDown(self):
        """清理测试环境"""
        # 清理临时目录
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # 删除创建的总库
        if self.library_id:
            LibraryService.delete_library(self.library_id, hard_delete=True)
    
    def test_get_library_overview(self):
        """测试获取总库概览"""
        # 先创建总库
        library, error = LibraryService.create_library(
            name="测试总库",
            root_path=self.temp_dir
        )
        self.assertIsNone(error)
        self.library_id = library.library_id
        
        # 获取总库概览
        overview = LibraryDashboardService.get_library_overview(library.library_id)
        self.assertIsNotNone(overview)
        self.assertEqual(overview['library']['name'], "测试总库")
        self.assertEqual(overview['library']['id'], library.library_id)
    
    def test_get_library_health(self):
        """测试获取总库健康状态"""
        # 先创建总库
        library, error = LibraryService.create_library(
            name="测试总库",
            root_path=self.temp_dir
        )
        self.assertIsNone(error)
        self.library_id = library.library_id
        
        # 获取总库健康状态
        health = LibraryDashboardService.get_library_health(library.library_id)
        self.assertIsNotNone(health)
        self.assertIn('score', health)
        self.assertIn('status', health)
        self.assertIn('metrics', health)

class TestLibraryReportService(unittest.TestCase):
    """总库报表服务测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时目录作为总库根路径
        self.temp_dir = tempfile.mkdtemp()
        self.library_id = None
    
    def tearDown(self):
        """清理测试环境"""
        # 清理临时目录
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # 删除创建的总库
        if self.library_id:
            LibraryService.delete_library(self.library_id, hard_delete=True)
    
    def test_generate_library_overview_report(self):
        """测试生成总库概览报表"""
        # 先创建总库
        library, error = LibraryService.create_library(
            name="测试总库",
            root_path=self.temp_dir
        )
        self.assertIsNone(error)
        self.library_id = library.library_id
        
        # 生成概览报表
        report_path, report_error = LibraryReportService.generate_library_overview_report(library.library_id)
        self.assertIsNone(report_error)
        self.assertTrue(os.path.exists(report_path))
        
        # 验证报表内容
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('总库概览报表', content)
        self.assertIn('测试总库', content)
    
    def test_generate_library_statistics_report(self):
        """测试生成总库统计报表"""
        # 先创建总库
        library, error = LibraryService.create_library(
            name="测试总库",
            root_path=self.temp_dir
        )
        self.assertIsNone(error)
        self.library_id = library.library_id
        
        # 生成统计报表
        report_path, report_error = LibraryReportService.generate_library_statistics_report(library.library_id)
        self.assertIsNone(report_error)
        self.assertTrue(os.path.exists(report_path))
        
        # 验证报表内容
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('总库统计报表', content)
        self.assertIn('测试总库', content)

if __name__ == '__main__':
    unittest.main()
