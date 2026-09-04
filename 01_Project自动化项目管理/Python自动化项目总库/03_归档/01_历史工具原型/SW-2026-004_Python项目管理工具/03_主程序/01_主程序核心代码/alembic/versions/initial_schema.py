# -*- coding: utf-8 -*-
"""
初始数据库结构

Revision ID: initial_schema
Revises:
Create Date: 2026-03-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建初始数据库表"""
    # 项目表
    op.create_table(
        'projects',
        sa.Column('project_id', sa.String(length=50), primary_key=True),
        sa.Column('code', sa.String(length=50), unique=True, nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('business_line', sa.String(length=50), nullable=False),
        sa.Column('template_id', sa.String(length=50)),
        sa.Column('manager', sa.String(length=100)),
        sa.Column('description', sa.Text()),
        sa.Column('path', sa.String(length=500)),
        sa.Column('status', sa.String(length=50), default='ACTIVE'),
        sa.Column('sequence', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('deleted_at', sa.DateTime()),
    )
    op.create_index('idx_projects_code', 'projects', ['code'])
    op.create_index('idx_projects_status', 'projects', ['status'])
    op.create_index('idx_projects_business_line', 'projects', ['business_line'])

    # 模板表
    op.create_table(
        'templates',
        sa.Column('template_id', sa.String(length=50), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('structure', sa.JSON()),
        sa.Column('templates', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # 库表
    op.create_table(
        'libraries',
        sa.Column('library_id', sa.String(length=50), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('current_version', sa.String(length=50)),
        sa.Column('repository_url', sa.String(length=500)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # 库版本表
    op.create_table(
        'library_versions',
        sa.Column('version_id', sa.String(length=50), primary_key=True),
        sa.Column('library_id', sa.String(length=50), sa.ForeignKey('libraries.library_id')),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('release_date', sa.DateTime()),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('idx_library_versions_library_id', 'library_versions', ['library_id'])

    # 库依赖表
    op.create_table(
        'library_dependencies',
        sa.Column('dependency_id', sa.String(length=50), primary_key=True),
        sa.Column('library_id', sa.String(length=50), sa.ForeignKey('libraries.library_id')),
        sa.Column('dependency_name', sa.String(length=200), nullable=False),
        sa.Column('version_constraint', sa.String(length=100)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('idx_library_dependencies_library_id', 'library_dependencies', ['library_id'])

    # 库变更表
    op.create_table(
        'library_changes',
        sa.Column('change_id', sa.String(length=50), primary_key=True),
        sa.Column('library_id', sa.String(length=50), sa.ForeignKey('libraries.library_id')),
        sa.Column('change_type', sa.String(length=50)),
        sa.Column('old_version', sa.String(length=50)),
        sa.Column('new_version', sa.String(length=50)),
        sa.Column('description', sa.Text()),
        sa.Column('change_date', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('status', sa.String(length=50)),
    )
    op.create_index('idx_library_changes_library_id', 'library_changes', ['library_id'])

    # 任务表
    op.create_table(
        'tasks',
        sa.Column('task_id', sa.String(length=50), primary_key=True),
        sa.Column('project_id', sa.String(length=50), sa.ForeignKey('projects.project_id')),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('status', sa.String(length=50)),
        sa.Column('priority', sa.String(length=50)),
        sa.Column('assignee', sa.String(length=100)),
        sa.Column('due_date', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_tasks_project_id', 'tasks', ['project_id'])

    # 里程碑表
    op.create_table(
        'milestones',
        sa.Column('milestone_id', sa.String(length=50), primary_key=True),
        sa.Column('project_id', sa.String(length=50), sa.ForeignKey('projects.project_id')),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('due_date', sa.DateTime()),
        sa.Column('status', sa.String(length=50)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('idx_milestones_project_id', 'milestones', ['project_id'])

    # 缺陷表
    op.create_table(
        'defects',
        sa.Column('defect_id', sa.String(length=50), primary_key=True),
        sa.Column('project_id', sa.String(length=50), sa.ForeignKey('projects.project_id')),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('severity', sa.String(length=50)),
        sa.Column('status', sa.String(length=50)),
        sa.Column('reporter', sa.String(length=100)),
        sa.Column('assignee', sa.String(length=100)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_defects_project_id', 'defects', ['project_id'])

    # 规范表
    op.create_table(
        'specs',
        sa.Column('spec_id', sa.String(length=50), primary_key=True),
        sa.Column('project_id', sa.String(length=50), sa.ForeignKey('projects.project_id')),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('version', sa.String(length=50)),
        sa.Column('content', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_specs_project_id', 'specs', ['project_id'])

    # 变卦表
    op.create_table(
        'changes',
        sa.Column('change_id', sa.String(length=50), primary_key=True),
        sa.Column('project_id', sa.String(length=50), sa.ForeignKey('projects.project_id')),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('change_type', sa.String(length=50)),
        sa.Column('status', sa.String(length=50)),
        sa.Column('requested_by', sa.String(length=100)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_changes_project_id', 'changes', ['project_id'])

    # 审批表
    op.create_table(
        'approvals',
        sa.Column('approval_id', sa.String(length=50), primary_key=True),
        sa.Column('change_id', sa.String(length=50), sa.ForeignKey('changes.change_id')),
        sa.Column('approver', sa.String(length=100)),
        sa.Column('status', sa.String(length=50)),
        sa.Column('comments', sa.Text()),
        sa.Column('approved_at', sa.DateTime()),
    )
    op.create_index('idx_approvals_change_id', 'approvals', ['change_id'])

    # 影响表
    op.create_table(
        'impacts',
        sa.Column('impact_id', sa.String(length=50), primary_key=True),
        sa.Column('change_id', sa.String(length=50), sa.ForeignKey('changes.change_id')),
        sa.Column('impact_type', sa.String(length=50)),
        sa.Column('description', sa.Text()),
        sa.Column('severity', sa.String(length=50)),
    )
    op.create_index('idx_impacts_change_id', 'impacts', ['change_id'])

    # 插件表
    op.create_table(
        'plugins',
        sa.Column('plugin_id', sa.String(length=50), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('version', sa.String(length=50)),
        sa.Column('author', sa.String(length=100)),
        sa.Column('is_enabled', sa.Boolean(), default=True),
        sa.Column('config', sa.JSON()),
        sa.Column('installed_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    """删除所有表"""
    op.drop_index('idx_approvals_change_id', 'approvals')
    op.drop_index('idx_impacts_change_id', 'impacts')
    op.drop_index('idx_changes_project_id', 'changes')
    op.drop_index('idx_specs_project_id', 'specs')
    op.drop_index('idx_defects_project_id', 'defects')
    op.drop_index('idx_milestones_project_id', 'milestones')
    op.drop_index('idx_tasks_project_id', 'tasks')
    op.drop_index('idx_library_changes_library_id', 'library_changes')
    op.drop_index('idx_library_dependencies_library_id', 'library_dependencies')
    op.drop_index('idx_library_versions_library_id', 'library_versions')
    op.drop_index('idx_projects_status', 'projects')
    op.drop_index('idx_projects_business_line', 'projects')
    op.drop_index('idx_projects_code', 'projects')

    op.drop_table('approvals')
    op.drop_table('impacts')
    op.drop_table('changes')
    op.drop_table('specs')
    op.drop_table('defects')
    op.drop_table('milestones')
    op.drop_table('tasks')
    op.drop_table('library_changes')
    op.drop_table('library_dependencies')
    op.drop_table('library_versions')
    op.drop_table('libraries')
    op.drop_table('templates')
    op.drop_table('projects')
    op.drop_table('plugins')
