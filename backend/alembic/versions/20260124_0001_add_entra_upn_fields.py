"""Add Entra UPN fields to employees

Revision ID: 20260124_0001
Revises: 20260123_0002
Create Date: 2026-01-24

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260124_0001"
down_revision = "20260123_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add entra_upn field to store the User Principal Name from Entra ID
    op.add_column(
        "employees",
        sa.Column("entra_upn", sa.String(255), nullable=True),
    )

    # Add entra_upn_mismatch flag to indicate if UPN differs from email
    op.add_column(
        "employees",
        sa.Column("entra_upn_mismatch", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("employees", "entra_upn_mismatch")
    op.drop_column("employees", "entra_upn")
