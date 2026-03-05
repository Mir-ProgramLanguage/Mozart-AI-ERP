"""初始化数据库表结构

Revision ID: 001_initial
Revises: 
Create Date: 2026-03-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建 actors 表
    op.create_table(
        'actors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('display_name', sa.String(50), nullable=False),
        sa.Column('actor_type', sa.String(20), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('ai_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('capabilities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('capability_history', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('total_contributions', sa.Numeric(12, 2), nullable=True),
        sa.Column('contributions_by_type', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('contribution_count', sa.Integer(), nullable=True),
        sa.Column('total_rewards', sa.Numeric(12, 2), nullable=True),
        sa.Column('available_rewards', sa.Numeric(12, 2), nullable=True),
        sa.Column('reward_history', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('trust_score', sa.Numeric(3, 2), nullable=True),
        sa.Column('reputation_score', sa.Numeric(3, 2), nullable=True),
        sa.Column('current_tasks', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('availability', sa.Numeric(3, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_active', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('display_name')
    )
    op.create_index(op.f('ix_actors_actor_type'), 'actors', ['actor_type'], unique=False)
    op.create_index(op.f('ix_actors_user_id'), 'actors', ['user_id'], unique=False)

    # 创建 events 表
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('attachments', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_analysis', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('contribution_type', sa.String(50), nullable=True),
        sa.Column('contribution_status', sa.String(20), nullable=True),
        sa.Column('contribution_value', sa.Numeric(12, 2), nullable=True),
        sa.Column('value_confidence', sa.Numeric(3, 2), nullable=True),
        sa.Column('actual_value', sa.Numeric(12, 2), nullable=True),
        sa.Column('value_realized_at', sa.DateTime(), nullable=True),
        sa.Column('value_calculation', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('related_events', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('related_tasks', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('beneficiaries', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_actor_id'), 'events', ['actor_id'], unique=False)
    op.create_index(op.f('ix_events_contribution_type'), 'events', ['contribution_type'], unique=False)
    op.create_index(op.f('ix_events_contribution_status'), 'events', ['contribution_status'], unique=False)
    op.create_index(op.f('ix_events_created_at'), 'events', ['created_at'], unique=False)

    # 创建 rewards 表
    op.create_table(
        'rewards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reward_type', sa.String(50), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('contribution_type', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('claimed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rewards_actor_id'), 'rewards', ['actor_id'], unique=False)
    op.create_index(op.f('ix_rewards_status'), 'rewards', ['status'], unique=False)

    # 创建 tasks 表
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('assigned_to', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('related_events', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_status'), 'tasks', ['status'], unique=False)

    # 创建 actor_interactions 表
    op.create_table(
        'actor_interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interaction_type', sa.String(30), nullable=False),
        sa.Column('from_actor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('from_actor_name', sa.String(50), nullable=True),
        sa.Column('to_actor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('to_actor_name', sa.String(50), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('context', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_response', sa.Text(), nullable=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('events_created', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_actor_interactions_interaction_type'), 'actor_interactions', ['interaction_type'], unique=False)
    op.create_index(op.f('ix_actor_interactions_from_actor_id'), 'actor_interactions', ['from_actor_id'], unique=False)
    op.create_index(op.f('ix_actor_interactions_to_actor_id'), 'actor_interactions', ['to_actor_id'], unique=False)
    op.create_index(op.f('ix_actor_interactions_status'), 'actor_interactions', ['status'], unique=False)
    op.create_index(op.f('ix_actor_interactions_created_at'), 'actor_interactions', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_actor_interactions_created_at'), table_name='actor_interactions')
    op.drop_index(op.f('ix_actor_interactions_status'), table_name='actor_interactions')
    op.drop_index(op.f('ix_actor_interactions_to_actor_id'), table_name='actor_interactions')
    op.drop_index(op.f('ix_actor_interactions_from_actor_id'), table_name='actor_interactions')
    op.drop_index(op.f('ix_actor_interactions_interaction_type'), table_name='actor_interactions')
    op.drop_table('actor_interactions')

    op.drop_index(op.f('ix_tasks_status'), table_name='tasks')
    op.drop_table('tasks')

    op.drop_index(op.f('ix_rewards_status'), table_name='rewards')
    op.drop_index(op.f('ix_rewards_actor_id'), table_name='rewards')
    op.drop_table('rewards')

    op.drop_index(op.f('ix_events_created_at'), table_name='events')
    op.drop_index(op.f('ix_events_contribution_status'), table_name='events')
    op.drop_index(op.f('ix_events_contribution_type'), table_name='events')
    op.drop_index(op.f('ix_events_actor_id'), table_name='events')
    op.drop_table('events')

    op.drop_index(op.f('ix_actors_user_id'), table_name='actors')
    op.drop_index(op.f('ix_actors_actor_type'), table_name='actors')
    op.drop_table('actors')
