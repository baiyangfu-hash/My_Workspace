# -*- coding: utf-8 -*-
"""
数据修复脚本：将已有的项目关联到默认总库

用途：修复 V2.5.5 发现的 bug（项目未正确归档到总库）
运行方式：python repair_library_projects.py
"""
import sys
from pathlib import Path

# 添加项目根目录到 sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def repair():
    print("=" * 60)
    print("总库数据修复脚本")
    print("=" * 60)

    from src.dao.database import Database
    from src.models.library import LibraryProject, Library, Category
    from src.models.project import Project
    from src.core.constants import BusinessLine, BUSINESS_LINE_DESC

    db = Database()
    session = db.get_session()

    try:
        # 1. 获取默认总库
        default_lib = session.query(Library).filter(
            Library.status == 'active'
        ).first()

        if not default_lib:
            print("❌ 错误：找不到活跃的总库")
            return False

        print(f"\n✓ 找到默认总库:")
        print(f"  - ID: {default_lib.library_id}")
        print(f"  - 名称: {default_lib.name}")
        print(f"  - 状态: {default_lib.status}")

        # 2. 获取所有项目
        projects = session.query(Project).all()
        print(f"\n✓ 找到 {len(projects)} 个项目:")
        for p in projects:
            print(f"  - {p.code}: {p.name}")

        # 3. 为每个项目创建关联（如果尚未关联）
        added_count = 0
        skipped_count = 0

        for project in projects:
            existing = session.query(LibraryProject).filter(
                LibraryProject.library_id == default_lib.library_id,
                LibraryProject.project_id == project.project_id
            ).first()

            if not existing:
                association = LibraryProject(
                    library_id=default_lib.library_id,
                    project_id=project.project_id
                )
                session.add(association)
                added_count += 1
                print(f"\n✓ 已关联: {project.code} → {default_lib.name}")
            else:
                skipped_count += 1
                print(f"\n- 跳过(已关联): {project.code}")

        # 4. 检查并创建缺失的分类
        from src.services.library_service import LibraryService
        from datetime import datetime
        import uuid

        categories = session.query(Category).filter(
            Category.library_id == default_lib.library_id
        ).all()

        if len(categories) == 0:
            print(f"\n⚠️ 未找到分类，正在创建...")
            for business_line in BusinessLine:
                category_name = BUSINESS_LINE_DESC.get(business_line, business_line.value)
                # 生成分类ID（与 LibraryService.create_category 一致）
                category_id = f"CAT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
                category = Category(
                    category_id=category_id,
                    library_id=default_lib.library_id,
                    name=category_name,
                    description=f"{category_name}分类"
                )
                session.add(category)
                print(f"  ✓ 创建分类: {category_name} (ID: {category_id})")

        # 5. 提交事务
        session.commit()

        print("\n" + "=" * 60)
        print("✅ 数据修复完成！")
        print("=" * 60)
        print(f"新增关联: {added_count} 个项目")
        print(f"跳过(已存在): {skipped_count} 个项目")
        print(f"\n请重启应用程序并检查'总库管理'选项卡")

        return True

    except Exception as e:
        session.rollback()
        print(f"\n❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = repair()
    input("\n按回车键退出...")
    sys.exit(0 if success else 1)
