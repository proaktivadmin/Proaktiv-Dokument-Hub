"""Add notifications table

Revision ID: 20260124_0003
Revises: 20260124_0002
Create Date: 2026-01-24
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260124_0003"
down_revision = "20260124_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="info"),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notifications")),
    )
    op.create_index("idx_notifications_unread", "notifications", ["is_read"], unique=False)
    op.create_index("idx_notifications_created", "notifications", ["created_at"], unique=False)
    op.create_index("idx_notifications_type", "notifications", ["type"], unique=False)
    op.create_index("idx_notifications_entity", "notifications", ["entity_type", "entity_id"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_notifications_entity", table_name="notifications")
    op.drop_index("idx_notifications_type", table_name="notifications")
    op.drop_index("idx_notifications_created", table_name="notifications")
    op.drop_index("idx_notifications_unread", table_name="notifications")
    op.drop_table("notifications")
