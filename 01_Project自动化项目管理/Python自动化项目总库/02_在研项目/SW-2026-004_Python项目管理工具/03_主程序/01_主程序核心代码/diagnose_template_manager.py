#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断脚本 - 检查模板管理模块的问题

运行方式：
    cd d:\BaiduSyncdisk\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-004_Python项目管理工具\03_主程序\01_主程序核心代码
    python diagnose_template_manager.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.template_service import TemplateService
from src.dao.template_dao import TemplateDAO
from src.models.template import Template

def main():
    print("=" * 80)
    print("模板管理模块诊断报告")
    print("=" * 80)
    
    # 1. 检查 TemplateService.list_templates()
    print("\n1. 测试 TemplateService.list_templates():")
    try:
        templates = TemplateService.list_templates()
        print(f"   ✅ 成功获取 {len(templates)} 个模板")
        
        if templates:
            print(f"\n   模板列表详情:")
            for i, tmpl in enumerate(templates, 1):
                print(f"\n   [{i}] 模板ID: {tmpl.template_id}")
                print(f"       名称: {tmpl.name}")
                print(f"       版本: {tmpl.version}")
                print(f"       编译器: {tmpl.compiler}")
                print(f"       场景: {tmpl.scene}")
                print(f"       内置: {tmpl.is_builtin}")
                print(f"       业务线: {tmpl.business_lines}")
                print(f"       描述: {(tmpl.description or '')[:50]}...")
                
                # 检查必要属性是否存在
                attrs = ['template_id', 'name', 'version', 'compiler', 'scene', 
                        'is_builtin', 'business_lines', 'description']
                missing = [attr for attr in attrs if not hasattr(tmpl, attr)]
                if missing:
                    print(f"       ⚠️ 缺少属性: {missing}")
                else:
                    print(f"       ✅ 所有属性完整")
        else:
            print("   ❌ 未获取到任何模板！")
            
    except Exception as e:
        print(f"   ❌ 获取模板失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 2. 直接使用 TemplateDAO 查询
    print("\n\n2. 测试 TemplateDAO.list():")
    try:
        templates_dao = TemplateDAO.list()
        print(f"   ✅ DAO 层返回 {len(templates_dao)} 个模板")
        
        if templates_dao != templates:
            print(f"   ⚠️ Service 和 DAO 返回结果不一致!")
            print(f"      Service: {len(templates)} 个")
            print(f"      DAO: {len(templates_dao)} 个")
        
    except Exception as e:
        print(f"   ❌ DAO 查询失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. 检查数据库连接
    print("\n\n3. 检查数据库连接:")
    try:
        from src.core.database import db
        with db.get_session() as session:
            count = session.query(Template).count()
            print(f"   ✅ 数据库连接正常")
            print(f"   数据库中模板总数: {count} (包括非活跃)")
            
            active_count = session.query(Template).filter(Template.is_active == True).count()
            print(f"   活跃模板数: {active_count}")
            
            builtin_count = session.query(Template).filter(
                Template.is_active == True,
                Template.is_builtin == True
            ).count()
            print(f"   内置模板数: {builtin_count}")
            
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. 模拟 UI 显示逻辑
    print("\n\n4. 模拟 UI 显示逻辑 (_display_templates):")
    try:
        from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QApplication
        from PyQt5.QtCore import Qt
        
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels([
            "模板ID", "模板名称", "版本", "编译器", "适用场景", "业务线", "内置", "描述", "操作"
        ])
        
        print(f"   设置行数: {len(templates)}")
        table.setRowCount(len(templates))
        
        for row, tmpl in enumerate(templates):
            item_id = QTableWidgetItem(tmpl.template_id)
            item_name = QTableWidgetItem(tmpl.name)
            item_version = QTableWidgetItem(tmpl.version)
            item_compiler = QTableWidgetItem(tmpl.compiler or "-")
            item_scene = QTableWidgetItem(tmpl.scene or "-")
            
            business_lines = tmpl.business_lines or []
            bl_text = ", ".join(business_lines) if business_lines else "-"
            item_bl = QTableWidgetItem(bl_text)
            
            item_builtin = QTableWidgetItem("是" if tmpl.is_builtin else "否")
            item_desc = QTableWidgetItem((tmpl.description or "-")[:50])
            
            table.setItem(row, 0, item_id)
            table.setItem(row, 1, item_name)
            table.setItem(row, 2, item_version)
            table.setItem(row, 3, item_compiler)
            table.setItem(row, 4, item_scene)
            table.setItem(row, 5, item_bl)
            table.setItem(row, 6, item_builtin)
            table.setItem(row, 7, item_desc)
            
            print(f"   行 {row}: {tmpl.template_id} - {tmpl.name} ✅")
        
        print(f"\n   ✅ 表格填充完成，共 {table.rowCount()} 行")
        print(f"   表格列数: {table.columnCount()}")
        print(f"   表格可见行数: {table.visibleRegion().rects()}")
        
    except Exception as e:
        print(f"   ❌ UI 显示模拟失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("诊断完成")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 诊断过程发生严重错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)