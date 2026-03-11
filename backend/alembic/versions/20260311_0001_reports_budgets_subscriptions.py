"""Add report budgets and subscriptions tables

Revision ID: 20260311_0001
Revises: 20260221_0001
Create Date: 2026-03-11
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260311_0001"
down_revision = "20260221_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "report_budgets",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=True),
        sa.Column("budget_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("idx_report_budgets_department_year", "report_budgets", ["department_id", "year"], unique=False)
    op.create_index("idx_report_budgets_year_month", "report_budgets", ["year", "month"], unique=False)

    op.create_table(
        "report_subscriptions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("report_type", sa.String(length=50), nullable=False, server_default="best_performers"),
        sa.Column("cadence", sa.String(length=20), nullable=False, server_default="weekly"),
        sa.Column("recipients", sa.JSON(), nullable=False),
        sa.Column("department_ids", sa.JSON(), nullable=False),
        sa.Column("include_vat", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("day_of_week", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("day_of_month", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("send_hour", sa.Integer(), nullable=False, server_default="8"),
        sa.Column("timezone", sa.String(length=50), nullable=False, server_default="Europe/Oslo"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_status", sa.String(length=20), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("idx_report_subscriptions_active", "report_subscriptions", ["is_active"], unique=False)
    op.create_index("idx_report_subscriptions_next_run", "report_subscriptions", ["next_run_at"], unique=False)
    op.create_index("idx_report_subscriptions_cadence", "report_subscriptions", ["cadence"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_report_subscriptions_cadence", table_name="report_subscriptions")
    op.drop_index("idx_report_subscriptions_next_run", table_name="report_subscriptions")
    op.drop_index("idx_report_subscriptions_active", table_name="report_subscriptions")
    op.drop_table("report_subscriptions")

    op.drop_index("idx_report_budgets_year_month", table_name="report_budgets")
    op.drop_index("idx_report_budgets_department_year", table_name="report_budgets")
    op.drop_table("report_budgets")
