# -*- coding: utf-8 -*-
"""
分类关联修复脚本：将已有项目分配到正确的业务线分类

用途：修复 V2.5.5 数据修复后分类不显示的问题
运行方式：python repair_categories.py
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def repair():
    print("=" * 60)
    print("分类关联修复脚本")
    print("=" * 60)
    
    from src.dao.database import Database
    from src.models.library import LibraryProject, Category, Library
    from src.models.project import Project
    from src.core.constants import BusinessLine, BUSINESS_LINE_DESC
    
    db = Database()
    session = db.get_session()
    
    try:
        # 1. 获取默认总库
        default_lib = session.query(Library).filter(Library.status == 'active').first()
        if not default_lib:
            print("❌ 错误：找不到默认总库")
            return False
        
        print(f"\n✓ 默认总库: {default_lib.name} (ID={default_lib.library_id})")
        
        # 2. 获取所有分类并建立映射
        categories = session.query(Category).filter(
            Category.library_id == default_lib.library_id
        ).all()
        
        # 建立分类名称 -> ID 的映射
        category_map = {}
        for cat in categories:
            category_map[cat.name] = cat.category_id
            print(f"  - 分类: {cat.name} (ID={cat.category_id})")
        
        # 建立 BusinessLine 枚举 -> 分类名称 的映射
        business_line_to_category = {}
        for bl in BusinessLine:
            desc = BUSINESS_LINE_DESC.get(bl, bl.value)
            if desc in category_map:
                business_line_to_category[bl] = desc
        
        print("\n业务线 → 分类映射:")
        for bl, cat_name in business_line_to_category.items():
            print(f"  {bl.value} → {cat_name}")
        
        # 3. 更新所有未分配分类的关联记录
        associations = session.query(LibraryProject).filter(
            LibraryProject.library_id == default_lib.library_id,
            LibraryProject.category_id == None  # 只处理未分配分类的
        ).all()
        
        print(f"\n找到 {len(associations)} 个未分配分类的项目关联")
        
        updated_count = 0
        for assoc in associations:
            # 获取对应的项目
            project = session.query(Project).get(assoc.project_id)
            if not project:
                print(f"  ⚠️ 找不到项目 {assoc.project_id}，跳过")
                continue
            
            # 根据项目的业务线确定分类
            bl = project.business_line
            if bl in business_line_to_category:
                target_cat_name = business_line_to_category[bl]
                target_cat_id = category_map[target_cat_name]
                
                # 更新关联记录的分类
                assoc.category_id = target_cat_id
                updated_count += 1
                print(f"  ✓ {project.code} ({project.name}) → {target_cat_name}")
            else:
                print(f"  ⚠️ {project.code} 的业务线 {bl.value} 无匹配分类")
        
        # 4. 提交更改
        session.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ 分类关联修复完成！共更新 {updated_count} 个项目")
        print("=" * 60)
        print("\n请重启应用程序或点击'刷新'按钮查看效果")
        
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