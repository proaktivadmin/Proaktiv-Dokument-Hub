"""Add content column to templates for HTML storage

Revision ID: 0002
Revises: 0001
Create Date: 2025-12-14

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add content column for storing HTML template content directly."""
    op.add_column('templates', sa.Column('content', sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove content column."""
    op.drop_column('templates', 'content')



