"""Add parent_office_id for sub-departments.

Revision ID: 20260123_0002
Revises: 20260123_0001
Create Date: 2026-01-23

This adds support for sub-departments (e.g., Næring, Næringsoppgjør)
that should be displayed under their parent office rather than as
separate top-level offices.
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260123_0002"
down_revision = "20260123_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add parent_office_id for sub-department hierarchy
    op.add_column(
        "offices",
        sa.Column(
            "parent_office_id",
            UUID(as_uuid=True),
            sa.ForeignKey("offices.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    # Add index for parent lookup
    op.create_index("idx_offices_parent_office_id", "offices", ["parent_office_id"])

    # Add office_type to distinguish main offices from sub-departments
    op.add_column(
        "offices",
        sa.Column(
            "office_type",
            sa.String(20),
            nullable=False,
            server_default="main",  # 'main', 'sub', 'regional'
        ),
    )


def downgrade() -> None:
    op.drop_index("idx_offices_parent_office_id", table_name="offices")
    op.drop_column("offices", "parent_office_id")
    op.drop_column("offices", "office_type")
