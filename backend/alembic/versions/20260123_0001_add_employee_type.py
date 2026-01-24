"""Add employee_type field for distinguishing internal vs external employees.

Revision ID: 20260123_0001
Revises: 20260120_0002
Create Date: 2026-01-23

This adds an employee_type field to track:
- 'internal' - Regular Proaktiv employees (default)
- 'external' - External contractors, developers, consultants
- 'system' - System/service accounts

External employees can be synced from Vitec Next but are kept separate
from department reporting and Entra ID sync.
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260123_0001"
down_revision = "202601200002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add employee_type column with default 'internal'
    op.add_column(
        "employees",
        sa.Column(
            "employee_type",
            sa.String(20),
            nullable=False,
            server_default="internal",
        ),
    )

    # Add index for filtering by employee type
    op.create_index("idx_employees_employee_type", "employees", ["employee_type"])

    # Add external_company column for tracking contractor company
    op.add_column(
        "employees",
        sa.Column(
            "external_company",
            sa.String(200),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_index("idx_employees_employee_type", table_name="employees")
    op.drop_column("employees", "employee_type")
    op.drop_column("employees", "external_company")
