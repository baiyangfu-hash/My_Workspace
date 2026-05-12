# -*- coding: utf-8 -*-
"""
深度诊断：检查项目和关联表的数据一致性
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def diagnose():
    from src.dao.database import Database
    from src.models.library import LibraryProject, Library, Category
    from src.models.project import Project
    
    db = Database()
    session = db.get_session()
    
    try:
        print("=" * 70)
        print("【诊断 1】library_projects 表中的所有记录")
        print("=" * 70)
        assocs = session.query(LibraryProject).all()
        for a in assocs:
            print(f"  library_id={a.library_id} | project_id={a.project_id} | category_id={a.category_id}")
        
        print("\n" + "=" * 70)
        print("【诊断 2】projects 表中的所有记录")
        print("=" * 70)
        projs = session.query(Project).all()
        for p in projs:
            print(f"  project_id={p.project_id} | code={p.code} | name={p.name}")
        
        print("\n" + "=" * 70)
        print("【诊断 3】交叉验证")
        print("=" * 70)
        proj_ids_in_projects = set(p.project_id for p in projs)
        mismatched = []
        for a in assocs:
            exists = a.project_id in proj_ids_in_projects
            status = "✓ 匹配" if exists else "✗ 不匹配！"
            print(f"  {a.project_id} → {status}")
            if not exists:
                mismatched.append(a.project_id)
        
        if mismatched:
            print(f"\n⚠️ 有 {len(mismatched)} 个关联记录引用了不存在的项目 ID！")
            print("\n需要重新创建正确的关联记录。")
            
            # 自动修复方案
            print("\n" + "=" * 70)
            print("【自动修复】删除错误关联，用正确 ID 重建")
            print("=" * 70)
            
            default_lib = session.query(Library).first()
            if not default_lib:
                print("❌ 找不到默认总库")
                return
            
            # 删除所有旧的关联记录
            old_count = session.query(LibraryProject).delete()
            session.commit()
            print(f"  已删除 {old_count} 条旧关联记录")
            
            # 用正确的 project_id 重新创建
            categories = session.query(Category).filter(
                Category.library_id == default_lib.library_id
            ).all()
            cat_map = {c.name: c.category_id for c in categories}
            
            from src.core.constants import BusinessLine, BUSINESS_LINE_DESC
            bl_to_cat = {}
            for bl in BusinessLine:
                desc = BUSINESS_LINE_DESC.get(bl, bl.value)
                if desc in cat_map:
                    bl_to_cat[bl] = cat_map[desc]
            
            new_count = 0
            for proj in projs:
                cat_id = bl_to_cat.get(proj.business_line)
                assoc = LibraryProject(
                    library_id=default_lib.library_id,
                    project_id=proj.project_id,
                    category_id=cat_id
                )
                session.add(assoc)
                new_count += 1
                cat_name = [k for k,v in cat_map.items() if v==cat_id][0] if cat_id else "未分类"
                print(f"  ✓ {proj.code} → {cat_name}")
            
            session.commit()
            print(f"\n✅ 修复完成！重建了 {new_count} 条正确的关联记录")
        
    finally:
        session.close()

if __name__ == "__main__":
    diagnose()
    input("\n按回车退出...")