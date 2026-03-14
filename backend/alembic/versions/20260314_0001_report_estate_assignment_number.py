"""Add assignment_number (oppdragsnummer) to report_sales_estate_cache

Revision ID: 20260314_0001
Revises: 20260312_0002
Create Date: 2026-03-14

"""

import sqlalchemy as sa

from alembic import op

revision = "20260314_0001"
down_revision = "20260312_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "report_sales_estate_cache",
        sa.Column("assignment_number", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("report_sales_estate_cache", "assignment_number")
