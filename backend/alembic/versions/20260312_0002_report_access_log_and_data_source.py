"""Add report_access_log table and data_source column to cache tables

Revision ID: 20260312_0002
Revises: 20260312_0001
Create Date: 2026-03-12

Adds:
- report_access_log table for audit trail of report views/downloads/emails
- data_source column on report_sales_estate_cache and report_sales_transaction_cache
  to support multi-source ingestion (Vitec Next live sync + future legacy import)

Post-migration verification:
    SELECT data_source, COUNT(*) FROM report_sales_transaction_cache GROUP BY data_source;
    SELECT data_source, COUNT(*) FROM report_sales_estate_cache GROUP BY data_source;
    -- Both should show only 'vitec_next' rows.

Retention policy for report_access_log (run periodically):
    DELETE FROM report_access_log WHERE created_at < now() - interval '90 days';
    UPDATE report_access_log SET ip_address = NULL
     WHERE created_at < now() - interval '30 days' AND ip_address IS NOT NULL;
"""

import sqlalchemy as sa

from alembic import op

revision = "20260312_0002"
down_revision = "20260312_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- report_access_log ---
    op.create_table(
        "report_access_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_email", sa.String(length=200), nullable=False, server_default="anonymous"),
        sa.Column("endpoint", sa.String(length=200), nullable=False),
        sa.Column("action", sa.String(length=30), nullable=False, server_default="view"),
        sa.Column("params_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_report_access_log_user", "report_access_log", ["user_email"], unique=False)
    op.create_index("idx_report_access_log_created", "report_access_log", ["created_at"], unique=False)

    # --- data_source on estate cache ---
    op.add_column(
        "report_sales_estate_cache",
        sa.Column("data_source", sa.String(length=30), nullable=False, server_default="vitec_next"),
    )
    op.create_index(
        "idx_report_sales_estate_cache_source", "report_sales_estate_cache", ["data_source"], unique=False,
    )
    op.create_index(
        "idx_report_sales_estate_cache_dept_source",
        "report_sales_estate_cache",
        ["department_id", "data_source"],
        unique=False,
    )

    # --- data_source on transaction cache ---
    op.add_column(
        "report_sales_transaction_cache",
        sa.Column("data_source", sa.String(length=30), nullable=False, server_default="vitec_next"),
    )
    op.create_index(
        "idx_report_sales_tx_cache_source", "report_sales_transaction_cache", ["data_source"], unique=False,
    )
    op.create_index(
        "idx_report_sales_tx_cache_dept_source_date",
        "report_sales_transaction_cache",
        ["department_id", "data_source", "posting_date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_report_sales_tx_cache_dept_source_date", table_name="report_sales_transaction_cache")
    op.drop_index("idx_report_sales_tx_cache_source", table_name="report_sales_transaction_cache")
    op.drop_column("report_sales_transaction_cache", "data_source")

    op.drop_index("idx_report_sales_estate_cache_dept_source", table_name="report_sales_estate_cache")
    op.drop_index("idx_report_sales_estate_cache_source", table_name="report_sales_estate_cache")
    op.drop_column("report_sales_estate_cache", "data_source")

    op.drop_index("idx_report_access_log_created", table_name="report_access_log")
    op.drop_index("idx_report_access_log_user", table_name="report_access_log")
    op.drop_table("report_access_log")
