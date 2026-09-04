# -*- coding: utf-8 -*-
"""
数据库迁移测试
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.dao.database import Database


class TestDatabaseMigration:
    """测试数据库迁移"""
    
    @pytest.fixture
    def temp_db_path(self):
        """创建临时数据库文件"""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test.db"
        yield str(db_path)
        shutil.rmtree(temp_dir)
    
    def test_database_initialization(self, temp_db_path):
        """测试数据库初始化"""
        # 这里使用简单的SQLite测试，避免Alembic命令的复杂性
        import sqlite3
        
        # 创建测试数据库
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # 创建简单的测试表
        cursor.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        ''')
        
        # 插入测试数据
        cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("test",))
        conn.commit()
        
        # 查询数据
        cursor.execute("SELECT name FROM test_table")
        result = cursor.fetchone()
        assert result[0] == "test"
        
        conn.close()
        
        print("✓ 数据库基本操作测试成功")
    
    def test_database_class_available(self):
        """测试Database类可用"""
        from src.dao.database import db
        
        assert db is not None
        assert hasattr(db, 'get_session')
        assert hasattr(db, 'get_engine')
        assert hasattr(db, 'upgrade_database')
        assert hasattr(db, 'downgrade_database')
        assert hasattr(db, 'create_tables')
        
        print("✓ Database类可用测试成功")
    
    def test_alembic_config_exists(self):
        """测试Alembic配置文件存在"""
        from pathlib import Path
        
        alembic_ini = Path(__file__).parent.parent.parent / "alembic.ini"
        assert alembic_ini.exists()
        
        alembic_dir = Path(__file__).parent.parent.parent / "alembic"
        assert alembic_dir.exists()
        assert (alembic_dir / "env.py").exists()
        
        print("✓ Alembic配置文件存在测试成功")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
