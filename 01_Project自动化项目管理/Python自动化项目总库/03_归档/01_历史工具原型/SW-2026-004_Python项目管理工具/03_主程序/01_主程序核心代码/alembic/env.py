# -*- coding: utf-8 -*-
"""
Alembic环境配置文件
"""

from logging.config import fileConfig
import sys
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入模型基类
from src.models.base import Base

# 导入所有模型，确保它们被注册
# 这里需要导入所有使用Base的模型
try:
    from src.models.project import Project
    from src.models.template import Template
    from src.models.library import Library
    from src.models.library_version import LibraryVersion
    from src.models.library_dependency import LibraryDependency
    from src.models.library_change import LibraryChange
    from src.models.task import Task
    from src.models.milestone import Milestone
    from src.models.defect import Defect
    from src.models.spec import Spec
    from src.models.change import Change
    from src.models.approval import Approval
    from src.models.impact import Impact
    from src.models.plugin import Plugin
except ImportError as e:
    print(f"警告：部分模型导入失败: {e}")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# 从应用配置获取数据库URL
def get_url():
    """获取数据库URL"""
    try:
        from src.core.settings import settings
        return settings.database.url
    except ImportError:
        # 如果settings不可用，使用alembic.ini中的配置
        return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
