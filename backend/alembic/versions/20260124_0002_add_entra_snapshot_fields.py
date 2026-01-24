"""Add Entra snapshot fields to employees

Revision ID: 20260124_0002
Revises: 20260124_0001
Create Date: 2026-01-24

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260124_0002"
down_revision = "20260124_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("employees", sa.Column("entra_user_id", sa.String(64), nullable=True))
    op.add_column("employees", sa.Column("entra_mail", sa.String(255), nullable=True))
    op.add_column("employees", sa.Column("entra_display_name", sa.String(255), nullable=True))
    op.add_column("employees", sa.Column("entra_given_name", sa.String(100), nullable=True))
    op.add_column("employees", sa.Column("entra_surname", sa.String(100), nullable=True))
    op.add_column("employees", sa.Column("entra_job_title", sa.String(100), nullable=True))
    op.add_column("employees", sa.Column("entra_mobile_phone", sa.String(50), nullable=True))
    op.add_column("employees", sa.Column("entra_department", sa.String(200), nullable=True))
    op.add_column("employees", sa.Column("entra_office_location", sa.String(100), nullable=True))
    op.add_column("employees", sa.Column("entra_street_address", sa.String(255), nullable=True))
    op.add_column("employees", sa.Column("entra_postal_code", sa.String(20), nullable=True))
    op.add_column("employees", sa.Column("entra_country", sa.String(10), nullable=True))
    op.add_column("employees", sa.Column("entra_account_enabled", sa.Boolean(), nullable=True))
    op.add_column(
        "employees",
        sa.Column(
            "entra_mismatch_fields",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
    )
    op.add_column("employees", sa.Column("entra_last_synced_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("employees", "entra_last_synced_at")
    op.drop_column("employees", "entra_mismatch_fields")
    op.drop_column("employees", "entra_account_enabled")
    op.drop_column("employees", "entra_country")
    op.drop_column("employees", "entra_postal_code")
    op.drop_column("employees", "entra_street_address")
    op.drop_column("employees", "entra_office_location")
    op.drop_column("employees", "entra_department")
    op.drop_column("employees", "entra_mobile_phone")
    op.drop_column("employees", "entra_job_title")
    op.drop_column("employees", "entra_surname")
    op.drop_column("employees", "entra_given_name")
    op.drop_column("employees", "entra_display_name")
    op.drop_column("employees", "entra_mail")
    op.drop_column("employees", "entra_user_id")
