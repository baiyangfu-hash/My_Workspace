"""V2.1.0: 变更管理模块工程化升级

Revision ID: v21_change_mgmt
Revises: initial_schema
Create Date: 2026-04-12

Upgrade: 为 changes 表添加14个V2.1.0新字段 (二维分类+传播链+分级审批)
Downgrade: 移除所有V2.1.0新增字段
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'v21_change_mgmt'
down_revision: Union[str, None] = 'initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === V2.1.0: 变更管理模块工程化升级 ===
    # 新增字段总数: 19个 (替代/扩展原有8个字段)

    # 1. 二维分类字段 (Domain × Nature × Scope) - 替代原 change_type
    op.add_column('changes', sa.Column('domain', sa.String(10), nullable=True, server_default='PLC'))
    op.add_column('changes', sa.Column('nature', sa.String(10), nullable=True, server_default='OPT'))
    op.add_column('changes', sa.Column('scope', sa.String(10), nullable=True, server_default='LOCAL'))

    # 2. 优先级和详细内容
    op.add_column('changes', sa.Column('priority', sa.String(10), nullable=True, server_default='P2'))
    op.add_column('changes', sa.Column('reason', sa.Text(), nullable=True))
    op.add_column('changes', sa.Column('content_before', sa.Text(), nullable=True))
    op.add_column('changes', sa.Column('content_after', sa.Text(), nullable=True))
    op.add_column('changes', sa.Column('impact_analysis', sa.Text(), nullable=True))

    # 3. 传播链与关联变更
    op.add_column('changes', sa.Column('related_changes', sa.JSON(), nullable=True))
    op.add_column('changes', sa.Column('propagation_chain', sa.Text(), nullable=True))

    # 4. 分级审批字段
    op.add_column('changes', sa.Column('approval_level', sa.String(30), nullable=True))
    op.add_column('changes', sa.Column('reviewer', sa.String(50), nullable=True))

    # 5. 完整时间戳链
    op.add_column('changes', sa.Column('approved_at', sa.DateTime(), nullable=True))
    op.add_column('changes', sa.Column('implemented_at', sa.DateTime(), nullable=True))
    op.add_column('changes', sa.Column('completed_at', sa.DateTime(), nullable=True))

    # 6. 细化人员字段 (替代原 requested_by)
    op.add_column('changes', sa.Column('proposer', sa.String(100), nullable=True))
    op.add_column('changes', sa.Column('approver', sa.String(100), nullable=True))
    op.add_column('changes', sa.Column('implementer', sa.String(100), nullable=True))
    op.add_column('changes', sa.Column('attachment', sa.String(500), nullable=True))

    # 7. 数据迁移: 将旧字段的值映射到新字段 (向后兼容)
    op.execute("""
        UPDATE changes SET
            proposer = requested_by,
            domain = CASE
                WHEN change_type IN ('需求变更', '需求') THEN 'REQ'
                WHEN change_type IN ('缺陷修复', '缺陷') THEN 'DEF'
                WHEN change_type IN ('优化改进', '优化', '技术变更', '其他变更') THEN 'OPT'
                WHEN change_type IN ('配置调整', '配置', '资源变更') THEN 'CFG'
                WHEN change_type IN ('紧急变更', '紧急', '进度变更') THEN 'EMRG'
                ELSE 'OPT'
            END,
            nature = CASE
                WHEN change_type IN ('需求变更', '需求', '进度变更') THEN 'REQ'
                WHEN change_type IN ('缺陷修复', '缺陷') THEN 'DEF'
                WHEN change_type IN ('优化改进', '优化', '技术变更', '其他变更') THEN 'OPT'
                WHEN change_type IN ('配置调整', '配置', '资源变更') THEN 'CFG'
                WHEN change_type IN ('紧急变更', '紧急') THEN 'EMRG'
                ELSE 'OPT'
            END,
            scope = CASE
                WHEN description LIKE '%全局%' OR description LIKE '%系统%' OR description LIKE '%整体%' THEN 'SYSTEM'
                WHEN description LIKE '%模块%' OR description LIKE '%部分%' OR description LIKE '%多%' THEN 'MODULE'
                WHEN description LIKE '%局部%' OR description LIKE '%小%' OR description LIKE '%单%' THEN 'LOCAL'
                ELSE 'LOCAL'
            END,
            reason = description,
            impact_analysis = description
        WHERE requested_by IS NOT NULL
           OR change_type IS NOT NULL
    """)


def downgrade() -> None:
    # 按添加顺序逆序移除所有V2.1.0新增字段
    new_columns = [
        'attachment',
        'implementer',
        'approver',
        'proposer',
        'completed_at',
        'implemented_at',
        'approved_at',
        'reviewer',
        'approval_level',
        'propagation_chain',
        'related_changes',
        'impact_analysis',
        'content_after',
        'content_before',
        'reason',
        'priority',
        'scope',
        'nature',
        'domain',
    ]
    for col in new_columns:
        op.drop_column('changes', col)
