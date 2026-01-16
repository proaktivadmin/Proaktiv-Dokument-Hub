"""Fix vitec_merge_fields column type from text[] to JSONB

Revision ID: 0005
Revises: 0004
Create Date: 2026-01-17 01:00:00.000000

The vitec_merge_fields column was created as text[] in the initial migration,
but the SQLAlchemy model expects JSONB. This migration converts the column type.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0005'
down_revision: str = '0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Convert vitec_merge_fields from text[] to JSONB."""
    # Step 1: Add a temporary JSONB column
    op.add_column('templates', sa.Column('vitec_merge_fields_new', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    # Step 2: Migrate data from text[] to JSONB
    # Convert the text array to a JSON array
    op.execute("""
        UPDATE templates 
        SET vitec_merge_fields_new = COALESCE(
            (SELECT jsonb_agg(elem) FROM unnest(vitec_merge_fields) AS elem),
            '[]'::jsonb
        )
        WHERE vitec_merge_fields IS NOT NULL
    """)
    
    # Step 3: Drop the old column
    op.drop_column('templates', 'vitec_merge_fields')
    
    # Step 4: Rename the new column to the original name
    op.alter_column('templates', 'vitec_merge_fields_new', new_column_name='vitec_merge_fields')


def downgrade() -> None:
    """Revert vitec_merge_fields from JSONB back to text[]."""
    # Step 1: Add a temporary text[] column
    op.add_column('templates', sa.Column('vitec_merge_fields_old', postgresql.ARRAY(sa.Text()), nullable=True))
    
    # Step 2: Migrate data from JSONB to text[]
    op.execute("""
        UPDATE templates 
        SET vitec_merge_fields_old = ARRAY(
            SELECT jsonb_array_elements_text(vitec_merge_fields)
        )
        WHERE vitec_merge_fields IS NOT NULL
    """)
    
    # Step 3: Drop the JSONB column
    op.drop_column('templates', 'vitec_merge_fields')
    
    # Step 4: Rename the old column back
    op.alter_column('templates', 'vitec_merge_fields_old', new_column_name='vitec_merge_fields')
