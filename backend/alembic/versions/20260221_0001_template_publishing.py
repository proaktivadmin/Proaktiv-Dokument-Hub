"""Add template publishing workflow columns

Revision ID: 20260221_0001
Revises: 20260201_0001
Create Date: 2026-02-21
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260221_0001"
down_revision = "20260201_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Idempotent: columns may already exist from manual Railway application.
    # Using raw SQL with ADD COLUMN IF NOT EXISTS for safety.
    conn = op.get_bind()

    conn.execute(sa.text(
        "ALTER TABLE templates ADD COLUMN IF NOT EXISTS workflow_status VARCHAR(20) NOT NULL DEFAULT 'draft'"
    ))
    conn.execute(sa.text(
        "ALTER TABLE templates ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMPTZ"
    ))
    conn.execute(sa.text(
        "ALTER TABLE templates ADD COLUMN IF NOT EXISTS reviewed_by VARCHAR(100)"
    ))
    conn.execute(sa.text(
        "ALTER TABLE templates ADD COLUMN IF NOT EXISTS published_version INTEGER"
    ))
    conn.execute(sa.text(
        "ALTER TABLE templates ADD COLUMN IF NOT EXISTS is_archived_legacy BOOLEAN NOT NULL DEFAULT false"
    ))
    conn.execute(sa.text(
        "ALTER TABLE templates ADD COLUMN IF NOT EXISTS origin VARCHAR(30)"
    ))
    conn.execute(sa.text(
        "ALTER TABLE templates ADD COLUMN IF NOT EXISTS vitec_source_hash VARCHAR(64)"
    ))
    conn.execute(sa.text(
        "ALTER TABLE templates ADD COLUMN IF NOT EXISTS ckeditor_validated BOOLEAN NOT NULL DEFAULT false"
    ))
    conn.execute(sa.text(
        "ALTER TABLE templates ADD COLUMN IF NOT EXISTS ckeditor_validated_at TIMESTAMPTZ"
    ))
    conn.execute(sa.text(
        "ALTER TABLE templates ADD COLUMN IF NOT EXISTS property_types JSONB"
    ))

    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_templates_workflow_status ON templates (workflow_status)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_templates_origin ON templates (origin)"
    ))

    conn.execute(sa.text(
        "UPDATE templates SET workflow_status = status WHERE workflow_status = 'draft' AND status != 'draft'"
    ))


def downgrade() -> None:
    op.drop_index("idx_templates_origin", table_name="templates")
    op.drop_index("idx_templates_workflow_status", table_name="templates")

    op.drop_column("templates", "property_types")
    op.drop_column("templates", "ckeditor_validated_at")
    op.drop_column("templates", "ckeditor_validated")
    op.drop_column("templates", "vitec_source_hash")
    op.drop_column("templates", "origin")
    op.drop_column("templates", "is_archived_legacy")
    op.drop_column("templates", "published_version")
    op.drop_column("templates", "reviewed_by")
    op.drop_column("templates", "reviewed_at")
    op.drop_column("templates", "workflow_status")
