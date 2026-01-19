"""Add office/employee profile fields

Revision ID: 20260119_0001
Revises: 20260118_0003_firecrawl_scrapes
Create Date: 2026-01-19
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "202601190001"
down_revision = "202601180003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("offices", sa.Column("profile_image_url", sa.Text(), nullable=True))
    op.add_column("offices", sa.Column("description", sa.Text(), nullable=True))

    op.add_column("employees", sa.Column("profile_image_url", sa.Text(), nullable=True))
    op.add_column("employees", sa.Column("description", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("employees", "description")
    op.drop_column("employees", "profile_image_url")

    op.drop_column("offices", "description")
    op.drop_column("offices", "profile_image_url")
