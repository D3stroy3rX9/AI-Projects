"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-11-07 20:20:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    sentiment_label_enum = postgresql.ENUM(
        'positive', 'neutral', 'negative',
        name='sentimentlabelenum'
    )
    sentiment_label_enum.create(op.get_bind())

    source_enum = postgresql.ENUM(
        'api', 'batch', 'webhook',
        name='sourceenum'
    )
    source_enum.create(op.get_bind())

    # Create models table
    op.create_table(
        'models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('algorithm', sa.String(length=100), nullable=False),
        sa.Column('f1_score', sa.Float(), nullable=False),
        sa.Column('training_samples', sa.Integer(), nullable=False),
        sa.Column('vocabulary_size', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('model_path', sa.String(length=500), nullable=True),
        sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.CheckConstraint('f1_score >= 0 AND f1_score <= 1', name='f1_range'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_models_id', 'models', ['id'])
    op.create_index('ix_models_is_active', 'models', ['is_active'])
    op.create_index('ix_models_active_created', 'models', ['is_active', 'created_at'])

    # Create training_data table
    op.create_table(
        'training_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('label', sentiment_label_enum, nullable=False),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('used_in_training', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_training_data_id', 'training_data', ['id'])
    op.create_index('ix_training_data_label', 'training_data', ['label'])
    op.create_index('ix_training_data_used_in_training', 'training_data', ['used_in_training'])

    # Create analysis table
    op.create_table(
        'analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('text_hash', sa.String(length=64), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('sentiment_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('emotion_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('predicted_label', sentiment_label_enum, nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('analyzed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('source', source_enum, nullable=False),
        sa.Column('extra_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.CheckConstraint('confidence >= 0 AND confidence <= 1', name='confidence_range'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('text_hash')
    )
    op.create_index('ix_analysis_id', 'analysis', ['id'])
    op.create_index('ix_analysis_text_hash', 'analysis', ['text_hash'])
    op.create_index('ix_analysis_predicted_label', 'analysis', ['predicted_label'])
    op.create_index('ix_analysis_analyzed_at', 'analysis', ['analyzed_at'])
    op.create_index('ix_analysis_source', 'analysis', ['source'])
    op.create_index('ix_analysis_label_time', 'analysis', ['predicted_label', 'analyzed_at'])

    # Create analytics_summary table
    op.create_table(
        'analytics_summary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('hour', sa.Integer(), nullable=True),
        sa.Column('sentiment_avg', sa.Float(), nullable=False),
        sa.Column('positive_count', sa.Integer(), nullable=False),
        sa.Column('neutral_count', sa.Integer(), nullable=False),
        sa.Column('negative_count', sa.Integer(), nullable=False),
        sa.Column('total_count', sa.Integer(), nullable=False),
        sa.CheckConstraint('total_count = positive_count + neutral_count + negative_count', name='count_sum'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_analytics_summary_id', 'analytics_summary', ['id'])
    op.create_index('ix_analytics_summary_date', 'analytics_summary', ['date'])
    op.create_index('ix_summary_date_hour', 'analytics_summary', ['date', 'hour'])

    # Enable TimescaleDB extension (if available)
    # Note: This requires TimescaleDB to be installed
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")

    # Convert analysis table to hypertable for time-series data
    op.execute("""
        SELECT create_hypertable(
            'analysis',
            'analyzed_at',
            if_not_exists => TRUE,
            migrate_data => TRUE
        );
    """)


def downgrade() -> None:
    # Drop tables
    op.drop_index('ix_summary_date_hour', table_name='analytics_summary')
    op.drop_index('ix_analytics_summary_date', table_name='analytics_summary')
    op.drop_index('ix_analytics_summary_id', table_name='analytics_summary')
    op.drop_table('analytics_summary')

    op.drop_index('ix_analysis_label_time', table_name='analysis')
    op.drop_index('ix_analysis_source', table_name='analysis')
    op.drop_index('ix_analysis_analyzed_at', table_name='analysis')
    op.drop_index('ix_analysis_predicted_label', table_name='analysis')
    op.drop_index('ix_analysis_text_hash', table_name='analysis')
    op.drop_index('ix_analysis_id', table_name='analysis')
    op.drop_table('analysis')

    op.drop_index('ix_training_data_used_in_training', table_name='training_data')
    op.drop_index('ix_training_data_label', table_name='training_data')
    op.drop_index('ix_training_data_id', table_name='training_data')
    op.drop_table('training_data')

    op.drop_index('ix_models_active_created', table_name='models')
    op.drop_index('ix_models_is_active', table_name='models')
    op.drop_index('ix_models_id', table_name='models')
    op.drop_table('models')

    # Drop enum types
    sa.Enum(name='sourceenum').drop(op.get_bind())
    sa.Enum(name='sentimentlabelenum').drop(op.get_bind())
