# -*- coding: utf-8 -*-
"""
直接修复：为已有的 3 个关联记录设置正确的 category_id
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def fix():
    from src.dao.database import Database
    from src.models.library import LibraryProject, Library, Category
    from src.models.project import Project
    from src.core.constants import BusinessLine, BUSINESS_LINE_DESC
    
    db = Database()
    session = db.get_session()
    
    try:
        default_lib = session.query(Library).first()
        print(f"默认总库: {default_lib.name} (ID={default_lib.library_id})")
        
        # 获取分类映射
        categories = session.query(Category).filter(
            Category.library_id == default_lib.library_id
        ).all()
        cat_map = {c.name: c.category_id for c in categories}
        
        bl_to_cat = {}
        for bl in BusinessLine:
            desc = BUSINESS_LINE_DESC.get(bl, bl.value)
            if desc in cat_map:
                bl_to_cat[bl] = cat_map[desc]
        print(f"业务线→分类映射: {[(k.value, v) for k,v in bl_to_cat.items()]}")
        
        # 直接用 update 更新 category_id
        assocs = session.query(LibraryProject).filter(
            LibraryProject.library_id == default_lib.library_id,
            LibraryProject.category_id == None
        ).all()
        
        print(f"\n找到 {len(assocs)} 条需要修复的关联记录")
        
        for assoc in assocs:
            # 通过 project_id 找到项目
            proj = session.query(Project).filter(
                Project.project_id == assoc.project_id
            ).first()
            
            if proj and proj.business_line in bl_to_cat:
                new_cat_id = bl_to_cat[proj.business_line]
                assoc.category_id = new_cat_id
                cat_name = [k for k,v in cat_map.items() if v==new_cat_id][0]
                print(f"  ✓ {proj.code} → {cat_name}")
            else:
                bl_name = proj.business_line.value if proj else "UNKNOWN"
                print(f"  ⚠️ {assoc.project_id[:16]}... (业务线={bl_name}) 无匹配分类")
        
        session.commit()
        print("\n✅ 修复完成！请重启应用或点击刷新")
        
    finally:
        session.close()

if __name__ == "__main__":
    fix()
    input("\n按回车退出...")