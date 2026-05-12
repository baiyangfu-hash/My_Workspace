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
            print(f"  assoc_id={a.id if hasattr(a,'id') else 'N/A'}")
            print(f"    library_id  = {a.library_id}")
            print(f"    project_id  = {a.project_id}")
            print(f"    category_id = {a.category_id}")
        
        print("\n" + "=" * 70)
        print("【诊断 2】projects 表中的所有记录")
        print("=" * 70)
        projs = session.query(Project).all()
        for p in projs:
            print(f"  project_id   = {p.project_id}")
            print(f"  code         = {p.code}")
            print(f"  name         = {p.name}")
            print(f"  business_line= {p.business_line}")
        
        print("\n" + "=" * 70)
        print("【诊断 3】交叉验证：library_projects.project_id 是否存在于 projects 表")
        print("=" * 70)
        proj_ids_in_projects = set(p.project_id for p in projs)
        for a in assocs:
            exists = a.project_id in proj_ids_in_projects
            status = "✓ 匹配" if exists else "✗ 不匹配！"
            print(f"  {a.project_id[:20]}... → {status}")
            
            if not exists:
                # 尝试模糊匹配
                for p in projs:
                    if a.project_id in p.project_id or p.project_id in a.project_id:
                        print(f"    可能对应: {p.project_id} ({p.code})")
        
        # 检查是否有通过 code 关联的方式
        print("\n" + "=" * 70)
        print("【诊断 4】尝试通过 project.code 反查")
        print("=" * 70)
        for a in assocs:
            proj = session.query(Project).filter(
                Project.project_id == a.project_id
            ).first()
            if not proj:
                print(f"  library_projects 引用的 ID {a.project_id} 在 projects 表中不存在！")
                print(f"    这就是分类无法显示的根本原因")
                
    finally:
        session.close()

if __name__ == "__main__":
    diagnose()
    input("\n按回车退出...")