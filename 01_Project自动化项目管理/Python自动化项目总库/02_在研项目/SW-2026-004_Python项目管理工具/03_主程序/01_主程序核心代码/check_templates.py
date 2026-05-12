import sqlite3

db_path = r'd:\BaiduSyncdisk\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-004_Python项目管理工具\03_主程序\01_主程序核心代码\data\project_manager.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('SELECT template_id, name, version, is_builtin FROM templates ORDER BY template_id')
rows = cursor.fetchall()

print(f'总计 {len(rows)} 个模板:\n')
for r in rows:
    builtin_str = "内置" if r[3] else "自定义"
    print(f'{r[0]:30} | {r[1]:25} | {r[2]:8} | {builtin_str}')

conn.close()
