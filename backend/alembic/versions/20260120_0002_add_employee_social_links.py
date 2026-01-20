"""Add employee social links and featured flag

Revision ID: 20260120_0002
Revises: 20260120_0001
Create Date: 2026-01-20
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "202601200002"
down_revision = "202601200001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use IF NOT EXISTS to make migration idempotent
    # (columns may have been added manually)
    op.execute("ALTER TABLE employees ADD COLUMN IF NOT EXISTS facebook_url TEXT")
    op.execute("ALTER TABLE employees ADD COLUMN IF NOT EXISTS instagram_url TEXT")
    op.execute("ALTER TABLE employees ADD COLUMN IF NOT EXISTS twitter_url TEXT")
    op.execute("ALTER TABLE employees ADD COLUMN IF NOT EXISTS is_featured_broker BOOLEAN DEFAULT FALSE")


def downgrade() -> None:
    op.drop_column("employees", "is_featured_broker")
    op.drop_column("employees", "twitter_url")
    op.drop_column("employees", "instagram_url")
    op.drop_column("employees", "facebook_url")
