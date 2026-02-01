"""Add signature_overrides table

Revision ID: 20260201_0001
Revises: 20260124_0004
Create Date: 2026-02-01
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260201_0001"
down_revision = "20260124_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "signature_overrides",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "employee_id",
            sa.String(36),
            sa.ForeignKey("employees.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        # Contact overrides
        sa.Column("display_name", sa.String(200), nullable=True),
        sa.Column("job_title", sa.String(100), nullable=True),
        sa.Column("mobile_phone", sa.String(50), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("office_name", sa.String(200), nullable=True),
        # Social URL overrides
        sa.Column("facebook_url", sa.Text, nullable=True),
        sa.Column("instagram_url", sa.Text, nullable=True),
        sa.Column("linkedin_url", sa.Text, nullable=True),
        sa.Column("employee_url", sa.Text, nullable=True),
        # Audit timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_signature_overrides_employee_id", "signature_overrides", ["employee_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_signature_overrides_employee_id", table_name="signature_overrides")
    op.drop_table("signature_overrides")
