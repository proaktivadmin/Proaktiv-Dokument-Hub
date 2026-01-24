"""Add Entra ID columns to offices table

Revision ID: 20260124_0004
Revises: 20260124_0003
Create Date: 2026-01-24
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260124_0004"
down_revision = "20260124_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("offices", sa.Column("entra_group_id", sa.String(64), nullable=True))
    op.add_column("offices", sa.Column("entra_group_name", sa.String(255), nullable=True))
    op.add_column("offices", sa.Column("entra_group_mail", sa.String(255), nullable=True))
    op.add_column("offices", sa.Column("entra_group_description", sa.Text(), nullable=True))
    op.add_column("offices", sa.Column("entra_sharepoint_url", sa.Text(), nullable=True))
    op.add_column("offices", sa.Column("entra_member_count", sa.Integer(), nullable=True))
    op.add_column(
        "offices",
        sa.Column(
            "entra_mismatch_fields",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
    )
    op.add_column("offices", sa.Column("entra_last_synced_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("idx_offices_entra_group_id", "offices", ["entra_group_id"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_offices_entra_group_id", table_name="offices")
    op.drop_column("offices", "entra_last_synced_at")
    op.drop_column("offices", "entra_mismatch_fields")
    op.drop_column("offices", "entra_member_count")
    op.drop_column("offices", "entra_sharepoint_url")
    op.drop_column("offices", "entra_group_description")
    op.drop_column("offices", "entra_group_mail")
    op.drop_column("offices", "entra_group_name")
    op.drop_column("offices", "entra_group_id")
