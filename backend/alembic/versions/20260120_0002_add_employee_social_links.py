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
    op.add_column("employees", sa.Column("facebook_url", sa.Text(), nullable=True))
    op.add_column("employees", sa.Column("instagram_url", sa.Text(), nullable=True))
    op.add_column("employees", sa.Column("twitter_url", sa.Text(), nullable=True))
    op.add_column(
        "employees",
        sa.Column(
            "is_featured_broker",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )


def downgrade() -> None:
    op.drop_column("employees", "is_featured_broker")
    op.drop_column("employees", "twitter_url")
    op.drop_column("employees", "instagram_url")
    op.drop_column("employees", "facebook_url")
