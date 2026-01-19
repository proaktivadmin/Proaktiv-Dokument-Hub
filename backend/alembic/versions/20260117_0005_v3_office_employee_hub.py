"""V3 Office & Employee Hub - Core Tables

Revision ID: 0008
Revises: 0007
Create Date: 2026-01-17

Creates V3 database schema:
- Creates offices table for office locations
- Creates employees table for staff management
- Creates external_listings table for third-party tracking
- Creates checklist_templates table for onboarding/offboarding templates
- Creates checklist_instances table for assigned checklists
- Creates company_assets table for scoped file storage
- Creates postal_codes table for territory mapping
- Creates office_territories table for postal code allocations
- Creates layout_partial_versions table for versioning
- Creates layout_partial_defaults table for assignment rules
- Adds vitec_id to categories table
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0008'
down_revision: Union[str, None] = '0007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ===========================================================================
    # Migration 1: Add vitec_id to categories table
    # ===========================================================================
    op.add_column('categories', sa.Column('vitec_id', sa.Integer(), nullable=True))
    op.create_index('idx_categories_vitec_id', 'categories', ['vitec_id'], unique=True)

    # ===========================================================================
    # Migration 2: Create offices table
    # ===========================================================================
    op.create_table(
        'offices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('short_code', sa.String(10), nullable=False),
        
        # Contact
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        
        # Address
        sa.Column('street_address', sa.String(255), nullable=True),
        sa.Column('postal_code', sa.String(10), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        
        # Online Presence
        sa.Column('homepage_url', sa.Text(), nullable=True),
        sa.Column('google_my_business_url', sa.Text(), nullable=True),
        sa.Column('facebook_url', sa.Text(), nullable=True),
        sa.Column('instagram_url', sa.Text(), nullable=True),
        sa.Column('linkedin_url', sa.Text(), nullable=True),
        
        # Territory Map Color
        sa.Column('color', sa.String(7), nullable=False, server_default='#4A90D9'),
        
        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id', name=op.f('pk_offices')),
        sa.UniqueConstraint('short_code', name=op.f('uq_offices_short_code'))
    )
    op.create_index('idx_offices_city', 'offices', ['city'], unique=False)
    op.create_index('idx_offices_is_active', 'offices', ['is_active'], unique=False)

    # ===========================================================================
    # Migration 3: Create employees table
    # ===========================================================================
    op.create_table(
        'employees',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('office_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Basic Info
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('title', sa.String(100), nullable=True),
        
        # Contact
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        
        # Online Presence
        sa.Column('homepage_profile_url', sa.Text(), nullable=True),
        sa.Column('linkedin_url', sa.Text(), nullable=True),
        
        # Employment Lifecycle
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        
        # Offboarding Timeline
        sa.Column('hide_from_homepage_date', sa.Date(), nullable=True),
        sa.Column('delete_data_date', sa.Date(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id', name=op.f('pk_employees')),
        sa.ForeignKeyConstraint(['office_id'], ['offices.id'], name=op.f('fk_employees_office_id'), ondelete='CASCADE'),
        sa.CheckConstraint("status IN ('active', 'onboarding', 'offboarding', 'inactive')", name='ck_employees_status')
    )
    op.create_index('idx_employees_office_id', 'employees', ['office_id'], unique=False)
    op.create_index('idx_employees_status', 'employees', ['status'], unique=False)
    op.create_index('idx_employees_email', 'employees', ['email'], unique=False)

    # ===========================================================================
    # Migration 4: Create external_listings table
    # ===========================================================================
    op.create_table(
        'external_listings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        
        # Link to office or employee (one must be set)
        sa.Column('office_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=True),
        
        # Listing Details
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('listing_url', sa.Text(), nullable=False),
        sa.Column('listing_type', sa.String(20), nullable=False, server_default='office'),
        
        # Verification
        sa.Column('status', sa.String(20), nullable=False, server_default='pending_check'),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_verified_by', sa.String(255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id', name=op.f('pk_external_listings')),
        sa.ForeignKeyConstraint(['office_id'], ['offices.id'], name=op.f('fk_external_listings_office_id'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], name=op.f('fk_external_listings_employee_id'), ondelete='CASCADE'),
        sa.CheckConstraint("source IN ('anbudstjenester', 'finn', 'nummeropplysning', '1881', 'gulesider', 'google', 'other')", name='ck_external_listings_source'),
        sa.CheckConstraint("listing_type IN ('office', 'broker', 'company')", name='ck_external_listings_type'),
        sa.CheckConstraint("status IN ('verified', 'needs_update', 'pending_check', 'removed')", name='ck_external_listings_status')
    )
    op.create_index('idx_external_listings_office_id', 'external_listings', ['office_id'], unique=False)
    op.create_index('idx_external_listings_employee_id', 'external_listings', ['employee_id'], unique=False)
    op.create_index('idx_external_listings_status', 'external_listings', ['status'], unique=False)

    # ===========================================================================
    # Migration 5: Create checklist_templates table
    # ===========================================================================
    op.create_table(
        'checklist_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('items', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id', name=op.f('pk_checklist_templates')),
        sa.CheckConstraint("type IN ('onboarding', 'offboarding')", name='ck_checklist_templates_type')
    )
    op.create_index('idx_checklist_templates_type', 'checklist_templates', ['type'], unique=False)

    # ===========================================================================
    # Migration 6: Create checklist_instances table
    # ===========================================================================
    op.create_table(
        'checklist_instances',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='in_progress'),
        sa.Column('items_completed', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id', name=op.f('pk_checklist_instances')),
        sa.ForeignKeyConstraint(['template_id'], ['checklist_templates.id'], name=op.f('fk_checklist_instances_template_id'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], name=op.f('fk_checklist_instances_employee_id'), ondelete='CASCADE'),
        sa.CheckConstraint("status IN ('in_progress', 'completed', 'cancelled')", name='ck_checklist_instances_status')
    )
    op.create_index('idx_checklist_instances_employee_id', 'checklist_instances', ['employee_id'], unique=False)
    op.create_index('idx_checklist_instances_status', 'checklist_instances', ['status'], unique=False)

    # ===========================================================================
    # Migration 7: Create company_assets table
    # ===========================================================================
    op.create_table(
        'company_assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        
        # Ownership (one of these defines scope)
        sa.Column('office_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_global', sa.Boolean(), nullable=False, server_default='false'),
        
        # File Info
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('category', sa.String(50), nullable=False, server_default='other'),
        sa.Column('content_type', sa.String(100), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('storage_path', sa.Text(), nullable=False),  # WebDAV or blob path
        
        # Metadata
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id', name=op.f('pk_company_assets')),
        sa.ForeignKeyConstraint(['office_id'], ['offices.id'], name=op.f('fk_company_assets_office_id'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], name=op.f('fk_company_assets_employee_id'), ondelete='CASCADE'),
        sa.CheckConstraint("category IN ('logo', 'photo', 'marketing', 'document', 'other')", name='ck_company_assets_category')
    )
    op.create_index('idx_company_assets_office_id', 'company_assets', ['office_id'], unique=False)
    op.create_index('idx_company_assets_employee_id', 'company_assets', ['employee_id'], unique=False)
    op.create_index('idx_company_assets_category', 'company_assets', ['category'], unique=False)
    op.create_index('idx_company_assets_is_global', 'company_assets', ['is_global'], unique=False)

    # ===========================================================================
    # Migration 8: Create postal_codes table
    # ===========================================================================
    op.create_table(
        'postal_codes',
        sa.Column('postal_code', sa.String(10), nullable=False),
        sa.Column('postal_name', sa.String(100), nullable=False),
        sa.Column('municipality_code', sa.String(10), nullable=True),
        sa.Column('municipality_name', sa.String(100), nullable=True),
        sa.Column('category', sa.String(10), nullable=True),  # 'G' (street), 'B' (PO box), etc.
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('postal_code', name=op.f('pk_postal_codes'))
    )
    op.create_index('idx_postal_codes_municipality', 'postal_codes', ['municipality_code'], unique=False)

    # ===========================================================================
    # Migration 9: Create office_territories table
    # ===========================================================================
    op.create_table(
        'office_territories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('office_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('postal_code', sa.String(10), nullable=False),
        sa.Column('source', sa.String(50), nullable=False, server_default='vitec_next'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_blacklisted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('valid_from', sa.Date(), nullable=True),
        sa.Column('valid_to', sa.Date(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id', name=op.f('pk_office_territories')),
        sa.ForeignKeyConstraint(['office_id'], ['offices.id'], name=op.f('fk_office_territories_office_id'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['postal_code'], ['postal_codes.postal_code'], name=op.f('fk_office_territories_postal_code'), ondelete='CASCADE'),
        sa.CheckConstraint("source IN ('vitec_next', 'finn', 'anbudstjenester', 'homepage', 'other')", name='ck_office_territories_source'),
        sa.UniqueConstraint('office_id', 'postal_code', 'source', name='uq_office_territory_source')
    )
    op.create_index('idx_office_territories_office_id', 'office_territories', ['office_id'], unique=False)
    op.create_index('idx_office_territories_postal_code', 'office_territories', ['postal_code'], unique=False)
    op.create_index('idx_office_territories_source', 'office_territories', ['source'], unique=False)

    # ===========================================================================
    # Migration 10: Create layout_partial_versions table
    # ===========================================================================
    op.create_table(
        'layout_partial_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('partial_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('html_content', sa.Text(), nullable=False),
        sa.Column('change_notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(255), nullable=False),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id', name=op.f('pk_layout_partial_versions')),
        sa.ForeignKeyConstraint(['partial_id'], ['layout_partials.id'], name=op.f('fk_layout_partial_versions_partial_id'), ondelete='CASCADE'),
        sa.UniqueConstraint('partial_id', 'version_number', name='uq_layout_partial_version')
    )
    op.create_index('idx_layout_partial_versions_partial_id', 'layout_partial_versions', ['partial_id'], unique=False)

    # ===========================================================================
    # Migration 11: Create layout_partial_defaults table
    # ===========================================================================
    op.create_table(
        'layout_partial_defaults',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('partial_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scope', sa.String(20), nullable=False, server_default='all'),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('medium', sa.String(10), nullable=True),  # 'pdf', 'email', 'sms'
        sa.Column('priority', sa.Integer(), nullable=False, server_default='1'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id', name=op.f('pk_layout_partial_defaults')),
        sa.ForeignKeyConstraint(['partial_id'], ['layout_partials.id'], name=op.f('fk_layout_partial_defaults_partial_id'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name=op.f('fk_layout_partial_defaults_category_id'), ondelete='CASCADE'),
        sa.CheckConstraint("scope IN ('all', 'category', 'medium')", name='ck_layout_partial_defaults_scope'),
        sa.CheckConstraint("medium IS NULL OR medium IN ('pdf', 'email', 'sms')", name='ck_layout_partial_defaults_medium')
    )
    op.create_index('idx_layout_partial_defaults_partial_id', 'layout_partial_defaults', ['partial_id'], unique=False)
    op.create_index('idx_layout_partial_defaults_scope', 'layout_partial_defaults', ['scope'], unique=False)

    # ===========================================================================
    # Migration 12: Update layout_partials type constraint for 'signature' and 'stilark'
    # ===========================================================================
    # Drop old constraint (was renamed to _v2 in migration 0006) and add new one with additional types
    op.drop_constraint('ck_layout_partial_type_v2', 'layout_partials', type_='check')
    op.create_check_constraint(
        'ck_layout_partial_type_v3',
        'layout_partials',
        "type IN ('header', 'footer', 'signature', 'stilark')"
    )


def downgrade() -> None:
    # Restore old layout_partials type constraint (revert to _v2 name)
    op.drop_constraint('ck_layout_partial_type_v3', 'layout_partials', type_='check')
    op.create_check_constraint(
        'ck_layout_partial_type_v2',
        'layout_partials',
        "type IN ('header', 'footer', 'signature')"
    )
    
    # Drop new tables in reverse order
    op.drop_table('layout_partial_defaults')
    op.drop_table('layout_partial_versions')
    op.drop_table('office_territories')
    op.drop_table('postal_codes')
    op.drop_table('company_assets')
    op.drop_table('checklist_instances')
    op.drop_table('checklist_templates')
    op.drop_table('external_listings')
    op.drop_table('employees')
    op.drop_table('offices')
    
    # Remove vitec_id from categories
    op.drop_index('idx_categories_vitec_id', table_name='categories')
    op.drop_column('categories', 'vitec_id')
