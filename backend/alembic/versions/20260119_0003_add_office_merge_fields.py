"""Add office merge fields: organization_number, legal_name, banner_image_url

Revision ID: 20260119_0003
Revises: 20260119_0002
Create Date: 2026-01-19

Adds fields to support merging offices by organization number and storing
both marketing name (name) and legal name separately.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "202601190003"
down_revision = "202601190002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add organization_number for matching/merging offices
    op.add_column(
        "offices",
        sa.Column("organization_number", sa.String(length=20), nullable=True)
    )
    op.create_index(
        "idx_offices_organization_number",
        "offices",
        ["organization_number"],
        unique=False,
    )
    
    # Add legal_name to store the legal company name separately
    op.add_column(
        "offices",
        sa.Column("legal_name", sa.String(length=200), nullable=True)
    )
    
    # Add banner_image_url for office card banners
    op.add_column(
        "offices",
        sa.Column("banner_image_url", sa.Text(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("offices", "banner_image_url")
    op.drop_column("offices", "legal_name")
    op.drop_index("idx_offices_organization_number", table_name="offices")
    op.drop_column("offices", "organization_number")
