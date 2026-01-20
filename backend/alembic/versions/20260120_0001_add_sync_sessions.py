"""Add sync_sessions table

Revision ID: 20260120_0001
Revises: 20260119_0003
Create Date: 2026-01-20
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "202601200001"
down_revision = "202601190003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sync_sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column(
            "preview_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "decisions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sync_sessions")),
    )
    op.create_index("idx_sync_sessions_status", "sync_sessions", ["status"], unique=False)
    op.create_index("idx_sync_sessions_expires_at", "sync_sessions", ["expires_at"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_sync_sessions_expires_at", table_name="sync_sessions")
    op.drop_index("idx_sync_sessions_status", table_name="sync_sessions")
    op.drop_table("sync_sessions")
