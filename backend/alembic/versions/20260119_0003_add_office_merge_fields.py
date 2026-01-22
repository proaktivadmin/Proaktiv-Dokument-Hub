"""Add office merge fields: organization_number, legal_name, banner_image_url

Revision ID: 20260119_0003
Revises: 20260119_0002
Create Date: 2026-01-19

Adds fields to support merging offices by organization number and storing
both marketing name (name) and legal name separately.
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "202601190003"
down_revision = "202601190002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use IF NOT EXISTS to make migration idempotent
    op.execute("ALTER TABLE offices ADD COLUMN IF NOT EXISTS organization_number VARCHAR(20)")
    op.execute("ALTER TABLE offices ADD COLUMN IF NOT EXISTS legal_name VARCHAR(200)")
    op.execute("ALTER TABLE offices ADD COLUMN IF NOT EXISTS banner_image_url TEXT")

    # Create index if not exists
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_offices_organization_number
        ON offices (organization_number)
    """)


def downgrade() -> None:
    op.drop_column("offices", "banner_image_url")
    op.drop_column("offices", "legal_name")
    op.drop_index("idx_offices_organization_number", table_name="offices")
    op.drop_column("offices", "organization_number")
