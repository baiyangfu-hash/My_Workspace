# -*- coding: utf-8 -*-
"""
总库管理问题诊断脚本
用于排查"总库显示 0 个项目"的问题
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到 sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def diagnose():
    print("=" * 60)
    print("总库管理问题诊断报告")
    print("=" * 60)

    # 1. 导入必要的模块
    try:
        from src.dao.database import Database
        from src.models.library import Library, LibraryProject, Category
        from src.models.project import Project
        from sqlalchemy.orm import sessionmaker, Session
        from sqlalchemy import text

        print("\n✓ 模块导入成功")
    except Exception as e:
        print(f"\n✗ 模块导入失败: {e}")
        return

    # 2. 连接数据库
    db = Database()
    session = db.get_session()

    try:
        # 3. 检查 libraries 表
        print("\n" + "-" * 40)
        print("【检查 1】libraries 表（总库表）")
        print("-" * 40)

        libraries = session.query(Library).all()
        print(f"总库数量: {len(libraries)}")
        for lib in libraries:
            print(f"  - ID: {lib.library_id}")
            print(f"    名称: {lib.name}")
            print(f"    状态: {lib.status}")
            print(f"    根路径: {lib.root_path}")
            print(f"    创建时间: {lib.created_at}")
            print()

        # 4. 检查 projects 表
        print("-" * 40)
        print("【检查 2】projects 表（项目表）")
        print("-" * 40)

        projects = session.query(Project).all()
        print(f"项目数量: {len(projects)}")
        for proj in projects:
            print(f"  - ID: {proj.project_id}")
            print(f"    编号: {proj.code}")
            print(f"    名称: {proj.name}")
            print(f"    业务线: {proj.business_line}")
            print(f"    状态: {proj.status}")
            print()

        # 5. 检查 library_projects 关联表（关键！）
        print("-" * 40)
        print("【检查 3】library_projects 表（关联表）⭐ 最关键")
        print("-" * 40)

        associations = session.query(LibraryProject).all()
        print(f"关联记录数量: {len(associations)}")
        if associations:
            for assoc in associations:
                print(f"  - 总库ID: {assoc.library_id} → 项目ID: {assoc.project_id}")
                if assoc.category_id:
                    print(f"    分类ID: {assoc.category_id}")
        else:
            print("  ⚠️ 关联表为空！这就是 bug 根因！")
            print("  解释：项目虽然存在于 projects 表，但没有关联到任何总库")
            print("  所以总库管理模块查不到这些项目")

        # 6. 检查 categories 表
        print("\n" + "-" * 40)
        print("【检查 4】categories 表（分类表）")
        print("-" * 40)

        categories = session.query(Category).all()
        print(f"分类数量: {len(categories)}")
        for cat in categories:
            print(f"  - ID: {cat.category_id}")
            print(f"    名称: {cat.name}")
            print(f"    所属总库: {cat.library_id}")
            print()

        # 7. 诊断结论
        print("=" * 60)
        print("【诊断结论】")
        print("=" * 60)

        if len(associations) == 0 and len(projects) > 0:
            print("❌ 问题确认：library_projects 关联表为空")
            print(f"   - 有 {len(projects)} 个项目在 projects 表")
            print(f"   - 但没有一条关联记录")
            print("\n根本原因可能是：")
            print("  1. 创建项目时 add_project_to_library() 失败")
            print("  2. 默认总库 ID 不匹配导致查找失败")
            print("  3. 异常被静默捕获（warning 级别日志）")

            if len(libraries) > 0:
                default_lib = libraries[0]
                print(f"\n当前默认总库信息：")
                print(f"  - ID: {default_lib.library_id}")
                print(f"  - 名称: {default_lib.name}")
                print(f"\n期望的硬编码 ID: LIB-DEFAULT-001")
                if default_lib.library_id != "LIB-DEFAULT-001":
                    print(f"  ⚠️ 不匹配！这就是问题所在！")

        elif len(associations) > 0:
            print("✓ 关联表有数据，问题可能在其他地方")
            print("   建议：检查 UI 刷新逻辑或缓存问题")
        else:
            print("ℹ️ 数据库完全为空（全新安装？）")

    finally:
        session.close()

if __name__ == "__main__":
    diagnose()
    print("\n诊断完成")
