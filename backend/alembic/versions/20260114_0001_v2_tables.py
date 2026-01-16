"""V2 Tables - Vitec Metadata, Merge Fields, Code Patterns, Layout Partials

Revision ID: 0003
Revises: 0002
Create Date: 2026-01-14

Creates V2 database schema:
- Adds Vitec metadata fields to templates table
- Creates merge_fields table for Flettekode system
- Creates code_patterns table for reusable HTML snippets
- Creates layout_partials table for headers/footers
- Seeds initial merge fields from common Vitec patterns
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ===========================================================================
    # Migration 1: Add Vitec metadata fields to templates table
    # ===========================================================================
    op.add_column('templates', sa.Column('preview_thumbnail_url', sa.Text(), nullable=True))
    op.add_column('templates', sa.Column('channel', sa.String(20), nullable=False, server_default='pdf_email'))
    op.add_column('templates', sa.Column('template_type', sa.String(50), nullable=True, server_default='Objekt/Kontakt'))
    op.add_column('templates', sa.Column('receiver_type', sa.String(50), nullable=True))
    op.add_column('templates', sa.Column('receiver', sa.String(100), nullable=True))
    op.add_column('templates', sa.Column('extra_receivers', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'))
    op.add_column('templates', sa.Column('phases', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'))
    op.add_column('templates', sa.Column('assignment_types', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'))
    op.add_column('templates', sa.Column('ownership_types', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'))
    op.add_column('templates', sa.Column('departments', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'))
    op.add_column('templates', sa.Column('email_subject', sa.String(500), nullable=True))
    op.add_column('templates', sa.Column('header_template_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('templates', sa.Column('footer_template_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('templates', sa.Column('margin_top', sa.Numeric(precision=4, scale=2), nullable=False, server_default='1.5'))
    op.add_column('templates', sa.Column('margin_bottom', sa.Numeric(precision=4, scale=2), nullable=False, server_default='1.0'))
    op.add_column('templates', sa.Column('margin_left', sa.Numeric(precision=4, scale=2), nullable=False, server_default='1.0'))
    op.add_column('templates', sa.Column('margin_right', sa.Numeric(precision=4, scale=2), nullable=False, server_default='1.2'))
    
    # Create index for channel filtering
    op.create_index('idx_templates_channel', 'templates', ['channel'], unique=False)

    # ===========================================================================
    # Migration 2: Create merge_fields table
    # ===========================================================================
    op.create_table(
        'merge_fields',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('path', sa.String(200), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('label', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('example_value', sa.String(500), nullable=True),
        sa.Column('data_type', sa.String(50), nullable=False, server_default='string'),
        sa.Column('is_iterable', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('parent_model', sa.String(100), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_merge_fields')),
        sa.UniqueConstraint('path', name=op.f('uq_merge_fields_path'))
    )
    op.create_index('idx_merge_fields_category', 'merge_fields', ['category'], unique=False)
    op.create_index('idx_merge_fields_path', 'merge_fields', ['path'], unique=False)
    op.create_index('idx_merge_fields_parent_model', 'merge_fields', ['parent_model'], unique=False)

    # ===========================================================================
    # Migration 3: Create code_patterns table
    # ===========================================================================
    op.create_table(
        'code_patterns',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('html_code', sa.Text(), nullable=False),
        sa.Column('variables_used', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('preview_thumbnail_url', sa.Text(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_by', sa.String(255), nullable=False),
        sa.Column('updated_by', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_code_patterns'))
    )
    op.create_index('idx_code_patterns_category', 'code_patterns', ['category'], unique=False)
    op.create_index('idx_code_patterns_name', 'code_patterns', ['name'], unique=False)

    # ===========================================================================
    # Migration 4: Create layout_partials table
    # ===========================================================================
    op.create_table(
        'layout_partials',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('context', sa.String(50), nullable=False, server_default='all'),
        sa.Column('html_content', sa.Text(), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_by', sa.String(255), nullable=False),
        sa.Column('updated_by', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_layout_partials')),
        sa.CheckConstraint("type IN ('header', 'footer')", name='ck_layout_partial_type'),
        sa.CheckConstraint("context IN ('pdf', 'email', 'all')", name='ck_layout_partial_context')
    )
    op.create_index('idx_layout_partials_type', 'layout_partials', ['type'], unique=False)
    op.create_index('idx_layout_partials_context', 'layout_partials', ['context'], unique=False)
    op.create_index('idx_layout_partials_is_default', 'layout_partials', ['is_default'], unique=False)

    # Add foreign key constraints to templates for header/footer
    op.create_foreign_key(
        'fk_templates_header_template_id',
        'templates', 'layout_partials',
        ['header_template_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_templates_footer_template_id',
        'templates', 'layout_partials',
        ['footer_template_id'], ['id'],
        ondelete='SET NULL'
    )

    # ===========================================================================
    # Migration 5: Seed initial merge fields
    # ===========================================================================
    merge_fields_table = sa.table(
        'merge_fields',
        sa.column('path', sa.String),
        sa.column('category', sa.String),
        sa.column('label', sa.String),
        sa.column('description', sa.Text),
        sa.column('example_value', sa.String),
        sa.column('data_type', sa.String),
        sa.column('is_iterable', sa.Boolean),
        sa.column('parent_model', sa.String)
    )
    
    # Seed data
    op.bulk_insert(merge_fields_table, [
        # Selger fields
        {'path': 'selger.navnutenfullmektigogkontaktperson', 'category': 'Selger', 'label': 'Navn (Full)', 'description': 'Navn uten fullmektig', 'example_value': 'Ola Nordmann', 'data_type': 'string', 'is_iterable': True, 'parent_model': 'Model.selgere'},
        {'path': 'selger.hovedgatenavnognr', 'category': 'Selger', 'label': 'Adresse', 'description': 'Gate og nr', 'example_value': 'Storgata 1', 'data_type': 'string', 'is_iterable': True, 'parent_model': 'Model.selgere'},
        {'path': 'selger.hovedpostnr', 'category': 'Selger', 'label': 'Postnummer', 'description': 'Postnummer', 'example_value': '0123', 'data_type': 'string', 'is_iterable': True, 'parent_model': 'Model.selgere'},
        {'path': 'selger.hovedpoststed', 'category': 'Selger', 'label': 'Poststed', 'description': 'Poststed', 'example_value': 'Oslo', 'data_type': 'string', 'is_iterable': True, 'parent_model': 'Model.selgere'},
        {'path': 'selger.emailadresse', 'category': 'Selger', 'label': 'E-post', 'description': 'Email adresse', 'example_value': 'ola@example.com', 'data_type': 'string', 'is_iterable': True, 'parent_model': 'Model.selgere'},
        {'path': 'selger.hovedtlf', 'category': 'Selger', 'label': 'Telefon', 'description': 'Hovedtelefon', 'example_value': '+47 123 45 678', 'data_type': 'string', 'is_iterable': True, 'parent_model': 'Model.selgere'},
        {'path': 'selger.idnummer', 'category': 'Selger', 'label': 'Fødselsnr', 'description': 'ID nummer', 'example_value': '010180*****', 'data_type': 'string', 'is_iterable': True, 'parent_model': 'Model.selgere'},
        
        # Eiendom fields
        {'path': 'eiendom.gatenavnognr', 'category': 'Eiendom', 'label': 'Adresse', 'description': 'Gatenavn og nr', 'example_value': 'Parkveien 10', 'data_type': 'string', 'is_iterable': False, 'parent_model': 'Model.eiendom'},
        {'path': 'eiendom.postnr', 'category': 'Eiendom', 'label': 'Postnummer', 'description': 'Postnummer', 'example_value': '0350', 'data_type': 'string', 'is_iterable': False, 'parent_model': 'Model.eiendom'},
        {'path': 'eiendom.poststed', 'category': 'Eiendom', 'label': 'Poststed', 'description': 'Poststed', 'example_value': 'Oslo', 'data_type': 'string', 'is_iterable': False, 'parent_model': 'Model.eiendom'},
        {'path': 'komplettmatrikkelutvidet', 'category': 'Eiendom', 'label': 'Matrikkel', 'description': 'Komplett matrikkel', 'example_value': 'Gnr 1 Bnr 23', 'data_type': 'string', 'is_iterable': False, 'parent_model': None},
        {'path': 'eiendom.boligtype', 'category': 'Eiendom', 'label': 'Boligtype', 'description': 'Type bolig', 'example_value': 'Leilighet', 'data_type': 'string', 'is_iterable': False, 'parent_model': 'Model.eiendom'},
        {'path': 'eiendom.pris', 'category': 'Eiendom', 'label': 'Prisantydning', 'description': 'Pris', 'example_value': '5 900 000', 'data_type': 'number', 'is_iterable': False, 'parent_model': 'Model.eiendom'},
        
        # Megler fields
        {'path': 'ansvarligmegler.navn', 'category': 'Megler', 'label': 'Ansvarlig Navn', 'description': 'Megler navn', 'example_value': 'Kari Meglersen', 'data_type': 'string', 'is_iterable': False, 'parent_model': 'Model.ansvarligmegler'},
        {'path': 'ansvarligmegler.tittel', 'category': 'Megler', 'label': 'Ansvarlig Tittel', 'description': 'Megler tittel', 'example_value': 'Eiendomsmegler MNEF', 'data_type': 'string', 'is_iterable': False, 'parent_model': 'Model.ansvarligmegler'},
        {'path': 'meglerkontor.markedsforingsnavn', 'category': 'Megler', 'label': 'Kontor Navn', 'description': 'Markedsføringsnavn', 'example_value': 'Proaktiv Eiendom AS', 'data_type': 'string', 'is_iterable': False, 'parent_model': 'Model.meglerkontor'},
        {'path': 'meglerkontor.besoksadresse', 'category': 'Megler', 'label': 'Kontor Adresse', 'description': 'Besøksadresse', 'example_value': 'Torggata 5, Oslo', 'data_type': 'string', 'is_iterable': False, 'parent_model': 'Model.meglerkontor'},
        {'path': 'oppgjor.kontornavn', 'category': 'Megler', 'label': 'Oppgjør Navn', 'description': 'Oppgjørsavdeling', 'example_value': 'Proaktiv Oppgjør', 'data_type': 'string', 'is_iterable': False, 'parent_model': 'Model.oppgjor'},
        
        # Økonomi fields
        {'path': 'oppdrag.provisjonprosent', 'category': 'Økonomi', 'label': 'Provisjon %', 'description': 'Sats', 'example_value': '2.5', 'data_type': 'number', 'is_iterable': False, 'parent_model': 'Model.oppdrag'},
        {'path': 'oppdrag.selgersamletsum', 'category': 'Økonomi', 'label': 'Samlet Sum', 'description': 'Selger samlet sum', 'example_value': '125 000', 'data_type': 'number', 'is_iterable': False, 'parent_model': 'Model.oppdrag'},
        {'path': 'oppdrag.selgerutleggsum', 'category': 'Økonomi', 'label': 'Utlegg Sum', 'description': 'Sum utlegg', 'example_value': '25 000', 'data_type': 'number', 'is_iterable': False, 'parent_model': 'Model.oppdrag'},
    ])


def downgrade() -> None:
    # Drop foreign keys first
    op.drop_constraint('fk_templates_footer_template_id', 'templates', type_='foreignkey')
    op.drop_constraint('fk_templates_header_template_id', 'templates', type_='foreignkey')
    
    # Drop new tables
    op.drop_table('layout_partials')
    op.drop_table('code_patterns')
    op.drop_table('merge_fields')
    
    # Remove Vitec metadata columns from templates
    op.drop_index('idx_templates_channel', table_name='templates')
    op.drop_column('templates', 'margin_right')
    op.drop_column('templates', 'margin_left')
    op.drop_column('templates', 'margin_bottom')
    op.drop_column('templates', 'margin_top')
    op.drop_column('templates', 'footer_template_id')
    op.drop_column('templates', 'header_template_id')
    op.drop_column('templates', 'email_subject')
    op.drop_column('templates', 'departments')
    op.drop_column('templates', 'ownership_types')
    op.drop_column('templates', 'assignment_types')
    op.drop_column('templates', 'phases')
    op.drop_column('templates', 'extra_receivers')
    op.drop_column('templates', 'receiver')
    op.drop_column('templates', 'receiver_type')
    op.drop_column('templates', 'template_type')
    op.drop_column('templates', 'channel')
    op.drop_column('templates', 'preview_thumbnail_url')
