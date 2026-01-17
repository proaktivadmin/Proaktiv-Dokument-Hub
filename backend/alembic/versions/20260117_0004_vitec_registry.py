"""Add VitecTemplateRegistry table for inventory tracking

Revision ID: 0007
Revises: 0006
Create Date: 2026-01-17 14:00:00.000000

This migration creates the vitec_template_registry table to track
the inventory of Vitec Next templates and their sync status.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0007'
down_revision: str = '0006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'vitec_template_registry',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, 
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('vitec_name', sa.String(255), nullable=False, unique=True,
                  comment='Official Vitec template name'),
        sa.Column('vitec_type', sa.String(50), nullable=False,
                  comment='Template type: Objekt/Kontakt, System'),
        sa.Column('vitec_phase', sa.String(50), nullable=True,
                  comment='Primary phase: Innsalg, Til salgs, etc.'),
        sa.Column('vitec_category', sa.String(100), nullable=True,
                  comment='Vitec document category'),
        sa.Column('vitec_channel', sa.String(20), nullable=True,
                  comment='Channel: pdf, email, sms'),
        sa.Column('description', sa.Text(), nullable=True,
                  comment='Description of the template purpose'),
        sa.Column('local_template_id', postgresql.UUID(as_uuid=True), nullable=True,
                  comment='FK to local template if synced'),
        sa.Column('sync_status', sa.String(20), nullable=False, default='missing',
                  comment='Status: synced, missing, modified, local_only'),
        sa.Column('last_checked', sa.DateTime(timezone=True), nullable=True,
                  comment='Last time sync status was checked'),
        sa.Column('created_at', sa.DateTime(timezone=True), 
                  server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), onupdate=sa.func.now()),
        
        # Foreign key
        sa.ForeignKeyConstraint(['local_template_id'], ['templates.id'],
                               ondelete='SET NULL'),
    )
    
    # Create indexes
    op.create_index('idx_vitec_registry_name', 'vitec_template_registry', ['vitec_name'])
    op.create_index('idx_vitec_registry_type', 'vitec_template_registry', ['vitec_type'])
    op.create_index('idx_vitec_registry_phase', 'vitec_template_registry', ['vitec_phase'])
    op.create_index('idx_vitec_registry_sync_status', 'vitec_template_registry', ['sync_status'])
    op.create_index('idx_vitec_registry_local_template', 'vitec_template_registry', ['local_template_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_vitec_registry_local_template', 'vitec_template_registry')
    op.drop_index('idx_vitec_registry_sync_status', 'vitec_template_registry')
    op.drop_index('idx_vitec_registry_phase', 'vitec_template_registry')
    op.drop_index('idx_vitec_registry_type', 'vitec_template_registry')
    op.drop_index('idx_vitec_registry_name', 'vitec_template_registry')
    
    # Drop table
    op.drop_table('vitec_template_registry')
