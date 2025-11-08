"""Initial schema - translations table

Revision ID: 001
Revises:
Create Date: 2024-11-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create translations table"""
    op.create_table(
        'translations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('source_language', sa.String(10), nullable=False),
        sa.Column('target_language', sa.String(10), nullable=False),
        sa.Column('source_text', sa.Text(), nullable=False),
        sa.Column('translated_text', sa.Text(), nullable=False),
        sa.Column('audio_duration', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('user_id', sa.String(255), nullable=True),
        sa.Column('session_id', sa.String(255), nullable=True),
    )

    # Create indexes for common queries
    op.create_index('idx_translations_created_at', 'translations', ['created_at'])
    op.create_index('idx_translations_session_id', 'translations', ['session_id'])
    op.create_index('idx_translations_user_id', 'translations', ['user_id'])


def downgrade() -> None:
    """Drop translations table"""
    op.drop_index('idx_translations_user_id', 'translations')
    op.drop_index('idx_translations_session_id', 'translations')
    op.drop_index('idx_translations_created_at', 'translations')
    op.drop_table('translations')
