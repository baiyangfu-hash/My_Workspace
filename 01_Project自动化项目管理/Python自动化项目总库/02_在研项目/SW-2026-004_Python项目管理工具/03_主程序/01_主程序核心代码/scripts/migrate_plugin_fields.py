# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 添加插件新字段

运行此脚本以更新数据库表结构
"""
import sqlite3
from pathlib import Path

MIGRATION_SQL = """
-- 添加插件市场相关字段
ALTER TABLE plugins ADD COLUMN download_url VARCHAR(500);
ALTER TABLE plugins ADD COLUMN repository VARCHAR(500);
ALTER TABLE plugins ADD COLUMN homepage VARCHAR(500);
ALTER TABLE plugins ADD COLUMN tags JSON DEFAULT '[]';
ALTER TABLE plugins ADD COLUMN icon VARCHAR(200);
ALTER TABLE plugins ADD COLUMN min_app_version VARCHAR(20);
ALTER TABLE plugins ADD COLUMN max_app_version VARCHAR(20);
ALTER TABLE plugins ADD COLUMN changelog TEXT;
ALTER TABLE plugins ADD COLUMN rating FLOAT DEFAULT 0.0;
ALTER TABLE plugins ADD COLUMN download_count INTEGER DEFAULT 0;
ALTER TABLE plugins ADD COLUMN installed_at DATETIME DEFAULT CURRENT_TIMESTAMP;
"""


def run_migration(db_path: str = None):
    """运行迁移"""
    if db_path is None:
        db_path = Path(__file__).parent.parent / "data" / "project_manager.db"
    else:
        db_path = Path(db_path)
    
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        return False
    
    print(f"正在迁移数据库: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(plugins)")
        columns = [row[1] for row in cursor.fetchall()]
        
        migrations_to_run = []
        
        if 'download_url' not in columns:
            migrations_to_run.append("ALTER TABLE plugins ADD COLUMN download_url VARCHAR(500)")
        
        if 'repository' not in columns:
            migrations_to_run.append("ALTER TABLE plugins ADD COLUMN repository VARCHAR(500)")
        
        if 'homepage' not in columns:
            migrations_to_run.append("ALTER TABLE plugins ADD COLUMN homepage VARCHAR(500)")
        
        if 'tags' not in columns:
            migrations_to_run.append("ALTER TABLE plugins ADD COLUMN tags TEXT DEFAULT '[]'")
            migrations_to_run.append("UPDATE plugins SET tags = '[]' WHERE tags IS NULL")
        
        if 'icon' not in columns:
            migrations_to_run.append("ALTER TABLE plugins ADD COLUMN icon VARCHAR(200)")
        
        if 'min_app_version' not in columns:
            migrations_to_run.append("ALTER TABLE plugins ADD COLUMN min_app_version VARCHAR(20)")
        
        if 'max_app_version' not in columns:
            migrations_to_run.append("ALTER TABLE plugins ADD COLUMN max_app_version VARCHAR(20)")
        
        if 'changelog' not in columns:
            migrations_to_run.append("ALTER TABLE plugins ADD COLUMN changelog TEXT")
        
        if 'rating' not in columns:
            migrations_to_run.append("ALTER TABLE plugins ADD COLUMN rating REAL")
            migrations_to_run.append("UPDATE plugins SET rating = 0.0 WHERE rating IS NULL")
        
        if 'download_count' not in columns:
            migrations_to_run.append("ALTER TABLE plugins ADD COLUMN download_count INTEGER")
            migrations_to_run.append("UPDATE plugins SET download_count = 0 WHERE download_count IS NULL")
        
        if 'installed_at' not in columns:
            migrations_to_run.append("ALTER TABLE plugins ADD COLUMN installed_at DATETIME")
        
        if not migrations_to_run:
            print("数据库已是最新版本，无需迁移")
            return True
        
        for sql in migrations_to_run:
            print(f"执行: {sql}")
            cursor.execute(sql)
        
        conn.commit()
        print(f"迁移完成，共执行 {len(migrations_to_run)} 条语句")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"迁移失败: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else None
    success = run_migration(db_path)
    sys.exit(0 if success else 1)
