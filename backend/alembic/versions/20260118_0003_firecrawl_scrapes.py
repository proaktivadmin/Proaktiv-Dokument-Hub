"""Add Firecrawl scrape history table

Revision ID: 20260118_0003
Revises: 20260118_0002_add_microsoft_integration
Create Date: 2026-01-18

Creates `firecrawl_scrapes` to store scrape requests + results.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "202601180003"
down_revision = "202601180002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "firecrawl_scrapes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("requested_formats", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default="[]"),
        sa.Column("only_main_content", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("wait_for_ms", sa.Integer(), nullable=True),
        sa.Column("timeout_ms", sa.Integer(), nullable=True),
        sa.Column("include_tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default="[]"),
        sa.Column("exclude_tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default="[]"),
        sa.Column("result_markdown", sa.Text(), nullable=True),
        sa.Column("result_html", sa.Text(), nullable=True),
        sa.Column("result_raw_html", sa.Text(), nullable=True),
        sa.Column("result_links", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default="[]"),
        sa.Column("result_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default="{}"),
        sa.Column("result_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default="{}"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_firecrawl_scrapes")),
    )
    op.create_index("idx_firecrawl_scrapes_created_at", "firecrawl_scrapes", ["created_at"], unique=False)
    op.create_index("idx_firecrawl_scrapes_status", "firecrawl_scrapes", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_firecrawl_scrapes_status", table_name="firecrawl_scrapes")
    op.drop_index("idx_firecrawl_scrapes_created_at", table_name="firecrawl_scrapes")
    op.drop_table("firecrawl_scrapes")
