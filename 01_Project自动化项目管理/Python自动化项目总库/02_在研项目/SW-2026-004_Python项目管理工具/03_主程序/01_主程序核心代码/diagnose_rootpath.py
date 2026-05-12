import sqlite3
import os

DB_PATH = r"d:\BaiduSyncdisk\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-004_Python项目管理工具\03_主程序\01_主程序核心代码\data\project_manager.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("=" * 60)
print("数据库 root_path 诊断报告")
print("=" * 60)

cur.execute("SELECT library_id, name, root_path FROM libraries")
rows = cur.fetchall()

if not rows:
    print("libraries 表为空")
else:
    print(f"\n共 {len(rows)} 条记录:\n")
    for row in rows:
        lib_id, name, root_path = row
        has_abs = bool(root_path and (":" in str(root_path) or "\\" in str(root_path)))
        status = "⚠️ 含绝对路径" if has_abs else "✅ 安全"
        print(f"  ID: {lib_id}")
        print(f"  名称: {name}")
        print(f"  root_path: [{root_path or '(空)'}]")
        print(f"  状态: {status}")
        print()

print("-" * 60)

abs_count = sum(1 for _, _, rp in rows if rp and (":" in str(rp) or "\\" in str(rp)))
print(f"\n诊断结果: {len(rows)} 条记录中, {abs_count} 条包含绝对路径")

if abs_count > 0:
    print("\n执行清理: 将含绝对路径的 root_path 清空...")
    cur.execute("UPDATE libraries SET root_path = '' WHERE root_path LIKE '%:%' OR root_path LIKE '%\\\\%'")
    conn.commit()
    print(f"✅ 已清理 {cur.rowcount} 条记录")

    cur.execute("SELECT library_id, name, root_path FROM libraries")
    for row in cur.fetchall:
        pass
    cur.execute("SELECT library_id, name, root_path FROM libraries")
    rows2 = cur.fetchall()
    print("\n清理后状态:")
    for row in rows2:
        lib_id, name, root_path = row
        print(f"  {name}: root_path = [{root_path or '(空)'}]")

conn.close()
print("\n诊断完成!")
