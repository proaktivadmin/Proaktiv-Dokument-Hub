"""Fix JSONB columns - NO-OP for Railway

Revision ID: 0004
Revises: 0003
Create Date: 2026-01-17 00:30:00.000000

Note: This migration was originally intended to convert text[] columns to JSONB.
However, the V2 migration (0003) already creates all JSON columns as JSONB.
This migration is kept for schema version tracking but performs no operations.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0004'
down_revision: str = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    No-op migration.
    
    The columns phases, departments, extra_receivers, assignment_types, 
    ownership_types are already created as JSONB in migration 0003.
    This migration is kept for version tracking purposes only.
    """
    pass


def downgrade() -> None:
    """No-op downgrade."""
    pass
