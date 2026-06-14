# -*- coding: utf-8 -*-
"""V2.8.0 模板管理优化：新增 schema_version、base_template_id、applied_template_version

Revision ID: v2_8_0_template_optimization
Revises: initial_schema
Create Date: 2026-06-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'v2_8_0_template_optimization'
down_revision: Union[str, None] = 'initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """新增模板版本管理和继承字段"""
    # templates 表新增 schema_version 列
    op.add_column('templates', sa.Column('schema_version', sa.String(length=10), nullable=True, comment='模板结构版本号'))
    # templates 表新增 base_template_id 列
    op.add_column('templates', sa.Column('base_template_id', sa.String(length=32), nullable=True, comment='继承的父模板ID'))

    # projects 表新增 applied_template_version 列
    op.add_column('projects', sa.Column('applied_template_version', sa.String(length=20), nullable=True, comment='创建时应用的模板版本'))

    # 回填已有数据
    op.execute("UPDATE templates SET schema_version = '1.0' WHERE schema_version IS NULL")
    op.execute("UPDATE projects SET applied_template_version = '1.0' WHERE applied_template_version IS NULL")


def downgrade() -> None:
    """回滚：移除新增列"""
    op.drop_column('projects', 'applied_template_version')
    op.drop_column('templates', 'base_template_id')
    op.drop_column('templates', 'schema_version')
