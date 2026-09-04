# -*- coding: utf-8 -*-
"""
数据库连接管理
"""
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional

from src.core.config import Config
from src.utils.logger import setup_logger
from src.models.base import Base
import subprocess
import sys

logger = setup_logger(__name__)

class Database:
    """数据库管理类"""
    _instance: Optional["Database"] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._engine = None
                cls._instance._SessionLocal = None
                cls._instance._init_engine()
        return cls._instance
    
    @property
    def engine(self):
        """获取数据库引擎"""
        return self._engine
    
    def _init_engine(self):
        """初始化数据库引擎"""
        import sys
        from pathlib import Path
        
        db_config = Config.get("database")
        if not db_config:
            db_config = {
                "db_type": "sqlite",
                "db_path": "data/project_manager.db",
                "echo": False
            }
        db_type = db_config.get("db_type", "sqlite")
        
        if db_type == "sqlite":
            db_path = db_config.get("db_path", "data/project_manager.db")
            if getattr(sys, 'frozen', False):
                base_path = Path(sys.executable).parent
            else:
                base_path = Path(__file__).parent.parent.parent
            if not Path(db_path).is_absolute():
                db_path = str(base_path / db_path)
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            url = f"sqlite:///{db_path}"
        else:
            # 其他数据库类型支持
            host = db_config.get("host", "localhost")
            port = db_config.get("port", 3306)
            user = db_config.get("user", "root")
            password = db_config.get("password", "")
            db_name = db_config.get("db_name", "project_manager")
            url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4"
        
        echo = db_config.get("echo", False)
        pool_size = db_config.get("pool_size", 5)
        max_overflow = db_config.get("max_overflow", 10)
        
        logger.info(f"初始化数据库连接: {url}")
        
        if db_type == "sqlite":
            self._engine = create_engine(
                url,
                echo=echo,
                connect_args={"check_same_thread": False}
            )
        else:
            self._engine = create_engine(
                url,
                echo=echo,
                pool_size=pool_size,
                max_overflow=max_overflow,
                connect_args={}
            )
        
        self._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
        
        # 自动创建表
        auto_migrate = db_config.get("auto_migrate", True)
        if auto_migrate:
            self.create_tables()
    
    def create_tables(self):
        """创建所有数据库表（含自动迁移）"""
        logger.info("创建数据库表结构")

        # 先创建基础表结构
        Base.metadata.create_all(bind=self._engine)

        # V2.1.0: 自动迁移 - 检测并添加缺失的列
        self._auto_migrate_tables()

        # V2.1.0: 修复现有 JSON 字段数据（处理旧数据库中的 NULL/空字符串）
        self._fix_json_columns_data()
    
    def _auto_migrate_tables(self):
        """
        自动迁移：为已存在的表添加模型中新定义的列
        
        解决问题：
        - 模型更新后（如Change添加domain/nature/scope字段）
        - 但数据库表还是旧结构，导致 "no such column" 错误
        """
        try:
            from sqlalchemy import inspect, text
            
            inspector = inspect(self._engine)
            
            with self._engine.connect() as conn:
                for table_name, table in Base.metadata.tables.items():
                    if table_name in inspector.get_table_names():
                        existing_columns = {col['name'] for col in inspector.get_columns(table_name)}
                        model_columns = {col.name for col in table.columns}
                        
                        missing_columns = model_columns - existing_columns
                        
                        if missing_columns:
                            logger.warning(f"检测到表 '{table_name}' 缺少 {len(missing_columns)} 个列: {missing_columns}")
                            
                            for col_name in missing_columns:
                                col = table.columns[col_name]
                                col_type = col.type.compile(dialect=self._engine.dialect)

                                default_clause = ""
                                if col.default is not None:
                                    if hasattr(col.default, 'arg'):
                                        default_val = col.default.arg
                                        if isinstance(default_val, str):
                                            default_clause = f" DEFAULT '{default_val}'"
                                        elif isinstance(default_val, (int, float)):
                                            default_clause = f" DEFAULT {default_val}"
                                        else:
                                            default_clause = f" DEFAULT '{default_val}'"
                                    elif callable(col.default):
                                        pass  # 可调用默认值需要特殊处理

                                nullable = "" if col.nullable else " NOT NULL"

                                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}{nullable}{default_clause}"

                                # 使用事务上下文管理器（SQLAlchemy 2.0 推荐方式）
                                try:
                                    with conn.begin():
                                        conn.execute(text(alter_sql))
                                    logger.info(f"✅ 已添加列: {table_name}.{col_name} ({col_type})")

                                    # 对于 JSON 类型列，修复现有数据中的 NULL 或空字符串
                                    if isinstance(col.type, type(text('').type)) or 'JSON' in str(col.type):
                                        try:
                                            json_default = '{}'  # JSON 空对象
                                            with conn.begin():
                                                update_sql = "UPDATE {} SET {} = '{}' WHERE {} IS NULL OR {} = ''".format(
                                                    table_name, col_name, json_default, col_name, col_name
                                                )
                                                conn.execute(text(update_sql))
                                            logger.info(f"  📝 已修复 {table_name}.{col_name} 的旧数据为默认值")
                                        except Exception as fix_e:
                                            logger.warning(f"  ⚠️ 修复旧数据失败（可忽略）: {fix_e}")
                                except Exception as e:
                                    logger.error(f"❌ 添加列失败: {table_name}.{col_name} - {e}")
                    
        except Exception as e:
            logger.exception(f"自动迁移失败: {e}")
            logger.warning("建议手动删除数据库文件重新启动，或执行数据库升级")

    def _fix_json_columns_data(self):
        """
        修复现有 JSON 字段数据（处理旧数据库中的 NULL/空字符串）

        解决问题：
        - 旧数据库中 JSON 字段可能是 NULL 或空字符串
        - SQLAlchemy 2.0 的 JSON 类型处理器无法解析空字符串，导致 JSONDecodeError
        """
        try:
            from sqlalchemy import inspect, text

            inspector = inspect(self._engine)

            with self._engine.connect() as conn:
                for table_name, table in Base.metadata.tables.items():
                    if table_name not in inspector.get_table_names():
                        continue

                    # 查找表中的 JSON 类型列
                    for col in table.columns:
                        col_type_str = str(col.type)
                        if 'JSON' in col_type_str:
                            # 检查并修复该列的 NULL 或空字符串数据
                            try:
                                with conn.begin():
                                    # 检查是否有需要修复的数据
                                    check_sql = "SELECT COUNT(*) FROM {} WHERE {} IS NULL OR {} = ''".format(
                                        table_name, col.name, col.name
                                    )
                                    result = conn.execute(text(check_sql)).scalar()

                                    if result and result > 0:
                                        json_default = '{}'  # JSON 空对象
                                        update_sql = "UPDATE {} SET {} = '{}' WHERE {} IS NULL OR {} = ''".format(
                                            table_name, col.name, json_default, col.name, col.name
                                        )
                                        conn.execute(text(update_sql))
                                        logger.info(f"📝 已修复表 '{table_name}' 的 '{col.name}' 列: {result} 条记录")
                            except Exception as fix_e:
                                logger.warning(f"⚠️ 修复 {table_name}.{col.name} 数据失败（可忽略）: {fix_e}")

        except Exception as e:
            logger.warning(f"JSON 数据修复过程出错（通常可忽略）: {e}")

    def drop_tables(self):
        """删除所有数据库表（谨慎使用）"""
        logger.warning("删除所有数据库表")
        Base.metadata.drop_all(bind=self._engine)
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self._SessionLocal()
    
    def get_engine(self):
        """获取数据库引擎"""
        return self._engine
    
    def get_alembic_config(self):
        """获取Alembic配置路径"""
        from pathlib import Path
        return str(Path(__file__).parent.parent.parent / "alembic.ini")
    
    def run_alembic_command(self, command: str):
        """运行Alembic命令
        
        Args:
            command: Alembic命令，如 "upgrade head", "downgrade -1", 等
            
        Returns:
            (success: bool, output: str)
        """
        import subprocess
        from pathlib import Path
        
        try:
            alembic_ini = self.get_alembic_config()
            project_root = Path(alembic_ini).parent
            
            cmd = [sys.executable, "-m", "alembic", "-c", alembic_ini] + command.split()
            result = subprocess.run(
                cmd,
                cwd=str(project_root),
                capture_output=True,
                text=True
            )
            
            output = result.stdout + result.stderr
            if result.returncode == 0:
                logger.info(f"Alembic命令执行成功: {command}")
                return True, output
            else:
                logger.error(f"Alembic命令执行失败: {command}\n输出: {output}")
                return False, output
                
        except Exception as e:
            logger.error(f"运行Alembic命令时出错: {e}")
            return False, str(e)
    
    def upgrade_database(self, revision: str = "head") -> tuple[bool, str]:
        """升级数据库到指定版本
        
        Args:
            revision: 目标版本，默认为"head"（最新版本）
            
        Returns:
            (success: bool, output: str)
        """
        logger.info(f"升级数据库到版本: {revision}")
        return self.run_alembic_command(f"upgrade {revision}")
    
    def downgrade_database(self, revision: str) -> tuple[bool, str]:
        """降级数据库到指定版本
        
        Args:
            revision: 目标版本
            
        Returns:
            (success: bool, output: str)
        """
        logger.info(f"降级数据库到版本: {revision}")
        return self.run_alembic_command(f"downgrade {revision}")
    
    def get_current_revision(self) -> tuple[bool, Optional[str]]:
        """获取当前数据库版本
        
        Returns:
            (success: bool, revision: str or None)
        """
        success, output = self.run_alembic_command("current")
        if success and output:
            for line in output.split("\n"):
                if line.strip() and not line.startswith("INFO"):
                    parts = line.strip().split()
                    if parts:
                        return True, parts[0]
        return False, None
    
    def create_migration(self, message: str, autogenerate: bool = True) -> tuple[bool, str]:
        """创建新的迁移脚本
        
        Args:
            message: 迁移描述
            autogenerate: 是否自动生成
            
        Returns:
            (success: bool, output: str)
        """
        cmd = f"revision -m '{message}'"
        if autogenerate:
            cmd += " --autogenerate"
        logger.info(f"创建迁移: {message}")
        return self.run_alembic_command(cmd)

# 全局数据库实例
db = Database()
