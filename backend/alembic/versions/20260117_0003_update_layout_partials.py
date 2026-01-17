"""Update layout_partials for signatures and document types

Revision ID: 0006
Revises: 0005
Create Date: 2026-01-17 12:00:00.000000

This migration:
1. Adds 'document_type' column for specialized footers
2. Updates type constraint to include 'signature'
3. Updates context constraint to include 'sms'
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0006'
down_revision: str = '0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add document_type column
    op.add_column(
        'layout_partials',
        sa.Column('document_type', sa.String(50), nullable=True)
    )
    
    # Create index for document_type
    op.create_index(
        'idx_layout_partials_document_type',
        'layout_partials',
        ['document_type']
    )
    
    # Drop old constraints
    op.drop_constraint('ck_layout_partial_type', 'layout_partials', type_='check')
    op.drop_constraint('ck_layout_partial_context', 'layout_partials', type_='check')
    
    # Create new constraints with expanded values
    op.create_check_constraint(
        'ck_layout_partial_type_v2',
        'layout_partials',
        "type IN ('header', 'footer', 'signature')"
    )
    op.create_check_constraint(
        'ck_layout_partial_context_v2',
        'layout_partials',
        "context IN ('pdf', 'email', 'sms', 'all')"
    )


def downgrade() -> None:
    # Drop new constraints
    op.drop_constraint('ck_layout_partial_type_v2', 'layout_partials', type_='check')
    op.drop_constraint('ck_layout_partial_context_v2', 'layout_partials', type_='check')
    
    # Restore old constraints
    op.create_check_constraint(
        'ck_layout_partial_type',
        'layout_partials',
        "type IN ('header', 'footer')"
    )
    op.create_check_constraint(
        'ck_layout_partial_context',
        'layout_partials',
        "context IN ('pdf', 'email', 'all')"
    )
    
    # Drop index and column
    op.drop_index('idx_layout_partials_document_type', 'layout_partials')
    op.drop_column('layout_partials', 'document_type')
