"""Add report sales cache tables

Revision ID: 20260312_0001
Revises: 20260311_0001
Create Date: 2026-03-12
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260312_0001"
down_revision = "20260311_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "report_sales_estate_cache",
        sa.Column("estate_key", sa.String(length=120), primary_key=True),
        sa.Column("installation_id", sa.String(length=50), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("estate_id", sa.String(length=64), nullable=False),
        sa.Column("sold_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("address", sa.Text(), nullable=False, server_default=""),
        sa.Column("property_type", sa.String(length=100), nullable=False, server_default="—"),
        sa.Column("assignment_type", sa.String(length=100), nullable=False, server_default="—"),
        sa.Column("brokers", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_report_sales_estate_cache_dept", "report_sales_estate_cache", ["department_id"], unique=False)
    op.create_index(
        "idx_report_sales_estate_cache_installation",
        "report_sales_estate_cache",
        ["installation_id"],
        unique=False,
    )
    op.create_index("idx_report_sales_estate_cache_sold", "report_sales_estate_cache", ["sold_at"], unique=False)

    op.create_table(
        "report_sales_transaction_cache",
        sa.Column("transaction_key", sa.String(length=80), primary_key=True),
        sa.Column("installation_id", sa.String(length=50), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("posting_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("account", sa.String(length=16), nullable=False, server_default=""),
        sa.Column("user_id", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("estate_id", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("vat_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "idx_report_sales_tx_cache_dept_date",
        "report_sales_transaction_cache",
        ["department_id", "posting_date"],
        unique=False,
    )
    op.create_index(
        "idx_report_sales_tx_cache_installation",
        "report_sales_transaction_cache",
        ["installation_id"],
        unique=False,
    )
    op.create_index("idx_report_sales_tx_cache_user", "report_sales_transaction_cache", ["user_id"], unique=False)
    op.create_index("idx_report_sales_tx_cache_estate", "report_sales_transaction_cache", ["estate_id"], unique=False)
    op.create_index("idx_report_sales_tx_cache_account", "report_sales_transaction_cache", ["account"], unique=False)

    op.create_table(
        "report_sales_cache_state",
        sa.Column("state_key", sa.String(length=120), primary_key=True),
        sa.Column("installation_id", sa.String(length=50), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("last_estates_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("month_sync", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_report_sales_cache_state_dept", "report_sales_cache_state", ["department_id"], unique=False)
    op.create_index(
        "idx_report_sales_cache_state_installation",
        "report_sales_cache_state",
        ["installation_id"],
        unique=False,
    )

    op.create_table(
        "report_sales_sync_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("installation_id", sa.String(length=50), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=40), nullable=False, server_default="cache_sync"),
        sa.Column("from_date", sa.String(length=32), nullable=False),
        sa.Column("to_date", sa.String(length=32), nullable=False),
        sa.Column("estates_upserted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("transactions_upserted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_report_sales_sync_events_created", "report_sales_sync_events", ["created_at"], unique=False)
    op.create_index(
        "idx_report_sales_sync_events_dept_created",
        "report_sales_sync_events",
        ["department_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "idx_report_sales_sync_events_installation",
        "report_sales_sync_events",
        ["installation_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_report_sales_sync_events_installation", table_name="report_sales_sync_events")
    op.drop_index("idx_report_sales_sync_events_dept_created", table_name="report_sales_sync_events")
    op.drop_index("idx_report_sales_sync_events_created", table_name="report_sales_sync_events")
    op.drop_table("report_sales_sync_events")

    op.drop_index("idx_report_sales_cache_state_installation", table_name="report_sales_cache_state")
    op.drop_index("idx_report_sales_cache_state_dept", table_name="report_sales_cache_state")
    op.drop_table("report_sales_cache_state")

    op.drop_index("idx_report_sales_tx_cache_account", table_name="report_sales_transaction_cache")
    op.drop_index("idx_report_sales_tx_cache_estate", table_name="report_sales_transaction_cache")
    op.drop_index("idx_report_sales_tx_cache_user", table_name="report_sales_transaction_cache")
    op.drop_index("idx_report_sales_tx_cache_installation", table_name="report_sales_transaction_cache")
    op.drop_index("idx_report_sales_tx_cache_dept_date", table_name="report_sales_transaction_cache")
    op.drop_table("report_sales_transaction_cache")

    op.drop_index("idx_report_sales_estate_cache_sold", table_name="report_sales_estate_cache")
    op.drop_index("idx_report_sales_estate_cache_installation", table_name="report_sales_estate_cache")
    op.drop_index("idx_report_sales_estate_cache_dept", table_name="report_sales_estate_cache")
    op.drop_table("report_sales_estate_cache")
