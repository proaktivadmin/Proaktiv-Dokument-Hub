"""Fix JSONB columns that were created as text[] arrays

Revision ID: 20260117_0001
Revises: 20260114_0001
Create Date: 2026-01-17 00:30:00.000000

This migration converts the text[] columns to JSONB to match the
cross-database compatible JSONType adapter.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0004'
down_revision: str = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Convert text[] columns to jsonb in templates table
    # First, drop the default and convert the data
    
    # vitec_merge_fields: text[] -> jsonb
    op.execute("""
        ALTER TABLE templates 
        ALTER COLUMN vitec_merge_fields TYPE jsonb 
        USING COALESCE(to_jsonb(vitec_merge_fields), '[]'::jsonb)
    """)
    
    # phases: text[] -> jsonb
    op.execute("""
        ALTER TABLE templates 
        ALTER COLUMN phases TYPE jsonb 
        USING COALESCE(to_jsonb(phases), '[]'::jsonb)
    """)
    
    # departments: text[] -> jsonb
    op.execute("""
        ALTER TABLE templates 
        ALTER COLUMN departments TYPE jsonb 
        USING COALESCE(to_jsonb(departments), '[]'::jsonb)
    """)
    
    # receiver_types: text[] -> jsonb
    op.execute("""
        ALTER TABLE templates 
        ALTER COLUMN receiver_types TYPE jsonb 
        USING COALESCE(to_jsonb(receiver_types), '[]'::jsonb)
    """)


def downgrade() -> None:
    # Convert back to text[] if needed (data loss may occur for complex JSON)
    op.execute("""
        ALTER TABLE templates 
        ALTER COLUMN vitec_merge_fields TYPE text[] 
        USING ARRAY(SELECT jsonb_array_elements_text(COALESCE(vitec_merge_fields, '[]'::jsonb)))
    """)
    
    op.execute("""
        ALTER TABLE templates 
        ALTER COLUMN phases TYPE text[] 
        USING ARRAY(SELECT jsonb_array_elements_text(COALESCE(phases, '[]'::jsonb)))
    """)
    
    op.execute("""
        ALTER TABLE templates 
        ALTER COLUMN departments TYPE text[] 
        USING ARRAY(SELECT jsonb_array_elements_text(COALESCE(departments, '[]'::jsonb)))
    """)
    
    op.execute("""
        ALTER TABLE templates 
        ALTER COLUMN receiver_types TYPE text[] 
        USING ARRAY(SELECT jsonb_array_elements_text(COALESCE(receiver_types, '[]'::jsonb)))
    """)
