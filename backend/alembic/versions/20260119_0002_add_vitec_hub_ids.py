"""Add Vitec Hub identifiers to offices/employees

Revision ID: 20260119_0002
Revises: 20260119_0001
Create Date: 2026-01-19
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "202601190002"
down_revision = "202601190001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("offices", sa.Column("vitec_department_id", sa.Integer(), nullable=True))
    op.create_index(
        "idx_offices_vitec_department_id",
        "offices",
        ["vitec_department_id"],
        unique=False,
    )

    op.add_column("employees", sa.Column("vitec_employee_id", sa.String(length=100), nullable=True))
    op.create_index(
        "idx_employees_vitec_employee_id",
        "employees",
        ["vitec_employee_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_employees_vitec_employee_id", table_name="employees")
    op.drop_column("employees", "vitec_employee_id")

    op.drop_index("idx_offices_vitec_department_id", table_name="offices")
    op.drop_column("offices", "vitec_department_id")
